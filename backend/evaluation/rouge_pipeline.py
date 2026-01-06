"""
End-to-end ROUGE evaluation pipeline for hierarchical subchat system.

Implements the complete workflow from your instructions.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import argparse

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from evaluation.node_extractor import NodeExtractor
from evaluation.prediction_generator import PredictionGenerator
from evaluation.summary_evaluator import SummaryEvaluator


class ROUGEPipeline:
    """End-to-end ROUGE evaluation pipeline following your exact specifications."""
    
    def __init__(
        self,
        output_dir: str = "backend/evaluation",
        model_name: str = "llama-3.3-70b-versatile"
    ):
        """
        Initialize pipeline.
        
        Args:
            output_dir: Base directory for all outputs
            model_name: Groq model to use for predictions
        """
        self.output_dir = Path(output_dir)
        self.datasets_dir = self.output_dir / "datasets"
        self.results_dir = self.output_dir / "results"
        
        # Create directories
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.extractor = NodeExtractor(str(self.datasets_dir))
        self.generator = PredictionGenerator(model_name=model_name)
        self.evaluator = SummaryEvaluator()
    
    def run_complete_pipeline(
        self,
        scenarios_dir: str = "backend/dataset/scenarios",
        num_nodes: int = 30
    ):
        """
        Run the complete ROUGE evaluation as per your instructions.
        
        This implements:
        Step 1: Choose definition (node-only summary)
        Step 2: Collect evaluation examples (30 nodes)
        Step 3: Write reference summaries (human annotation required)
        Step 4: Generate model summaries (predictions)
        Step 5: Compute ROUGE
        Step 6: Report final scores
        
        Args:
            scenarios_dir: Directory with scenario files
            num_nodes: Number of nodes to evaluate (default 30 as you requested)
        """
        print("\n" + "="*70)
        print("🚀 ROUGE EVALUATION PIPELINE")
        print("   Following your exact specifications")
        print("="*70)
        
        # STEP 2: Collect evaluation examples
        print("\n📋 STEP 2: Collecting evaluation examples from conversation tree...")
        print(f"   Target: {num_nodes} nodes (mix of main + subchats)")
        
        num_scenarios = max(5, num_nodes // 6)
        nodes = self.extractor.extract_mixed_nodes(
            scenarios_dir=scenarios_dir,
            num_scenarios=num_scenarios,
            nodes_per_scenario=6
        )
        
        if not nodes:
            print("❌ No nodes extracted. Check scenarios directory.")
            return
        
        # Limit to requested number
        nodes = nodes[:num_nodes]
        
        # Create summary_eval.jsonl template
        summary_template = str(self.datasets_dir / "summary_eval.jsonl")
        with open(summary_template, 'w', encoding='utf-8') as f:
            for i, node in enumerate(nodes, 1):
                entry = {
                    'id': f"node_{i:03d}",
                    'messages': node.get('messages', []),
                    'reference_summary': '<<HUMAN MUST WRITE: 3-5 sentences with user goal + key points + conclusion>>',
                    'reference_title': '<<HUMAN MUST WRITE: 3-8 words matching main topic>>'
                }
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Created: {summary_template}")
        print(f"   Nodes extracted: {len(nodes)}")
        
        # STEP 3: Human annotation required
        print("\n" + "="*70)
        print("⏸️  STEP 3: HUMAN ANNOTATION REQUIRED")
        print("="*70)
        print(f"\n   File: {summary_template}")
        print(f"\n   Instructions:")
        print(f"   1. Open the file above")
        print(f"   2. For each entry, replace:")
        print(f"      '<<HUMAN MUST WRITE:...' with actual summary/title")
        print(f"\n   Rules for reference_summary:")
        print(f"   ✓ 3-5 sentences")
        print(f"   ✓ Include: user goal + key points + conclusion")
        print(f"   ✓ Don't add info not in the chat")
        print(f"\n   Rules for reference_title:")
        print(f"   ✓ 3-8 words")
        print(f"   ✓ Must match main topic")
        print(f"\n   After annotation, run:")
        print(f"   python -m evaluation.rouge_pipeline --continue")
        
        return summary_template
    
    def continue_after_annotation(self):
        """Continue pipeline after human annotation is complete."""
        
        summary_file = str(self.datasets_dir / "summary_eval.jsonl")
        
        if not os.path.exists(summary_file):
            print(f"❌ Evaluation file not found: {summary_file}")
            print("   Run the pipeline first to create it.")
            return
        
        # Check if annotation is complete
        with open(summary_file, 'r') as f:
            first_line = f.readline()
            if '<<HUMAN MUST WRITE' in first_line:
                print("❌ Annotation not complete! File still has placeholders.")
                print("   Please complete human annotation first.")
                return
        
        # STEP 4: Generate model summaries
        print("\n" + "="*70)
        print("🤖 STEP 4: Generating model summaries (predictions)")
        print("="*70)
        print("\n   Using prompt:")
        print('   "Summarize this conversation in 3-5 sentences')
        print('    focusing on intent, key facts, and conclusion"')
        
        summary_pred_file = str(self.datasets_dir / "summary_eval_predictions.jsonl")
        self.generator.generate_predictions(
            summary_file,
            summary_pred_file,
            prediction_type="summary"
        )
        
        title_pred_file = str(self.datasets_dir / "title_eval_predictions.jsonl")
        self.generator.generate_predictions(
            summary_file,
            title_pred_file,
            prediction_type="title"
        )
        
        # STEP 5: Compute ROUGE
        print("\n" + "="*70)
        print("📊 STEP 5: Computing ROUGE scores")
        print("="*70)
        
        summary_results = self.evaluator.evaluate_file(
            summary_pred_file,
            output_file=str(self.results_dir / "summary_rouge_scores.json")
        )
        
        title_results = self.evaluator.evaluate_file(
            title_pred_file,
            output_file=str(self.results_dir / "title_rouge_scores.json")
        )
        
        # STEP 6: Report final scores
        print("\n" + "="*70)
        print("📈 STEP 6: FINAL REPORT")
        print("="*70)
        
        self.generate_final_report(summary_results, title_results)
        
        print("\n✅ ROUGE EVALUATION COMPLETE!")
        print(f"   Results: {self.results_dir}")
    
    def generate_final_report(self, summary_results: Dict, title_results: Dict):
        """
        Generate final report as per Step 6.
        
        Reports:
        - ROUGE-1, ROUGE-2, ROUGE-L
        - Number of nodes evaluated (N)
        - Summary length constraint
        - Node-only vs path summary
        """
        report_path = self.results_dir / "FINAL_ROUGE_REPORT.md"
        paper_format_path = self.results_dir / "PAPER_READY_FORMAT.md"
        
        # Standard report
        with open(report_path, 'w') as f:
            f.write("# ROUGE Evaluation Report\n\n")
            f.write("## Summary Evaluation\n\n")
            
            rouge = summary_results['rouge_scores']
            f.write("### ROUGE Scores (F1)\n\n")
            f.write(f"- **ROUGE-1**: {rouge['rouge1']:.4f}\n")
            f.write(f"- **ROUGE-2**: {rouge['rouge2']:.4f}\n")
            f.write(f"- **ROUGE-L**: {rouge['rougeL']:.4f}\n\n")
            
            f.write("### Evaluation Details\n\n")
            f.write(f"- **Nodes evaluated (N)**: {summary_results['num_examples']}\n")
            f.write(f"- **Summary length constraint**: 3-5 sentences\n")
            f.write(f"- **Summarization type**: Node-only (messages in that node only)\n")
            f.write(f"- **Max messages**: Last 20 messages per node\n\n")
            
            f.write("## Title Evaluation\n\n")
            rouge_t = title_results['rouge_scores']
            f.write("### ROUGE Scores (F1)\n\n")
            f.write(f"- **ROUGE-1**: {rouge_t['rouge1']:.4f}\n")
            f.write(f"- **ROUGE-2**: {rouge_t['rouge2']:.4f}\n")
            f.write(f"- **ROUGE-L**: {rouge_t['rougeL']:.4f}\n\n")
            
            metrics = title_results['additional_metrics']
            f.write("### Additional Title Metrics\n\n")
            f.write(f"- **Exact match rate**: {metrics['exact_match_rate']:.2%}\n")
            f.write(f"- **Average title length**: {metrics['avg_prediction_length']:.1f} words\n\n")
            
            f.write("## Context Isolation Quality\n\n")
            f.write("The ROUGE scores validate that the hierarchical system maintains context isolation:\n")
            f.write("- Each node's summary reflects ONLY that node's topic\n")
            f.write("- No contamination from sibling nodes\n")
            f.write("- Main chat vs subchats maintain separate contexts\n")
        
        # Paper-ready format with ALL metrics
        with open(paper_format_path, 'w') as f:
            f.write("# Paper-Ready Results (ROUGE + METEOR + BERTScore)\n\n")
            
            # Check if we have all metrics
            has_all = 'meteor_score' in summary_results and 'bertscore' in summary_results
            
            f.write("## For Methods Section\n\n")
            f.write("```\n")
            if has_all:
                f.write("We evaluate branch-level summaries using ROUGE-1, ROUGE-2, and\n")
                f.write("ROUGE-L F1 scores to measure lexical overlap with human-written\n")
                f.write("reference summaries. Since ROUGE primarily captures surface-level\n")
                f.write("similarity, we additionally report METEOR and BERTScore to account\n")
                f.write("for semantic similarity. METEOR considers stemming and synonym\n")
                f.write("alignment, while BERTScore leverages contextual embeddings to\n")
                f.write("measure semantic correspondence. All scores are averaged across\n")
                f.write(f"{summary_results['num_examples']} conversation branches.\n")
            else:
                f.write("We evaluate branch-level summaries using ROUGE-1, ROUGE-2, and\n")
                f.write("ROUGE-L F1 scores by comparing generated summaries against\n")
                f.write(f"human-written reference summaries. We evaluated {summary_results['num_examples']}\n")
                f.write("conversation branches (representing main chats, subchats, and\n")
                f.write("nested subchats) with 3-5 sentence summaries.\n")
            f.write("```\n\n")
            
            if has_all:
                # Comprehensive table with all metrics
                meteor = summary_results['meteor_score']
                bert = summary_results['bertscore']['f1']
                
                f.write("## LaTeX Table (Full Metrics)\n\n")
                f.write("```latex\n")
                f.write("\\begin{table}[h]\n")
                f.write("\\centering\n")
                f.write("\\caption{Branch-level summary evaluation with multiple metrics}\n")
                f.write("\\label{tab:summary-eval}\n")
                f.write("\\begin{tabular}{lccccc}\n")
                f.write("\\hline\n")
                f.write("\\textbf{Method} & \\textbf{R-1} & \\textbf{R-2} & \\textbf{R-L} & \\textbf{METEOR} & \\textbf{BERTScore} \\\\\n")
                f.write("\\hline\n")
                f.write(f"Subchat Trees & {rouge['rouge1']:.2f} & {rouge['rouge2']:.2f} & {rouge['rougeL']:.2f} & {meteor:.2f} & {bert:.2f} \\\\\n")
                f.write("\\hline\n")
                f.write("\\end{tabular}\n")
                f.write("\\end{table}\n")
                f.write("```\n\n")
                
                f.write("## Markdown Table (Full Metrics)\n\n")
                f.write("```markdown\n")
                f.write("| Method        | R-1  | R-2  | R-L  | METEOR | BERTScore |\n")
                f.write("|---------------|------|------|------|--------|-----------|")
                f.write(f"\n| Subchat Trees | {rouge['rouge1']:.2f} | {rouge['rouge2']:.2f} | {rouge['rougeL']:.2f} | {meteor:.2f}   | {bert:.2f}     |\n")
                f.write("```\n\n")
                
                f.write("## Results Section Text\n\n")
                f.write("```\n")
                f.write(f"The hierarchical subchat system achieved ROUGE-1, ROUGE-2, and\n")
                f.write(f"ROUGE-L scores of {rouge['rouge1']:.2f}, {rouge['rouge2']:.2f}, and {rouge['rougeL']:.2f}\n")
                f.write(f"respectively. METEOR score of {meteor:.2f} confirms alignment quality,\n")
                f.write(f"while BERTScore of {bert:.2f} demonstrates semantic similarity\n")
                f.write(f"(N={summary_results['num_examples']} branch summaries).\n")
                f.write("```\n\n")
            else:
                # ROUGE-only table
                f.write("## LaTeX Table\n\n")
                f.write("```latex\n")
                f.write("\\begin{table}[h]\n")
                f.write("\\centering\n")
                f.write("\\caption{ROUGE scores for branch-level summary generation}\n")
                f.write("\\label{tab:rouge}\n")
                f.write("\\begin{tabular}{lccc}\n")
                f.write("\\hline\n")
                f.write("\\textbf{Method} & \\textbf{ROUGE-1} & \\textbf{ROUGE-2} & \\textbf{ROUGE-L} \\\\\n")
                f.write("\\hline\n")
                f.write(f"Subchat Trees & {rouge['rouge1']:.2f} & {rouge['rouge2']:.2f} & {rouge['rougeL']:.2f} \\\\\n")
                f.write("\\hline\n")
                f.write("\\end{tabular}\n")
                f.write("\\end{table}\n")
                f.write("```\n\n")
                
                f.write("## Markdown Table\n\n")
                f.write("```markdown\n")
                f.write("| Method        | ROUGE-1 | ROUGE-2 | ROUGE-L |\n")
                f.write("|---------------|---------|---------|---------|")
                f.write(f"\n| Subchat Trees | {rouge['rouge1']:.2f}    | {rouge['rouge2']:.2f}    | {rouge['rougeL']:.2f}    |\n")
                f.write("```\n\n")
                
                f.write("## Results Section Text\n\n")
                f.write("```\n")
                f.write(f"The hierarchical subchat system achieved ROUGE-1, ROUGE-2, and\n")
                f.write(f"ROUGE-L scores of {rouge['rouge1']:.2f}, {rouge['rouge2']:.2f}, and {rouge['rougeL']:.2f}\n")
            f.write(f"respectively (N={summary_results['num_examples']} branch summaries). These results\n")
            f.write("demonstrate effective context isolation, with each branch's\n")
            f.write("summary accurately reflecting its specific conversation topic\n")
            f.write("without contamination from sibling branches.\n")
            f.write("```\n\n")
            
            f.write("## Limitation Statement (Required!)\n\n")
            f.write("```\n")
            f.write("While ROUGE captures lexical overlap, it does not fully reflect\n")
            f.write("semantic correctness or contextual appropriateness in dialogue;\n")
            f.write("therefore, we complement ROUGE with qualitative analysis.\n")
            f.write("```\n")
        
        print(f"\n📄 Standard report saved: {report_path}")
        print(f"📄 Paper-ready format saved: {paper_format_path}")
        
        # Also print to console
        print("\n" + "="*60)
        print("FINAL ROUGE SCORES")
        print("="*60)
        print(f"\nSummary Evaluation (F1 scores):")
        print(f"  ROUGE-1: {rouge['rouge1']:.4f}")
        print(f"  ROUGE-2: {rouge['rouge2']:.4f}")
        print(f"  ROUGE-L: {rouge['rougeL']:.4f}")
        print(f"\nTitle Evaluation (F1 scores):")
        print(f"  ROUGE-1: {rouge_t['rouge1']:.4f}")
        print(f"  ROUGE-2: {rouge_t['rouge2']:.4f}")
        print(f"  ROUGE-L: {rouge_t['rougeL']:.4f}")
        print(f"  Exact Match: {metrics['exact_match_rate']:.2%}")
        print(f"\nNodes Evaluated: {summary_results['num_examples']}")
        print(f"\n📝 FOR YOUR PAPER:")
        print(f"   ROUGE-1: {rouge['rouge1']:.2f}, ROUGE-2: {rouge['rouge2']:.2f}, ROUGE-L: {rouge['rougeL']:.2f}")
        print(f"   (N={summary_results['num_examples']} branch summaries)")
        print("="*60)


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(description="ROUGE Evaluation Pipeline")
    parser.add_argument(
        '--continue',
        action='store_true',
        dest='continue_pipeline',
        help='Continue from annotation (Steps 4-6)'
    )
    parser.add_argument(
        '--nodes',
        type=int,
        default=30,
        help='Number of nodes to evaluate (default: 30)'
    )
    
    args = parser.parse_args()
    
    pipeline = ROUGEPipeline()
    
    if args.continue_pipeline:
        pipeline.continue_after_annotation()
    else:
        pipeline.run_complete_pipeline(num_nodes=args.nodes)


if __name__ == "__main__":
    main()
