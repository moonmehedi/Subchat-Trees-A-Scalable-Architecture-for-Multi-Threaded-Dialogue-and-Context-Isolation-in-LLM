#!/usr/bin/env python3
"""
Append context slug to node_type across all scenario JSON files.

Rules:
- Keep 'main' as 'main' (unchanged).
- For subchats, map the creation step's node_type to node_type + '_' + slug(context).
- For subsequent steps, replace node_type and parent_node_type using the mapping.

Idempotent: running multiple times should not duplicate suffixes.
"""

import json
import re
from pathlib import Path

SCENARIOS_DIR = Path(__file__).resolve().parents[1] / "scenarios"


def slugify(text: str) -> str:
    text = text.strip().lower()
    # Replace non-alphanumeric with underscores
    text = re.sub(r"[^a-z0-9]+", "_", text)
    # Collapse multiple underscores
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def already_suffixed(node_type: str, context: str) -> bool:
    suf = slugify(context)
    return node_type.endswith("_" + suf)


def process_scenario(path: Path) -> bool:
    try:
        data = json.loads(path.read_text())
    except Exception as e:
        print(f"❌ Failed to read {path.name}: {e}")
        return False

    conversations = data.get("conversations", [])
    if not conversations:
        return False

    # Map original node_type -> augmented node_type using creation steps
    mapping = {}

    changed = False

    for step in conversations:
        node_type = step.get("node_type", "main")
        context = step.get("context", "")
        action = step.get("action", "")

        # Update parent_node_type if we have a mapping
        parent_node_type = step.get("parent_node_type")
        if parent_node_type and parent_node_type in mapping:
            step["parent_node_type"] = mapping[parent_node_type]
            changed = True

        # Skip 'main'
        if node_type == "main":
            continue

        # If this is a creation step, define mapping based on context
        if action == "create_subchat":
            ctx_slug = slugify(context)
            # If already suffixed correctly, keep as-is
            if not already_suffixed(node_type, context):
                new_node_type = f"{node_type}_{ctx_slug}" if ctx_slug else node_type
            else:
                new_node_type = node_type

            # Record mapping from original (bare) label to augmented
            # If node_type was already suffixed, map to itself for downstream references
            bare = node_type
            mapping[bare] = new_node_type

            # Apply to current creation step
            if step.get("node_type") != new_node_type:
                step["node_type"] = new_node_type
                changed = True

        else:
            # For non-creation steps, if we've seen a mapping for this node_type, apply it
            if node_type in mapping:
                if step["node_type"] != mapping[node_type]:
                    step["node_type"] = mapping[node_type]
                    changed = True

            else:
                # If this node_type already contains a suffix that matches its own context, leave it
                # Otherwise, do not invent mapping blindly; rely on creation steps
                pass

        # After potentially updating node_type, also update parent_node_type if mapping now exists
        parent_node_type = step.get("parent_node_type")
        if parent_node_type and parent_node_type in mapping:
            if step["parent_node_type"] != mapping[parent_node_type]:
                step["parent_node_type"] = mapping[parent_node_type]
                changed = True

    if changed:
        path.write_text(json.dumps(data, indent=2))
        print(f"✅ Updated: {path}")
    else:
        print(f"ℹ️  No changes: {path}")
    return changed


def main():
    files = sorted(SCENARIOS_DIR.glob("*.json"))
    if not files:
        print(f"No scenario files found in {SCENARIOS_DIR}")
        return

    any_changed = False
    for p in files:
        if process_scenario(p):
            any_changed = True

    if any_changed:
        print("\n🎉 Completed updating node_type with context suffixes.")
    else:
        print("\nNothing to update — scenarios already suffixed or no matching patterns.")


if __name__ == "__main__":
    main()
