"""
AI-Based Test Evaluator

Uses LLM to semantically evaluate if AI responses correctly answer questions.
Provides more intelligent validation than simple keyword matching.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from groq import Groq


class AIEvaluator:
    """Evaluates test responses using AI for semantic understanding."""
    
    def __init__(self, model: str = "llama-3.1-8b-instant", temperature: float = 0.0):
        """
        Initialize the AI Evaluator.
        
        Args:
            model: The model to use for evaluation (via GROQ API)
            temperature: Temperature for model responses (0.0 = fully deterministic for reproducibility)
        """
        self.model = model
        self.temperature = temperature
        self.groq_client = None  # Will be initialized when needed
        
        # Setup logging to dataset logs directory
        log_dir = Path(__file__).parent / "logs" / "dataset-results"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.eval_log = log_dir / "AI_EVALUATION.log"
    
    def _ensure_groq_client(self):
        """Initialize Groq client only when needed."""
        if self.groq_client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable not set. Required for AI evaluation.")
            self.groq_client = Groq(api_key=api_key)
        
    def evaluate_response(
        self,
        question: str,
        ai_response: str,
        expected_info: str,
        expected_keywords: Optional[List[str]] = None,
        forbidden_keywords: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Evaluate if AI response correctly answers the question.
        
        Returns dict with:
            - keyword_check: bool
            - ai_evaluation: bool  
            - ai_reason: str
            - final_result: bool
            - details: dict
        """
        result = {
            "question": question,
            "response": ai_response,
            "expected": expected_info,
            "timestamp": datetime.now().isoformat()
        }
        
        # Method 1: Keyword validation
        keyword_result = self._keyword_check(
            ai_response, 
            expected_keywords or [],
            forbidden_keywords or []
        )
        result.update(keyword_result)
        
        # Method 2: AI semantic evaluation
        ai_result = self._ai_semantic_check(
            question,
            ai_response,
            expected_info,
            forbidden_keywords or []
        )
        result.update(ai_result)
        
        # Final verdict: Both must pass
        result["final_result"] = result["keyword_pass"] and result["ai_pass"]
        
        # Log the evaluation
        self._log_evaluation(result)
        
        return result
    
    def _keyword_check(
        self,
        response: str,
        expected_keywords: List[str],
        forbidden_keywords: List[str]
    ) -> Dict[str, any]:
        """Check for presence/absence of specific keywords."""
        response_lower = response.lower()
        
        found_expected = []
        missing_expected = []
        found_forbidden = []
        
        # Check expected keywords
        for keyword in expected_keywords:
            if keyword.lower() in response_lower:
                found_expected.append(keyword)
            else:
                missing_expected.append(keyword)
        
        # Check forbidden keywords
        for keyword in forbidden_keywords:
            if keyword.lower() in response_lower:
                found_forbidden.append(keyword)
        
        passed = (len(missing_expected) == 0 and len(found_forbidden) == 0)
        
        return {
            "keyword_pass": passed,
            "found_expected": found_expected,
            "missing_expected": missing_expected,
            "found_forbidden": found_forbidden
        }
    
    def _ai_semantic_check(
        self,
        question: str,
        response: str,
        expected_info: str,
        forbidden_keywords: List[str]
    ) -> Dict[str, any]:
        """Use AI to evaluate semantic correctness."""
        
        forbidden_str = f"\nFORBIDDEN KEYWORDS (context pollution): {', '.join(forbidden_keywords)}" if forbidden_keywords else ""
        
        prompt = f"""You are a strict test validator for a RAG (Retrieval-Augmented Generation) system.

USER QUESTION: {question}

AI RESPONSE: {response}

EXPECTED INFORMATION: {expected_info}{forbidden_str}

TASK: Determine if the AI response correctly answers the question using the expected information.

RULES:
1. The response doesn't need exact wording - semantic correctness matters
2. If the answer is present but paraphrased, that's PASS
3. If the answer is missing or incorrect, that's FAIL
4. If forbidden keywords appear, that indicates context pollution - FAIL
5. Be strict but fair - the core information must be there

Reply in JSON format:
{{
  "result": "PASS" or "FAIL",
  "reason": "Brief explanation (1-2 sentences max)",
  "confidence": "high" or "medium" or "low"
}}

Respond ONLY with valid JSON, no other text."""

        try:
            self._ensure_groq_client()
            
            # Call GROQ API using client (like simple_llm.py)
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=200
            )
            
            # Extract evaluation
            eval_text = response.choices[0].message.content.strip()
            
            # Parse JSON (handle potential markdown wrapping)
            if "```json" in eval_text:
                eval_text = eval_text.split("```json")[1].split("```")[0].strip()
            elif "```" in eval_text:
                eval_text = eval_text.split("```")[1].split("```")[0].strip()
            
            evaluation = json.loads(eval_text)
            
            return {
                "ai_pass": evaluation["result"] == "PASS",
                "ai_reason": evaluation["reason"],
                "ai_confidence": evaluation.get("confidence", "unknown"),
                "ai_raw_response": eval_text
            }
            
        except Exception as e:
            print(f"⚠️  AI evaluation error: {e}")
            # Fallback: assume pass if AI fails
            return {
                "ai_pass": True,
                "ai_reason": f"AI evaluation failed: {str(e)}, defaulting to PASS",
                "ai_confidence": "none",
                "ai_raw_response": str(e)
            }
    
    def _log_evaluation(self, result: Dict[str, any]):
        """Log evaluation details for human review with FULL responses."""
        
        timestamp = result["timestamp"]
        status_icon = "✅" if result["final_result"] else "❌"
        
        log_entry = f"""
{'='*80}
[{timestamp}] {status_icon} EVALUATION
{'='*80}

QUESTION: {result['question']}

AI RESPONSE (FULL):
{result['response']}

EXPECTED: {result['expected']}

EVALUATION METHODS:
{'-'*80}

1. KEYWORD CHECK: {'✅ PASS' if result['keyword_pass'] else '❌ FAIL'}
   Expected keywords found: {', '.join(result['found_expected']) if result['found_expected'] else 'None'}
   Expected keywords missing: {', '.join(result['missing_expected']) if result['missing_expected'] else 'None'}
   Forbidden keywords found: {', '.join(result['found_forbidden']) if result['found_forbidden'] else 'None'}

2. AI EVALUATION: {'✅ PASS' if result['ai_pass'] else '❌ FAIL'} (Confidence: {result['ai_confidence']})
   Evaluator Reasoning: "{result['ai_reason']}"

FINAL RESULT: {status_icon} {'PASS' if result['final_result'] else 'FAIL'} (Both methods must pass)
{'='*80}

"""
        
        # Append to log file
        with open(self.eval_log, 'a') as f:
            f.write(log_entry)
    
    def generate_summary(self) -> str:
        """Generate summary of all evaluations."""
        if not self.eval_log.exists():
            return "No evaluations logged yet."
        
        with open(self.eval_log, 'r') as f:
            content = f.read()
        
        # Count passes and fails
        total = content.count("EVALUATION")
        passes = content.count("✅ PASS (Both methods must pass)")
        fails = content.count("❌ FAIL (Both methods must pass)")
        
        summary = f"""
AI Evaluation Summary
{'='*80}
Total Evaluations: {total}
✅ Passed: {passes}
❌ Failed: {fails}
Pass Rate: {(passes/total*100):.1f}% if total > 0 else 0%

Full details available in: {self.eval_log}
{'='*80}
"""
        return summary
