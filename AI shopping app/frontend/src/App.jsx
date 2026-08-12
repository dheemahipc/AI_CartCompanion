import { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import useChat from './hooks/useChat';
import './App.css';

/**
 * Root application component.
 * Composes Header, Sidebar, and ChatWindow together.
 */
export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const {
    messages,
    isLoading,
    settings,
    setSettings,
    sendMessage,
    stopGenerating,
    clearChat,
  } = useChat();

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <Header
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        onClearChat={clearChat}
      />

      {/* Main content area */}
      <div className="flex-1 relative overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          settings={settings}
          onSettingsChange={setSettings}
        />

        {/* Chat Window */}
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSend={sendMessage}
          onStop={stopGenerating}
        />
      </div>
    </div>
  );
}
