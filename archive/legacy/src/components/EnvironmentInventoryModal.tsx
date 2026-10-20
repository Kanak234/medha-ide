import React from 'react';
import { Cpu, CheckCircle2, AlertCircle, X, Shield, Server } from 'lucide-react';
import { SystemInventory } from '../types';

interface EnvironmentInventoryModalProps {
  inventory: SystemInventory;
  onClose: () => void;
}

export const EnvironmentInventoryModal: React.FC<EnvironmentInventoryModalProps> = ({ inventory, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-6 z-50 select-none">
      <div className="bg-[#0f172a] border border-[#334155] rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="p-4 border-b border-[#1e293b] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">System Hardware & Toolchain Environment Inventory</h3>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-[#1e293b] text-[#64748b] hover:text-white rounded">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Inventory Body */}
        <div className="p-4 flex-1 overflow-y-auto space-y-4">
          {/* Hardware Specs */}
          <div className="bg-[#090d16] p-4 rounded-xl border border-[#1e293b] grid grid-cols-4 gap-3 text-center font-mono">
            <div className="bg-[#1e293b]/60 p-2.5 rounded border border-[#334155]">
              <span className="text-[10px] text-[#64748b] block">Operating System</span>
              <span className="text-xs text-cyan-300 font-bold">Linux x86_64</span>
            </div>
            <div className="bg-[#1e293b]/60 p-2.5 rounded border border-[#334155]">
              <span className="text-[10px] text-[#64748b] block">CPU Cores</span>
              <span className="text-xs text-emerald-400 font-bold">{inventory.cpuCores} Threads</span>
            </div>
            <div className="bg-[#1e293b]/60 p-2.5 rounded border border-[#334155]">
              <span className="text-[10px] text-[#64748b] block">Memory (RAM)</span>
              <span className="text-xs text-purple-300 font-bold">{inventory.totalRamGB} GB Total</span>
            </div>
            <div className="bg-[#1e293b]/60 p-2.5 rounded border border-[#334155]">
              <span className="text-[10px] text-[#64748b] block">GPU Hardware</span>
              <span className="text-xs text-amber-300 font-bold">NVIDIA RTX 4060</span>
            </div>
          </div>

          {/* Installed Toolchains List */}
          <div className="space-y-2">
            <span className="text-xs font-bold text-[#e2e8f0]">Detected Compilers, SDKs & Toolchains</span>
            <div className="grid grid-cols-2 gap-3">
              {inventory.tools.map((tool) => (
                <div key={tool.name} className="p-3 bg-[#090d16] rounded-xl border border-[#1e293b] flex flex-col justify-between space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{tool.name}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      Installed {tool.version}
                    </span>
                  </div>
                  <p className="text-[11px] text-[#94a3b8]">{tool.description}</p>
                  <span className="text-[10px] font-mono text-[#64748b]">Path: {tool.path}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#1e293b] flex justify-between items-center text-xs text-[#64748b]">
          <span>Inventory automatically scanned at startup. All toolchains configured.</span>
          <button onClick={onClose} className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-bold">
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
