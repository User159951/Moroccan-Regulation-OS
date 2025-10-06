import type { ChatMessage, ChatResponse, SessionInfo, WebSocketMessage } from "@/types/chat";

const API_BASE = "http://localhost:8000";

export const api = {
  async sendMessage(data: ChatMessage): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Failed to send message");
    return response.json();
  },

  async getSessions(): Promise<SessionInfo[]> {
    const response = await fetch(`${API_BASE}/sessions`);
    if (!response.ok) throw new Error("Failed to fetch sessions");
    return response.json();
  },

  async getSession(id: string): Promise<SessionInfo> {
    const response = await fetch(`${API_BASE}/sessions/${id}`);
    if (!response.ok) throw new Error("Failed to fetch session");
    return response.json();
  },

  async deleteSession(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/sessions/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Failed to delete session");
  },

  async exportPDF(id: string): Promise<Blob> {
    const response = await fetch(`${API_BASE}/sessions/${id}/export/pdf`);
    if (!response.ok) throw new Error("Failed to export PDF");
    return response.blob();
  },

  async checkHealth(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error("API health check failed");
    return response.json();
  },

  async getTeams(): Promise<{ teams: string[]; agents: string[] }> {
    const response = await fetch(`${API_BASE}/teams`);
    if (!response.ok) throw new Error("Failed to fetch teams");
    return response.json();
  },

  async createSession(): Promise<{ session_id: string }> {
    const response = await fetch(`${API_BASE}/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) throw new Error("Failed to create session");
    return response.json();
  },

  // WebSocket connection management
  connectWebSocket(sessionId: string, onMessage: (data: WebSocketMessage) => void, onError: (error: Event) => void, onConnect: () => void, onDisconnect: () => void): WebSocket {
    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      onConnect();
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        onError(error as Event);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      onDisconnect();
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError(error);
    };
    
    return ws;
  },

  sendWebSocketMessage(ws: WebSocket, message: string, team: string): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ message, team }));
    } else {
      console.warn('WebSocket not connected');
    }
  },
};
