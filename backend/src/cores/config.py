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
    
    # Model configurations - centralized model names
    model_tool_calling: str = 'llama-3.3-70b-versatile'  # For tool/function calling decisions
    model_base: str = 'llama-3.1-8b-instant'  # For conversation, reasoning, and response generation

    #chip: llama-3.1-8b-instant base:openai/gpt-oss-20b toolcalling:llama-3.3-70b-versatile
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load API keys from environment after initialization
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Setting()