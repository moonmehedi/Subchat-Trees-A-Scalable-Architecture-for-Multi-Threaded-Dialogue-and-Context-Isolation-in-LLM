#!/usr/bin/env python3
"""
merge_and_interleave.py — Variable-Block Randomized Interleaving (VBRI)

Merges all structured scenario JSONs (excluding 06_lost_in_conversation_sharded_humaneval.json)
into a single flat multi-topic dataset with realistic conversation-switching patterns.

CRITICAL DESIGN: Temporal order is PRESERVED within each source conversation.
Only the interleaving ORDER between different source conversations is randomized.

Algorithm: Variable-Block Randomized Interleaving (VBRI)
  1. Load each source conversation and split into consecutive same-context blocks
  2. Maintain a FIFO queue per source conversation (preserving original turn order)
  3. If a block exceeds --max_block_size, split it (but keep sub-blocks in order)
  4. Interleave by picking WHICH SOURCE CONVERSATION to take the next block from:
     - Recently active source gets a configurable return probability (default 0.3)
       → simulates real users who stay on one thread for a few turns before switching
     - All other sources share the remaining probability uniformly
  5. Within each source, blocks always come out in their original temporal order (FIFO)

This produces realistic patterns like:
  Conv A block 1 → Conv C block 1 → Conv A block 2 → Conv B block 1 → Conv C block 2
  (A's blocks are always in order, C's blocks are always in order, etc.)

Paper reference:
  "Variable-Block Randomized Interleaving (VBRI) — a block-randomized
   design where source conversations are interleaved at the block level
   while strictly preserving intra-conversation temporal order. Consecutive
   same-topic turns are grouped into atomic blocks (max 4 turns) and the
   interleaving selects which source conversation to draw from next, with
   a 0.3 return probability to simulate realistic multi-topic conversation
   switching patterns. Block randomization follows clinical trial methodology
   (Efird, 2011; Schulz & Grimes, 2002), while the return probability models
   conversational topic revisitation dynamics (Svennevig, 1999)."

Usage:
  python merge_and_interleave.py --seed 42 --return_probability 0.3 --max_block_size 4
"""

import json
import argparse
import random
import os
from pathlib import Path
from collections import defaultdict, OrderedDict
from typing import List, Dict, Any, Tuple


def load_scenario(filepath: str) -> Dict[str, Any]:
    """Load a structured scenario JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_conversations(scenario: Dict[str, Any], source_file: str) -> List[Dict[str, Any]]:
    """
    Extract conversations from a scenario, tagging each entry with provenance.
    Skips the step-1 intro/instruction message (shared across all files).
    """
    conv_key = "conversations" if "conversations" in scenario else "conversation"
    conversations = scenario.get(conv_key, [])

    tagged = []
    for entry in conversations:
        # Skip step 1 (the instruction prompt) — we'll add a single shared one
        if entry.get("step") == 1 and entry.get("context") in ("intro", "step_1"):
            continue

        # Tag with provenance (don't modify original fields)
        enriched = dict(entry)
        enriched["source_conversation_id"] = scenario.get("conversation_id", "unknown")
        enriched["source_scenario"] = scenario.get("scenario_name", "unknown")
        enriched["original_step"] = entry.get("step")
        tagged.append(enriched)

    return tagged


def split_into_ordered_blocks(
    entries: List[Dict[str, Any]], max_block_size: int = 4
) -> List[List[Dict[str, Any]]]:
    """
    Split a single source conversation into consecutive same-context blocks.
    Blocks exceeding max_block_size are split into smaller sub-blocks.
    
    CRITICAL: Block order is the ORIGINAL temporal order of the conversation.
    Block[0] always comes before Block[1] in time.
    """
    if not entries:
        return []

    blocks = []
    current_block = [entries[0]]
    current_context = entries[0].get("context")

    for entry in entries[1:]:
        ctx = entry.get("context")
        if ctx == current_context:
            current_block.append(entry)
        else:
            blocks.append(current_block)
            current_block = [entry]
            current_context = ctx

    if current_block:
        blocks.append(current_block)

    # Split oversized blocks (preserving order within each split)
    split_blocks = []
    for block in blocks:
        if len(block) <= max_block_size:
            split_blocks.append(block)
        else:
            for i in range(0, len(block), max_block_size):
                sub = block[i : i + max_block_size]
                if sub:
                    split_blocks.append(sub)

    return split_blocks


def vbri_interleave(
    source_queues: Dict[str, List[List[Dict[str, Any]]]],
    return_probability: float = 0.3,
    rng: random.Random = None,
) -> List[Dict[str, Any]]:
    """
    Variable-Block Randomized Interleaving (VBRI) — Source-Level.

    Each source conversation has a FIFO queue of blocks (in original temporal order).
    At each step, we pick WHICH SOURCE to draw the next block from:
      - With probability `return_probability`, continue with the same source
        (simulates a user staying in one conversation thread for a burst)
      - Otherwise, pick uniformly at random from other sources with remaining blocks

    GUARANTEE: Within each source, blocks are always emitted in their original
    temporal order. Step 37 always comes before step 40 within the same source.
    """
    if rng is None:
        rng = random.Random(42)

    interleaved = []
    last_source = None
    active_sources = set(src for src, q in source_queues.items() if q)

    while active_sources:
        # Try to continue with last source (return probability)
        if (
            last_source is not None
            and last_source in active_sources
            and rng.random() < return_probability
        ):
            chosen_source = last_source
        else:
            # Pick from OTHER sources (or all if last_source exhausted)
            candidates = [s for s in active_sources if s != last_source]
            if not candidates:
                candidates = list(active_sources)
            chosen_source = rng.choice(candidates)

        # Pop the FIRST block from chosen source (FIFO = temporal order preserved)
        block = source_queues[chosen_source].pop(0)
        interleaved.extend(block)
        last_source = chosen_source

        # Update active sources
        if not source_queues[chosen_source]:
            active_sources.discard(chosen_source)

    return interleaved


def build_shared_intro() -> Dict[str, Any]:
    """Create a single shared introduction message for the merged dataset."""
    return {
        "step": 1,
        "context": "intro",
        "message": (
            "I'm going to ask you questions across multiple topics. Here's how the test works:\n\n"
            "When I introduce a new topic, I will use this pattern:\n"
            "topic_name : user query\n\n"
            "Example:\nmedical_treatments : how does one remove tumors with electromagnetism?\n\n"
            "Once a topic is introduced, you MUST keep using that topic name in ALL your answers, "
            "even if I don't repeat it in follow-up questions.\n\n"
            "Example:\nUser: what about pancreatic tumors?\n"
            "You must answer starting with:\nmedical_treatments: ...\n\n"
            "Sub-topics may also appear using this pattern:\n"
            "topic_name_subtopic_name : user query\n\n"
            "REQUIRED FORMAT for EVERY response:\n"
            "Start your answer with the active topic or sub-topic name, followed by a colon, "
            "then give your actual answer.\n\n"
            "IMPORTANT: This is a long conversation covering many different topics. "
            "I may switch between topics frequently and return to earlier topics. "
            "You must track which topic is currently active and always prefix your response "
            "with the correct topic name.\n\n"
            "Do you understand these instructions?"
        ),
        "expected": (
            "Acknowledged. I understand. I will prefix all responses with the active topic "
            "or sub-topic name. I will track topic switches and returns throughout the conversation."
        ),
        "node_type": "main",
        "action": "",
        "linear_failure_risk": "none - establishing baseline with topic tracking instruction",
        "source_conversation_id": "merged",
        "source_scenario": "Merged Multi-Topic VBRI Dataset",
        "original_step": 1,
    }


def compute_statistics(
    conversations: List[Dict[str, Any]],
    source_files: List[str],
) -> Dict[str, Any]:
    """Compute statistics about the interleaved dataset."""
    # Topic distribution
    topic_counts = defaultdict(int)
    source_counts = defaultdict(int)
    risk_counts = defaultdict(int)

    for entry in conversations:
        if entry.get("context") == "intro":
            continue
        topic_counts[entry.get("context", "unknown")] += 1
        source_counts[entry.get("source_conversation_id", "unknown")] += 1
        risk = entry.get("linear_failure_risk", "unknown")
        if isinstance(risk, str):
            risk = risk.split(" ")[0] if " " in risk else risk
        risk_counts[risk] += 1

    # Measure topic switches
    switches = 0
    source_switches = 0
    returns = 0
    recent_topics = []
    for i in range(1, len(conversations)):
        prev_ctx = conversations[i - 1].get("context")
        curr_ctx = conversations[i].get("context")
        prev_src = conversations[i - 1].get("source_conversation_id")
        curr_src = conversations[i].get("source_conversation_id")
        if curr_ctx != prev_ctx:
            switches += 1
            if curr_ctx in recent_topics[-8:]:
                returns += 1
            recent_topics.append(prev_ctx)
        if curr_src != prev_src:
            source_switches += 1

    # Longest consecutive same-topic run
    max_run = 1
    current_run = 1
    for i in range(1, len(conversations)):
        if conversations[i].get("context") == conversations[i - 1].get("context"):
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1

    # Verify temporal order preservation per source
    temporal_violations = 0
    source_steps: Dict[str, int] = {}
    for entry in conversations:
        src = entry.get("source_conversation_id", "merged")
        orig_step = entry.get("original_step", 0)
        if src in source_steps:
            if orig_step < source_steps[src] and src != "merged":
                temporal_violations += 1
        source_steps[src] = orig_step

    return {
        "total_turns": len(conversations),
        "unique_topics": len(topic_counts),
        "topic_distribution": dict(
            sorted(topic_counts.items(), key=lambda x: -x[1])
        ),
        "source_distribution": dict(source_counts),
        "risk_distribution": dict(risk_counts),
        "total_topic_switches": switches,
        "source_conversation_switches": source_switches,
        "topic_returns": returns,
        "return_rate": round(returns / max(switches, 1), 3),
        "max_consecutive_same_topic": max_run,
        "source_files_count": len(source_files),
        "temporal_order_violations": temporal_violations,
        "temporal_order_preserved": temporal_violations == 0,
    }


def generate_interleaving_preview(conversations: List[Dict[str, Any]], n: int = 50) -> str:
    """Generate a visual preview of the interleaving pattern."""
    lines = []
    prev_ctx = None
    prev_src = None
    for i, entry in enumerate(conversations[:n]):
        ctx = entry.get("context", "?")
        src = entry.get("source_conversation_id", "?")[:8]
        orig = entry.get("original_step", "?")
        
        markers = []
        if src != prev_src and prev_src is not None:
            markers.append("🔀 SRC-SWITCH")
        if ctx != prev_ctx and prev_ctx is not None:
            recent = [c.get("context") for c in conversations[max(0, i - 10) : i]]
            if ctx in recent:
                markers.append("🔄 TOPIC-RETURN")
            else:
                markers.append("➡️  NEW-TOPIC")
        
        marker_str = " │ ".join(markers) if markers else ""
        lines.append(
            f"  Step {entry.get('step', '?'):>3} │ orig:{str(orig):>3} │ "
            f"src:{src} │ {ctx:<42} │ {marker_str}"
        )
        prev_ctx = ctx
        prev_src = src
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Merge & interleave scenario datasets using VBRI algorithm"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--return_probability",
        type=float,
        default=0.3,
        help="Probability of continuing with the same source conversation (default: 0.3)",
    )
    parser.add_argument(
        "--max_block_size",
        type=int,
        default=4,
        help="Maximum turns in a single topic-run block (default: 4)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output filename (default: merged_realistic_interleaved.json)",
    )
    parser.add_argument(
        "--scenarios_dir",
        type=str,
        default=None,
        help="Path to scenarios directory (default: same directory as this script)",
    )
    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    scenarios_dir = Path(args.scenarios_dir) if args.scenarios_dir else script_dir
    output_name = args.output or "merged_realistic_interleaved.json"
    output_path = scenarios_dir / output_name

    # Exclude list
    exclude_files = {
        "06_lost_in_conversation_sharded_humaneval.json",
        output_name,
        Path(__file__).name,
    }

    # Discover structured scenario files
    scenario_files = sorted(
        [
            f
            for f in scenarios_dir.glob("*_structured.json")
            if f.name not in exclude_files
        ]
    )

    if not scenario_files:
        print("❌ No structured scenario files found!")
        return

    print("=" * 80)
    print("🔀 VARIABLE-BLOCK RANDOMIZED INTERLEAVING (VBRI) — TEMPORAL-PRESERVING")
    print("=" * 80)
    print(f"  Seed:               {args.seed}")
    print(f"  Return probability: {args.return_probability}")
    print(f"  Max block size:     {args.max_block_size}")
    print(f"  Output:             {output_path.name}")
    print(f"  Source files:       {len(scenario_files)}")
    print()
    print("  ⚡ GUARANTEE: Temporal order within each source conversation is PRESERVED.")
    print("  ⚡ Only the interleaving order BETWEEN sources is randomized.")
    print("=" * 80)

    # ─────────────────────────────────────────────────────────
    # Step 1: Load all scenarios → build per-source FIFO queues
    # ─────────────────────────────────────────────────────────
    source_queues: Dict[str, List[List[Dict[str, Any]]]] = {}
    source_metadata = []
    all_topics = []
    total_entries = 0

    for sf in scenario_files:
        scenario = load_scenario(str(sf))
        entries = extract_conversations(scenario, sf.name)
        conv_id = scenario.get("conversation_id", sf.stem)

        # Split into temporal-order blocks (FIFO queue)
        blocks = split_into_ordered_blocks(entries, max_block_size=args.max_block_size)
        source_queues[conv_id] = blocks
        total_entries += len(entries)

        # Collect metadata
        source_metadata.append(
            {
                "file": sf.name,
                "conversation_id": conv_id,
                "scenario_name": scenario.get("scenario_name"),
                "original_turns": scenario.get("total_turns"),
                "extracted_turns": len(entries),
                "blocks": len(blocks),
                "topics": scenario.get("topics", []),
            }
        )
        all_topics.extend(scenario.get("topics", []))

        # Show per-source block summary
        block_contexts = [b[0].get("context", "?") for b in blocks]
        print(f"  ✅ {sf.name}")
        print(f"     {len(entries)} turns → {len(blocks)} blocks (temporal FIFO)")
        # Show first few block contexts to verify order
        preview = " → ".join(block_contexts[:8])
        if len(block_contexts) > 8:
            preview += f" → ... ({len(block_contexts) - 8} more)"
        print(f"     Order: {preview}")
        print()

    print(f"  📊 Total entries: {total_entries}")
    print(f"  📦 Total blocks:  {sum(len(q) for q in source_queues.values())}")

    # ─────────────────────────────────────────────────────────
    # Step 2: VBRI Interleave (source-level, temporal-preserving)
    # ─────────────────────────────────────────────────────────
    rng = random.Random(args.seed)
    interleaved = vbri_interleave(source_queues, args.return_probability, rng)

    # ─────────────────────────────────────────────────────────
    # Step 3: Add shared intro and re-number steps
    # ─────────────────────────────────────────────────────────
    intro = build_shared_intro()
    final_conversations = [intro]
    for i, entry in enumerate(interleaved):
        entry["step"] = i + 2  # Start from 2 (step 1 is intro)
        final_conversations.append(entry)

    print(f"\n  ✅ Interleaved: {len(final_conversations)} total turns (including intro)")

    # ─────────────────────────────────────────────────────────
    # Step 4: VERIFY temporal order preservation
    # ─────────────────────────────────────────────────────────
    print("\n  🔍 Verifying temporal order preservation per source...")
    per_source_steps: Dict[str, List[int]] = defaultdict(list)
    for entry in final_conversations:
        src = entry.get("source_conversation_id", "merged")
        if src != "merged":
            per_source_steps[src].append(entry.get("original_step", 0))

    all_preserved = True
    for src, steps in per_source_steps.items():
        is_sorted = all(steps[i] <= steps[i + 1] for i in range(len(steps) - 1))
        status = "✅" if is_sorted else "❌ VIOLATED"
        if not is_sorted:
            all_preserved = False
        print(f"     {src[:12]}... : {status} ({len(steps)} turns)")

    if all_preserved:
        print("  ✅ ALL source conversations preserve temporal order!")
    else:
        print("  ❌ WARNING: Temporal order violations detected!")

    # ─────────────────────────────────────────────────────────
    # Step 5: Compute statistics
    # ─────────────────────────────────────────────────────────
    stats = compute_statistics(final_conversations, [sf.name for sf in scenario_files])

    # ─────────────────────────────────────────────────────────
    # Step 6: Build output JSON
    # ─────────────────────────────────────────────────────────
    output = {
        "scenario_name": "Merged Multi-Topic VBRI Interleaved Dataset (Temporal-Preserving)",
        "conversation_title": "Variable-Block Randomized Interleaving of All Structured Scenarios",
        "description": (
            "A single flat multi-topic dataset created by merging all structured scenario "
            "conversations and interleaving them using Variable-Block Randomized Interleaving "
            "(VBRI) with strict temporal order preservation. Within each source conversation, "
            "the original turn order is maintained exactly — only the interleaving order "
            "BETWEEN source conversations is randomized. Consecutive same-topic turns are "
            f"preserved as atomic blocks (max {args.max_block_size} turns) and the algorithm "
            f"selects which source conversation to draw from next with a {args.return_probability} "
            "return probability. This tests whether an LLM can disentangle interleaved "
            "multi-source conversations in a linear context without hierarchical subchat support, "
            "while preserving the natural temporal flow of each conversation thread."
        ),
        "data_source": "Merged from LMSYS Chat-1M structured scenarios",
        "conversation_id": "merged_vbri_temporal",
        "total_turns": len(final_conversations),
        "shuffle_config": {
            "algorithm": "Variable-Block Randomized Interleaving (VBRI) — Temporal-Preserving",
            "seed": args.seed,
            "return_probability": args.return_probability,
            "max_block_size": args.max_block_size,
            "temporal_order_preserved": True,
            "interleave_level": "source_conversation (not topic-level)",
            "paper_reference": (
                "Block randomization (Efird, 2011; Schulz & Grimes, 2002) with "
                "conversational topic revisitation dynamics (Svennevig, 1999). "
                "Intra-conversation temporal order strictly preserved to maintain "
                "natural follow-up chains and context dependencies."
            ),
        },
        "source_files": source_metadata,
        "merged_topics": sorted(set(all_topics)),
        "statistics": stats,
        "linear_vs_hierarchical": {
            "linear_challenges": [
                "All topics from 5 different conversations interleaved into single flat context",
                "LLM must track 40+ unique topic contexts without hierarchical isolation",
                "Topic returns require recalling context from many turns ago across source boundaries",
                "No subchat boundaries — every source-switch risks context contamination",
                "Follow-up questions from one source appear after unrelated turns from another source",
                "Temporal dependencies (e.g., 'the above code') span across interleaved foreign turns",
            ],
            "hierarchical_advantages": [
                "Each topic isolated in its own subchat node with dedicated context",
                "Topic switches are clean — no contamination between branches",
                "Follow-up questions naturally find their parent context in the tree",
                "Topic returns just reactivate the existing subchat node",
                "Context window not wasted on irrelevant interleaved turns from other sources",
            ],
        },
        "conversations": final_conversations,
    }

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  💾 Saved to: {output_path}")

    # ─────────────────────────────────────────────────────────
    # Print statistics
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("📊 DATASET STATISTICS")
    print("=" * 80)
    print(f"  Total turns:                   {stats['total_turns']}")
    print(f"  Unique topics:                 {stats['unique_topics']}")
    print(f"  Topic switches:                {stats['total_topic_switches']}")
    print(f"  Source conversation switches:   {stats['source_conversation_switches']}")
    print(f"  Topic returns:                 {stats['topic_returns']}")
    print(f"  Return rate:                   {stats['return_rate']:.1%}")
    print(f"  Max consecutive same-topic:    {stats['max_consecutive_same_topic']}")
    print(f"  Temporal order violations:     {stats['temporal_order_violations']}")
    print(f"  Temporal order preserved:      {'✅ YES' if stats['temporal_order_preserved'] else '❌ NO'}")

    print("\n  📈 Risk distribution:")
    for risk, count in sorted(stats["risk_distribution"].items()):
        print(f"      {risk:<12}: {count}")

    print("\n  📁 Source contribution:")
    for src, count in stats["source_distribution"].items():
        print(f"      {src[:12]}...: {count} turns")

    print("\n  🏷️  Top 15 topics by frequency:")
    for topic, count in list(stats["topic_distribution"].items())[:15]:
        print(f"      {topic:<42}: {count} turns")

    # ─────────────────────────────────────────────────────────
    # Print interleaving preview
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("👀 INTERLEAVING PREVIEW (first 50 turns)")
    print("  NOTE: 'orig' = original step # within source (must always increase per source)")
    print("=" * 80)
    preview = generate_interleaving_preview(final_conversations, n=50)
    print(preview)

    print("\n" + "=" * 80)
    print("✅ MERGE COMPLETE — TEMPORAL ORDER PRESERVED!")
    print("=" * 80)


if __name__ == "__main__":
    main()
