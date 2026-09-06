import React from 'react';
import { Cpu, Zap, Layers, AlertCircle, HelpCircle } from 'lucide-react';
import { ComplexityResult } from '../types';

interface ComplexityPanelProps {
  complexity: ComplexityResult;
}

export const ComplexityPanel: React.FC<ComplexityPanelProps> = ({ complexity }) => {
  return (
    <div className="w-80 bg-[#0f172a] border-l border-[#1e293b] flex flex-col h-full overflow-y-auto select-none p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#1e293b] pb-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <span className="font-bold text-xs uppercase tracking-wider text-white">
            Big-O Complexity Analysis
          </span>
        </div>
        <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
          Confidence {complexity.confidence}%
        </span>
      </div>

      {/* Main Big-O Cards */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-[#1e293b]/70 border border-[#334155] rounded-xl p-3 flex flex-col gap-1">
          <span className="text-[10px] font-medium uppercase tracking-wider text-[#94a3b8]">
            Time Complexity
          </span>
          <span className={`text-xl font-extrabold font-mono ${
            complexity.timeComplexity === 'O(1)' || complexity.timeComplexity === 'O(log n)' ? 'text-emerald-400' :
            complexity.timeComplexity === 'O(n)' || complexity.timeComplexity === 'O(n log n)' ? 'text-cyan-400' :
            complexity.timeComplexity === 'O(n²)' ? 'text-amber-400' : 'text-rose-400'
          }`}>
            {complexity.timeComplexity}
          </span>
          <span className="text-[10px] text-[#64748b]">Worst: {complexity.worstCase}</span>
        </div>

        <div className="bg-[#1e293b]/70 border border-[#334155] rounded-xl p-3 flex flex-col gap-1">
          <span className="text-[10px] font-medium uppercase tracking-wider text-[#94a3b8]">
            Space Complexity
          </span>
          <span className="text-xl font-extrabold font-mono text-indigo-400">
            {complexity.spaceComplexity}
          </span>
          <span className="text-[10px] text-[#64748b]">Aux: {complexity.auxiliarySpace}</span>
        </div>
      </div>

      {/* Cases Breakdown Grid */}
      <div className="bg-[#090d16] rounded-lg p-3 border border-[#1e293b] space-y-2">
        <span className="text-xs font-semibold text-[#e2e8f0] block">Asymptotic Bounds</span>
        <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
          <div className="bg-[#1e293b]/50 p-2 rounded border border-[#334155]">
            <span className="text-[10px] text-[#64748b] block">Best Ω</span>
            <span className="text-emerald-400 font-bold">{complexity.bestCase}</span>
          </div>
          <div className="bg-[#1e293b]/50 p-2 rounded border border-[#334155]">
            <span className="text-[10px] text-[#64748b] block">Average Θ</span>
            <span className="text-cyan-400 font-bold">{complexity.averageCase}</span>
          </div>
          <div className="bg-[#1e293b]/50 p-2 rounded border border-[#334155]">
            <span className="text-[10px] text-[#64748b] block">Worst O</span>
            <span className="text-rose-400 font-bold">{complexity.worstCase}</span>
          </div>
        </div>
      </div>

      {/* Step-by-Step Reasoning */}
      <div className="space-y-2">
        <span className="text-xs font-semibold text-[#e2e8f0] flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-purple-400" />
          Derivation & Reasoning
        </span>
        <ul className="space-y-1.5 text-xs text-[#94a3b8]">
          {complexity.reasoning.map((reason, idx) => (
            <li key={idx} className="bg-[#1e293b]/40 border border-[#334155]/40 rounded p-2 text-[11px] leading-relaxed flex items-start gap-1.5">
              <span className="text-cyan-400 font-mono font-bold">•</span>
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Spatial Allocations */}
      {complexity.spatialAllocations.length > 0 && (
        <div className="space-y-2">
          <span className="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5" />
            Memory Allocations
          </span>
          {complexity.spatialAllocations.map((alloc, idx) => (
            <div key={idx} className="bg-amber-950/20 border border-amber-800/30 rounded p-2 text-[11px] text-amber-300">
              {alloc}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
