import { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import InputBar from './InputBar';

/**
 * Main chat window: scrollable message list + input bar.
 * Handles auto-scroll to bottom when new messages arrive.
 */
export default function ChatWindow({
  messages,
  isLoading,
  onSend,
  onStop,
}) {
  const scrollRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      {/* Message list */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto py-4"
      >
        {messages.length === 0 ? (
          <EmptyState onSuggestionClick={onSend} />
        ) : (
          <div className="max-w-3xl mx-auto space-y-1">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {/* Show typing indicator when loading and last message has no content yet */}
            {isLoading &&
              messages.length > 0 &&
              messages[messages.length - 1].role === 'assistant' &&
              !messages[messages.length - 1].content && (
                <TypingIndicator />
              )}
          </div>
        )}
      </div>

      {/* Input bar */}
      <InputBar onSend={onSend} onStop={onStop} isLoading={isLoading} />
    </div>
  );
}

/**
 * Empty state shown when there are no messages yet.
 * Suggestion buttons trigger a query when clicked.
 */
function EmptyState({ onSuggestionClick }) {
  const suggestions = [
    'What is the return policy?',
    'How long does shipping take?',
    'What payment methods are accepted?',
    'Check my order status',
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <img
        src="/shopassist_ai_logo.png"
        alt="ShopAssist AI"
        className="w-64 object-contain mb-4"
      />
      <p className="text-sm text-gray-500 mb-8 max-w-md">
        Ask me anything about products, orders, shipping policies, or returns.
        I use AI-powered search to find the most relevant information.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
        {suggestions.map((text) => (
          <button
            key={text}
            onClick={() => onSuggestionClick(text)}
            className="text-left text-sm px-4 py-3 rounded-xl border border-gray-200 bg-white hover:bg-indigo-50 hover:border-indigo-300 text-gray-700 transition-all shadow-sm"
          >
            {text}
          </button>
        ))}
      </div>

      <p className="text-xs text-gray-400 mt-6 max-w-md">
        Want to test order lookup? Use this dummy Order ID:{' '}
        <code className="text-indigo-500 bg-indigo-50 px-1.5 py-0.5 rounded text-[11px]">
          f074757f-cc58-4c88-8390-ff2184a83134
        </code>
      </p>
    </div>
  );
}
