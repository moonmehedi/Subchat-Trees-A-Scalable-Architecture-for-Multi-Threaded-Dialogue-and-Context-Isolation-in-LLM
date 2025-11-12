#!/usr/bin/env python3
"""
Context Classifier for Binary Classification
Classifies responses as TP, TN, FP, or FN based on context matching
"""

import os
import re
from groq import Groq
from typing import Literal, Dict, Any

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
    """Binary classifier for context isolation testing"""
    
    def __init__(self):
        """Initialize with Groq client for LLM fallback"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")
        
        self.groq_client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"  # Cheap, fast model for classification
    
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
        Use LLM to classify ambiguous responses
        
        Args:
            response: AI response text
            expected_context: Expected context
        
        Returns:
            Classification result
        """
        
        prompt = f"""Is this response primarily about {expected_context}?

Response: "{response}"

Answer only with: yes or no"""
        
        try:
            result = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a binary classifier. Answer only 'yes' or 'no'."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0
            )
            
            answer = result.choices[0].message.content.strip().lower()
            
            if "yes" in answer:
                return "TP"
            else:
                return "FN"
        
        except Exception as e:
            print(f"⚠️  LLM classification failed: {e}")
            # Default to FN on error (conservative)
            return "FN"
    
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
