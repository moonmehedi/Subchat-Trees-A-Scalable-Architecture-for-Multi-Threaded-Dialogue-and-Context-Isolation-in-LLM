#!/usr/bin/env python3
"""
Quick verification script to test API key loading and configuration.
"""

import os
from pathlib import Path

def test_env_loading():
    """Test that .env file loads properly with API keys"""
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    print("✅ .env file found")
    
    # Load environment variables from .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ dotenv loaded successfully")
    except ImportError:
        print("⚠️  dotenv not installed, loading manually...")
        
        # Manual .env loading for testing
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    
    # Test API keys
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"), 
        "LANGCHAIN_API_KEY": os.getenv("LANGCHAIN_API_KEY")
    }
    
    print("\n🔑 API Key Status:")
    all_keys_present = True
    
    for key_name, key_value in api_keys.items():
        if key_value and key_value != "your_*_api_key_here":
            print(f"✅ {key_name}: {'*' * 10}...{key_value[-4:] if len(key_value) > 4 else '****'}")
        else:
            print(f"❌ {key_name}: Not set or placeholder")
            all_keys_present = False
    
    # Test other important settings
    print("\n⚙️  Configuration Status:")
    config_checks = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "CHROMA_DB_PATH": os.getenv("CHROMA_DB_PATH"),
        "LLM_MODEL": os.getenv("LLM_MODEL"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT")
    }
    
    for setting, value in config_checks.items():
        if value:
            print(f"✅ {setting}: {value}")
        else:
            print(f"⚠️  {setting}: Not set")
    
    print(f"\n🎯 Overall Status: {'Ready for development!' if all_keys_present else 'API keys need configuration'}")
    return all_keys_present

if __name__ == "__main__":
    test_env_loading()
