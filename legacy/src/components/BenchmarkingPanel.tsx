import React, { useState } from 'react';
import { Gauge, Play, Trophy, Cpu, Zap, RotateCcw } from 'lucide-react';
import { runBenchmarkComparison } from '../services/benchmarkingEngine';
import { BenchmarkComparison } from '../types';

export const BenchmarkingPanel: React.FC = () => {
  const [comparison, setComparison] = useState<BenchmarkComparison>({
    title: 'Linear Search O(n) vs Hash Map Lookup O(1)',
    description: 'Executes 50,000 iterations to compare quadratic/linear array searching against constant time hash lookups.',
    implementationA: {
      name: 'Implementation A: Nested Linear Loop Search',
      language: 'typescript',
      code: `function searchA(arr: number[], target: number) {
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] === target) return i;
  }
  return -1;
}`
    },
    implementationB: {
      name: 'Implementation B: Bitwise & Hash Map Direct Lookup',
      language: 'typescript',
      code: `function searchB(map: Map<number, number>, target: number) {
  return map.get(target) ?? -1;
}`
    }
  });

  const [isRunning, setIsRunning] = useState(false);

  const handleRunBenchmark = async () => {
    setIsRunning(true);
    const updated = await runBenchmarkComparison(comparison);
    setComparison(updated);
    setIsRunning(false);
  };

  return (
    <div className="flex-1 bg-[#090d16] flex flex-col h-full overflow-hidden select-none p-4 space-y-4">
      {/* Top Banner */}
      <div className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-500/20 text-amber-400 rounded-lg border border-amber-500/30">
            <Gauge className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">{comparison.title}</h2>
            <p className="text-xs text-[#94a3b8]">{comparison.description}</p>
          </div>
        </div>

        <button
          onClick={handleRunBenchmark}
          disabled={isRunning}
          className="px-5 py-2 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white rounded-lg text-xs font-bold shadow-lg shadow-amber-900/30 flex items-center gap-2 transition-all"
        >
          {isRunning ? <RotateCcw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
          {isRunning ? 'Running Profiler...' : 'Execute Local Benchmark'}
        </button>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-2 gap-4 flex-1 overflow-y-auto">
        {/* Implementation A */}
        <div className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b] flex flex-col space-y-3">
          <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
            <span className="text-xs font-bold text-rose-300">{comparison.implementationA.name}</span>
            <span className="text-[10px] font-mono bg-[#1e293b] px-2 py-0.5 rounded text-[#94a3b8]">
              {comparison.resultA ? comparison.resultA.timeComplexity : 'O(n)'}
            </span>
          </div>

          <pre className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b] text-xs font-mono text-[#e2e8f0]">
            {comparison.implementationA.code}
          </pre>

          {comparison.resultA && (
            <div className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b] space-y-2 flex-1">
              <span className="text-[11px] font-bold uppercase text-[#94a3b8]">Execution Metrics</span>
              <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
                <div className="bg-[#1e293b] p-2 rounded">
                  <span className="text-[10px] text-[#64748b] block">Time Elapsed</span>
                  <span className="text-rose-400 font-bold">{comparison.resultA.executionTimeMs} ms</span>
                </div>
                <div className="bg-[#1e293b] p-2 rounded">
                  <span className="text-[10px] text-[#64748b] block">Throughput</span>
                  <span className="text-cyan-400 font-bold">{comparison.resultA.operationsPerSec.toLocaleString()} ops/s</span>
                </div>
                <div className="bg-[#1e293b] p-2 rounded">
                  <span className="text-[10px] text-[#64748b] block">Memory</span>
                  <span className="text-indigo-400 font-bold">{comparison.resultA.memoryUsedMB} MB</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Implementation B */}
        <div className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b] flex flex-col space-y-3">
          <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
            <span className="text-xs font-bold text-emerald-300">{comparison.implementationB.name}</span>
            <span className="text-[10px] font-mono bg-[#1e293b] px-2 py-0.5 rounded text-[#94a3b8]">
              {comparison.resultB ? comparison.resultB.timeComplexity : 'O(1)'}
            </span>
          </div>

          <pre className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b] text-xs font-mono text-emerald-200">
            {comparison.implementationB.code}
          </pre>

          {comparison.resultB && (
            <div className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b] space-y-2 flex-1">
              <span className="text-[11px] font-bold uppercase text-[#94a3b8]">Execution Metrics</span>
              <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
                <div className="bg-[#1e293b] p-2 rounded">
                  <span className="text-[10px] text-[#64748b] block">Time Elapsed</span>
                  <span className="text-emerald-400 font-bold">{comparison.resultB.executionTimeMs} ms</span>
                </div>
                <div className="bg-[#1e293b] p-2 rounded">
                  <span className="text-[10px] text-[#64748b] block">Throughput</span>
                  <span className="text-cyan-400 font-bold">{comparison.resultB.operationsPerSec.toLocaleString()} ops/s</span>
                </div>
                <div className="bg-[#1e293b] p-2 rounded">
                  <span className="text-[10px] text-[#64748b] block">Memory</span>
                  <span className="text-indigo-400 font-bold">{comparison.resultB.memoryUsedMB} MB</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Winner Rationale Banner */}
      {comparison.conclusion && (
        <div className="bg-gradient-to-r from-amber-950/50 via-yellow-950/30 to-emerald-950/50 border border-amber-500/40 p-3 rounded-xl flex items-center gap-3">
          <Trophy className="w-6 h-6 text-amber-400 shrink-0" />
          <p className="text-xs text-amber-200 font-medium">{comparison.conclusion}</p>
        </div>
      )}
    </div>
  );
};
