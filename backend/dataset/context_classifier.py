#!/usr/bin/env python3
"""
Context Classifier for Binary Classification
Classifies responses as TP, TN, FP, or FN based on context matching

Supports dual backends:
- Groq (cloud): Used when GROQ_API_KEY is set in environment
- vLLM (local): Used on Kaggle or when Groq is not available
"""

import os
import re
import json
from typing import Literal, Dict, Any

# Groq import is optional
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

# Context keyword definitions - will be matched as whole words with boundaries
CONTEXT_KEYWORDS = {
    "programming": [
        "function", "variable", "loop", "class", "import",
        "syntax", "error", "debug", "compile", "execute", "return",
        "array", "dictionary", "integer", "boolean",
        "lambda", "iterator", "module", "package", "library"
    ],
    "snake": [
        "reptile", "venom", "prey", "hunt", "coil", "fangs", "habitat",
        "scales", "constrictor", "bite", "capture", "species",
        "slither", "shed skin", "eggs", "predator", "nocturnal", "camouflage",
        "python snake", "boa", "anaconda", "serpent"
    ],
    "project": [
        "research", "conservation", "permit", "documentation",
        "specimen", "field study", "survey", "funding", "proposal",
        "grant", "methodology", "publication", "thesis"
    ],
    "fruit": [
        "nutrition", "vitamin", "recipe", "orchard",
        "harvest", "organic", "juice", "fresh fruit", "healthy",
        "calories", "fiber", "antioxidant", "sweetness", "ripe"
    ],
    "company": [
        "business", "stock", "CEO", "market", "revenue",
        "iPhone", "iPad", "Mac", "software company", "hardware", "Apple Inc",
        "Cupertino", "Tim Cook", "shareholder", "quarterly", "earnings"
    ],
    "island": [
        "Indonesia", "tourism", "beach", "volcano", "travel",
        "Bali", "Jakarta", "tropical island", "ocean", "resort"
    ],
    "coffee": [
        "brew", "espresso", "latte", "cappuccino", "caffeine", "roast",
        "beans", "grind", "flavor", "aroma", "barista"
    ]
}


class ContextClassifier:
    """Binary classifier for context isolation testing.
    
    Strictly follows LLM_BACKEND setting from environment:
    - 'groq': Uses Groq cloud API for judging (requires GROQ_API_KEY)
    - 'vllm': Uses vLLM local GPU for judging (requires vLLM model to be loaded)
    
    No silent fallbacks - if specified backend is not available, raises error.
    """
    
    def __init__(self):
        """Initialize with Groq or vLLM client based on LLM_BACKEND setting."""
        import sys
        import os
        backend_path = os.path.join(os.path.dirname(__file__), '..')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        self.groq_client = None
        self.vllm_client = None
        self.use_groq = False
        self.use_vllm = False
        
        # Get LLM_BACKEND from environment (default to 'groq' for backward compatibility)
        llm_backend = os.getenv("LLM_BACKEND", "groq").strip().strip("'\"")
        print(f"🔧 ContextClassifier: LLM_BACKEND configured as: '{llm_backend}'")
        
        if llm_backend == "groq":
            # Use Groq for classification - STRICT, no fallback
            if not GROQ_AVAILABLE:
                raise RuntimeError(
                    "❌ LLM_BACKEND='groq' specified but groq package not installed!\n"
                    "   Install with: pip install groq\n"
                    "   If you want to use vLLM instead, set LLM_BACKEND='vllm' in .env"
                )
            
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise RuntimeError(
                    "❌ LLM_BACKEND='groq' specified but GROQ_API_KEY not found!\n"
                    "   Set GROQ_API_KEY in your .env file.\n"
                    "   If you want to use vLLM instead, set LLM_BACKEND='vllm' in .env"
                )
            
            self.groq_client = Groq(api_key=groq_api_key)
            self.use_groq = True
            self.groq_model = "llama-3.1-8b-instant"
            print("✅ ContextClassifier using GROQ for JUDGING/CLASSIFICATION")
        
        elif llm_backend == "vllm":
            # Use vLLM for classification - STRICT, no fallback
            try:
                from src.services.vllm_client import vllm_client
                if not vllm_client.is_available():
                    raise RuntimeError(
                        "❌ LLM_BACKEND='vllm' specified but vLLM model not loaded!\n"
                        "   Call VLLMClient.set_model(llm) before using ContextClassifier.\n"
                        "   If you want to use Groq instead, set LLM_BACKEND='groq' in .env"
                    )
                self.vllm_client = vllm_client
                self.use_vllm = True
                print("✅ ContextClassifier using vLLM for JUDGING/CLASSIFICATION")
            except ImportError as e:
                raise RuntimeError(
                    f"❌ LLM_BACKEND='vllm' specified but vLLM not available!\n"
                    f"   Import error: {e}\n"
                    "   Make sure backend/src/services/vllm_client.py is accessible.\n"
                    "   If you want to use Groq instead, set LLM_BACKEND='groq' in .env"
                )
        
        else:
            raise RuntimeError(
                f"❌ Unknown LLM_BACKEND for ContextClassifier: '{llm_backend}'\n"
                "   Valid options: 'groq', 'vllm'\n"
                "   Set LLM_BACKEND in your .env file."
            )
    
    def classify(
        self, 
        response: str, 
        expected_context: str
    ) -> Literal["TP", "TN", "FP", "FN"]:
        """
        Classify response using LLM only (more accurate and dynamic)
        
        Args:
            response: AI response text
            expected_context: Expected context (programming, snake, etc.)
        
        Returns:
            "TP": True Positive - Response matches expected context
            "TN": True Negative - Response correctly avoids expected context
            "FP": False Positive - Wrong context appears
            "FN": False Negative - Expected context missing
        """
        
        # Use LLM classification directly - no keyword matching
        return self._llm_classify(response, expected_context)
    
    def _llm_classify(
        self, 
        response: str, 
        expected_context: str
    ) -> Literal["TP", "TN", "FP", "FN"]:
        """
        Use LLM to classify responses with strict prefix checking
        
        Args:
            response: AI response text
            expected_context: Expected context or strict prefix requirement
        
        Returns:
            Classification result (TP/TN/FP/FN)
        """
        
        prompt = f"""You are a strict test evaluator checking AI RESPONSE topic  matches with  REQUIREMENT topic .

REQUIREMENT: {expected_context}

AI RESPONSE: {response}

RULES:
1. Check IF both Topic matches and AI RESPONSE and REQUIREMENT relates to the same topic
2. The very first word(s) in AI RESPONSE define the topic name, match this with Requirement
3. If AI RESPONSE topic matches with starts with ANY of the rejected prefixes or topics , return NO
4. Ignore everything after the prefix - we only care about the START
5. Be STRICT - wrong prefix = NO, even if content is correct

EXAMPLES:

Requirement: "Response must start with 'by_length:' (not odd_count:, not move_one_ball:)"
Response: "by_length: Here is the solution..."
Answer: yes

Requirement: "Response must start with 'by_length:' (not odd_count:, not move_one_ball:)"
Response: "odd_count: To solve by_length..."
Answer: no (starts with wrong prefix odd_count:)

Requirement: "Response must start with 'Python:' (not Java:, not C++:)"
Response: "Python: Here's how to use lists..."
Answer: yes

Requirement: "Response must start with 'Python:' (not Java:, not C++:)"
Response: "Java: You can use ArrayList..."
Answer: no (starts with wrong prefix Java:)

Does the response satisfy the requirement?

Answer only with: yes or no"""
        
        try:
            # Use appropriate backend for classification
            if self.use_groq:
                # Use Groq API
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[
                        {"role": "system", "content": "You are a strict test evaluator. Check if the response contain the right topic name at the beginning. Answer only 'yes' or 'no'."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0,
                    max_tokens=50
                )
                result = response.choices[0].message.content.strip()
            elif self.use_vllm:
                # Use vLLM for classification (Kaggle GPU)
                messages = [
                    {"role": "system", "content": "You are a strict test evaluator. Check if the response contain the right topic name at the beginning. Answer only 'yes' or 'no'."},
                    {"role": "user", "content": prompt}
                ]
                
                result = self.vllm_client.generate(
                    messages=messages,
                    temperature=0,
                    max_tokens=50
                )
            else:
                # No backend available - default to FN
                print("⚠️  No LLM backend configured for classification")
                return "FN"
            
            answer = result.strip().lower()

            print('****************** The answer from LLm***************',answer,prompt)
            
            if "yes" in answer:
                return "TP"
            else:
                return "FN"
        
        except Exception as e:
            print(f"❌ CRITICAL: LLM classification failed: {e}")
            import traceback
            traceback.print_exc()
            # Re-raise to stop execution
            raise
    
    def get_classification_details(
        self,
        response: str,
        expected_context: str
    ) -> Dict[str, Any]:
        """
        Get detailed classification information using LLM
        
        Returns:
            - classification: TP/TN/FP/FN
            - method: "llm"
            - explanation: Why this classification was chosen
        """
        
        classification = self.classify(response, expected_context)
        
        return {
            "classification": classification,
            "method": "llm",
            "explanation": f"LLM classified response as {classification} for context '{expected_context}'"
        }
