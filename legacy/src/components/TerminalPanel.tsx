import React, { useState } from 'react';
import { Terminal as TerminalIcon, Play, Trash2, Plus, CornerDownLeft } from 'lucide-react';

interface TerminalPanelProps {
  logs: string[];
  onClearLogs: () => void;
  onExecuteCommand: (cmd: string) => void;
}

export const TerminalPanel: React.FC<TerminalPanelProps> = ({
  logs,
  onClearLogs,
  onExecuteCommand
}) => {
  const [commandInput, setCommandInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!commandInput.trim()) return;
    onExecuteCommand(commandInput.trim());
    setCommandInput('');
  };

  return (
    <div className="h-48 bg-[#090d16] border-t border-[#1e293b] flex flex-col font-mono text-xs select-none">
      {/* Terminal Top Bar */}
      <div className="h-8 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between px-3">
        <div className="flex items-center gap-2">
          <TerminalIcon className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-bold text-[11px] uppercase tracking-wider text-[#e2e8f0]">
            Integrated Terminal (Bash / POSIX)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onClearLogs}
            className="p-1 hover:bg-[#1e293b] text-[#64748b] hover:text-rose-400 rounded transition-colors"
            title="Clear Console Output"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Terminal Output Log Area */}
      <div className="flex-1 p-3 overflow-y-auto space-y-1 text-[#e2e8f0]">
        {logs.length === 0 ? (
          <span className="text-[#64748b] text-[11px] block">
            Ready. Type commands below (e.g. gcc main.cpp -o main, python3 main.py, pytest, git status).
          </span>
        ) : (
          logs.map((log, idx) => (
            <div key={idx} className="leading-relaxed">
              <span className="text-cyan-400 select-none mr-2">kanak@medha-ide:~/Desktop/ide$</span>
              <span>{log}</span>
            </div>
          ))
        )}
      </div>

      {/* Command Prompt Form */}
      <form onSubmit={handleSubmit} className="h-8 border-t border-[#1e293b] bg-[#0f172a] flex items-center px-3 gap-2">
        <span className="text-emerald-400 font-bold">$</span>
        <input
          type="text"
          value={commandInput}
          onChange={(e) => setCommandInput(e.target.value)}
          placeholder="Execute shell or build command..."
          className="flex-1 bg-transparent text-xs text-white placeholder-[#64748b] focus:outline-none"
        />
        <button type="submit" className="text-[#64748b] hover:text-cyan-400">
          <CornerDownLeft className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
};
