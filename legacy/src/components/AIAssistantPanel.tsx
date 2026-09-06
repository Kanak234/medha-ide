import React, { useState } from 'react';
import { Sparkles, Send, Eye, Wand2, Shield, TestTube, CheckCircle2, CornerDownLeft } from 'lucide-react';
import { AIMessage, SupportedLanguage } from '../types';
import { processAIQuery } from '../services/aiAssistantEngine';

interface AIAssistantPanelProps {
  activeCode?: string;
  activeLanguage?: SupportedLanguage;
  onApplySnippet: (code: string) => void;
}

export const AIAssistantPanel: React.FC<AIAssistantPanelProps> = ({
  activeCode,
  activeLanguage = 'typescript',
  onApplySnippet
}) => {
  const [messages, setMessages] = useState<AIMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      content: `Hello Kanak! I am your **Autonomous Offline-First AI Coding Assistant**.\n\n` +
        `I operate 100% offline with zero internet requirement. How can I assist with your workspace today?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      verified: true
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');

  const handleSend = (queryText?: string) => {
    const text = queryText || inputQuery;
    if (!text.trim()) return;

    const userMsg: AIMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      content: text.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const aiRes = processAIQuery(text.trim(), activeCode, activeLanguage);

    setMessages(prev => [...prev, userMsg, aiRes]);
    if (!queryText) setInputQuery('');
  };

  return (
    <div className="w-80 bg-[#0f172a] border-l border-[#1e293b] flex flex-col h-full overflow-hidden select-none">
      {/* Top Header */}
      <div className="p-3 border-b border-[#1e293b] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span className="font-bold text-xs uppercase tracking-wider text-white">AI Coding Assistant</span>
        </div>
        <span className="text-[10px] font-mono bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2 py-0.5 rounded">
          Offline Mode
        </span>
      </div>

      {/* Quick Action Buttons */}
      <div className="p-2 border-b border-[#1e293b] bg-[#090d16] flex flex-wrap gap-1">
        <button
          onClick={() => handleSend('Explain this code and analyze Big-O complexity.')}
          className="px-2 py-1 bg-[#1e293b] hover:bg-[#334155] text-cyan-300 rounded text-[10px] font-medium flex items-center gap-1"
        >
          <Eye className="w-3 h-3 text-cyan-400" /> Explain Code
        </button>

        <button
          onClick={() => handleSend('Make it better and refactor quadratic loops.')}
          className="px-2 py-1 bg-purple-950/60 hover:bg-purple-900/60 text-purple-300 rounded text-[10px] font-medium border border-purple-800/40"
        >
          <Wand2 className="w-3 h-3 text-purple-300" /> Make It Better
        </button>

        <button
          onClick={() => handleSend('Generate unit test suite for this code.')}
          className="px-2 py-1 bg-emerald-950/60 hover:bg-emerald-900/60 text-emerald-300 rounded text-[10px] font-medium border border-emerald-800/40"
        >
          <TestTube className="w-3 h-3 text-emerald-400" /> Generate Tests
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-3 overflow-y-auto space-y-3">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col space-y-1 ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`p-3 rounded-xl text-xs max-w-[90%] leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-purple-600 text-white rounded-br-none'
                  : 'bg-[#1e293b] text-[#e2e8f0] border border-[#334155] rounded-bl-none'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.content}</div>

              {/* Verified Badge */}
              {msg.verified && (
                <div className="mt-2 pt-1 border-t border-[#334155]/60 flex items-center gap-1 text-[10px] text-cyan-400 font-mono">
                  <CheckCircle2 className="w-3 h-3" /> AI GENERATED — Statically Audited
                </div>
              )}

              {/* Code Snippet Card */}
              {msg.codeSnippet && (
                <div className="mt-2 space-y-1">
                  <pre className="bg-[#090d16] p-2 rounded border border-[#334155] text-[11px] font-mono text-cyan-200 overflow-x-auto">
                    {msg.codeSnippet.code}
                  </pre>
                  <button
                    onClick={() => onApplySnippet(msg.codeSnippet!.code)}
                    className="w-full py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-[10px] font-bold shadow"
                  >
                    Insert Code Snippet into Active File
                  </button>
                </div>
              )}
            </div>
            <span className="text-[9px] text-[#64748b] px-1 font-mono">{msg.timestamp}</span>
          </div>
        ))}
      </div>

      {/* Input Form */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="p-2 border-t border-[#1e293b] bg-[#090d16] flex items-center gap-2">
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ask AI assistant..."
          className="flex-1 bg-[#1e293b] border border-[#334155] rounded-lg px-3 py-1.5 text-xs text-white placeholder-[#64748b] focus:outline-none focus:border-purple-400"
        />
        <button
          type="submit"
          className="p-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
};
