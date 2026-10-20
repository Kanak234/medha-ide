import React, { useState } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  CornerDownRight, 
  ArrowRight, 
  ArrowUp, 
  Bug, 
  Plus, 
  Trash2, 
  CircleDot, 
  Cpu, 
  Layers, 
  List
} from 'lucide-react';
import { defaultDebuggerEngine, DebuggerSessionState } from '../services/debuggerEngine';
import { SupportedLanguage } from '../types';

interface DebuggerPanelProps {
  activeFile?: string;
  activeLanguage?: SupportedLanguage;
  onSelectLine?: (line: number) => void;
}

export const DebuggerPanel: React.FC<DebuggerPanelProps> = ({
  activeFile = 'main.cpp',
  activeLanguage = 'cpp',
  onSelectLine
}) => {
  const [debugState, setDebugState] = useState<DebuggerSessionState>(() => defaultDebuggerEngine.getState());
  const [newWatch, setNewWatch] = useState('');

  const handleStartDebug = () => {
    const updated = defaultDebuggerEngine.startDebugging(activeFile, activeLanguage);
    setDebugState(updated);
  };

  const handleStopDebug = () => {
    const updated = defaultDebuggerEngine.stopDebugging();
    setDebugState(updated);
  };

  const handleStepOver = () => {
    const updated = defaultDebuggerEngine.stepOver();
    setDebugState(updated);
    if (onSelectLine && updated.currentLine) onSelectLine(updated.currentLine);
  };

  const handleStepInto = () => {
    const updated = defaultDebuggerEngine.stepInto();
    setDebugState(updated);
    if (onSelectLine && updated.currentLine) onSelectLine(updated.currentLine);
  };

  const handleStepOut = () => {
    const updated = defaultDebuggerEngine.stepOut();
    setDebugState(updated);
    if (onSelectLine && updated.currentLine) onSelectLine(updated.currentLine);
  };

  const handleContinue = () => {
    const updated = defaultDebuggerEngine.continueExecution();
    setDebugState(updated);
  };

  const handleAddWatch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWatch.trim()) return;
    defaultDebuggerEngine.addWatchExpression(newWatch.trim());
    setDebugState(defaultDebuggerEngine.getState());
    setNewWatch('');
  };

  return (
    <div className="w-80 bg-[#0f172a] border-r border-[#1e293b] flex flex-col h-full select-none text-xs text-slate-300">
      {/* Top Header & Debug Controls */}
      <div className="p-3 border-b border-[#1e293b] flex items-center justify-between bg-[#0b101d]">
        <div className="flex items-center gap-2">
          <Bug className="w-4 h-4 text-rose-400" />
          <span className="font-bold text-[11px] uppercase tracking-wider text-slate-200">
            Run & Debug (GDB / LLDB)
          </span>
        </div>

        {!debugState.active ? (
          <button
            onClick={handleStartDebug}
            className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-[11px] font-semibold transition-all shadow"
          >
            <Play className="w-3 h-3 fill-current" />
            Start
          </button>
        ) : (
          <button
            onClick={handleStopDebug}
            className="flex items-center gap-1 px-2 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded text-[11px] font-semibold transition-all shadow"
          >
            <Square className="w-3 h-3 fill-current" />
            Stop
          </button>
        )}
      </div>

      {/* Debug Control Toolbar */}
      {debugState.active && (
        <div className="h-9 bg-[#1e293b]/70 border-b border-[#1e293b] flex items-center justify-around px-2">
          <button onClick={handleContinue} className="p-1 hover:bg-[#334155] rounded text-emerald-400" title="Continue (F5)">
            <Play className="w-3.5 h-3.5 fill-current" />
          </button>
          <button onClick={handleStepOver} className="p-1 hover:bg-[#334155] rounded text-cyan-400" title="Step Over (F10)">
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
          <button onClick={handleStepInto} className="p-1 hover:bg-[#334155] rounded text-indigo-400" title="Step Into (F11)">
            <CornerDownRight className="w-3.5 h-3.5" />
          </button>
          <button onClick={handleStepOut} className="p-1 hover:bg-[#334155] rounded text-purple-400" title="Step Out (Shift+F11)">
            <ArrowUp className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto divide-y divide-[#1e293b]">
        {/* Backend Info Banner */}
        <div className="p-2.5 bg-[#090d16] text-[10px] text-cyan-300 font-mono flex items-center gap-1.5">
          <Cpu className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
          <span className="truncate">{debugState.debuggerBackend}</span>
        </div>

        {/* Variables Section (Locals & Watch) */}
        <div className="p-2.5 space-y-2">
          <div className="font-bold text-[11px] uppercase tracking-wider text-slate-400 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <List className="w-3.5 h-3.5 text-amber-400" />
              Variables & Memory
            </span>
          </div>

          <div className="space-y-1 font-mono text-[11px]">
            {debugState.variables.length === 0 ? (
              <div className="text-slate-500 italic text-[10px]">No active frame variables. Start debugging.</div>
            ) : (
              debugState.variables.map((v, i) => (
                <div key={i} className="flex items-center justify-between p-1 bg-[#1e293b]/40 rounded border border-[#1e293b]">
                  <span className="text-cyan-300 font-medium">{v.name}:</span>
                  <span className="text-slate-200 truncate max-w-[140px]">{v.value}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Watch Expressions */}
        <div className="p-2.5 space-y-2">
          <div className="font-bold text-[11px] uppercase tracking-wider text-slate-400 flex items-center justify-between">
            <span>Watch Expressions</span>
          </div>

          <form onSubmit={handleAddWatch} className="flex items-center gap-1">
            <input
              type="text"
              value={newWatch}
              onChange={(e) => setNewWatch(e.target.value)}
              placeholder="Add watch (e.g. ptr->data)..."
              className="flex-1 bg-[#090d16] border border-[#334155] rounded px-2 py-0.5 text-[11px] text-white focus:outline-none focus:border-cyan-400"
            />
            <button type="submit" className="p-1 bg-[#1e293b] hover:bg-[#334155] rounded text-cyan-400">
              <Plus className="w-3.5 h-3.5" />
            </button>
          </form>

          <div className="space-y-1 font-mono text-[10px]">
            {debugState.watchExpressions.map((w, idx) => (
              <div key={idx} className="p-1 bg-[#1e293b]/30 rounded text-purple-300 flex items-center justify-between">
                <span>{w}</span>
                <span className="text-slate-400">evaluated</span>
              </div>
            ))}
          </div>
        </div>

        {/* Call Stack Section */}
        <div className="p-2.5 space-y-2">
          <div className="font-bold text-[11px] uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            Call Stack
          </div>

          <div className="space-y-1 font-mono text-[11px]">
            {debugState.callStack.length === 0 ? (
              <div className="text-slate-500 italic text-[10px]">Call stack inactive.</div>
            ) : (
              debugState.callStack.map((frame) => (
                <div
                  key={frame.id}
                  onClick={() => onSelectLine?.(frame.line)}
                  className="p-1 bg-[#1e293b]/50 hover:bg-[#1e293b] rounded cursor-pointer text-indigo-200 border-l-2 border-indigo-500 flex items-center justify-between"
                >
                  <span className="font-medium truncate">{frame.functionName}</span>
                  <span className="text-[10px] opacity-70">:{frame.line}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Breakpoints List */}
        <div className="p-2.5 space-y-2">
          <div className="font-bold text-[11px] uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <CircleDot className="w-3.5 h-3.5 text-rose-500" />
            Breakpoints ({debugState.breakpoints.length})
          </div>

          <div className="space-y-1 font-mono text-[11px]">
            {debugState.breakpoints.map((bp) => (
              <div
                key={bp.id}
                onClick={() => onSelectLine?.(bp.line)}
                className="p-1 bg-[#1e293b]/40 hover:bg-[#1e293b] rounded cursor-pointer text-rose-300 flex items-center justify-between"
              >
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                  <span>{bp.file}:{bp.line}</span>
                </div>
                <span className="text-[9px] px-1 bg-[#090d16] rounded text-slate-400">Hits: {bp.hitCount}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
