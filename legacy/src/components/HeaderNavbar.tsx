import React from 'react';
import { 
  Play, 
  Cpu, 
  Sparkles, 
  Code2, 
  GraduationCap, 
  Gauge, 
  Database, 
  GitBranch, 
  Box, 
  Smartphone,
  FolderOpen,
  Layers,
  Palette,
  Globe
} from 'lucide-react';
import { SystemInventory } from '../types';
import { EDITIONS_CONFIG, IDEEdition } from '../services/editionsEngine';

interface HeaderNavbarProps {
  activeView: string;
  setActiveView: (view: string) => void;
  inventory: SystemInventory;
  onOpenInventory: () => void;
  onOpenTemplates: () => void;
  onOpenAbout?: () => void;
  onRunCode: () => void;
  isAiOpen: boolean;
  setIsAiOpen: (open: boolean) => void;
  currentEdition: IDEEdition;
  onOpenEditionsModal: () => void;
  currentTheme: string;
  onChangeTheme: (theme: string) => void;
}

export const HeaderNavbar: React.FC<HeaderNavbarProps> = ({
  activeView,
  setActiveView,
  inventory,
  onOpenInventory,
  onOpenTemplates,
  onOpenAbout,
  onRunCode,
  isAiOpen,
  setIsAiOpen,
  currentEdition,
  onOpenEditionsModal,
  currentTheme,
  onChangeTheme
}) => {
  const editionInfo = EDITIONS_CONFIG[currentEdition];

  return (
    <header className="h-14 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between px-4 select-none">
      {/* Brand & Logo & Edition Badge */}
      <div className="flex items-center gap-3">
        <div 
          onClick={onOpenAbout}
          className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 cursor-pointer hover:scale-105 transition-transform"
          title="About MEDHĀ IDE (Created by Kanak Prabhakar)"
        >
          <Code2 className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span 
              onClick={onOpenAbout}
              className="font-extrabold text-base tracking-wide bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-300 cursor-pointer hover:opacity-90 transition-opacity"
            >
              MEDHĀ<span className="text-white font-light">-IDE</span>
            </span>
            <button
              onClick={onOpenEditionsModal}
              className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border transition-all hover:scale-105 ${editionInfo.badgeColor} flex items-center gap-1`}
              title="Click to change IDE Software Edition"
            >
              <Layers className="w-3 h-3" />
              {editionInfo.name}
            </button>
          </div>
          <span className="text-[11px] text-[#64748b] block font-mono">
            /home/kanak/Desktop/ide
          </span>
        </div>
      </div>

      {/* Main Feature View Navigation */}
      <nav className="flex items-center gap-1 bg-[#090d16] p-1 rounded-xl border border-[#1e293b]">
        <button
          onClick={() => setActiveView('editor')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            activeView === 'editor' 
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm' 
              : 'text-[#94a3b8] hover:text-white hover:bg-[#1e293b]/50'
          }`}
        >
          <Code2 className="w-3.5 h-3.5" />
          Editor
        </button>

        <button
          onClick={() => setActiveView('learning')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            activeView === 'learning' 
              ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-sm' 
              : 'text-[#94a3b8] hover:text-white hover:bg-[#1e293b]/50'
          }`}
        >
          <GraduationCap className="w-3.5 h-3.5" />
          Learning Demos
        </button>

        <button
          onClick={() => setActiveView('benchmark')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            activeView === 'benchmark' 
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm' 
              : 'text-[#94a3b8] hover:text-white hover:bg-[#1e293b]/50'
          }`}
        >
          <Gauge className="w-3.5 h-3.5" />
          Benchmarking
        </button>

        <button
          onClick={() => setActiveView('database')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            activeView === 'database' 
              ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 shadow-sm' 
              : 'text-[#94a3b8] hover:text-white hover:bg-[#1e293b]/50'
          }`}
        >
          <Database className="w-3.5 h-3.5" />
          Database Studio
        </button>

        <button
          onClick={() => setActiveView('git')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            activeView === 'git' 
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm' 
              : 'text-[#94a3b8] hover:text-white hover:bg-[#1e293b]/50'
          }`}
        >
          <GitBranch className="w-3.5 h-3.5" />
          Git
        </button>

        <button
          onClick={() => setActiveView('devops')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            activeView === 'devops' 
              ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40 shadow-sm' 
              : 'text-[#94a3b8] hover:text-white hover:bg-[#1e293b]/50'
          }`}
        >
          <Box className="w-3.5 h-3.5" />
          DevOps & Docker
        </button>

        <button
          onClick={() => setActiveView('mobile')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            activeView === 'mobile' 
              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 shadow-sm' 
              : 'text-[#94a3b8] hover:text-white hover:bg-[#1e293b]/50'
          }`}
        >
          <Smartphone className="w-3.5 h-3.5" />
          Mobile Preview
        </button>

        <button
          onClick={() => setActiveView('browser')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            activeView === 'browser' 
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm' 
              : 'text-[#94a3b8] hover:text-white hover:bg-[#1e293b]/50'
          }`}
        >
          <Globe className="w-3.5 h-3.5" />
          Browser
        </button>
      </nav>

      {/* Action Controls, Theme Selector & Hardware Badge */}
      <div className="flex items-center gap-2.5">
        <button
          onClick={onRunCode}
          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-cyan-300 rounded-lg text-xs font-semibold border border-cyan-500/40 shadow-sm active:scale-95 transition-all"
          title="Build Project with compiler toolchain"
        >
          <Box className="w-3.5 h-3.5 text-cyan-400" />
          Build Project
        </button>

        <button
          onClick={onRunCode}
          className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-emerald-900/30 active:scale-95 transition-all"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          Run Project
        </button>

        <button
          onClick={onOpenTemplates}
          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-[#e2e8f0] rounded-lg text-xs font-medium transition-all border border-[#334155]"
          title="Load Project Templates"
        >
          <FolderOpen className="w-3.5 h-3.5 text-cyan-400" />
          Templates
        </button>

        {/* Theme Selector Dropdown */}
        <div className="relative flex items-center bg-[#1e293b]/80 border border-[#334155] rounded-lg px-2 py-1">
          <Palette className="w-3.5 h-3.5 text-purple-400 mr-1.5" />
          <select
            value={currentTheme}
            onChange={(e) => onChangeTheme(e.target.value)}
            className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer"
            title="Change UI Visual Theme"
          >
            <option value="dark" className="bg-slate-900 text-slate-200">Dark Modern</option>
            <option value="light" className="bg-slate-900 text-slate-200">Light Crisp</option>
            <option value="high-contrast" className="bg-slate-900 text-slate-200">High Contrast</option>
            <option value="cyberpunk" className="bg-slate-900 text-slate-200">Cyberpunk Neon</option>
            <option value="solarized" className="bg-slate-900 text-slate-200">Solarized Dark</option>
          </select>
        </div>

        <button
          onClick={onOpenInventory}
          className="flex items-center gap-2 px-2.5 py-1.5 bg-[#1e293b]/80 hover:bg-[#334155] text-[#94a3b8] hover:text-white rounded-lg text-xs font-medium border border-[#334155] transition-all"
          title="System Hardware & Toolchain Inventory"
        >
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span className="hidden md:inline font-mono">{inventory.cpuCores} Cores | {inventory.totalRamGB}GB</span>
        </button>

        <button
          onClick={() => setIsAiOpen(!isAiOpen)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
            isAiOpen 
              ? 'bg-purple-600 text-white border-purple-400 shadow-md shadow-purple-900/40' 
              : 'bg-purple-950/40 text-purple-300 border-purple-800/50 hover:bg-purple-900/40'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-purple-300" />
          AI Assistant
        </button>
      </div>
    </header>
  );
};
