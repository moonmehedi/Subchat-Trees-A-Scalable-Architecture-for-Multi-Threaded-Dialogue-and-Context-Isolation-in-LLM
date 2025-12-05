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
    
    # LLM Provider Selection
    llm_provider: str = 'ollama'  # Options: 'ollama', 'groq', 'openai'
    
    # Ollama settings
    ollama_base_url: str = 'http://localhost:11434'
    ollama_model: str = 'llama3.1:8b'
    ollama_num_threads: Optional[int] = None  # Auto-detect CPU cores
    
    # Model configurations - centralized model names
    model_tool_calling: str = 'llama-3.3-70b-versatile'  # For tool/function calling decisions (Groq)
    model_base: str = 'llama-3.1-8b-instant'  # For conversation (Groq)

    #chip: llama-3.1-8b-instant base:openai/gpt-oss-20b toolcalling:llama-3.3-70b-versatile
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load API keys from environment after initialization
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.llm_provider = os.getenv("LLM_PROVIDER", "ollama")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        
        # CPU optimization: use all available cores
        if self.ollama_num_threads is None:
            import multiprocessing
            self.ollama_num_threads = multiprocessing.cpu_count()
            print(f"🚀 Ollama will use {self.ollama_num_threads} CPU threads for inference")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Setting()