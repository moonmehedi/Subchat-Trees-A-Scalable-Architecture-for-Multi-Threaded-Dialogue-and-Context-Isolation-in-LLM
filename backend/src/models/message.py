from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime
import uuid # for generating unique IDs


class Message(BaseModel):
    """single message in hierarchical chat system"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # AUTO-GENERATED
    content:str = Field(min_length=1)
    role : str = Field(regex = '^(user|assistant|system)$')
    timestamp: datetime = Field(default_factory=datetime.now)   # AUTO-GENERATED
    node_id:str = Field(min_length=1)  # which node this message belongs to

    class Config:
        json_encodeers = {
            datetime: lambda v: v.isoformat()
        }


    

