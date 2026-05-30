import type { PlanItem } from "./events";

export interface ToolCallMessage {
  toolName: string;
  toolCallArgument: string;
  toolCallOutput: string;
  callid: string;
}

export interface Message {
  id: number;
  content: string | ToolCallMessage | PlanItem | string[];
  sender: 'user' | 'assistant' | 'system';
  type?: 'text' | 'reason' | 'tool_call' | 'worker' | 'report' | 'error' | 'plan' | 'new_agent' | 'image';
  inprogress?: boolean;
  timestamp: Date;
  requireConfirm?: boolean;
  confirmedStatus?: 'confirmed' | 'rejected';
}