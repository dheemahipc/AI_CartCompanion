import { useState, useCallback, useRef } from 'react';
import { streamQuery } from '../api/client';
import { generateId } from '../utils/formatters';

/**
 * Custom hook for chat state management with SSE streaming.
 *
 * Manages messages, settings, streaming state, and provides
 * sendMessage / stopGenerating / clearChat actions.
 */
export default function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [settings, setSettings] = useState({
    temperature: 0.7,
    maxTokens: 100,
    nResults: 3,
  });

  // AbortController ref for cancelling in-flight streams
  const abortRef = useRef(null);
  // Ref for accumulating streamed text (avoids re-render per token)
  const streamBufferRef = useRef('');
  // Ref for requestAnimationFrame ID
  const rafRef = useRef(null);
  // Conversation context for order verification flow
  const conversationContextRef = useRef(null);

  /**
   * Send a message and stream the assistant's response.
   */
  const sendMessage = useCallback(
    async (text) => {
      if (!text.trim() || isLoading) return;

      // Add user message
      const userMsg = {
        id: generateId(),
        role: 'user',
        content: text.trim(),
        timestamp: new Date(),
      };

      // Add empty assistant message (will be filled by streaming)
      const assistantMsg = {
        id: generateId(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };

      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setIsLoading(true);

      // Reset buffer
      streamBufferRef.current = '';

      // Create AbortController for this request
      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const stream = streamQuery(
          text.trim(),
          { ...settings, conversationContext: conversationContextRef.current },
          controller.signal,
        );

        for await (const { event, data } of stream) {
          if (event === 'token' && data.text) {
            // Accumulate text in buffer
            streamBufferRef.current += data.text;

            // Throttle state updates using requestAnimationFrame
            if (!rafRef.current) {
              rafRef.current = requestAnimationFrame(() => {
                const currentText = streamBufferRef.current;
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last && last.role === 'assistant') {
                    updated[updated.length - 1] = {
                      ...last,
                      content: currentText,
                    };
                  }
                  return updated;
                });
                rafRef.current = null;
              });
            }
          } else if (event === 'done') {
            // Capture conversation context for order verification flow
            if (data.conversation_context) {
              conversationContextRef.current = data.conversation_context;
            } else {
              conversationContextRef.current = null;
            }

            // Final flush - ensure all buffered text is rendered
            const finalText = streamBufferRef.current;
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.role === 'assistant') {
                updated[updated.length - 1] = {
                  ...last,
                  content: finalText,
                  isStreaming: false,
                };
              }
              return updated;
            });
          } else if (event === 'error') {
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.role === 'assistant') {
                updated[updated.length - 1] = {
                  ...last,
                  content: `Error: ${data.error || 'Something went wrong'}`,
                  isStreaming: false,
                  isError: true,
                };
              }
              return updated;
            });
          }
        }
      } catch (err) {
        if (err.name === 'AbortError') {
          // User cancelled - finalize whatever we have
          const partialText = streamBufferRef.current;
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.role === 'assistant') {
              updated[updated.length - 1] = {
                ...last,
                content: partialText || 'Generation stopped.',
                isStreaming: false,
              };
            }
            return updated;
          });
        } else {
          // Real error
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.role === 'assistant') {
              updated[updated.length - 1] = {
                ...last,
                content: `Error: ${err.message}`,
                isStreaming: false,
                isError: true,
              };
            }
            return updated;
          });
        }
      } finally {
        setIsLoading(false);
        abortRef.current = null;
        if (rafRef.current) {
          cancelAnimationFrame(rafRef.current);
          rafRef.current = null;
        }
      }
    },
    [isLoading, settings]
  );

  /**
   * Stop the current generation.
   */
  const stopGenerating = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
  }, []);

  /**
   * Clear all messages.
   */
  const clearChat = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading,
    settings,
    setSettings,
    sendMessage,
    stopGenerating,
    clearChat,
  };
}
