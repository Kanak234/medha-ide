import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, Wand2, ArrowRight, CheckCircle2 } from 'lucide-react';
import { QualityScore } from '../types';

interface QualityScorePanelProps {
  quality: QualityScore;
  onApplyOptimization: (newCode: string) => void;
}

export const QualityScorePanel: React.FC<QualityScorePanelProps> = ({ quality, onApplyOptimization }) => {
  const [showRefactorModal, setShowRefactorModal] = useState(false);

  return (
    <div className="w-80 bg-[#0f172a] border-l border-[#1e293b] flex flex-col h-full overflow-y-auto select-none p-4 space-y-4">
      {/* Header & Overall Score */}
      <div className="flex items-center justify-between border-b border-[#1e293b] pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span className="font-bold text-xs uppercase tracking-wider text-white">
            Code Quality Audit
          </span>
        </div>
        <span className={`text-xs font-mono font-extrabold px-2.5 py-0.5 rounded ${
          quality.overallScore >= 85 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' :
          quality.overallScore >= 70 ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40' :
          'bg-rose-500/20 text-rose-400 border border-rose-500/40'
        }`}>
          Grade {quality.complexityGrade} ({quality.overallScore}/100)
        </span>
      </div>

      {/* Metric Gauges */}
      <div className="space-y-2 bg-[#090d16] p-3 rounded-xl border border-[#1e293b]">
        <div className="space-y-1">
          <div className="flex justify-between text-xs font-medium">
            <span className="text-[#94a3b8]">Performance</span>
            <span className="text-emerald-400 font-mono">{quality.performanceScore}%</span>
          </div>
          <div className="w-full bg-[#1e293b] h-1.5 rounded-full overflow-hidden">
            <div className="bg-emerald-400 h-full rounded-full" style={{ width: `${quality.performanceScore}%` }}></div>
          </div>
        </div>

        <div className="space-y-1">
          <div className="flex justify-between text-xs font-medium">
            <span className="text-[#94a3b8]">Readability</span>
            <span className="text-cyan-400 font-mono">{quality.readabilityScore}%</span>
          </div>
          <div className="w-full bg-[#1e293b] h-1.5 rounded-full overflow-hidden">
            <div className="bg-cyan-400 h-full rounded-full" style={{ width: `${quality.readabilityScore}%` }}></div>
          </div>
        </div>

        <div className="space-y-1">
          <div className="flex justify-between text-xs font-medium">
            <span className="text-[#94a3b8]">Maintainability</span>
            <span className="text-purple-400 font-mono">{quality.maintainabilityScore}%</span>
          </div>
          <div className="w-full bg-[#1e293b] h-1.5 rounded-full overflow-hidden">
            <div className="bg-purple-400 h-full rounded-full" style={{ width: `${quality.maintainabilityScore}%` }}></div>
          </div>
        </div>
      </div>

      {/* Make It Better Refactoring Promotion Card */}
      {quality.makeItBetter && (
        <div className="bg-gradient-to-br from-purple-950/40 to-indigo-950/40 border border-purple-800/40 p-3 rounded-xl space-y-2">
          <div className="flex items-center gap-2 text-purple-300 font-semibold text-xs">
            <Wand2 className="w-4 h-4 text-purple-400 animate-spin" />
            <span>"Make It Better" Refactoring Ready!</span>
          </div>
          <p className="text-[11px] text-[#94a3b8]">
            Refactor O(n²) quadratic loop into linear O(n) hash map implementation.
          </p>
          <button
            onClick={() => setShowRefactorModal(true)}
            className="w-full py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded text-xs font-semibold shadow transition-colors"
          >
            Review & Apply Refactoring
          </button>
        </div>
      )}

      {/* Code Smells List */}
      <div className="space-y-2">
        <span className="text-xs font-semibold text-[#e2e8f0]">Detected Code Smells ({quality.smells.length})</span>
        {quality.smells.length === 0 ? (
          <div className="bg-[#090d16] p-3 rounded border border-[#1e293b] text-[11px] text-emerald-400 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>Zero code smells detected. Clean implementation!</span>
          </div>
        ) : (
          quality.smells.map((smell) => (
            <div key={smell.id} className="bg-[#1e293b]/50 border border-[#334155] p-2.5 rounded-lg text-xs space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-rose-300">{smell.type}</span>
                <span className="text-[10px] font-mono text-[#64748b]">Line {smell.line}</span>
              </div>
              <p className="text-[11px] text-[#94a3b8]">{smell.description}</p>
              <p className="text-[11px] text-cyan-300 font-medium">👉 {smell.recommendation}</p>
            </div>
          ))
        )}
      </div>

      {/* Make It Better Comparison Dialog */}
      {showRefactorModal && quality.makeItBetter && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-6 z-50">
          <div className="bg-[#0f172a] border border-[#334155] rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-[#1e293b] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Wand2 className="w-5 h-5 text-purple-400" />
                <h3 className="text-sm font-bold text-white">"Make It Better" Code Refactoring Comparison</h3>
              </div>
              <button
                onClick={() => setShowRefactorModal(false)}
                className="text-[#64748b] hover:text-white text-xs px-2 py-1 bg-[#1e293b] rounded"
              >
                Close
              </button>
            </div>

            <div className="p-4 flex-1 overflow-y-auto space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-rose-400 block">Original Code ({quality.makeItBetter.timeComplexityBefore})</span>
                  <pre className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b] text-xs font-mono text-[#94a3b8] overflow-x-auto">
                    {quality.makeItBetter.originalCode}
                  </pre>
                </div>
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-emerald-400 block">Optimized Code ({quality.makeItBetter.timeComplexityAfter})</span>
                  <pre className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b] text-xs font-mono text-emerald-300 overflow-x-auto">
                    {quality.makeItBetter.optimizedCode}
                  </pre>
                </div>
              </div>

              <div className="bg-[#1e293b]/70 p-3 rounded-xl border border-[#334155] space-y-2">
                <h4 className="text-xs font-bold text-cyan-300">Trade-Off Analysis & Rationale</h4>
                <p className="text-xs text-[#94a3b8]">{quality.makeItBetter.tradeoffs}</p>
              </div>
            </div>

            <div className="p-4 border-t border-[#1e293b] flex justify-end gap-2">
              <button
                onClick={() => setShowRefactorModal(false)}
                className="px-4 py-2 bg-[#1e293b] text-white rounded text-xs font-medium"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onApplyOptimization(quality.makeItBetter!.optimizedCode);
                  setShowRefactorModal(false);
                }}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded text-xs font-bold shadow-lg"
              >
                Apply Optimization to Active File
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
