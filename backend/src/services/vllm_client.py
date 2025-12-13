"""
vLLM Client for Kaggle GPU Inference
Provides a singleton interface to the globally loaded vLLM model
"""

from typing import List, Dict, Optional
import os

class VLLMClient:
    """
    Singleton client for vLLM model inference on Kaggle GPUs.
    Uses the globally loaded `llm` object from the notebook.
    """
    
    _instance = None
    _llm = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VLLMClient, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def set_model(cls, llm_model):
        """
        Set the globally loaded vLLM model from Kaggle notebook.
        Call this once after loading the model in the notebook.
        
        Example in notebook:
            from backend.src.services.vllm_client import VLLMClient
            VLLMClient.set_model(llm)  # Pass the loaded vLLM model
        """
        cls._llm = llm_model
        print("✅ vLLM model registered with VLLMClient")
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if vLLM model is loaded and available"""
        return cls._llm is not None
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 1000,
        top_p: float = 0.9
    ) -> str:
        """
        Generate response from vLLM model.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            
        Returns:
            Generated text response
        """
        if not self.is_available():
            raise RuntimeError(
                "vLLM model not loaded. "
                "Call VLLMClient.set_model(llm) in your notebook first."
            )
        
        # Convert messages to prompt format
        prompt = self._messages_to_prompt(messages)
        
        # Import here to avoid issues when vllm not available
        from vllm import SamplingParams
        
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        
        # Generate response
        outputs = self._llm.generate([prompt], sampling_params)
        
        # Extract text from output
        generated_text = outputs[0].outputs[0].text
        
        # Store usage stats (approximate)
        self.last_usage = {
            "prompt_tokens": len(prompt.split()) * 1.3,  # Rough estimate
            "completion_tokens": len(generated_text.split()) * 1.3,  # Rough estimate
            "total_tokens": (len(prompt) + len(generated_text)) * 1.3 / 4  # Rough estimate
        }
        
        return generated_text
    
    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 1000,
        top_p: float = 0.9
    ):
        """
        Generate streaming response from vLLM model.
        
        Note: vLLM doesn't support true streaming in the same way as APIs,
        so we'll yield the complete response at once.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling
            
        Yields:
            Generated text chunks
        """
        # For simplicity, generate full response and yield it
        # vLLM's streaming is more complex and not needed for this use case
        response = self.generate(messages, temperature, max_tokens, top_p)
        
        # Yield in chunks to simulate streaming
        chunk_size = 50
        for i in range(0, len(response), chunk_size):
            yield response[i:i+chunk_size]
    
    def get_last_usage(self) -> Dict[str, int]:
        """Get approximate token usage from last generation"""
        return getattr(self, 'last_usage', {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        })
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert OpenAI-style messages to a single prompt string.
        Follows Qwen chat template format.
        """
        prompt_parts = []
        
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        # Add final prompt for assistant response
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)


# Global singleton instance
vllm_client = VLLMClient()
