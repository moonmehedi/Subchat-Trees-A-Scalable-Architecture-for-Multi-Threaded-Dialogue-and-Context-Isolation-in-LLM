"""
Extract conversation nodes from hierarchical subchat system for ROUGE evaluation.

This script extracts nodes with their messages to create evaluation datasets.
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class NodeExtractor:
    """Extract conversation nodes from various sources for evaluation."""
    
    def __init__(self, output_dir: str = "backend/evaluation/datasets"):
        """
        Initialize node extractor.
        
        Args:
            output_dir: Directory to save extracted node data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_from_scenario(self, scenario_path: str) -> List[Dict[str, Any]]:
        """
        Extract nodes from a test scenario JSON file.
        
        Args:
            scenario_path: Path to scenario JSON file
            
        Returns:
            List of node dictionaries with messages
        """
        with open(scenario_path, 'r', encoding='utf-8') as f:
            scenario = json.load(f)
        
        # Group messages by node_type
        nodes = {}
        
        for conv in scenario.get('conversations', []):
            node_type = conv.get('node_type', 'main')
            
            if node_type not in nodes:
                nodes[node_type] = {
                    'node_id': node_type,
                    'node_type': node_type,
                    'title': conv.get('subchat_title', scenario.get('conversation_title', 'Untitled')),
                    'messages': [],
                    'context': conv.get('context', ''),
                    'scenario_name': scenario.get('scenario_name', '')
                }
            
            # Add message with role (alternate user/assistant)
            role = 'user' if conv.get('step', 1) % 2 == 1 else 'assistant'
            nodes[node_type]['messages'].append({
                'role': role,
                'content': conv.get('message', ''),
                'step': conv.get('step', 0)
            })
        
        return list(nodes.values())
    
    def extract_mixed_nodes(
        self, 
        scenarios_dir: str = "backend/dataset/scenarios",
        num_scenarios: int = 5,
        nodes_per_scenario: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Extract a mix of nodes from multiple scenarios.
        
        Args:
            scenarios_dir: Directory containing scenario JSON files
            num_scenarios: Number of scenarios to sample
            nodes_per_scenario: Target nodes per scenario
            
        Returns:
            List of extracted nodes with diversity
        """
        all_nodes = []
        scenario_path = Path(scenarios_dir)
        
        # Get all scenario files
        scenario_files = list(scenario_path.glob("*.json"))
        
        if not scenario_files:
            print(f"⚠️  No scenario files found in {scenarios_dir}")
            return []
        
        # Sample scenarios
        import random
        selected_scenarios = random.sample(
            scenario_files, 
            min(num_scenarios, len(scenario_files))
        )
        
        for scenario_file in selected_scenarios:
            try:
                nodes = self.extract_from_scenario(str(scenario_file))
                all_nodes.extend(nodes[:nodes_per_scenario])
                print(f"✅ Extracted {len(nodes)} nodes from {scenario_file.name}")
            except Exception as e:
                print(f"⚠️  Failed to extract from {scenario_file.name}: {e}")
        
        return all_nodes
    
    def create_evaluation_template(
        self, 
        nodes: List[Dict[str, Any]], 
        output_file: str = "evaluation_template.jsonl"
    ):
        """
        Create a JSONL template file for human annotation.
        
        Args:
            nodes: List of extracted nodes
            output_file: Output JSONL filename
        """
        output_path = self.output_dir / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, node in enumerate(nodes, 1):
                # Create template entry
                entry = {
                    'id': node.get('node_id', f'node_{i:03d}'),
                    'title': node.get('title', 'Untitled'),
                    'node_type': node.get('node_type', 'unknown'),
                    'context': node.get('context', ''),
                    'messages': node.get('messages', []),
                    # Placeholder for human annotation
                    'reference_summary': '<<ANNOTATE: Write 3-5 sentence summary>>',
                    'reference_title': '<<ANNOTATE: Write 3-8 word title>>',
                    # Metadata
                    'metadata': {
                        'scenario_name': node.get('scenario_name', ''),
                        'message_count': len(node.get('messages', [])),
                        'has_context': bool(node.get('context'))
                    }
                }
                
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"✅ Created evaluation template: {output_path}")
        print(f"   Total nodes: {len(nodes)}")
        print(f"   Next step: Manually add reference_summary and reference_title")
        
        return str(output_path)


def main():
    """Example usage."""
    extractor = NodeExtractor()
    
    # Extract mixed nodes from scenarios
    print("🔍 Extracting nodes from scenarios...")
    nodes = extractor.extract_mixed_nodes(
        scenarios_dir="backend/dataset/scenarios",
        num_scenarios=5,
        nodes_per_scenario=6
    )
    
    if nodes:
        # Create template for annotation
        print("\n📝 Creating evaluation template...")
        template_path = extractor.create_evaluation_template(
            nodes, 
            output_file="summary_eval_template.jsonl"
        )
        
        print(f"\n✅ Template created: {template_path}")
        print(f"\n📋 Next steps:")
        print(f"   1. Open {template_path}")
        print(f"   2. Replace '<<ANNOTATE...>>' with actual summaries/titles")
        print(f"   3. Save as 'summary_eval.jsonl' and 'title_eval.jsonl'")
        print(f"   4. Run prediction generator")
    else:
        print("❌ No nodes extracted. Check your scenarios directory.")


if __name__ == "__main__":
    main()
