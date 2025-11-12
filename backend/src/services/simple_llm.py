import openai
from groq import Groq
from typing import List, Dict
import json
from ..models.tree import TreeNode
from ..cores.config import settings  # Use your existing config
from .tools import ConversationTools
from ..utils.debug_logger import get_debug_logger

class SimpleLLMClient:
    """ Simple LLM client using Groq API with optional RAG """

    def __init__(self, api_key: str = None, enable_vector_index: bool = False):
        # Use provided api_key, or load from your config
        if api_key:
            self.groq_client = Groq(api_key=api_key)
        elif settings.groq_api_key:
            self.groq_client = Groq(api_key=settings.groq_api_key)
        else:
            print("⚠️  Warning: GROQ_API_KEY not found in config or environment. Using echo mode.")
            self.groq_client = None
        
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

        # Try to use Groq API if client is available
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model=settings.model_base,
                    messages=context_messages,
                    max_tokens=1000,  # Increased for longer responses
                    temperature=0.7,
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

        # Add recent messages from current node
        recent = node.buffer.get_recent(10)
        for msg in recent:
            context_messages.append({
                'role': msg['role'],
                'content': msg['text']
            })

        # Add current user message
        # context_messages.append({
        #     'role': 'user',
        #     'content': user_message
        # })

        print('entire context message before response ',context_messages)
        # Try to use Groq API streaming if client is available
        if self.groq_client:
            try:
                stream = self.groq_client.chat.completions.create(
                    model=settings.model_base,
                    messages=context_messages,
                    max_tokens=1000,
                    temperature=0.7,
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
                    max_tokens=1000,
                    temperature=0.7
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
                        max_tokens=1000,
                        temperature=0.7
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
                        max_tokens=1000,
                        temperature=0.7
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
            'content': """When answering questions, follow this reasoning process:

🧠 OPTIMIZED DECISION FRAMEWORK FOR RETRIEVAL MEMORY

⚙️ DEFAULT BEHAVIOR
Do NOT use the search tool by default.
First, check the last 10 messages (buffer).
Only trigger retrieval when the answer cannot be found in the buffer
and it clearly concerns the user’s past info or older discussions.

✅ USE THE TOOL ONLY IF ALL CONDITIONS ARE TRUE:
1. The question is about the user’s personal info
   (e.g., name, age, job, studies, hobbies, preferences)
   OR it asks about something previously discussed (in older conversations).
2. The information is not in the recent buffer (last ~10 messages).
3. You are certain the info was shared earlier (not guessing).

📘 GOOD USE EXAMPLES:
- “What’s my name again?”
- “Where do I study/work?”
- “What project was I working on last month?”
- “What did we discuss about France last week?”
- “Earlier you mentioned my research topic — what was it?”

🚫 NEVER USE FOR THESE:
- General knowledge: “What is quantum computing?”, “What is Python?”
- Current context or follow-up: “Tell me more”, “Can you explain that?”
- Chit-chat: “Hi”, “How are you?”, “Thanks”
- General advice or goals: “How can I be successful?”, “Where should I travel this summer?”
- Any question clearly answerable from the current buffer

⚠️ SPECIAL RULES:
- If you’re unsure, DO NOT use the tool.
- If retrieval returns irrelevant or mismatched results, ignore them completely and answer from reasoning.
- Never mention searching, memory, or tools — respond as if you remembered naturally.
- Retrieval should feel like authentic recall, not database lookup.

🔍 QUICK DECISION CHECKLIST (Yes = Use)
| Condition | Example | Decision |
|------------|----------|----------|
| Asking about user’s past info | “What did I tell you about my pet?” | ✅ |
| Refers to older topic | “What was my last project?” | ✅ |
| Info is in recent buffer | “You said I like cats?” | ❌ |
| General/world knowledge | “What is AI?” | ❌ |
| Uncertain or vague | “Tell me about success” | ❌ |

🧭 CORE PRINCIPLE
When in doubt, don’t use the tool.
Retrieval memory is for remembering, not researching.
"""
        })

        # Add follow-up context if exists
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
                    max_tokens=1000,
                    temperature=0.7
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
                        temperature=0.7
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
                        max_tokens=1000,
                        temperature=0.7
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
                    max_tokens=20,  # Short response for titles
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

        self.chat_manager = ChatGraphManager()
        self.forest = Forest()
        self.llm = SimpleLLMClient(enable_vector_index=enable_rag)
        self.enable_rag = enable_rag
        
        # Update chat_manager to use vector index
        if enable_rag and self.llm.vector_index:
            self.chat_manager.vector_index = self.llm.vector_index


    def start_new_conversation(self,title:str='New Chat')->TreeNode:
        """ Start new conversation tree """
        return self.forest.create_tree(title,self.chat_manager)
    
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