from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Setting(BaseModel):
    app_name :str  =  'subchat trees api'
    version:str = '0.1.0'
    debug:bool = True

    #server settings
    host: str = '0.0.0.0'
    port: int = 8000

    #llm settings
    openai_api_key:Optional[str]= None
    groq_api_key:Optional[str]= None
    default_model_name:str = 'gpt-4o-mini'
    
    # LLM Backend Selection
    llm_backend: str = 'groq'  # Options: 'groq', 'ollama', 'vllm'
    ollama_base_url: str = 'http://localhost:11434'  # Ollama API endpoint
    
    # vLLM settings (for Kaggle GPU inference)
    vllm_model_path: str = '/kaggle/input/qwen-3/transformers/14b-awq/1'  # Matches notebook model  # Path to vLLM model
    
    # Model configurations - centralized model names
    # Groq models (cloud)
    model_tool_calling_groq: str = 'llama-3.3-70b-versatile'  # For tool/function calling decisions
    model_base_groq: str = 'llama-3.1-8b-instant'  # For conversation, reasoning, and response generation
    
    # Ollama models (local)
    model_tool_calling_ollama: str = 'llama3.1:8b'  # Local Ollama model for tool calling
    model_base_ollama: str = 'llama3.1:8b'  # Local Ollama model for conversation
    
    # Active models (dynamically set based on backend)
    model_tool_calling: str = 'llama-3.3-70b-versatile'
    model_base: str = 'llama-3.1-8b-instant'

    #chip: llama-3.1-8b-instant base:openai/gpt-oss-20b toolcalling:llama-3.3-70b-versatile
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load API keys from environment after initialization
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Load LLM backend preference
        self.llm_backend = os.getenv("LLM_BACKEND", "groq").lower()
        
        # Set active models based on backend
        if self.llm_backend == "ollama":
            self.model_tool_calling = self.model_tool_calling_ollama
            self.model_base = self.model_base_ollama
            print(f"✅ Using Ollama backend with model: {self.model_base}")
        elif self.llm_backend == "vllm":
            self.model_tool_calling = "vllm-local"  # vLLM doesn't distinguish
            self.model_base = "vllm-local"
            print(f"✅ Using vLLM backend with Kaggle GPU: {self.vllm_model_path}")
        else:
            self.model_tool_calling = self.model_tool_calling_groq
            self.model_base = self.model_base_groq
            print(f"✅ Using Groq backend with model: {self.model_base}")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Setting()