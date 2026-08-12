/**
 * Animated typing indicator (3 bouncing dots).
 * Shown while waiting for the first token from the LLM.
 */
export default function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      <div className="flex items-center gap-1.5 bg-gray-100 rounded-2xl px-4 py-2.5">
        <span
          className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse-dot"
          style={{ animationDelay: '0s' }}
        />
        <span
          className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse-dot"
          style={{ animationDelay: '0.2s' }}
        />
        <span
          className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse-dot"
          style={{ animationDelay: '0.4s' }}
        />
      </div>
    </div>
  );
}
