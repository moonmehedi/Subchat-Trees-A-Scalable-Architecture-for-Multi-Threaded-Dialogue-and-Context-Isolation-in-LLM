// Frontend API Client for Backend Integration
// This connects the Next.js frontend to the FastAPI backend

const API_BASE_URL = 'http://localhost:8000';

export class HierarchicalChatAPI {
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  }

  async createSession() {
    const response = await fetch(`${API_BASE_URL}/api/v1/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'default' })
    });
    return response.json();
  }

  async sendMessage(sessionId, message) {
    const response = await fetch(`${API_BASE_URL}/api/v1/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
        parent_node_id: null
      })
    });
    return response.json();
  }
}

// For testing integration
if (typeof window !== 'undefined') {
  window.HierarchicalChatAPI = HierarchicalChatAPI;
}
