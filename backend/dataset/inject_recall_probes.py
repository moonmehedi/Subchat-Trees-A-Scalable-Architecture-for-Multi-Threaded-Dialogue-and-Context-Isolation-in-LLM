#!/usr/bin/env python3
"""
Inject Recall Probes into Merged Scenario JSON

Reads merged_realistic_interleaved.json, identifies topics with ≥3 turns,
builds reference text (user + assistant messages concatenated) per topic,
maps each topic to its primary subchat node_type, and appends recall probe
steps starting from step 310.

Each probe step:
  - is_recall_probe: true
  - action: "switch_node"
  - node_type: correct subchat or "main"
  - message: "Summarize everything we discussed about {topic}..."
  - reference_text: all user messages for that topic (for BLEU/ROUGE scoring)
  - reference_conversations: list of {role, message} dicts for detailed logging
  - expected: "recall_probe:{topic}"
"""

import json
import re
from pathlib import Path
from collections import defaultdict


MIN_TURNS = 3  # Minimum turns to be eligible for a recall probe


def normalize_context_to_topic(context: str) -> str:
    """Normalize a context string to its base topic name (mirrors runner logic)."""
    if not context or context in ("intro", "step_1"):
        return "general"
    base = context
    for pattern in [r"_step\d+", r"_intro", r"_final", r"_\d+$"]:
        base = re.sub(pattern, "", base)
    return base.rstrip("_") or "general"


def inject_recall_probes(scenario_path: str, output_path: str = None, min_turns: int = MIN_TURNS) -> dict:
    """
    Read the merged scenario JSON, append recall probe steps, and write back.

    Args:
        scenario_path: Path to the merged scenario JSON file
        output_path: Optional output path (defaults to overwriting the input file)
        min_turns: Minimum number of user turns a topic needs to be eligible

    Returns:
        Dict with injection stats: {topics_injected, topics_skipped, first_probe_step, last_probe_step}
    """
    scenario_path = Path(scenario_path)
    if output_path is None:
        output_path = scenario_path  # overwrite in-place
    else:
        output_path = Path(output_path)

    with open(scenario_path, "r") as f:
        scenario = json.load(f)

    conversations = scenario.get("conversations", [])

    # ── 1. Remove any previously injected probes ──────────────────────────
    original_conversations = [s for s in conversations if not s.get("is_recall_probe", False)]

    # ── 2. Build per-topic data ───────────────────────────────────────────
    #  topic -> {user_messages: [...], node_types: set(), conversations: [{role, msg}]}
    topic_data = defaultdict(lambda: {
        "user_messages": [],
        "node_types": set(),
        "conversations": [],  # (role, message) pairs for detailed logging
    })

    for step_data in original_conversations:
        context = step_data.get("context", "")
        if not context or context in ("intro", "step_1"):
            continue
        topic = normalize_context_to_topic(context)
        if topic == "general":
            continue

        node_type = step_data.get("node_type", "main")
        message = step_data.get("message", "")
        expected = step_data.get("expected", "")

        topic_data[topic]["node_types"].add(node_type)
        topic_data[topic]["user_messages"].append(message)
        # Store the user message for reference conversations
        topic_data[topic]["conversations"].append({
            "role": "user",
            "message": message,
            "step": step_data.get("step", 0)
        })
        # Store expected (acts as approximate assistant response description)
        if expected:
            topic_data[topic]["conversations"].append({
                "role": "expected",
                "message": expected,
                "step": step_data.get("step", 0)
            })

    # ── 3. Identify eligible topics and their primary subchat ─────────────
    eligible_topics = {}
    skipped_topics = []

    for topic, data in sorted(topic_data.items()):
        n_turns = len(data["user_messages"])
        if n_turns < min_turns:
            skipped_topics.append((topic, n_turns))
            continue

        # Find the primary subchat node_type (prefer subchat over main)
        subchat_nodes = [nt for nt in data["node_types"] if nt != "main"]
        if subchat_nodes:
            # Pick the most specific (longest name = deepest nested subchat)
            primary_node = max(subchat_nodes, key=len)
        else:
            primary_node = "main"

        eligible_topics[topic] = {
            "primary_node": primary_node,
            "n_turns": n_turns,
            "reference_text": " ".join(data["user_messages"]),
            "reference_conversations": data["conversations"],
            "is_main_only": primary_node == "main",
        }

    # ── 4. Build probe steps ──────────────────────────────────────────────
    last_original_step = max((s.get("step", 0) for s in original_conversations), default=0)
    probe_steps = []

    for i, (topic, info) in enumerate(sorted(eligible_topics.items()), start=1):
        step_num = last_original_step + i
        readable_topic = topic.replace("_", " ")

        probe_step = {
            "step": step_num,
            "context": topic,
            "message": (
                f"Summarize everything we have discussed about {readable_topic}. "
                f"Include all key points, details, and questions that were raised."
            ),
            "expected": f"recall_probe:{topic}",
            "node_type": info["primary_node"],
            "action": "switch_node",
            "parent_node_type": "",
            "subchat_title": "",
            "selected_text": "",
            "linear_failure_risk": "n/a",
            "source_conversation_id": "recall_probe",
            "source_scenario": "auto_generated_recall_probe",
            "original_step": step_num,
            # ── Recall probe specific fields ──
            "is_recall_probe": True,
            "reference_text": info["reference_text"],
            "reference_conversations": info["reference_conversations"],
            "probe_topic": topic,
            "probe_target_node": info["primary_node"],
            "is_main_only_topic": info["is_main_only"],
            "topic_turn_count": info["n_turns"],
        }
        probe_steps.append(probe_step)

    # ── 5. Append probes to scenario and save ─────────────────────────────
    scenario["conversations"] = original_conversations + probe_steps
    scenario["total_turns"] = len(scenario["conversations"])

    # Add probe metadata
    scenario["recall_probe_config"] = {
        "min_turns_threshold": min_turns,
        "total_probes_injected": len(probe_steps),
        "eligible_topics": len(eligible_topics),
        "skipped_topics": len(skipped_topics),
        "main_only_topics": sum(1 for info in eligible_topics.values() if info["is_main_only"]),
        "subchat_topics": sum(1 for info in eligible_topics.values() if not info["is_main_only"]),
        "first_probe_step": last_original_step + 1 if probe_steps else None,
        "last_probe_step": last_original_step + len(probe_steps) if probe_steps else None,
        "probe_topics": sorted(eligible_topics.keys()),
    }

    with open(output_path, "w") as f:
        json.dump(scenario, f, indent=2, ensure_ascii=False)

    stats = {
        "topics_injected": len(probe_steps),
        "topics_skipped": len(skipped_topics),
        "first_probe_step": last_original_step + 1 if probe_steps else None,
        "last_probe_step": last_original_step + len(probe_steps) if probe_steps else None,
        "eligible_topics": sorted(eligible_topics.keys()),
        "skipped_details": skipped_topics,
        "main_only_topics": [t for t, info in eligible_topics.items() if info["is_main_only"]],
        "subchat_topics": [t for t, info in eligible_topics.items() if not info["is_main_only"]],
    }

    return stats


def print_injection_report(stats: dict):
    """Print a human-readable report of what was injected."""
    print("=" * 70)
    print("RECALL PROBE INJECTION REPORT")
    print("=" * 70)
    print(f"  ✅ Topics injected:  {stats['topics_injected']}")
    print(f"  ❌ Topics skipped:   {stats['topics_skipped']} (< {MIN_TURNS} turns)")
    print(f"  📍 Probe step range: {stats['first_probe_step']} – {stats['last_probe_step']}")
    print()
    print(f"  🌿 Subchat-routed probes ({len(stats['subchat_topics'])}):")
    for t in sorted(stats["subchat_topics"]):
        print(f"     • {t}")
    print()
    print(f"  🏠 Main-only probes ({len(stats['main_only_topics'])}):")
    for t in sorted(stats["main_only_topics"]):
        print(f"     • {t}")
    print()
    if stats["skipped_details"]:
        print(f"  🚫 Skipped topics:")
        for t, n in sorted(stats["skipped_details"]):
            print(f"     • {t} ({n} turns)")
    print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Inject recall probes into merged scenario JSON")
    parser.add_argument(
        "--input", "-i",
        default=str(Path(__file__).parent / "scenarios" / "merged_realistic_interleaved.json"),
        help="Path to input scenario JSON",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to output JSON (default: overwrite input)",
    )
    parser.add_argument(
        "--min-turns", "-m",
        type=int,
        default=MIN_TURNS,
        help=f"Minimum turns for eligibility (default: {MIN_TURNS})",
    )
    args = parser.parse_args()

    stats = inject_recall_probes(args.input, args.output, args.min_turns)
    print_injection_report(stats)
