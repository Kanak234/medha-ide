import React, { useRef, useState } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';
import { X, Sparkles, Wand2, Shield, Eye, Keyboard, Code2 } from 'lucide-react';
import { EditorTab, SupportedLanguage } from '../types';

export type KeymapMode = 'vscode' | 'vim' | 'nano' | 'jetbrains';

interface CodeEditorPanelProps {
  tabs: EditorTab[];
  activeTabId?: string;
  onSelectTab: (tabId: string) => void;
  onCloseTab: (tabId: string) => void;
  onCodeChange: (tabId: string, content: string) => void;
  onOptimizeCode: () => void;
  onExplainCode: () => void;
  onSecurityAudit: () => void;
}

export const CodeEditorPanel: React.FC<CodeEditorPanelProps> = ({
  tabs,
  activeTabId,
  onSelectTab,
  onCloseTab,
  onCodeChange,
  onOptimizeCode,
  onExplainCode,
  onSecurityAudit
}) => {
  const activeTab = tabs.find(t => t.id === activeTabId);
  const editorRef = useRef<any>(null);
  const [keymapMode, setKeymapMode] = useState<KeymapMode>('vscode');
  const [vimState, setVimState] = useState<'NORMAL' | 'INSERT' | 'VISUAL'>('NORMAL');

  const handleEditorMount: OnMount = (editor) => {
    editorRef.current = editor;
  };

  React.useEffect(() => {
    if (editorRef.current && activeTab?.cursorLine) {
      editorRef.current.revealLineInCenter(activeTab.cursorLine);
      editorRef.current.setPosition({
        lineNumber: activeTab.cursorLine,
        column: activeTab.cursorColumn || 1
      });
    }
  }, [activeTab?.cursorLine, activeTab?.cursorColumn]);

  const getMonacoLang = (lang?: SupportedLanguage): string => {
    switch (lang) {
      case 'cpp': case 'c': return 'cpp';
      case 'python': return 'python';
      case 'rust': return 'rust';
      case 'go': return 'go';
      case 'java': return 'java';
      case 'sql': return 'sql';
      case 'html': return 'html';
      case 'css': return 'css';
      case 'javascript': return 'javascript';
      case 'typescript': return 'typescript';
      case 'bash': case 'zsh': case 'fish': return 'shell';
      case 'json': return 'json';
      case 'yaml': return 'yaml';
      default: return 'typescript';
    }
  };

  if (!activeTab) {
    return (
      <div className="flex-1 bg-[#090d16] flex flex-col items-center justify-center text-[#64748b] select-none p-6 text-center">
        <Sparkles className="w-12 h-12 mb-3 text-cyan-500/40 animate-pulse" />
        <h3 className="text-lg font-semibold text-[#e2e8f0]">No File Open</h3>
        <p className="text-xs max-w-sm mt-1 text-[#64748b]">
          Select a file from the workspace explorer or load a demo project template to start coding.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-[#090d16] overflow-hidden">
      {/* Editor Tab Bar */}
      <div className="h-9 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between px-2 overflow-x-auto select-none">
        <div className="flex items-center gap-1">
          {tabs.map((tab) => {
            const isActive = tab.id === activeTabId;
            return (
              <div
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded-t-md cursor-pointer border-t-2 transition-all ${
                  isActive
                    ? 'bg-[#090d16] text-cyan-300 border-cyan-400 font-medium'
                    : 'text-[#64748b] border-transparent hover:text-[#e2e8f0] hover:bg-[#1e293b]/40'
                }`}
              >
                <span>{tab.title}</span>
                {tab.isDirty && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onCloseTab(tab.id);
                  }}
                  className="hover:text-rose-400 p-0.5 rounded transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            );
          })}
        </div>

        {/* Editor Mode Selector & Quick Action Controls */}
        <div className="flex items-center gap-2">
          {/* Keymap Mode Selector */}
          <div className="flex items-center gap-1 bg-[#1e293b] px-2 py-0.5 rounded border border-[#334155]">
            <Keyboard className="w-3 h-3 text-indigo-400" />
            <select
              value={keymapMode}
              onChange={(e) => setKeymapMode(e.target.value as KeymapMode)}
              className="bg-transparent text-[11px] font-semibold text-white focus:outline-none cursor-pointer"
            >
              <option value="vscode" className="bg-[#0f172a]">VS Code Mode</option>
              <option value="vim" className="bg-[#0f172a]">Vim Mode (:w :q)</option>
              <option value="nano" className="bg-[#0f172a]">Nano Mode (^O ^X)</option>
              <option value="jetbrains" className="bg-[#0f172a]">JetBrains Suite</option>
            </select>
          </div>

          {keymapMode === 'vim' && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30">
              -- {vimState} --
            </span>
          )}

          {keymapMode === 'nano' && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
              ^G Help ^O WriteOut
            </span>
          )}

          <button
            onClick={onExplainCode}
            className="flex items-center gap-1 px-2 py-1 bg-[#1e293b] hover:bg-[#334155] text-cyan-300 rounded text-[11px] font-medium transition-colors"
            title="Explain Code Architecture"
          >
            <Eye className="w-3 h-3 text-cyan-400" />
            Explain
          </button>

          <button
            onClick={onOptimizeCode}
            className="flex items-center gap-1 px-2 py-1 bg-purple-950/60 hover:bg-purple-900/60 text-purple-300 rounded text-[11px] font-medium border border-purple-800/40 transition-colors"
            title="Make It Better (Refactor Loop Optimization)"
          >
            <Wand2 className="w-3 h-3 text-purple-300" />
            Make It Better
          </button>

          <button
            onClick={onSecurityAudit}
            className="flex items-center gap-1 px-2 py-1 bg-rose-950/60 hover:bg-rose-900/60 text-rose-300 rounded text-[11px] font-medium border border-rose-800/40 transition-colors"
            title="Run OWASP Static Security Audit"
          >
            <Shield className="w-3 h-3 text-rose-400" />
            Security Audit
          </button>
        </div>
      </div>

      {/* Editor Content Area */}
      <div className="flex-1 relative">
        <Editor
          height="100%"
          language={getMonacoLang(activeTab.language)}
          value={activeTab.content}
          onChange={(val) => onCodeChange(activeTab.id, val || '')}
          onMount={handleEditorMount}
          theme="vs-dark"
          options={{
            fontSize: 13.5,
            fontFamily: "'JetBrains Mono', monospace",
            minimap: { enabled: true, renderCharacters: false },
            lineNumbers: 'on',
            roundedSelection: true,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            padding: { top: 12 },
            cursorStyle: keymapMode === 'vim' ? 'block' : 'line',
            cursorBlinking: keymapMode === 'vim' ? 'solid' : 'smooth'
          }}
        />
      </div>
    </div>
  );
};
