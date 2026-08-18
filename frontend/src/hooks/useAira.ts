import { useState, useCallback, useEffect } from 'react';
import { airaAPI, MessageData, ConversationData } from '@/services/aira.service';
import { farmAPI, FarmData } from '@/lib/api';

export function useAira() {
  const [conversations, setConversations] = useState<ConversationData[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageData[]>([]);
  
  // Farm Context
  const [farms, setFarms] = useState<FarmData[]>([]);
  const [activeFarmId, setActiveFarmId] = useState<string | null>(null);
  const [isFarmLocked, setIsFarmLocked] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial data (conversations and farms)
  const initialize = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const [convRes, farmRes] = await Promise.all([
        airaAPI.listConversations(),
        farmAPI.list()
      ]);
      setConversations(convRes.conversations || []);
      setFarms(farmRes.farms || []);
      
      // Auto-select first farm if available and no active farm
      if (farmRes.farms && farmRes.farms.length > 0 && !activeFarmId) {
        setActiveFarmId(farmRes.farms[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load Aira data');
    } finally {
      setIsLoading(false);
    }
  }, [activeFarmId]);

  useEffect(() => {
    initialize();
  }, [initialize]);

  const loadConversation = useCallback(async (id: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await airaAPI.getConversation(id);
      setCurrentConversationId(data.id);
      setMessages(data.messages || []);
      
      // Lock farm context to the conversation's farm if it has one
      if (data.farm_id) {
        setActiveFarmId(data.farm_id);
        setIsFarmLocked(true);
      } else {
        setIsFarmLocked(false);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const startNewConversation = useCallback(() => {
    setCurrentConversationId(null);
    setMessages([]);
    setIsFarmLocked(false);
    setError(null);
  }, []);

  const [abortController, setAbortController] = useState<AbortController | null>(null);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;

    // Optimistically add user message
    const tempUserMsg: MessageData = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };
    
    // Add empty assistant message to stream into
    const aiMsgId = `ai-${Date.now()}`;
    const initialAiMsg: MessageData = {
      id: aiMsgId,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, tempUserMsg, initialAiMsg]);
    setIsTyping(true);
    setError(null);

    const controller = new AbortController();
    setAbortController(controller);

    try {
      const stream = airaAPI.chatStream({
        message: text,
        conversation_id: currentConversationId || undefined,
        farm_id: activeFarmId || undefined
      }, controller.signal);

      let isFirstChunk = true;

      for await (const event of stream) {
        if (isFirstChunk) {
          setIsTyping(false); // Hide generic typing indicator once stream starts
          isFirstChunk = false;
        }

        if (event.type === 'chunk') {
          setMessages(prev => prev.map(m => 
            m.id === aiMsgId ? { ...m, content: m.content + event.content } : m
          ));
        } else if (event.type === 'done') {
          // If this is a new conversation, update the ID and lock the farm
          if (!currentConversationId) {
            setCurrentConversationId(event.conversation_id);
            if (activeFarmId) setIsFarmLocked(true);
            // Refresh conversations list to get the new title
            airaAPI.listConversations().then(res => setConversations(res.conversations || []));
          }
        } else if (event.type === 'error') {
          throw new Error(event.message);
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // Handle explicit interruption
        setMessages(prev => prev.map(m => 
          m.id === aiMsgId ? { ...m, interrupted: true } : m
        ));
      } else {
        // Handle unexpected network/backend error during streaming
        setError(err.message || 'Failed to send message');
        // If it failed before any chunks, we can remove the empty AI message
        setMessages(prev => {
          const aiMsg = prev.find(m => m.id === aiMsgId);
          if (aiMsg && !aiMsg.content) {
            return prev.filter(m => m.id !== aiMsgId && m.id !== tempUserMsg.id); // Also remove user msg if totally failed
          }
          return prev.map(m => m.id === aiMsgId ? { ...m, interrupted: true } : m);
        });
      }
    } finally {
      setIsTyping(false);
      setAbortController(null);
    }
  }, [currentConversationId, activeFarmId]);

  const abortGeneration = useCallback(() => {
    if (abortController) {
      abortController.abort();
    }
  }, [abortController]);

  const deleteConversation = useCallback(async (id: string) => {
    try {
      await airaAPI.deleteConversation(id);
      setConversations(prev => prev.filter(c => c.id !== id));
      if (currentConversationId === id) {
        startNewConversation();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete conversation');
    }
  }, [currentConversationId, startNewConversation]);

  const activeFarm = farms.find(f => f.id === activeFarmId);

  return {
    conversations,
    currentConversationId,
    messages,
    farms,
    activeFarmId,
    activeFarm,
    isFarmLocked,
    isLoading,
    isTyping,
    error,
    setActiveFarmId,
    loadConversation,
    startNewConversation,
    sendMessage,
    abortGeneration,
    deleteConversation,
    refresh: initialize
  };
}
