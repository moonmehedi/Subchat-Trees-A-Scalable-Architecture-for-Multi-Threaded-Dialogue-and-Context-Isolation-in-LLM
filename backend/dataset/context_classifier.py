#!/usr/bin/env python3
"""
Context Classifier for Binary Classification
Classifies responses as TP, TN, FP, or FN based on context matching
"""

import os
import re
import json
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
            result = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strict test evaluator. Check if the response contain the right topic name at the beginning. Answer only 'yes' or 'no'."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0
            )
            
            answer = result.choices[0].message.content.strip().lower()

            print('****************** The answer from LLm***************',answer,prompt)
            
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
