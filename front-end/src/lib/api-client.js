// Frontend API Client for Hierarchical Backend Integration
// This connects the Next.js frontend to the FastAPI backend

const API_BASE_URL = 'http://localhost:8000';

export class HierarchicalChatAPI {
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error(`Health check failed: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  // Create a new conversation (root node) with default "New Chat" title
  async createConversation(title = 'New Chat') {
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      });
      if (!response.ok) throw new Error(`Failed to create conversation: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Create conversation error:', error);
      throw error;
    }
  }

  // Send a message to a conversation
  async sendMessage(conversationId, content) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content })
      });
      if (!response.ok) throw new Error(`Failed to send message: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Send message error:', error);
      throw error;
    }
  }

  // Send a message with streaming response
  async sendMessageStream(conversationId, content, onChunk, onTitle, onComplete, onError) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}/messages/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content })
      });

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep the last incomplete line in the buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ') && line.trim() !== 'data:') {
            try {
              const jsonStr = line.slice(6).trim();
              if (jsonStr) {
                const data = JSON.parse(jsonStr);
                
                switch (data.type) {
                  case 'token':
                    onChunk?.(data.content);
                    break;
                  case 'title':
                    onTitle?.(data.content);
                    break;
                  case 'done':
                    onComplete?.();
                    return;
                  case 'error':
                    onError?.(new Error(data.content));
                    return;
                }
              }
            } catch (parseError) {
              console.warn('Failed to parse SSE data:', line, 'Error:', parseError.message);
            }
          }
        }
      }
    } catch (error) {
      console.error('Send message stream error:', error);
      onError?.(error);
    }
  }

  // Create a subchat from a parent conversation with follow-up context
  async createSubchat(parentConversationId, title, selectedText = null, followUpContext = null, contextType = 'follow_up') {
    try {
      // Build request body with follow-up context information
      const requestBody = {
        title,
        // Include context fields to help AI understand what this subchat is about
        selected_text: selectedText,      // Text that was selected from parent conversation
        follow_up_context: followUpContext, // What the user wants to explore about the selected text
        context_type: contextType         // Type of subchat (follow_up, new_topic, etc.)
      };

      const response = await fetch(`${API_BASE_URL}/api/conversations/${parentConversationId}/subchats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      
      if (!response.ok) throw new Error(`Failed to create subchat: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Create subchat error:', error);
      throw error;
    }
  }

  // Get conversation details
  async getConversation(conversationId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}`);
      if (!response.ok) throw new Error(`Failed to get conversation: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Get conversation error:', error);
      throw error;
    }
  }

  // Get conversation history
  async getConversationHistory(conversationId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}/history`);
      if (!response.ok) throw new Error(`Failed to get history: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Get history error:', error);
      throw error;
    }
  }

  // 🧹 REMOVED: generateAiTitle method - title generation now happens automatically in backend
}

// For testing integration
if (typeof window !== 'undefined') {
  window.HierarchicalChatAPI = HierarchicalChatAPI;
}
