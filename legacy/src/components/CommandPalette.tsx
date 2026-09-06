import React, { useState, useEffect } from 'react';
import { Search, Terminal, Play, Bug, ShieldAlert, Cpu, Sparkles, FolderOpen, Save, Moon, Layers } from 'lucide-react';

export interface CommandPaletteAction {
  id: string;
  title: string;
  category: string;
  shortcut?: string;
  icon: React.ReactNode;
  perform: () => void;
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  actions: CommandPaletteAction[];
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose, actions }) => {
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'p') {
        e.preventDefault();
        if (isOpen) onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filtered = actions.filter(a =>
    a.title.toLowerCase().includes(search.toLowerCase()) ||
    a.category.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelect = (action: CommandPaletteAction) => {
    action.perform();
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-xs z-50 flex items-start justify-center pt-20 px-4">
      <div className="w-full max-w-xl bg-[#0f172a] border border-[#334155] rounded-xl shadow-2xl overflow-hidden font-sans text-slate-200">
        {/* Command Search Input */}
        <div className="p-3 border-b border-[#1e293b] flex items-center gap-2 bg-[#0b101d]">
          <Search className="w-4 h-4 text-cyan-400 shrink-0" />
          <input
            type="text"
            autoFocus
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Type a command or search actions (e.g. Run, Debug, Build, Theme)..."
            className="w-full bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none font-mono"
          />
          <kbd className="px-1.5 py-0.5 text-[10px] bg-[#1e293b] border border-[#334155] rounded text-slate-400 font-mono">
            ESC
          </kbd>
        </div>

        {/* Action List */}
        <div className="max-h-80 overflow-y-auto p-1.5 divide-y divide-[#1e293b]/40 text-xs">
          {filtered.length === 0 ? (
            <div className="p-4 text-center text-slate-500 italic">No matching commands found.</div>
          ) : (
            filtered.map((action, idx) => (
              <div
                key={action.id}
                onClick={() => handleSelect(action)}
                className={`p-2 rounded-lg cursor-pointer flex items-center justify-between transition-colors ${
                  idx === selectedIndex ? 'bg-cyan-500/20 text-cyan-200 border border-cyan-500/30' : 'hover:bg-[#1e293b]'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <div className="text-cyan-400">{action.icon}</div>
                  <div>
                    <div className="font-semibold text-slate-100">{action.title}</div>
                    <div className="text-[10px] text-slate-400 font-mono uppercase">{action.category}</div>
                  </div>
                </div>
                {action.shortcut && (
                  <kbd className="px-2 py-0.5 text-[10px] bg-[#090d16] border border-[#334155] rounded text-cyan-300 font-mono">
                    {action.shortcut}
                  </kbd>
                )}
              </div>
            ))
          )}
        </div>

        <div className="p-2 border-t border-[#1e293b] bg-[#070a12] text-[10px] text-slate-500 flex items-center justify-between px-3 font-mono">
          <span>Navigation: ↑ ↓ Arrows | Exec: Enter</span>
          <span>MEDHĀ Command Palette v1.0</span>
        </div>
      </div>
    </div>
  );
};
