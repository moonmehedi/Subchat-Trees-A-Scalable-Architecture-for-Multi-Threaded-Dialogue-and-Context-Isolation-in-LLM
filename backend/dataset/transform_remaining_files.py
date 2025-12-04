#!/usr/bin/env python3
"""
Transform remaining 3 files in nested_dataset to evaluation format
"""

import json
import re
from pathlib import Path

# File definitions with topic mappings
files_to_transform = {
    "22807e655dd042348cb0ee4023672e70_structured.json": {
        "topics": {
            2: ("personas_roleplay", "First persona request"),
            3: None,  # Continue personas
            4: None,  # Continue personas
            5: None,  # Continue personas
            6: None,  # Continue personas
            7: None,  # Continue personas
            8: ("llm_knowledge", "LLM meta-discussion"),
            9: None,  # Create subchat_1
            10: None,
            11: None,
            12: ("game_degree_guess", "Degree guessing game"),
            13: None,  # Create subchat_2
            14: None,
            15: None,
            16: None,
            17: None,
            18: None,
            19: None,
            20: None,
            21: ("game_twenty_questions", "Twenty Questions game"),
            22: None,  # Create subchat_3
            # Steps 23-29 continue game
            30: None,
            31: None,  # Create subchat_4
            # Steps 32-48 continue
            49: None,
            50: ("game_twenty_questions_role_reversal", "Role reversal confusion"),  # Create subchat_6
        }
    },
    "eaf06f12a1d74e5ca30a7ca94a7c4128_structured.json": {
        "topics": {
            2: ("cookies_preferences", "Cookie preferences"),
            3: None,
            4: None,
            5: ("cookies_recipe_halving", "Recipe halving with math errors"),
            # More topics to be identified
        }
    },
    "ec366fd3e4b5482e8acac750f9b3b55b_structured.json": {
        "topics": {
            2: ("history_india", "Indian history"),
            # More topics with explicit "New thread" markers
        }
    }
}

def add_instruction_step(data):
    """Add Step 1 instruction message"""
    instruction = {
        "step": 1,
        "context": "step_1",
        "message": "Welcome to the Topic Tracking Test! This is an evaluation dataset designed to test your ability to maintain context across multiple concurrent topics and subtopics.\n\nFormat Instructions:\n- When introducing a NEW topic or sub-topic, I will prefix my question with: topic_name : actual question\n- When continuing an existing topic, I will ask the question WITHOUT any prefix\n- You must ALWAYS respond by starting with 'topic_name:' (with colon) followed by your answer\n- The topic name indicates which conversation thread you should be in\n\nExample patterns:\nIntroduction: \"topic_name : user query\"\nFollow-up: \"actual question\" (no prefix needed)\nYour response format: \"topic_name: [your answer here]\"\n\nSub-topics use parent_subtopic naming:\nIntroduction: \"parent_subtopic : user query\"\nYour response: \"parent_subtopic: [your answer]\"\n\nRemember:\n- ALWAYS start responses with 'topic_name:' even when I don't use a prefix\n- Topic prefixes in my questions are ONLY for introducing new topics\n- Follow-up questions continue the current active topic\n\nLet's begin the test. Track the topics carefully!",
        "expected": "Response must acknowledge understanding of topic tracking test format and readiness to begin",
        "node_type": "main",
        "action": "",
        "linear_failure_risk": "low"
    }
    
    # Shift all existing steps by 1
    for conv in data['conversations']:
        conv['step'] += 1
        conv['context'] = f"step_{conv['step']}"
    
    # Insert instruction at beginning
    data['conversations'].insert(0, instruction)
    data['total_turns'] += 1

def update_expected_fields(data):
    """Update all expected fields to require topic prefix"""
    current_topic = None
    
    for conv in data['conversations']:
        if conv['step'] == 1:
            continue  # Skip instruction
        
        # Detect topic introductions (messages with topic_name : pattern)
        message = conv.get('message', '')
        topic_match = re.match(r'^(\w+(?:_\w+)*)\s*:\s*', message)
        
        if topic_match:
            current_topic = topic_match.group(1)
        
        # Update expected field
        if current_topic and 'expected' in conv:
            expected = conv['expected']
            # Add "Response must start with 'topic:'" prefix
            if not expected.startswith("Response must start with"):
                conv['expected'] = f"Response must start with '{current_topic}:' - {expected}"

def transform_file(filename):
    """Transform a single file"""
    filepath = Path("nested_dataset") / filename
    
    print(f"\n{'='*80}")
    print(f"Transforming: {filename}")
    print(f"{'='*80}")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    print(f"  Original turns: {data['total_turns']}")
    
    # Add instruction step
    add_instruction_step(data)
    
    print(f"  After adding instruction: {data['total_turns']}")
    
    # Update expected fields
    update_expected_fields(data)
    
    # Save
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Saved: {filepath}")

if __name__ == "__main__":
    for filename in files_to_transform.keys():
        try:
            transform_file(filename)
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'='*80}")
    print("✅ Transformation complete for all files!")
    print(f"{'='*80}")
