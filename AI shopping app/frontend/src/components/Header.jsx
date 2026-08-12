import { Bars3Icon, TrashIcon } from '@heroicons/react/24/outline';

/**
 * App header with title and sidebar toggle.
 */
export default function Header({ onToggleSidebar, onClearChat }) {
  return (
    <header className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 shadow-sm">
      {/* Left: sidebar toggle + title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-gray-100 rounded-lg transition-colors"
          title="Toggle settings"
        >
          <Bars3Icon className="w-5 h-5" />
        </button>

        <img
          src="/shopassist_ai_logo.png"
          alt="ShopAssist AI"
          className="h-9 object-contain"
        />
      </div>

      {/* Right: clear chat */}
      <button
        onClick={onClearChat}
        className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        title="Clear chat"
      >
        <TrashIcon className="w-4 h-4" />
        <span className="hidden sm:inline">Clear</span>
      </button>
    </header>
  );
}
