/**
 * API Client for ShopAssist AI
 * Handles all communication with the FastAPI backend including SSE streaming.
 */

const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * Stream a RAG query response via Server-Sent Events.
 * Uses fetch + ReadableStream (not EventSource) because we need POST.
 *
 * @param {string} query - The user's question
 * @param {object} options - { nResults, maxTokens, temperature }
 * @param {AbortSignal} signal - AbortController signal for cancellation
 * @yields {{ event: string, data: object }} Parsed SSE events
 */
export async function* streamQuery(query, options = {}, signal = null) {
  const response = await fetch(`${API_BASE}/api/query/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      n_results: options.nResults || 3,
      max_length: options.maxTokens || 100,
      temperature: options.temperature || 0.7,
      conversation_context: options.conversationContext || null,
    }),
    signal,
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Parse SSE events from the buffer
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep the last (potentially incomplete) line

    let eventType = null;
    for (const line of lines) {
      if (line.startsWith('event: ')) {
        eventType = line.slice(7).trim();
      } else if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          yield { event: eventType, data };
        } catch (e) {
          console.warn('Failed to parse SSE data:', line);
        }
        eventType = null;
      }
    }
  }
}

/**
 * Non-streaming query (backward compat with existing endpoint)
 */
export async function queryRAG(query, options = {}) {
  const response = await fetch(`${API_BASE}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      n_results: options.nResults || 3,
      max_length: options.maxTokens || 512,
      temperature: options.temperature || 0.7,
    }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

/**
 * Get knowledge base statistics
 */
export async function getStats() {
  const response = await fetch(`${API_BASE}/api/stats`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
