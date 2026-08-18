import request, { getToken, API_BASE_URL } from "@/lib/api";

export interface MessageData {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  interrupted?: boolean;
}

export interface ConversationData {
  id: string;
  title: string | null;
  farm_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetailData extends ConversationData {
  messages: MessageData[];
}

export interface ConversationListResponse {
  conversations: ConversationData[];
  total: number;
}

export interface ChatRequestData {
  message: string;
  conversation_id?: string;
  farm_id?: string;
}

export interface ChatResponseData {
  response: string;
  conversation_id: string;
}

export type ChatStreamEvent = 
  | { type: "chunk"; content: string }
  | { type: "done"; conversation_id: string }
  | { type: "error"; message: string };

export const airaAPI = {
  chat: (data: ChatRequestData) =>
    request<ChatResponseData>("/ai/chat", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  async *chatStream(data: ChatRequestData, signal?: AbortSignal): AsyncGenerator<ChatStreamEvent, void, unknown> {
    const token = getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "Accept": "text/event-stream",
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/ai/chat/stream`, {
      method: "POST",
      headers,
      body: JSON.stringify(data),
      signal,
    });

    if (!response.ok) {
      // Try to parse error response if not 429
      let errorMessage = "Stream failed to start.";
      if (response.status === 429) {
        errorMessage = "Rate limit exceeded. Please try again later.";
      } else {
        try {
          const err = await response.json();
          errorMessage = err.message || errorMessage;
        } catch {
          // ignore
        }
      }
      throw new Error(errorMessage);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("No readable stream in response");

    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Process full events split by \n\n
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || ""; // Keep the last incomplete part in the buffer

        for (const part of parts) {
          const trimmed = part.trim();
          if (!trimmed) continue;
          
          if (trimmed.startsWith("data: ")) {
            const jsonStr = trimmed.substring(6); // remove "data: "
            if (jsonStr === "[DONE]") continue; // Standard SSE close if needed
            try {
              const event: ChatStreamEvent = JSON.parse(jsonStr);
              yield event;
            } catch (e) {
              console.error("Failed to parse SSE event", e, jsonStr);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },

  listConversations: () =>
    request<ConversationListResponse>("/ai/conversations"),

  getConversation: (id: string) =>
    request<ConversationDetailData>(`/ai/conversations/${id}`),

  deleteConversation: (id: string) =>
    request<void>(`/ai/conversations/${id}`, { method: "DELETE" }),
};
