import { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import {
  Cog6ToothIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline';

/**
 * Collapsible sidebar with settings and info.
 */
export default function Sidebar({ isOpen, onClose, settings, onSettingsChange }) {
  const [activeTab, setActiveTab] = useState('settings');

  const tabs = [
    { id: 'settings', label: 'Settings', icon: Cog6ToothIcon },
    { id: 'about', label: 'About', icon: InformationCircleIcon },
  ];

  return (
    <>
      {/* Overlay (mobile) */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-40 md:hidden overlay-enter"
          onClick={onClose}
        />
      )}

      {/* Sidebar panel */}
      <div
        className={`fixed top-0 left-0 h-full w-72 bg-white border-r border-gray-200 shadow-lg z-50 transform transition-transform duration-250 ease-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Sidebar header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-800">Configuration</h2>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Tab buttons */}
        <div className="flex border-b border-gray-200">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="p-4 overflow-y-auto" style={{ height: 'calc(100% - 105px)' }}>
          {activeTab === 'settings' && (
            <SettingsTab settings={settings} onChange={onSettingsChange} />
          )}
          {activeTab === 'about' && <AboutTab />}
        </div>
      </div>
    </>
  );
}

/**
 * Settings tab: RAG parameters
 */
function SettingsTab({ settings, onChange }) {
  return (
    <div className="space-y-5">
      {/* Temperature */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <label className="text-xs font-medium text-gray-700">
            Temperature
          </label>
          <span className="text-xs font-mono text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
            {settings.temperature.toFixed(1)}
          </span>
        </div>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={settings.temperature}
          onChange={(e) =>
            onChange({ ...settings, temperature: parseFloat(e.target.value) })
          }
          className="w-full"
        />
        <div className="flex justify-between text-[10px] text-gray-400 mt-0.5">
          <span>Precise</span>
          <span>Creative</span>
        </div>
      </div>

      {/* Max Tokens */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <label className="text-xs font-medium text-gray-700">
            Max Tokens
          </label>
          <span className="text-xs font-mono text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
            {settings.maxTokens}
          </span>
        </div>
        <input
          type="range"
          min="50"
          max="500"
          step="25"
          value={settings.maxTokens}
          onChange={(e) =>
            onChange({ ...settings, maxTokens: parseInt(e.target.value) })
          }
          className="w-full"
        />
        <div className="flex justify-between text-[10px] text-gray-400 mt-0.5">
          <span>Shorter</span>
          <span>Longer</span>
        </div>
      </div>

      {/* Number of Results */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <label className="text-xs font-medium text-gray-700">
            Context Documents
          </label>
          <span className="text-xs font-mono text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
            {settings.nResults}
          </span>
        </div>
        <input
          type="range"
          min="1"
          max="10"
          step="1"
          value={settings.nResults}
          onChange={(e) =>
            onChange({ ...settings, nResults: parseInt(e.target.value) })
          }
          className="w-full"
        />
        <div className="flex justify-between text-[10px] text-gray-400 mt-0.5">
          <span>Focused</span>
          <span>Broad</span>
        </div>
      </div>
    </div>
  );
}

/**
 * About tab
 */
function AboutTab() {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">
          About
        </h3>
        <p className="text-xs text-gray-600 leading-relaxed">
          ShopAssist AI is an AI-powered Q&A assistant that uses
          Retrieval-Augmented Generation (RAG) to answer questions about
          products, orders, and retail policies.
        </p>
      </div>

      <div>
        <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">
          Tech Stack
        </h3>
        <div className="space-y-1.5">
          {[
            { label: 'LLM', value: 'Llama 3.3 70B (Groq)' },
            { label: 'Embeddings', value: 'MiniLM-L6-v2' },
            { label: 'Vector DB', value: 'ChromaDB' },
            { label: 'Backend', value: 'FastAPI' },
            { label: 'Frontend', value: 'React + Tailwind' },
            { label: 'PII Protection', value: 'Microsoft Presidio' },
          ].map((item) => (
            <div
              key={item.label}
              className="flex items-center justify-between text-xs"
            >
              <span className="text-gray-500">{item.label}</span>
              <span className="font-medium text-gray-700">{item.value}</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">
          Data Sources
        </h3>
        <div className="space-y-1.5">
          {[
            { label: 'Products', value: '26,280 items' },
            { label: 'Orders', value: '10,000 transactions' },
            { label: 'Policies', value: '100+ Q&As' },
          ].map((item) => (
            <div
              key={item.label}
              className="flex items-center justify-between text-xs"
            >
              <span className="text-gray-500">{item.label}</span>
              <span className="font-medium text-gray-700">{item.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
