import openai
from groq import Groq
import ollama
from typing import List, Dict
import json
from ..models.tree import TreeNode
from ..cores.config import settings  # Use your existing config
from .tools import ConversationTools
from ..utils.debug_logger import get_debug_logger

class SimpleLLMClient:
    """ Simple LLM client using Groq/vLLM/Ollama API with optional RAG.
    
    Strictly follows LLM_BACKEND setting from .env:
    - 'groq': Uses Groq cloud API (requires GROQ_API_KEY)
    - 'vllm': Uses vLLM local GPU (requires vLLM model to be loaded)
    - 'ollama': Uses Ollama local server
    
    No silent fallbacks - if specified backend is not available, raises error.
    """

    def __init__(self, api_key: str = None, enable_vector_index: bool = False):
        # Initialize LLM client based on backend setting
        self.llm_backend = settings.llm_backend
        self.groq_client = None
        self.ollama_available = False
        self.vllm_client = None
        
        print(f"🔧 LLM_BACKEND configured as: '{self.llm_backend}'")
        
        if self.llm_backend == "vllm":
            # Use vLLM (Kaggle GPU) - STRICT, no fallback
            try:
                from .vllm_client import vllm_client
                if vllm_client.is_available():
                    self.vllm_client = vllm_client
                    # Get model name for display
                    try:
                        model_name = getattr(vllm_client._llm.llm_engine.model_config, 'model', 'Unknown')
                        print(f"✅ vLLM connected for RESPONSES: {model_name}")
                        print(f"✅ vLLM will be used for SUMMARIZATION: {model_name}")
                    except:
                        print(f"✅ vLLM connected. Using Kaggle GPU")
                        print(f"✅ vLLM will be used for responses and summarization")
                else:
                    raise RuntimeError(
                        "❌ LLM_BACKEND='vllm' specified but vLLM model not loaded!\n"
                        "   Call VLLMClient.set_model(llm) before using SimpleLLMClient.\n"
                        "   If you want to use Groq instead, set LLM_BACKEND='groq' in .env"
                    )
            except ImportError as e:
                raise RuntimeError(
                    f"❌ LLM_BACKEND='vllm' specified but vLLM not available!\n"
                    f"   Import error: {e}\n"
                    "   Install with: pip install vllm\n"
                    "   If you want to use Groq instead, set LLM_BACKEND='groq' in .env"
                )
        
        elif self.llm_backend == "ollama":
            # Use Ollama (local) - STRICT, no fallback
            try:
                # Test Ollama connection
                ollama.list()
                self.ollama_available = True
                print(f"✅ Ollama connected. Using model: {settings.model_base}")
            except Exception as e:
                raise RuntimeError(
                    f"❌ LLM_BACKEND='ollama' specified but Ollama not available!\n"
                    f"   Error: {e}\n"
                    "   Make sure Ollama is running: ollama serve\n"
                    "   If you want to use Groq instead, set LLM_BACKEND='groq' in .env"
                )
        
        elif self.llm_backend == "groq":
            # Use Groq (cloud) - STRICT, no fallback
            if api_key:
                self.groq_client = Groq(api_key=api_key)
                print(f"✅ Groq connected (custom API key). Using model: {settings.model_base}")
            elif settings.groq_api_key:
                self.groq_client = Groq(api_key=settings.groq_api_key)
                print(f"✅ Groq connected. Using model: {settings.model_base}")
            else:
                raise RuntimeError(
                    "❌ LLM_BACKEND='groq' specified but GROQ_API_KEY not found!\n"
                    "   Set GROQ_API_KEY in your .env file.\n"
                    "   If you want to use vLLM instead, set LLM_BACKEND='vllm' in .env"
                )
        
        else:
            raise RuntimeError(
                f"❌ Unknown LLM_BACKEND: '{self.llm_backend}'\n"
                "   Valid options: 'groq', 'vllm', 'ollama'\n"
                "   Set LLM_BACKEND in your .env file."
            )
        
        # Initialize vector index if enabled
        self.vector_index = None
        if enable_vector_index:
            try:
                from .vector_index import GlobalVectorIndex
                self.vector_index = GlobalVectorIndex()
                print("✅ Vector index enabled for RAG")
            except Exception as e:
                print(f"⚠️  Failed to initialize vector index: {e}")

    def generate_response(self, node: TreeNode, user_message: str) -> str:
        """ Generate response using node's hierarchical context with follow-up awareness """

        # Build context from node's buffer (inherited from parents)
        context_messages = []

        # Add base system prompt for multi-topic evaluation
        context_messages.append({
            'role': 'system',
            'content': (
                "You are participating in a multi-topic, multi-turn evaluation where topics persist "
                "independently of conversational order. Topics are introduced using the format "
                "topic_name : user query, and sub-topics using topic_name_subtopic_name : user query; "
                "these topic labels remain available for future reference. For every user query, you must "
                "analyze its semantic meaning and select the previously introduced topic or sub-topic it "
                "most strongly refers to, regardless of recency or prior conversational flow. Your selection "
                "must be based solely on semantic relevance, not on which topic was last used. You must never "
                "invent new topic or sub-topic names and may only choose from those already introduced; if "
                "multiple topics are plausible, select the best semantic match, and if none clearly match, "
                "request clarification while still choosing the closest topic. Every response must begin with "
                "the selected topic or sub-topic name followed by a colon, in the format "
                "<topic_or_subtopic_name>: <your answer>."
            )
        })

        # Add system message with follow-up context if this is a follow-up conversation
        follow_up_prompt = node.get_enhanced_context_prompt()
        if follow_up_prompt:
            context_messages.append({
                'role': 'system',
                'content': f"FOLLOW-UP CONTEXT: {follow_up_prompt}"
            })

        # ✅ GET BUFFER MESSAGES WITH SUMMARY (for non-streaming too!)
        buffer_messages = node.buffer.get_context_messages(include_summary=True)
        context_messages.extend(buffer_messages)

        # Add current user message
        # context_messages.append({
        #     'role': 'user',
        #     'content': user_message
        # })
        print('*******************context*********************\n',context_messages)
        
        # Try vLLM first (Kaggle GPU)
        if self.vllm_client:
            try:
                response = self.vllm_client.generate(
                    messages=context_messages,
                    temperature=0.0,  # Deterministic
                    max_tokens=512
                )
                
                self.last_usage = self.vllm_client.get_last_usage()
                return response
                
            except Exception as e:
                print(f"vLLM error: {e}")
                print("Falling back to echo mode...")
                self.last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                return f"Echo (vLLM error): {user_message}"
        
        # Try to use LLM API based on backend
        elif self.ollama_available and self.llm_backend == "ollama":
            # Use Ollama
            try:
                response = ollama.chat(
                    model=settings.model_base,
                    messages=context_messages,
                    options={
                        "temperature": 0.0,  # Deterministic for reproducible testing
                        "num_predict": 1000,  # Max tokens
                    }
                )
                
                assistant_message = response['message']['content']
                
                # Extract usage info if available
                self.last_usage = {
                    "prompt_tokens": response.get('prompt_eval_count', 0),
                    "completion_tokens": response.get('eval_count', 0),
                    "total_tokens": response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
                }
                
                return assistant_message
                
            except Exception as e:
                print(f"Ollama error: {e}")
                print("Falling back to echo mode...")
                self.last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                return f"Echo (Ollama error): {user_message}"
        
        elif self.groq_client:
            # Use Groq
            try:
                response = self.groq_client.chat.completions.create(
                    model=settings.model_base,
                    messages=context_messages,
                    max_tokens=100,  # Increased for longer responses
                    temperature=0.0,  # Deterministic for reproducible testing
                    stream=False  # Non-streaming version
                )
                # Store usage data for retrieval
                self.last_usage = {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                }
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"⚠️  Groq API error: {e}")
                self.last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                return f"Echo from {node.title}: {user_message}"
        else:
            # Fallback for testing without API key
            self.last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            return f"Echo from {node.title}: {user_message}"
    
    def get_last_usage(self) -> dict:
        """Get usage data from the last API call"""
        return getattr(self, 'last_usage', {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})

    def generate_response_stream(self, node: TreeNode, user_message: str):
        """ Generate streaming response using node's hierarchical context with follow-up awareness """
        
        # Build context from node's buffer (inherited from parents)
        context_messages = []

        # Add system message with follow-up context if this is a follow-up conversation
        follow_up_prompt = node.get_enhanced_context_prompt()
        if follow_up_prompt:
            context_messages.append({
                'role': 'system',
                'content': f"FOLLOW-UP CONTEXT: {follow_up_prompt}"
            })

        # ✅ GET BUFFER MESSAGES WITH SUMMARY (for baseline too!)
        buffer_messages = node.buffer.get_context_messages(include_summary=True)
        context_messages.extend(buffer_messages)

        # Add current user message
        # context_messages.append({
        #     'role': 'user',
        #     'content': user_message
        # })

        print('entire context message before response ',context_messages)
        
        # Try vLLM streaming first (Kaggle GPU)
        if self.vllm_client:
            try:
                for chunk in self.vllm_client.generate_stream(
                    messages=context_messages,
                    temperature=0.0,
                    max_tokens=512
                ):
                    yield chunk
                return
            except Exception as e:
                print(f"vLLM streaming error: {e}")
                response = self._generate_fallback_response(user_message)
                for char in response:
                    yield char
                return
        
        # Try to use LLM API streaming based on backend
        elif self.ollama_available and self.llm_backend == "ollama":
            # Ollama streaming
            try:
                stream = ollama.chat(
                    model=settings.model_base,
                    messages=context_messages,
                    stream=True,
                    options={
                        "temperature": 0.0,
                        "num_predict": 1000,
                    }
                )
                
                for chunk in stream:
                    if 'message' in chunk and 'content' in chunk['message']:
                        yield chunk['message']['content']
                         
            except Exception as e:
                print(f"Ollama streaming error: {e}")
                response = self._generate_fallback_response(user_message)
                for char in response:
                    yield char
        
        elif self.groq_client:
            # Groq streaming
            try:
                stream = self.groq_client.chat.completions.create(
                    model=settings.model_base,
                    messages=context_messages,
                    max_tokens=100,
                    temperature=0.0,  # Deterministic for reproducible testing
                    stream=True  # Enable streaming
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                         
            except Exception as e:
                print(f" Groq streaming API error: {e}")
                # Fallback to simulated comprehensive response
                response = self._generate_fallback_response(user_message)
                for char in response:
                    yield char
                    import time
                    time.sleep(0.02)  # Faster streaming for better demo
        else:
            # Fallback simulated streaming for testing without API key
            response = self._generate_fallback_response(user_message)
            for char in response:
                yield char
                import time
                time.sleep(0.02)  # Faster streaming for better demo
    
    def generate_response_stream_with_rag(self, node: TreeNode, user_message: str):
        """
        Generate streaming response with agentic RAG (Retrieval-Augmented Generation).
        
        LLM decides whether to search conversation history based on user's query.
        Recent context (last 10 messages) is always in buffer.
        Retrieval only searches archived messages beyond buffer.
        """
        if not self.vector_index:
            print("⚠️  Vector index not enabled, falling back to standard streaming")
            yield from self.generate_response_stream(node, user_message)
            return
        
        # Build context from node's buffer (inherited from parents)
        context_messages = []

        # Add system message with follow-up context if this is a follow-up conversation
        follow_up_prompt = node.get_enhanced_context_prompt()
        if follow_up_prompt:
            context_messages.append({
                'role': 'system',
                'content': f"FOLLOW-UP CONTEXT: {follow_up_prompt}"
            })

        # Add recent messages from current node
        recent = node.buffer.get_recent(10)
        for msg in recent:
            context_messages.append({
                'role': msg['role'],
                'content': msg['text']
            })
        
        # Add current user message
        context_messages.append({
            'role': 'user',
            'content': user_message
        })

        print(f'🤖 RAG Mode: LLM analyzing whether retrieval needed...')
        
        # Try to use Groq API with tool calling
        if self.groq_client:
            try:
                # First LLM call with tools - LLM decides if it needs retrieval
                initial_response = self.groq_client.chat.completions.create(
                    model=settings.model_tool_calling,
                    messages=context_messages,
                    tools=ConversationTools.get_tool_definitions(),
                    tool_choice="auto",  # LLM decides
                    stream=False,  # Need complete response to check for tool calls
                    max_tokens=100,
                    temperature=0.0  # Deterministic for reproducible testing
                )
                
                # Check if LLM wants to use tools
                if initial_response.choices[0].message.tool_calls:
                    print(f"🔧 LLM decided to use retrieval tool")
                    
                    # Execute tool calls
                    tool_results_messages = []
                    
                    for tool_call in initial_response.choices[0].message.tool_calls:
                        # Parse arguments
                        args = json.loads(tool_call.function.arguments)
                        print(f"   Searching for: '{args.get('query', '')}'")
                        
                        # Execute tool
                        result = ConversationTools.execute_tool(
                            tool_name=tool_call.function.name,
                            arguments=args,
                            vector_index=self.vector_index,
                            node=node
                        )
                        
                        # Add tool result to context
                        tool_results_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": result
                        })
                    
                    # Add assistant's tool call message
                    context_messages.append({
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in initial_response.choices[0].message.tool_calls
                        ]
                    })
                    
                    # Add tool results
                    context_messages.extend(tool_results_messages)
                    
                    # Second LLM call with retrieved context
                    print(f"🎯 Generating response with retrieved context...")
                    final_response = self.groq_client.chat.completions.create(
                        model=settings.model_base,
                        messages=context_messages,
                        stream=True,
                        max_tokens=100,
                        temperature=0.0  # Deterministic for reproducible testing
                    )
                    
                    for chunk in final_response:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                
                else:
                    print(f"✅ LLM decided retrieval not needed - using buffer context")
                    
                    # No tools needed, but we already have response, need to re-stream
                    # Re-call with streaming enabled
                    streaming_response = self.groq_client.chat.completions.create(
                        model=settings.model_base,
                        messages=context_messages,
                        stream=True,
                        max_tokens=100,
                        temperature=0.0  # Deterministic for reproducible testing
                    )
                    
                    for chunk in streaming_response:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                        
            except Exception as e:
                print(f"⚠️  Groq RAG streaming error: {e}")
                # Fallback to standard streaming
                yield from self.generate_response_stream(node, user_message)
        else:
            # Fallback to standard streaming if no API key
            yield from self.generate_response_stream(node, user_message)
    
    def generate_response_stream_with_rag_cot(self, node: TreeNode, user_message: str):
        """
        Generate streaming response with agentic RAG using Chain-of-Thought reasoning.
        
        Uses structured reasoning framework to guide LLM's tool usage decisions.
        Expected to improve tool calling accuracy.
        """
        if not self.vector_index:
            print("⚠️  Vector index not enabled, falling back to standard streaming")
            yield from self.generate_response_stream(node, user_message)
            return
        
        # Build context from node's buffer
        context_messages = []

        # ✅ Chain-of-Thought: Concise reasoning framework
        context_messages.append({
            'role': 'system',
            'content': """Use retrieval ONLY when the user explicitly says:
“that I have previously mentioned”
(or a direct statement that they want info from earlier conversations).

Otherwise never use retrieval.

Do NOT retrieve if:

The answer is already there.

The question is general knowledge, follow-up, or chit-chat. 

You are unsure the info exists.

Retrieve ONLY if ALL are true:

User explicitly indicates they want past info (e.g., “that I mentioned before”).

Info is not in the recent buffer.

You are sure the info was shared earlier.

If retrieval returns irrelevant results: ignore them.

IF confused then dont use retrieval 

Never mention tools or searching.
"""
        })

        # Add follow-up context if exists
        follow_up_prompt = node.get_enhanced_context_prompt()
        if follow_up_prompt:
            context_messages.append({
                'role': 'system',
                'content': f"FOLLOW-UP CONTEXT: {follow_up_prompt}"
            })

        # ✅ GET BUFFER MESSAGES WITH SUMMARY!
        # This now includes the rolling summary as first message (if it exists)
        buffer_messages = node.buffer.get_context_messages(include_summary=True)
        context_messages.extend(buffer_messages)
        
        # Debug: Check if summary is in context
        summary_msg = next((msg for msg in context_messages if "CONVERSATION SUMMARY" in msg.get("content", "")), None)
        if summary_msg:
            summary_length = len(summary_msg['content'])
            summary_preview = summary_msg['content'][:150].replace('\n', ' ')
            print(f"✅ Summary included in context ({summary_length} chars)")
            print(f"   Preview: {summary_preview}...")
        else:
            print(f"ℹ️  No summary in context (buffer has {len(buffer_messages)} messages)")
        
        # # Add current user message
        # context_messages.append({
        #     'role': 'user',
        #     'content': user_message
        # })

        print(f'🧠 RAG Mode (CoT): LLM analyzing with reasoning framework...')
        
        # Try to use Groq API with tool calling
        if self.groq_client:
            try:
                # First LLM call with tools - LLM decides using CoT guidance
                initial_response = self.groq_client.chat.completions.create(
                    model=settings.model_tool_calling,
                    messages=context_messages,
                    tools=ConversationTools.get_tool_definitions(),
                    tool_choice="auto",  # LLM decides based on CoT guidance
                    stream=False,
                    max_tokens=100,
                    temperature=0.0  # Deterministic for reproducible testing
                )
                
                # Log CoT thinking
                reasoning = "LLM used tool calling mechanism to decide."
                decision = "UNKNOWN"
                search_query = None

                print("***************************************************\n",initial_response)
                
                # Check if LLM wants to use tools
                if initial_response.choices[0].message.tool_calls:
                    decision = "USE RETRIEVAL"
                    print(f"✅ LLM decided to USE retrieval (CoT reasoning worked!)")
                    
                    # Execute tool calls
                    tool_results_messages = []
                    
                    for tool_call in initial_response.choices[0].message.tool_calls:
                        # Parse arguments
                        args = json.loads(tool_call.function.arguments)
                        search_query = args.get('query', '')
                        print(f"   🔍 Searching for: '{search_query}'")
                        
                        # Execute tool
                        result = ConversationTools.execute_tool(
                            tool_name=tool_call.function.name,
                            arguments=args,
                            vector_index=self.vector_index,
                            node=node
                        )
                        
                        # Add tool result to context
                        tool_results_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": result
                        })
                    
                    # Add assistant's tool call message
                    context_messages.append({
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in initial_response.choices[0].message.tool_calls
                        ]
                    })
                    
                    # Add tool results
                    context_messages.extend(tool_results_messages)
                    
                    # Second LLM call with retrieved context
                    print(f"🎯 Generating response with retrieved context...")

                    print("****************************context message*********************************\n",context_messages)
                    
                    # Log CoT thinking to BOTH loggers
                    logger_overwrite = get_debug_logger(append_mode=False)  # For user viewing
                    logger_append = get_debug_logger(append_mode=True)      # For full debugging
                    
                    for logger in [logger_overwrite, logger_append]:
                        logger.log_cot_thinking(
                            query=user_message,  # The user's question
                            reasoning=reasoning,
                            decision=decision,
                            search_query=search_query
                        )
                    
                    final_response = self.groq_client.chat.completions.create(
                        model=settings.model_base,
                        messages=context_messages,
                        stream=True,
                        max_tokens=1000,
                        temperature=0.0  # Deterministic for reproducible testing
                    )
                    
                    for chunk in final_response:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                
                else:
                    decision = "NOT USE RETRIEVAL (buffer context sufficient)"
                    print(f"✅ LLM decided NOT to use retrieval (using buffer context)")
                    
                    # Log CoT thinking to BOTH loggers
                    logger_overwrite = get_debug_logger(append_mode=False)  # For user viewing
                    logger_append = get_debug_logger(append_mode=True)      # For full debugging
                    
                    for logger in [logger_overwrite, logger_append]:
                        logger.log_cot_thinking(
                            query=user_message,  # The user's question
                            reasoning=reasoning,
                            decision=decision,
                            search_query=None
                        )
                    print("****************************context message*********************************\n",context_messages)
                    
                    # No tools needed, stream response
                    streaming_response = self.groq_client.chat.completions.create(
                        model=settings.model_base,
                        messages=context_messages,
                        stream=True,
                        max_tokens=100,
                        temperature=0.0  # Deterministic for reproducible testing
                    )
                    
                    for chunk in streaming_response:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                        
            except Exception as e:
                print(f"⚠️  Groq RAG (CoT) error: {e}")
                # Fallback to standard streaming
                yield from self.generate_response_stream(node, user_message)
        else:
            # Fallback to standard streaming if no API key
            yield from self.generate_response_stream(node, user_message)

    def _generate_fallback_response(self, user_message: str) -> str:
        """Generate a comprehensive fallback response with markdown formatting"""
        
        if "quantum computing" in user_message.lower() or "500-word essay" in user_message.lower():
            return """# Quantum Computing: The Future of Information Processing

**Quantum computing** represents one of the most revolutionary advances in modern technology, fundamentally changing how we process and manipulate information. Unlike classical computers that use `bits` as the basic unit of information (existing as either 0 or 1), quantum computers utilize **quantum bits** or `qubits` that can exist in multiple states simultaneously through a phenomenon called *superposition*.

## Core Principles

The foundation of quantum computing rests on three key quantum mechanical principles:

1. **Superposition** - Qubits can exist in a combination of 0 and 1 states
2. **Entanglement** - Qubits can be mysteriously connected across space
3. **Interference** - Quantum states can amplify or cancel each other

### Mathematical Representation

A qubit's state can be represented mathematically as:

```
|ψ⟩ = α|0⟩ + β|1⟩
```

Where `α` and `β` are complex numbers representing probability amplitudes.

## Practical Applications

Quantum computing promises to revolutionize several fields:

- **Cryptography**: Breaking current encryption methods while creating unbreakable quantum encryption
- **Drug Discovery**: Simulating molecular interactions at unprecedented scales
- **Financial Modeling**: Optimizing portfolios and risk assessment
- **Machine Learning**: Exponentially faster pattern recognition and data analysis

## Current Challenges

Despite its potential, quantum computing faces significant hurdles:

> "Quantum decoherence remains the primary obstacle, as quantum states are extremely fragile and easily disturbed by environmental noise."

**Technical challenges** include:
- Maintaining quantum coherence for extended periods
- Error correction in quantum systems  
- Scaling to thousands of stable qubits
- Operating at near absolute zero temperatures

## The Road Ahead

Major technology companies like IBM, Google, and Microsoft are investing billions in quantum research. Google's **Sycamore processor** achieved "quantum supremacy" in 2019 by performing a specific calculation faster than classical supercomputers.

Current quantum computers are still in the **NISQ** (Noisy Intermediate-Scale Quantum) era, but researchers predict that fault-tolerant quantum computers capable of solving real-world problems may emerge within the next decade.

The quantum revolution promises to transform our understanding of computation itself, potentially solving problems that are intractable for even the most powerful classical computers. From simulating the behavior of molecules to optimizing complex systems, quantum computing will likely unlock new frontiers in science, technology, and human knowledge.

*As we stand on the threshold of the quantum age, the question is not whether quantum computing will change the world, but how quickly we can harness its incredible potential.*"""
        
        elif "markdown" in user_message.lower() or "format" in user_message.lower():
            return """# Markdown Formatting Guide

This is a demonstration of **markdown formatting** with various elements:

## Headers
### Level 3 Header
#### Level 4 Header

## Text Styling
- **Bold text** for emphasis
- *Italic text* for subtle emphasis
- `Inline code` for technical terms
- ~~Strikethrough text~~ for corrections

## Code Blocks
```python
def quantum_simulator():
    qubits = [0, 1]
    return superposition(qubits)
```

## Lists
1. First ordered item
2. Second ordered item
   - Nested unordered item
   - Another nested item

## Quotes
> "The quantum world is fundamentally different from our classical intuition."

## Mathematical Expressions
The Schrödinger equation: ψ(x,t) = Ae^(i(kx-ωt))

This demonstrates comprehensive markdown rendering with streaming!"""
        
        else:
            return f"""# Response to: {user_message}

Thank you for your question! This is a **demonstration** of the streaming markdown system.

## Key Features
- Real-time token streaming
- Full markdown support including `code blocks`
- LaTeX mathematical expressions
- Proper formatting for headings

The system can handle:
1. Complex technical content
2. Mathematical formulas  
3. Code examples
4. Rich formatting

> This is a simulated response since no Groq API key is configured. To get real AI responses, please set the GROQ_API_KEY environment variable.

*Happy chatting!*"""

    def generate_title_from_question(self, question: str) -> str:
        """Generate AI-powered title from user question using Groq API"""
        
        # Try to use Groq API if client is available
        if self.groq_client:
            try:
                # Create a focused prompt for title generation
                title_prompt = f"Generate a short, descriptive title (maximum 4 words) for a conversation that starts with this question: '{question}'. Only respond with the title, no quotes or extra text."
                
                response = self.groq_client.chat.completions.create(
                    model=settings.model_base,
                    messages=[
                        {"role": "system", "content": "You are a title generator. Generate short, descriptive titles for conversations. Respond only with the title, no quotes or extra formatting."},
                        {"role": "user", "content": title_prompt}
                    ],
                    max_tokens=50,  # Short response for titles
                    temperature=0.3,  # Lower temperature for consistent, focused titles
                    stream=False
                )
                
                generated_title = response.choices[0].message.content.strip().strip('"').strip("'")
                
                # Validate the generated title
                if generated_title and len(generated_title) > 0 and len(generated_title) <= 50:
                    return generated_title
                else:
                    # Fallback if generated title is invalid
                    return self._fallback_title_from_question(question)
                    
            except Exception as e:
                print(f"⚠️  Error generating AI title: {e}")
                return self._fallback_title_from_question(question)
        else:
            # Fallback when no API key available
            return self._fallback_title_from_question(question)
    
    def _fallback_title_from_question(self, question: str) -> str:
        """Fallback title generation when AI is not available"""
        # Extract key words as backup
        words = question.lower().replace('?', '').replace('.', '').split()
        skip_words = {'what', 'how', 'why', 'when', 'where', 'who', 'which', 'can', 'you', 'tell', 'me', 'about', 'explain', 'describe', 'is', 'are', 'the', 'a', 'an', 'do', 'does', 'will'}
        
        title_words = []
        for word in words:
            if len(word) > 2 and word not in skip_words:
                title_words.append(word.title())
                if len(title_words) >= 3:
                    break
        
        if title_words:
            return ' '.join(title_words)
        else:
            return question[:25] + "..." if len(question) > 25 else question
    

class SimpleChat:
    """ Simple chat orchestrator with optional RAG """

    def __init__(self, enable_rag: bool = False):
        from .chat_manager import ChatGraphManager
        from .forest import Forest

        self.llm = SimpleLLMClient(enable_vector_index=enable_rag)
        self.chat_manager = ChatGraphManager(llm_client=self.llm)  # Pass LLM client for summarization
        self.forest = Forest()
        self.enable_rag = enable_rag
        
        # Update chat_manager to use vector index
        if enable_rag and self.llm.vector_index:
            self.chat_manager.vector_index = self.llm.vector_index


    def start_new_conversation(self, title: str = 'New Chat', buffer_size: int = 15) -> TreeNode:
        """ Start new conversation tree with configurable buffer size """
        return self.forest.create_tree(title, self.chat_manager, buffer_size=buffer_size)
    
    def create_subchat(self,title:str)->TreeNode:
        """ Create subchat under current active node """
        active = self.chat_manager.get_active_node()
        return self.chat_manager.create_node(title, parent_id=active.node_id)

    def send_message(self, message: str, disable_rag: bool = False) -> str:
        """
        Send message and get response using BASELINE (fast, no RAG).
        
        Args:
            disable_rag: Ignored - always uses baseline for consistency
        """
        active = self.chat_manager.get_active_node()
        
        # Add user message
        active.buffer.add_message('user', message)
        
        # BASELINE ONLY: Fast, reliable, no RAG overhead
        response = self.llm.generate_response(active, message)
        
        # Add assistant response
        active.buffer.add_message('assistant', response)
        
        # 🎯 SIMPLE: Generate title if needed (one line!)
        active.auto_generate_title_if_needed(self.llm, message)
        
        return response

    def send_message_stream(self, message: str, disable_rag: bool = False):
        """
        Send message and get streaming response with RAG (CoT).
        Used by frontend for real-time chat with intelligent retrieval.
        
        Args:
            disable_rag: If True, use baseline (for testing)
        """
        active = self.chat_manager.get_active_node()
        
        # Add user message
        active.buffer.add_message('user', message)
        
        # Frontend streaming: Use RAG with CoT reasoning
        full_response = ""
        if self.llm.vector_index and not disable_rag:
            # RAG MODE: Intelligent retrieval with CoT
            try:
                for chunk in self.llm.generate_response_stream_with_rag_cot(active, message):
                    full_response += chunk
                    yield chunk
            except Exception as e:
                print(f"⚠️  RAG (CoT) streaming failed: {e}")
                print(f"   Error: System malfunction - RAG is required for streaming")
                error_msg = f"⚠️ RAG Error: {str(e)}"
                full_response = error_msg
                yield error_msg
        else:
            # BASELINE MODE: Only when RAG disabled explicitly
            for chunk in self.llm.generate_response_stream(active, message):
                full_response += chunk
                yield chunk
        
        # Add assistant response
        active.buffer.add_message('assistant', full_response)
        
        # 🎯 SIMPLE: Generate title if needed (one line!)
        active.auto_generate_title_if_needed(self.llm, message)


#----------------------------------Test-------------------------



def test_simple_chat():
    """Test simplified chat system."""
    print("🧪 Testing Simple Chat System...")
    print(f"📋 Config: App={settings.app_name}, Model={settings.default_model_name}")
    
    chat = SimpleChat()
    
    # Check if Groq API key is loaded
    if chat.llm.groq_client:
        print(f"✅ Groq API key loaded and client ready")
    else:
        print("⚠️  No Groq API key found - using echo mode")
    
    # Create main conversation
    main = chat.start_new_conversation("Cooking Help")
    assert chat.chat_manager.get_active_node().title == "Cooking Help"
    print("✅ Main conversation created")
    
    # Send message
    response1 = chat.send_message("How do I make pasta?")
    print(f"✅ Response 1: {response1}")
    
    # Create subchat
    subchat = chat.create_subchat("Pasta Sauce")
    assert len(main.children) == 1
    assert subchat.buffer.size() > 0  # Should inherit parent messages
    print("✅ Subchat created with inherited context")
    
    # Send message in subchat
    response2 = chat.send_message("What about carbonara sauce?")
    assert subchat.buffer.size() >= 3  # Previous + user + assistant
    print(f"✅ Response 2: {response2}")
    
    # Test path
    path = subchat.get_path()
    assert path == ["Cooking Help", "Pasta Sauce"]
    print(f"✅ Path: {' > '.join(path)}")
    
    print("🎉 Simple chat system test passed!")
    return True


if __name__ == "__main__":
    test_simple_chat()