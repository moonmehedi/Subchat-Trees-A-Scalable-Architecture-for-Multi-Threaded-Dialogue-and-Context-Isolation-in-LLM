"""
Generate predictions (summaries and titles) using your LLM system.

This script uses your existing Groq LLM to generate predictions for ROUGE evaluation.
"""

import json
import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
from groq import Groq

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.cores.config import settings


class PredictionGenerator:
    """Generate summaries and titles using LLM for ROUGE evaluation."""
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        """
        Initialize prediction generator.
        
        Args:
            model_name: Groq model name to use
        """
        # Use Groq client directly for simple text generation
        api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment or settings")
        
        self.groq_client = Groq(api_key=api_key)
        self.model_name = model_name
        self.summary_prompt_template = """You summarize conversations accurately.

Conversation Messages:
{messages}

Summarize this conversation in 3-5 sentences focusing on intent, key facts, and conclusion.

Summary:"""

        self.title_prompt_template = """You generate concise, descriptive titles.

Conversation Messages:
{messages}

Create a 3-8 word title that captures the main topic of this conversation.

Title:"""
    
    def format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages for prompt.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Formatted message string
        """
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', msg.get('text', ''))
            formatted.append(f"{role.upper()}: {content}")
        
        return "\n".join(formatted)
    
    def generate_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate summary for a conversation node.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Generated summary text
        """
        formatted_messages = self.format_messages(messages)
        prompt = self.summary_prompt_template.format(messages=formatted_messages)
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates accurate, concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            # Extract just the summary text (remove any extra formatting)
            content = response.choices[0].message.content
            summary = content.strip() if content else "[ERROR: Empty response]"
            return summary
            
        except Exception as e:
            print(f"⚠️  Error generating summary: {e}")
            return f"[ERROR: Could not generate summary]"
    
    def generate_title(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate title for a conversation node.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Generated title text
        """
        formatted_messages = self.format_messages(messages)
        prompt = self.title_prompt_template.format(messages=formatted_messages)
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, descriptive titles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            # Extract just the title (remove any extra formatting)
            content = response.choices[0].message.content
            if not content:
                return "[ERROR: Empty response]"
            
            title = content.strip().replace('"', '').replace("'", '')
            
            # Ensure it's not too long
            words = title.split()
            if len(words) > 8:
                title = ' '.join(words[:8])
            
            return title
            
        except Exception as e:
            print(f"⚠️  Error generating title: {e}")
            return f"[ERROR: Could not generate title]"
    
    def generate_predictions(
        self, 
        eval_file: str, 
        output_file: str,
        prediction_type: str = "summary"
    ) -> str:
        """
        Generate all predictions for an evaluation file.
        
        Args:
            eval_file: Path to evaluation JSONL file with references
            output_file: Path to save predictions
            prediction_type: Either 'summary' or 'title'
            
        Returns:
            Path to output file
        """
        predictions = []
        
        print(f"\n🤖 Generating {prediction_type} predictions...")
        print(f"   Input: {eval_file}")
        print(f"   Output: {output_file}")
        
        with open(eval_file, 'r', encoding='utf-8') as f:
            entries = [json.loads(line) for line in f]
        
        total = len(entries)
        
        for i, entry in enumerate(entries, 1):
            node_id = entry.get('id', f'node_{i}')
            messages = entry.get('messages', [])
            
            print(f"\n   [{i}/{total}] Processing {node_id}...")
            
            if prediction_type == "summary":
                prediction = self.generate_summary(messages)
                entry['prediction_summary'] = prediction
                print(f"      Summary: {prediction[:80]}...")
            else:  # title
                prediction = self.generate_title(messages)
                entry['prediction_title'] = prediction
                print(f"      Title: {prediction}")
            
            predictions.append(entry)
        
        # Save with predictions
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in predictions:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Saved {len(predictions)} predictions to {output_file}")
        
        return output_file


def main():
    """Example usage."""
    generator = PredictionGenerator()
    
    # Check if evaluation files exist
    summary_file = "backend/evaluation/datasets/summary_eval.jsonl"
    
    if os.path.exists(summary_file):
        print("🔍 Found summary evaluation file")
        generator.generate_predictions(
            summary_file,
            "backend/evaluation/datasets/summary_eval_predictions.jsonl",
            prediction_type="summary"
        )
    else:
        print(f"⚠️  Summary eval file not found: {summary_file}")
        print("   Run node_extractor.py first to create evaluation dataset")


if __name__ == "__main__":
    main()
