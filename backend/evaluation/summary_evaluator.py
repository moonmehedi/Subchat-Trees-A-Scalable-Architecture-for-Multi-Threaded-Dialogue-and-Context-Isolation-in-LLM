"""
Calculate comprehensive summary evaluation metrics: ROUGE, METEOR, and BERTScore.

This module provides multi-metric evaluation to assess both lexical overlap (ROUGE),
alignment with synonyms (METEOR), and semantic similarity (BERTScore).
"""

import json
import os
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import evaluate
import nltk
from bert_score import score as bertscore_compute


class SummaryEvaluator:
    """Calculate ROUGE, METEOR, and BERTScore for summary evaluation."""
    
    def __init__(self, download_nltk_data: bool = True):
        """
        Initialize comprehensive summary evaluator.
        
        Args:
            download_nltk_data: Whether to download NLTK data for METEOR
        """
        print("📊 Loading evaluation metrics...")
        
        # Download NLTK data for METEOR (first-time only)
        if download_nltk_data:
            try:
                nltk.data.find('corpora/wordnet')
            except LookupError:
                print("📥 Downloading NLTK WordNet data for METEOR...")
                nltk.download('wordnet', quiet=True)
                nltk.download('omw-1.4', quiet=True)
        
        # Load metrics from evaluate library
        self.rouge = evaluate.load("rouge")
        self.meteor = evaluate.load("meteor")
        
        # BERTScore model configuration
        self.bertscore_model = "microsoft/deberta-xlarge-mnli"  # Standard choice
        
        print("✅ All metrics ready: ROUGE, METEOR, BERTScore")
    
    def load_predictions(self, pred_file: str) -> Tuple[List[str], List[str], List[Dict]]:
        """
        Load predictions and references from JSONL file.
        
        Args:
            pred_file: Path to predictions JSONL file
            
        Returns:
            Tuple of (predictions, references, full_entries)
        """
        predictions = []
        references = []
        entries = []
        
        with open(pred_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                entries.append(entry)
                
                # Check which type of evaluation
                if 'prediction_summary' in entry:
                    predictions.append(entry['prediction_summary'])
                    references.append(entry['reference_summary'])
                elif 'prediction_title' in entry:
                    predictions.append(entry['prediction_title'])
                    references.append(entry['reference_title'])
        
        return predictions, references, entries
    
    def calculate_all_metrics(
        self,
        predictions: List[str],
        references: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate all evaluation metrics: ROUGE, METEOR, and BERTScore.
        
        Args:
            predictions: List of predicted texts
            references: List of reference texts
            
        Returns:
            Dictionary containing all metric scores
        """
        print(f"\n📊 Computing metrics for {len(predictions)} examples...")
        
        # 1. ROUGE scores (lexical overlap)
        print("  ⏳ Computing ROUGE...")
        rouge_results = self.rouge.compute(
            predictions=predictions,
            references=references,
            use_stemmer=True
        )
        
        # 2. METEOR scores (alignment + synonyms)
        print("  ⏳ Computing METEOR...")
        meteor_results = self.meteor.compute(
            predictions=predictions,
            references=references
        )
        
        # 3. BERTScore (semantic similarity)
        print("  ⏳ Computing BERTScore (this may take a minute)...")
        P, R, F1 = bertscore_compute(
            predictions,
            references,
            lang="en",
            model_type=self.bertscore_model,
            verbose=False
        )
        bertscore_f1 = F1.mean().item()
        bertscore_precision = P.mean().item()
        bertscore_recall = R.mean().item()
        
        # Combine all metrics
        results = {
            'rouge_scores': {
                'rouge1': rouge_results['rouge1'],
                'rouge2': rouge_results['rouge2'],
                'rougeL': rouge_results['rougeL']
            },
            'meteor_score': meteor_results['meteor'],
            'bertscore': {
                'f1': bertscore_f1,
                'precision': bertscore_precision,
                'recall': bertscore_recall
            },
            'num_examples': len(predictions)
        }
        
        print("  ✅ All metrics computed!")
        return results
    
    def calculate_rouge(
        self, 
        predictions: List[str], 
        references: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate ROUGE scores only (for backward compatibility).
        
        Args:
            predictions: List of predicted texts
            references: List of reference texts
            
        Returns:
            Dictionary of ROUGE scores
        """
        # Use evaluate library for all ROUGE scores
        results = self.rouge.compute(
            predictions=predictions,
            references=references,
            use_stemmer=True
        )
        
        # Calculate per-example scores for analysis
        per_example_scores = []
        for i, (pred, ref) in enumerate(zip(predictions, references)):
            # Compute individual scores
            individual = self.rouge.compute(
                predictions=[pred],
                references=[ref],
                use_stemmer=True
            )
            # individual is guaranteed to be a dict from rouge.compute()
            if individual:
                per_example_scores.append({
                    'rouge1': individual.get('rouge1', 0.0),
                    'rouge2': individual.get('rouge2', 0.0),
                    'rougeL': individual.get('rougeL', 0.0),
                })
        
        # Add statistics to results (which is guaranteed to be a dict)
        if results:
            results['per_example'] = per_example_scores
            results['num_examples'] = len(predictions)
        
        return results if results else {}
    
    def calculate_additional_metrics(
        self,
        predictions: List[str],
        references: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate additional evaluation metrics beyond ROUGE.
        
        Args:
            predictions: List of predicted texts
            references: List of reference texts
            
        Returns:
            Dictionary of additional metrics
        """
        exact_matches = sum(1 for p, r in zip(predictions, references) if p.strip().lower() == r.strip().lower())
        
        # Average lengths
        avg_pred_len = sum(len(p.split()) for p in predictions) / len(predictions)
        avg_ref_len = sum(len(r.split()) for r in references) / len(references)
        
        # Length ratio
        length_ratio = avg_pred_len / avg_ref_len if avg_ref_len > 0 else 0
        
        return {
            'exact_match_count': exact_matches,
            'exact_match_rate': exact_matches / len(predictions) if predictions else 0,
            'avg_prediction_length': avg_pred_len,
            'avg_reference_length': avg_ref_len,
            'length_ratio': length_ratio
        }
    
    def evaluate_file(
        self,
        pred_file: str,
        output_file: Optional[str] = None,
        use_all_metrics: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate a predictions file with comprehensive metrics.
        
        Args:
            pred_file: Path to predictions JSONL file
            output_file: Path to save results (optional)
            use_all_metrics: If True, compute ROUGE+METEOR+BERTScore; if False, only ROUGE
            
        Returns:
            Dictionary of all evaluation metrics
        """
        print(f"\n📊 Evaluating: {pred_file}")
        
        # Load data
        predictions, references, entries = self.load_predictions(pred_file)
        
        if not predictions:
            print("⚠️  No predictions found!")
            return {}
        
        print(f"   Found {len(predictions)} prediction-reference pairs")
        
        # Compute metrics
        if use_all_metrics:
            # Comprehensive evaluation: ROUGE + METEOR + BERTScore
            metric_results = self.calculate_all_metrics(predictions, references)
        else:
            # ROUGE only (for backward compatibility)
            rouge_scores = self.calculate_rouge(predictions, references)
            metric_results = {
                'rouge_scores': rouge_scores,
                'num_examples': len(predictions)
            }
        
        # Additional statistics
        additional_metrics = self.calculate_additional_metrics(predictions, references)
        
        # Combine all results
        results = {
            **metric_results,
            'additional_metrics': additional_metrics
        }
        
        # Print results
        self.print_results(results, use_all_metrics)
        
        # Save to file if specified
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Results saved to: {output_file}")
        
        return results
    
    def print_results(self, results: Dict[str, Any], show_all_metrics: bool = True):
        """
        Pretty print evaluation results.
        
        Args:
            results: Results dictionary
            show_all_metrics: Whether to show all metrics or just ROUGE
        """
        print("\n" + "="*60)
        print("📈 SUMMARY EVALUATION RESULTS")
        print("="*60)
        
        rouge = results['rouge_scores']
        print(f"\n🎯 ROUGE Scores (F1):")
        print(f"   ROUGE-1: {rouge['rouge1']:.4f}")
        print(f"   ROUGE-2: {rouge['rouge2']:.4f}")
        print(f"   ROUGE-L: {rouge['rougeL']:.4f}")
        
        if show_all_metrics and 'meteor_score' in results:
            print(f"\n🎯 METEOR Score:")
            print(f"   METEOR:  {results['meteor_score']:.4f}")
        
        if show_all_metrics and 'bertscore' in results:
            bert = results['bertscore']
            print(f"\n🎯 BERTScore:")
            print(f"   F1:        {bert['f1']:.4f}")
            print(f"   Precision: {bert['precision']:.4f}")
            print(f"   Recall:    {bert['recall']:.4f}")
        
        metrics = results['additional_metrics']
        print(f"\n📏 Additional Metrics:")
        print(f"   Exact Match Rate: {metrics['exact_match_rate']:.2%}")
        print(f"   Avg Prediction Length: {metrics['avg_prediction_length']:.1f} words")
        print(f"   Avg Reference Length: {metrics['avg_reference_length']:.1f} words")
        print(f"   Length Ratio: {metrics['length_ratio']:.2f}")
        
        print(f"\n📊 Dataset:")
        print(f"   Total Examples: {results['num_examples']}")
        
        # Paper-ready format
        print(f"\n📝 FOR YOUR PAPER:")
        if show_all_metrics and 'meteor_score' in results and 'bertscore' in results:
            print(f"   R-1: {rouge['rouge1']:.2f}, R-2: {rouge['rouge2']:.2f}, R-L: {rouge['rougeL']:.2f}, ")
            print(f"   METEOR: {results['meteor_score']:.2f}, BERTScore: {results['bertscore']['f1']:.2f}")
        else:
            print(f"   ROUGE-1: {rouge['rouge1']:.2f}, ROUGE-2: {rouge['rouge2']:.2f}, ROUGE-L: {rouge['rougeL']:.2f}")
        print(f"   (N={results['num_examples']} branch summaries)")
        
        print("="*60)
    
    def evaluate_file(self, pred_file: str, output_file: str = None, use_all_metrics: bool = True) -> Dict[str, Any]:
        """
        Evaluate predictions in a file using ROUGE and optionally METEOR and BERTScore.
        
        Args:
            pred_file: Path to predictions JSONL file
            output_file: Optional path to save results
            use_all_metrics: Whether to calculate METEOR and BERTScore (default: True)
            
        Returns:
            Dictionary of all evaluation metrics
        """
        print(f"\n📊 Evaluating: {pred_file}")
        
        # Load data
        predictions, references, entries = self.load_predictions(pred_file)
        
        if not predictions:
            print("❌ No predictions found in file")
            return {}
        
        print(f"   Loaded {len(predictions)} prediction-reference pairs")
        
        # Use comprehensive metric calculation if requested
        if use_all_metrics:
            results = self.calculate_all_metrics(predictions, references)
            results['evaluation_file'] = pred_file
        else:
            # Calculate ROUGE only
            rouge_scores = self.calculate_rouge(predictions, references)
            additional_metrics = self.calculate_additional_metrics(predictions, references)
            
            results = {
                'rouge_scores': {
                    'rouge1': rouge_scores['rouge1'],
                    'rouge2': rouge_scores['rouge2'],
                    'rougeL': rouge_scores['rougeL'],
                },
                'additional_metrics': additional_metrics,
                'num_examples': len(predictions),
                'evaluation_file': pred_file
            }
        
        # Print results
        self.print_results(results, show_all_metrics=use_all_metrics)
        
        # Save if output file specified
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Results saved to: {output_file}")
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """
        Pretty print evaluation results.
        
        Args:
            results: Results dictionary
        """
        print("\n" + "="*60)
        print("📈 ROUGE EVALUATION RESULTS")
        print("="*60)
        
        rouge = results['rouge_scores']
        print(f"\n🎯 ROUGE Scores (F1):")
        print(f"   ROUGE-1: {rouge['rouge1']:.4f}")
        print(f"   ROUGE-2: {rouge['rouge2']:.4f}")
        print(f"   ROUGE-L: {rouge['rougeL']:.4f}")
        
        metrics = results['additional_metrics']
        print(f"\n📏 Additional Metrics:")
        print(f"   Exact Match Rate: {metrics['exact_match_rate']:.2%}")
        print(f"   Avg Prediction Length: {metrics['avg_prediction_length']:.1f} words")
        print(f"   Avg Reference Length: {metrics['avg_reference_length']:.1f} words")
        print(f"   Length Ratio: {metrics['length_ratio']:.2f}")
        
        print(f"\n📊 Dataset:")
        print(f"   Total Examples: {results['num_examples']}")
        
        # Paper-ready format
        print(f"\n📝 FOR YOUR PAPER:")
        print(f"   ROUGE-1: {rouge['rouge1']:.2f}, ROUGE-2: {rouge['rouge2']:.2f}, ROUGE-L: {rouge['rougeL']:.2f}")
        print(f"   (N={results['num_examples']} branch summaries)")
        
        print("="*60)
    
    def format_for_paper(self, results: Dict[str, Any], include_all_metrics: bool = True) -> str:
        """
        Format results for academic paper reporting.
        
        Args:
            results: Results dictionary
            include_all_metrics: Whether to include METEOR and BERTScore in tables
            
        Returns:
            Formatted string ready for LaTeX tables
        """
        rouge = results['rouge_scores']
        n = results['num_examples']
        has_all = 'meteor_score' in results and 'bertscore' in results
        
        if include_all_metrics and has_all:
            # Full metrics table (ROUGE + METEOR + BERTScore)
            meteor = results['meteor_score']
            bert = results['bertscore']['f1']
            
            latex_table = f"""
% LaTeX table with comprehensive metrics
\\begin{{table}}[h]
\\centering
\\caption{{Branch-level summary evaluation with multiple metrics}}
\\label{{tab:summary-eval}}
\\begin{{tabular}}{{lccccc}}
\\hline
\\textbf{{Method}} & \\textbf{{R-1}} & \\textbf{{R-2}} & \\textbf{{R-L}} & \\textbf{{METEOR}} & \\textbf{{BERTScore}} \\\\
\\hline
Subchat Trees & {rouge['rouge1']:.2f} & {rouge['rouge2']:.2f} & {rouge['rougeL']:.2f} & {meteor:.2f} & {bert:.2f} \\\\
\\hline
\\end{{tabular}}
\\end{{table}}

% Text for results section:
The hierarchical subchat system achieved ROUGE-1, ROUGE-2, and ROUGE-L 
scores of {rouge['rouge1']:.2f}, {rouge['rouge2']:.2f}, and {rouge['rougeL']:.2f} 
respectively. METEOR score of {meteor:.2f} confirms alignment quality, while 
BERTScore of {bert:.2f} demonstrates semantic similarity (N={n} branch summaries).

% Markdown table:
| Method        | R-1  | R-2  | R-L  | METEOR | BERTScore |
|---------------|------|------|------|--------|-----------|
| Subchat Trees | {rouge['rouge1']:.2f} | {rouge['rouge2']:.2f} | {rouge['rougeL']:.2f} | {meteor:.2f}   | {bert:.2f}     |
"""
        else:
            # ROUGE only table
            latex_table = f"""
% LaTeX table for your paper (ROUGE only)
\\begin{{table}}[h]
\\centering
\\caption{{ROUGE scores for branch-level summary generation}}
\\label{{tab:rouge}}
\\begin{{tabular}}{{lccc}}
\\hline
\\textbf{{Method}} & \\textbf{{ROUGE-1}} & \\textbf{{ROUGE-2}} & \\textbf{{ROUGE-L}} \\\\
\\hline
Subchat Trees & {rouge['rouge1']:.2f} & {rouge['rouge2']:.2f} & {rouge['rougeL']:.2f} \\\\
\\hline
\\end{{tabular}}
\\end{{table}}

% Text for results section:
The hierarchical subchat system achieved ROUGE-1, ROUGE-2, and 
ROUGE-L scores of {rouge['rouge1']:.2f}, {rouge['rouge2']:.2f}, 
and {rouge['rougeL']:.2f} respectively (N={n} branch summaries).

% Markdown table:
| Method        | ROUGE-1 | ROUGE-2 | ROUGE-L |
|---------------|---------|---------|---------|
| Subchat Trees | {rouge['rouge1']:.2f}    | {rouge['rouge2']:.2f}    | {rouge['rougeL']:.2f}    |
"""
        return latex_table
    
    def compare_evaluations(
        self,
        summary_pred_file: str,
        title_pred_file: str,
        output_file: str = "backend/evaluation/results/comparison.json"
    ):
        """
        Compare summary and title evaluation results.
        
        Args:
            summary_pred_file: Path to summary predictions
            title_pred_file: Path to title predictions
            output_file: Path to save comparison
        """
        print("\n🔍 COMPARING SUMMARY VS TITLE EVALUATION\n")
        
        summary_results = self.evaluate_file(summary_pred_file)
        title_results = self.evaluate_file(title_pred_file)
        
        comparison = {
            'summary_evaluation': summary_results,
            'title_evaluation': title_results,
            'comparison': {
                'rouge1_diff': summary_results['rouge_scores']['rouge1'] - title_results['rouge_scores']['rouge1'],
                'rouge2_diff': summary_results['rouge_scores']['rouge2'] - title_results['rouge_scores']['rouge2'],
                'rougeL_diff': summary_results['rouge_scores']['rougeL'] - title_results['rouge_scores']['rougeL'],
            }
        }
        
        # Save comparison
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Comparison saved to: {output_file}")
        
        return comparison


def main():
    """Example usage."""
    evaluator = ROUGEEvaluator()
    
    # Check for prediction files
    summary_pred = "backend/evaluation/datasets/summary_eval_predictions.jsonl"
    title_pred = "backend/evaluation/datasets/title_eval_predictions.jsonl"
    
    if os.path.exists(summary_pred):
        print("🔍 Evaluating summary predictions...")
        evaluator.evaluate_file(
            summary_pred,
            output_file="backend/evaluation/results/summary_results.json"
        )
    else:
        print(f"⚠️  Summary predictions not found: {summary_pred}")
        print("   Run prediction_generator.py first")
    
    if os.path.exists(title_pred):
        print("\n🔍 Evaluating title predictions...")
        evaluator.evaluate_file(
            title_pred,
            output_file="backend/evaluation/results/title_results.json"
        )
    else:
        print(f"⚠️  Title predictions not found: {title_pred}")
    
    # Compare if both exist
    if os.path.exists(summary_pred) and os.path.exists(title_pred):
        print("\n🔍 Comparing both evaluations...")
        evaluator.compare_evaluations(summary_pred, title_pred)


if __name__ == "__main__":
    main()
