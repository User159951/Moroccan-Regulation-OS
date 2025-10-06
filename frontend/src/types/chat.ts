export type TeamType = "global" | "acaps" | "ammc";

export interface ChatMessage {
  message: string;
  team: TeamType;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  reasoning: string;
  session_id: string;
  timestamp: string;
  team_used: TeamType;
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  last_activity: string;
  message_count: number;
  team_used: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  reasoning?: string;
  timestamp: string;
  isReasoning?: boolean;
  stepNumber?: number;
  totalSteps?: number;
}

export interface Team {
  id: TeamType;
  name: string;
  description: string;
  color: string;
}

export interface WebSocketMessage {
  type: "reasoning_start" | "reasoning_step" | "response" | "error" | "terminal_log";
  message?: string;
  step?: string;
  response?: string;
  reasoning?: string;
  team_used?: string;
  timestamp: string;
  step_number?: number;
  total_steps?: number;
  content?: string;
}
