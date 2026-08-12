import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { UserCircleIcon, CpuChipIcon } from '@heroicons/react/24/solid';
import { formatTime } from '../utils/formatters';

/**
 * Renders a single chat message bubble.
 * User messages are right-aligned (indigo).
 * Assistant messages are left-aligned (gray) with Markdown rendering.
 */
export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const isError = message.isError;

  return (
    <div
      className={`flex gap-3 px-4 py-2 message-enter ${
        isUser ? 'flex-row-reverse' : 'flex-row'
      }`}
    >
      {/* Avatar */}
      <div className="flex-shrink-0 mt-1">
        {isUser ? (
          <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
            <UserCircleIcon className="w-5 h-5 text-white" />
          </div>
        ) : (
          <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
            <CpuChipIcon className="w-5 h-5 text-indigo-600" />
          </div>
        )}
      </div>

      {/* Message content */}
      <div className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`rounded-2xl px-4 py-2.5 ${
            isUser
              ? 'bg-indigo-600 text-white rounded-tr-md'
              : isError
              ? 'bg-red-50 text-red-700 border border-red-200 rounded-tl-md'
              : 'bg-white text-gray-800 border border-gray-200 rounded-tl-md shadow-sm'
          }`}
        >
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          ) : (
            <div
              className={`markdown-body text-sm leading-relaxed ${
                message.isStreaming && message.content
                  ? 'streaming-cursor'
                  : ''
              }`}
            >
              {message.content ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              ) : message.isStreaming ? (
                <span className="text-gray-400 italic">Thinking...</span>
              ) : null}
            </div>
          )}
        </div>

        {/* Timestamp */}
        <p
          className={`text-[10px] text-gray-400 mt-1 ${
            isUser ? 'text-right' : 'text-left'
          } px-1`}
        >
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
}
