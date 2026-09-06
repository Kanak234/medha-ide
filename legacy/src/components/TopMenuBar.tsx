import React, { useState } from 'react';
import { 
  Code2, 
  Play, 
  Bug, 
  Terminal as TerminalIcon, 
  FolderOpen, 
  Save, 
  Cpu, 
  Sparkles, 
  Layers,
  ChevronDown,
  Check,
  Settings
} from 'lucide-react';
import { SystemInventory } from '../types';
import { EDITIONS_CONFIG, IDEEdition } from '../services/editionsEngine';

interface TopMenuBarProps {
  currentEdition: IDEEdition;
  onOpenEditionsModal: () => void;
  onOpenAbout: () => void;
  onOpenInventory: () => void;
  onOpenTemplates: () => void;
  onRunCode: () => void;
  onStartDebug: () => void;
  buildConfig: 'Debug' | 'Release';
  setBuildConfig: (config: 'Debug' | 'Release') => void;
  selectedCompiler: string;
  setSelectedCompiler: (compiler: string) => void;
  inventory: SystemInventory;
  isAiOpen: boolean;
  setIsAiOpen: (open: boolean) => void;
  setActiveDrawer: (drawer: string) => void;
  setActiveView: (view: string) => void;
}

export const TopMenuBar: React.FC<TopMenuBarProps> = ({
  currentEdition,
  onOpenEditionsModal,
  onOpenAbout,
  onOpenInventory,
  onOpenTemplates,
  onRunCode,
  onStartDebug,
  buildConfig,
  setBuildConfig,
  selectedCompiler,
  setSelectedCompiler,
  inventory,
  isAiOpen,
  setIsAiOpen,
  setActiveDrawer,
  setActiveView
}) => {
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const editionInfo = EDITIONS_CONFIG[currentEdition];

  const handleMenuClick = (menu: string) => {
    setActiveMenu(activeMenu === menu ? null : menu);
  };

  const closeMenu = () => setActiveMenu(null);

  return (
    <div className="bg-[#0b101d] border-b border-[#1e293b] flex flex-col select-none text-xs text-slate-300">
      {/* Top Application Ribbon / Desktop Menu Row */}
      <div className="h-7 bg-[#070a12] border-b border-[#1e293b]/60 flex items-center justify-between px-3">
        <div className="flex items-center gap-4">
          {/* Brand Icon & Name */}
          <div 
            onClick={onOpenAbout} 
            className="flex items-center gap-2 cursor-pointer hover:opacity-90 transition-opacity"
          >
            <div className="w-5 h-5 rounded bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center">
              <Code2 className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-extrabold tracking-wide bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-indigo-300">
              MEDHĀ<span className="text-white font-light">-IDE</span>
            </span>
          </div>

          {/* Top Dropdown Menus */}
          <div className="flex items-center gap-1 font-sans text-[11px] text-slate-300 relative">
            {/* File Menu */}
            <div className="relative">
              <button
                onClick={() => handleMenuClick('file')}
                className={`px-2 py-0.5 rounded hover:bg-[#1e293b] ${activeMenu === 'file' ? 'bg-[#1e293b] text-white' : ''}`}
              >
                File
              </button>
              {activeMenu === 'file' && (
                <div className="absolute top-6 left-0 w-48 bg-[#0f172a] border border-[#1e293b] rounded shadow-2xl py-1 z-50">
                  <button onClick={() => { onOpenTemplates(); closeMenu(); }} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b] flex items-center justify-between">
                    <span>New / Template Project...</span>
                    <span className="text-[10px] text-slate-500">Ctrl+N</span>
                  </button>
                  <button onClick={() => { setActiveDrawer('explorer'); closeMenu(); }} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b] flex items-center justify-between">
                    <span>Open Workspace Folder</span>
                    <span className="text-[10px] text-slate-500">Ctrl+O</span>
                  </button>
                  <div className="border-t border-[#1e293b] my-1"></div>
                  <button onClick={closeMenu} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b] flex items-center justify-between">
                    <span>Save Active File</span>
                    <span className="text-[10px] text-slate-500">Ctrl+S</span>
                  </button>
                  <button onClick={closeMenu} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b] flex items-center justify-between">
                    <span>Save All Workspace</span>
                    <span className="text-[10px] text-slate-500">Ctrl+Shift+S</span>
                  </button>
                </div>
              )}
            </div>

            {/* Edit Menu */}
            <div className="relative">
              <button
                onClick={() => handleMenuClick('edit')}
                className={`px-2 py-0.5 rounded hover:bg-[#1e293b] ${activeMenu === 'edit' ? 'bg-[#1e293b] text-white' : ''}`}
              >
                Edit
              </button>
              {activeMenu === 'edit' && (
                <div className="absolute top-6 left-0 w-48 bg-[#0f172a] border border-[#1e293b] rounded shadow-2xl py-1 z-50">
                  <button onClick={() => { setActiveDrawer('search'); closeMenu(); }} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b] flex items-center justify-between">
                    <span>Find & Replace in Files</span>
                    <span className="text-[10px] text-slate-500">Ctrl+Shift+F</span>
                  </button>
                </div>
              )}
            </div>

            {/* View Menu */}
            <div className="relative">
              <button
                onClick={() => handleMenuClick('view')}
                className={`px-2 py-0.5 rounded hover:bg-[#1e293b] ${activeMenu === 'view' ? 'bg-[#1e293b] text-white' : ''}`}
              >
                View
              </button>
              {activeMenu === 'view' && (
                <div className="absolute top-6 left-0 w-48 bg-[#0f172a] border border-[#1e293b] rounded shadow-2xl py-1 z-50">
                  <button onClick={() => { setActiveDrawer('explorer'); setActiveView('editor'); closeMenu(); }} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b]">
                    Code Editor & Explorer
                  </button>
                  <button onClick={() => { setActiveDrawer('debugger'); closeMenu(); }} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b]">
                    Run & Debug Panel
                  </button>
                  <button onClick={() => { setActiveView('database'); closeMenu(); }} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b]">
                    Database Studio
                  </button>
                  <button onClick={() => { setActiveView('git'); closeMenu(); }} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b]">
                    Source Control (Git)
                  </button>
                </div>
              )}
            </div>

            {/* Run Menu */}
            <div className="relative">
              <button
                onClick={() => handleMenuClick('run')}
                className={`px-2 py-0.5 rounded hover:bg-[#1e293b] ${activeMenu === 'run' ? 'bg-[#1e293b] text-white' : ''}`}
              >
                Run
              </button>
              {activeMenu === 'run' && (
                <div className="absolute top-6 left-0 w-48 bg-[#0f172a] border border-[#1e293b] rounded shadow-2xl py-1 z-50">
                  <button onClick={() => { onRunCode(); closeMenu(); }} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b] flex items-center justify-between text-emerald-400">
                    <span>Run Without Debugging</span>
                    <span className="text-[10px] text-slate-500">Ctrl+F5</span>
                  </button>
                  <button onClick={() => { onStartDebug(); closeMenu(); }} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b] flex items-center justify-between text-rose-400">
                    <span>Start Debugging (GDB)</span>
                    <span className="text-[10px] text-slate-500">F5</span>
                  </button>
                </div>
              )}
            </div>

            {/* Help Menu */}
            <div className="relative">
              <button
                onClick={() => handleMenuClick('help')}
                className={`px-2 py-0.5 rounded hover:bg-[#1e293b] ${activeMenu === 'help' ? 'bg-[#1e293b] text-white' : ''}`}
              >
                Help
              </button>
              {activeMenu === 'help' && (
                <div className="absolute top-6 left-0 w-48 bg-[#0f172a] border border-[#1e293b] rounded shadow-2xl py-1 z-50">
                  <button onClick={() => { onOpenAbout(); closeMenu(); }} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b]">
                    About MEDHĀ IDE
                  </button>
                  <button onClick={() => { onOpenInventory(); closeMenu(); }} className="w-full text-left px-3 py-1.5 hover:bg-[#1e293b]">
                    System Hardware & Toolchains
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Info & Status Badges */}
        <div className="flex items-center gap-2 text-[10px]">
          <button
            onClick={onOpenEditionsModal}
            className={`px-2 py-0.5 rounded border transition-all ${editionInfo.badgeColor} flex items-center gap-1 font-bold`}
          >
            <Layers className="w-3 h-3" />
            {editionInfo.name}
          </button>
          <span className="font-mono text-slate-400 hidden lg:inline">
            /home/kanak/Desktop/ide
          </span>
        </div>
      </div>

      {/* Main IDE Quick Toolbar & Compiler / Build Config Controls */}
      <div className="h-9 bg-[#0f172a] px-3 flex items-center justify-between gap-3 font-sans">
        <div className="flex items-center gap-2">
          {/* Build Configuration Selector: Debug vs Release */}
          <div className="flex items-center bg-[#1e293b] border border-[#334155] rounded px-1 py-0.5 text-[11px]">
            <span className="text-[10px] text-slate-400 uppercase font-mono mr-1.5 pl-1">Config:</span>
            <button
              onClick={() => setBuildConfig('Debug')}
              className={`px-2 py-0.5 rounded text-[10px] font-bold transition-all ${buildConfig === 'Debug' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              Debug (-g)
            </button>
            <button
              onClick={() => setBuildConfig('Release')}
              className={`px-2 py-0.5 rounded text-[10px] font-bold transition-all ${buildConfig === 'Release' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              Release (-O2)
            </button>
          </div>

          {/* Compiler Toolchain Selector */}
          <div className="flex items-center bg-[#1e293b] border border-[#334155] rounded px-2 py-0.5 text-[11px]">
            <Cpu className="w-3.5 h-3.5 text-cyan-400 mr-1.5" />
            <select
              value={selectedCompiler}
              onChange={(e) => setSelectedCompiler(e.target.value)}
              className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer font-mono"
            >
              <option value="gcc" className="bg-[#0f172a]">GCC 15.2 (GNU C Compiler)</option>
              <option value="g++" className="bg-[#0f172a]">G++ 15.2 (GNU C++ Compiler)</option>
              <option value="python3" className="bg-[#0f172a]">Python 3.14 (Interpreter)</option>
              <option value="node" className="bg-[#0f172a]">Node.js v22 (TS / V8 Runtime)</option>
              <option value="rustc" className="bg-[#0f172a]">Rustc 1.84 (Cargo Compiler)</option>
              <option value="go" className="bg-[#0f172a]">Go 1.22 (Go Toolchain)</option>
              <option value="javac" className="bg-[#0f172a]">Javac 21 (OpenJDK)</option>
            </select>
          </div>
        </div>

        {/* Play & Debug Execution Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={onRunCode}
            className="flex items-center gap-1.5 px-3 py-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded text-xs font-semibold shadow-md active:scale-95 transition-all"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            Run Project
          </button>

          <button
            onClick={onStartDebug}
            className="flex items-center gap-1.5 px-3 py-1 bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500 text-white rounded text-xs font-semibold shadow-md active:scale-95 transition-all"
          >
            <Bug className="w-3.5 h-3.5" />
            Debug (GDB)
          </button>

          <button
            onClick={() => setIsAiOpen(!isAiOpen)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-semibold transition-all border ${
              isAiOpen 
                ? 'bg-purple-600 text-white border-purple-400 shadow-md' 
                : 'bg-purple-950/40 text-purple-300 border-purple-800/50 hover:bg-purple-900/40'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-300" />
            AI Assistant
          </button>
        </div>
      </div>
    </div>
  );
};
