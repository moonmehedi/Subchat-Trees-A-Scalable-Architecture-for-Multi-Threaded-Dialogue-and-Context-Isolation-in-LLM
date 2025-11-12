#!/usr/bin/env python3
"""Quick test for classifier fixes"""

from context_classifier import ContextClassifier

classifier = ContextClassifier()

# Test cases that were failing
test_cases = [
    {
        "response": "### Hello, World! in Python\n\n**1. Create a file**",
        "expected": "programming",
        "should_be": "TP"
    },
    {
        "response": "## 🎯 What Are Python Functions?\n\nA **function** is a reusable block of code that performs a specific task.",
        "expected": "programming",
        "should_be": "TP"
    },
    {
        "response": "## What Do Pythons Eat in the Wild?\n\nPythons are **large constrictors** that feed on a wide variety of vertebrate prey.",
        "expected": "snake",
        "should_be": "TP"
    }
]

print("Testing classifier with word boundaries...\n")

for i, test in enumerate(test_cases, 1):
    details = classifier.get_classification_details(
        test["response"],
        test["expected"]
    )
    
    status = "✅" if details["classification"] == test["should_be"] else "❌"
    print(f"{status} Test {i}: Expected {test['should_be']}, Got {details['classification']}")
    print(f"   Method: {details['method']}")
    print(f"   Expected keywords found: {details['expected_keywords_found']}")
    print(f"   Forbidden keywords found: {details['forbidden_keywords_found']}")
    print()
