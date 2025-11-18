"""
Dataset Explorer - Interactive tool to view and navigate conversation datasets

This script provides a readable view of various dialogue datasets stored in dataset_sources/.
It supports JSON files from:
- Schema-Guided Dialogue (SGD/DSTC8)
- MultiWOZ
- AmbigNQ
- And other JSON-formatted dialogue datasets

Usage:
    python explore_dataset.py                           # Interactive menu
    python explore_dataset.py --file <path>             # View specific file
    python explore_dataset.py --dataset sgd --split dev # View SGD dev set
    python explore_dataset.py --limit 3                 # Show only first 3 dialogues
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class DatasetExplorer:
    """Interactive explorer for conversation datasets"""
    
    def __init__(self, base_path: Optional[str] = None):
        """Initialize with path to dataset_sources folder"""
        if base_path is None:
            # Assume script is in backend/dataset/
            script_dir = Path(__file__).parent
            self.base_path = script_dir / "dataset_sources"
        else:
            self.base_path = Path(base_path)
        
        if not self.base_path.exists():
            raise FileNotFoundError(f"Dataset sources not found at: {self.base_path}")
    
    def list_available_datasets(self) -> List[str]:
        """List all available dataset directories"""
        datasets = []
        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('__'):
                datasets.append(item.name)
        return sorted(datasets)
    
    def load_json_file(self, file_path: Path) -> Any:
        """Load and parse a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            return None
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None
    
    def print_divider(self, char="=", length=80):
        """Print a visual divider"""
        print(char * length)
    
    def format_dialogue_sgd(self, dialogue: Dict, index: int, total: int) -> str:
        """Format a Schema-Guided Dialogue (DSTC8) dialogue for display"""
        output = []
        output.append(f"\n{'='*80}")
        output.append(f"DIALOGUE {index + 1}/{total}")
        output.append(f"{'='*80}")
        output.append(f"Dialogue ID: {dialogue.get('dialogue_id', 'N/A')}")
        
        services = dialogue.get('services', [])
        output.append(f"Services: {', '.join(services)}")
        
        turns = dialogue.get('turns', [])
        output.append(f"Number of turns: {len(turns)}")
        output.append(f"{'-'*80}")
        
        for turn_idx, turn in enumerate(turns, 1):
            speaker = turn.get('speaker', 'UNKNOWN')
            utterance = turn.get('utterance', '')
            
            if speaker == 'USER':
                output.append(f"\n👤 USER (Turn {turn_idx}):")
                output.append(f"   {utterance}")
                
                # Show frames (user intent)
                frames = turn.get('frames', [])
                if frames:
                    for frame in frames:
                        if 'state' in frame:
                            state = frame['state']
                            if 'active_intent' in state and state['active_intent'] != 'NONE':
                                output.append(f"   🎯 Intent: {state['active_intent']}")
                            slots = state.get('slot_values', {})
                            if slots:
                                output.append(f"   📋 Slots: {slots}")
            
            elif speaker == 'SYSTEM':
                output.append(f"\n🤖 SYSTEM (Turn {turn_idx}):")
                output.append(f"   {utterance}")
                
                # Show actions
                frames = turn.get('frames', [])
                if frames:
                    for frame in frames:
                        actions = frame.get('actions', [])
                        if actions:
                            action_strs = [f"{a.get('act', 'N/A')}({a.get('slot', '')})" for a in actions]
                            output.append(f"   🔧 Actions: {', '.join(action_strs)}")
        
        return '\n'.join(output)
    
    def format_dialogue_generic(self, dialogue: Dict, index: int, total: int) -> str:
        """Format a generic dialogue structure"""
        output = []
        output.append(f"\n{'='*80}")
        output.append(f"DIALOGUE {index + 1}/{total}")
        output.append(f"{'='*80}")
        
        # Try to find dialogue ID
        for key in ['dialogue_id', 'id', 'conversation_id', 'dialog_id']:
            if key in dialogue:
                output.append(f"ID: {dialogue[key]}")
                break
        
        # Print all top-level keys for reference
        output.append(f"Keys: {', '.join(dialogue.keys())}")
        output.append(f"{'-'*80}")
        
        # Try to find turns/messages
        messages = None
        for key in ['turns', 'messages', 'utterances', 'dialogue', 'conversation']:
            if key in dialogue:
                messages = dialogue[key]
                break
        
        if messages and isinstance(messages, list):
            output.append(f"Number of turns: {len(messages)}")
            output.append(f"{'-'*80}")
            
            for turn_idx, turn in enumerate(messages, 1):
                if isinstance(turn, dict):
                    # Try to find speaker
                    speaker = turn.get('speaker', turn.get('role', turn.get('from', 'UNKNOWN')))
                    # Try to find text
                    text = turn.get('utterance', turn.get('text', turn.get('content', str(turn))))
                    
                    icon = "👤" if 'user' in str(speaker).lower() else "🤖"
                    output.append(f"\n{icon} {speaker.upper()} (Turn {turn_idx}):")
                    output.append(f"   {text}")
                elif isinstance(turn, str):
                    output.append(f"\nTurn {turn_idx}: {turn}")
        else:
            # Just pretty-print the whole thing
            output.append("\nRaw content:")
            output.append(json.dumps(dialogue, indent=2))
        
        return '\n'.join(output)
    
    def view_sgd_dataset(self, split: str = "dev", limit: Optional[int] = None):
        """View Schema-Guided Dialogue dataset"""
        sgd_path = self.base_path / "dstc8-schema-guided-dialogue" / split
        
        if not sgd_path.exists():
            print(f"❌ SGD {split} split not found at: {sgd_path}")
            return
        
        # Find all dialogue JSON files
        dialogue_files = sorted([f for f in sgd_path.glob("dialogues_*.json")])
        
        if not dialogue_files:
            print(f"❌ No dialogue files found in: {sgd_path}")
            return
        
        print(f"\n📂 Loading Schema-Guided Dialogue ({split} split)")
        print(f"Found {len(dialogue_files)} dialogue files")
        
        total_dialogues = 0
        displayed = 0
        
        for file_idx, file_path in enumerate(dialogue_files, 1):
            print(f"\n📄 Processing file {file_idx}/{len(dialogue_files)}: {file_path.name}")
            
            data = self.load_json_file(file_path)
            if data is None:
                continue
            
            dialogues = data if isinstance(data, list) else [data]
            total_dialogues += len(dialogues)
            
            for dialogue_idx, dialogue in enumerate(dialogues):
                if limit and displayed >= limit:
                    print(f"\n✅ Reached display limit ({limit} dialogues)")
                    print(f"📊 Total dialogues in dataset: {total_dialogues} (across {len(dialogue_files)} files)")
                    return
                
                print(self.format_dialogue_sgd(dialogue, displayed, total_dialogues))
                displayed += 1
        
        print(f"\n✅ Displayed all {displayed} dialogues from {len(dialogue_files)} files")
    
    def view_json_file(self, file_path: Path, limit: Optional[int] = None):
        """View any JSON file with smart formatting"""
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        
        print(f"\n📂 Loading: {file_path}")
        data = self.load_json_file(file_path)
        
        if data is None:
            return
        
        # Check if it's a list of dialogues
        if isinstance(data, list):
            print(f"Found {len(data)} items")
            
            items_to_show = data[:limit] if limit else data
            
            for idx, item in enumerate(items_to_show):
                # Try to detect format
                if 'dialogue_id' in item and 'turns' in item:
                    # SGD format
                    print(self.format_dialogue_sgd(item, idx, len(data)))
                else:
                    # Generic format
                    print(self.format_dialogue_generic(item, idx, len(data)))
            
            if limit and len(data) > limit:
                print(f"\n... and {len(data) - limit} more items (use --limit to see more)")
        
        elif isinstance(data, dict):
            # Single dialogue or structured dataset
            if 'dialogues' in data or 'conversations' in data:
                dialogues = data.get('dialogues', data.get('conversations', []))
                print(f"Found {len(dialogues)} dialogues")
                
                items_to_show = dialogues[:limit] if limit else dialogues
                
                for idx, dialogue in enumerate(items_to_show):
                    print(self.format_dialogue_generic(dialogue, idx, len(dialogues)))
                
                if limit and len(dialogues) > limit:
                    print(f"\n... and {len(dialogues) - limit} more dialogues")
            else:
                # Just print it nicely
                print(json.dumps(data, indent=2))
        
        print(f"\n✅ Finished viewing: {file_path.name}")
    
    def interactive_menu(self):
        """Show interactive menu for dataset exploration"""
        while True:
            self.print_divider("=")
            print("📊 DATASET EXPLORER - Interactive Menu")
            self.print_divider("=")
            
            datasets = self.list_available_datasets()
            
            print("\nAvailable datasets:")
            for idx, dataset in enumerate(datasets, 1):
                print(f"  {idx}. {dataset}")
            
            print(f"\n  0. Exit")
            
            try:
                choice = input("\nSelect dataset number (or 0 to exit): ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                
                dataset_idx = int(choice) - 1
                if 0 <= dataset_idx < len(datasets):
                    dataset_name = datasets[dataset_idx]
                    self.explore_dataset(dataset_name)
                else:
                    print("❌ Invalid selection")
            
            except ValueError:
                print("❌ Please enter a number")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
    
    def explore_dataset(self, dataset_name: str):
        """Explore a specific dataset"""
        dataset_path = self.base_path / dataset_name
        
        print(f"\n📂 Exploring: {dataset_name}")
        
        # Special handling for known datasets
        if dataset_name == "dstc8-schema-guided-dialogue":
            print("\nAvailable splits:")
            print("  1. dev (development set)")
            print("  2. train (training set)")
            print("  3. test (test set)")
            
            split_choice = input("\nSelect split (1-3, or Enter for dev): ").strip()
            split_map = {"1": "dev", "2": "train", "3": "test", "": "dev"}
            split = split_map.get(split_choice, "dev")
            
            limit_input = input("How many dialogues to show? (Enter for all): ").strip()
            limit = int(limit_input) if limit_input.isdigit() else None
            
            self.view_sgd_dataset(split, limit)
        
        else:
            # Find JSON files in the dataset
            json_files = list(dataset_path.glob("*.json"))
            
            if not json_files:
                print(f"❌ No JSON files found in {dataset_name}")
                return
            
            print(f"\nFound {len(json_files)} JSON files:")
            for idx, file in enumerate(json_files, 1):
                print(f"  {idx}. {file.name}")
            
            try:
                file_choice = input("\nSelect file number: ").strip()
                file_idx = int(file_choice) - 1
                
                if 0 <= file_idx < len(json_files):
                    limit_input = input("How many items to show? (Enter for 5): ").strip()
                    limit = int(limit_input) if limit_input.isdigit() else 5
                    
                    self.view_json_file(json_files[file_idx], limit)
                else:
                    print("❌ Invalid file number")
            
            except ValueError:
                print("❌ Please enter a valid number")


def main():
    """Main entry point with CLI argument support"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Explore conversation datasets in a readable format",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--file', 
        type=str, 
        help='Path to a specific JSON file to view (relative to dataset_sources/)'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['sgd', 'multiwoz', 'ambignq'],
        help='View a specific dataset'
    )
    parser.add_argument(
        '--split',
        type=str,
        default='dev',
        choices=['train', 'dev', 'test'],
        help='Dataset split to view (default: dev)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of dialogues to display'
    )
    
    args = parser.parse_args()
    
    try:
        explorer = DatasetExplorer()
        
        if args.file:
            # View specific file
            file_path = explorer.base_path / args.file
            explorer.view_json_file(file_path, args.limit)
        
        elif args.dataset:
            # View specific dataset
            if args.dataset == 'sgd':
                explorer.view_sgd_dataset(args.split, args.limit)
            else:
                print(f"Dataset '{args.dataset}' viewer not yet implemented")
        
        else:
            # Interactive mode
            explorer.interactive_menu()
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
