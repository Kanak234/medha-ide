import React, { useState } from 'react';
import { GraduationCap, Play, SkipForward, RotateCcw, Check, AlertCircle, ArrowRight, Code } from 'lucide-react';
import { EDUCATIONAL_DEMOS } from '../services/educationalDemos';
import { EducationalDemo } from '../types';

export const EducationalDemosPanel: React.FC = () => {
  const [selectedDemo, setSelectedDemo] = useState<EducationalDemo>(EDUCATIONAL_DEMOS[0]);
  const [activeStep, setActiveStep] = useState(0);

  const steps = selectedDemo.visualizerSteps || [];
  const currentStep = steps[activeStep];

  return (
    <div className="flex-1 bg-[#090d16] flex flex-col h-full overflow-hidden select-none">
      {/* Top Header */}
      <div className="p-4 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/20 text-purple-400 rounded-lg border border-purple-500/30">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Learning & Interactive Educational Demos Library</h2>
            <p className="text-xs text-[#94a3b8]">Runnable control flow, loop deep dives, data structures, and algorithm visualizers</p>
          </div>
        </div>

        {/* Demo Selector Buttons */}
        <div className="flex items-center gap-1.5 overflow-x-auto max-w-xl">
          {EDUCATIONAL_DEMOS.map((demo) => (
            <button
              key={demo.id}
              onClick={() => {
                setSelectedDemo(demo);
                setActiveStep(0);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                selectedDemo.id === demo.id
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-[#1e293b] text-[#94a3b8] hover:text-white'
              }`}
            >
              {demo.title.split(':')[0]}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="flex-1 p-4 grid grid-cols-12 gap-4 overflow-y-auto">
        {/* Left Column: Code & Comparison */}
        <div className="col-span-7 flex flex-col gap-4">
          <div className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b] space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-cyan-300">{selectedDemo.title}</h3>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                {selectedDemo.category}
              </span>
            </div>
            <p className="text-xs text-[#94a3b8]">{selectedDemo.description}</p>

            <pre className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b] text-xs font-mono text-cyan-200 overflow-x-auto">
              {selectedDemo.code}
            </pre>
          </div>

          {/* Good vs Bad Implementation Comparison */}
          {(selectedDemo.goodCode || selectedDemo.badCode) && (
            <div className="grid grid-cols-2 gap-3">
              {selectedDemo.badCode && (
                <div className="bg-rose-950/20 border border-rose-800/30 p-3 rounded-xl space-y-1.5">
                  <span className="text-xs font-bold text-rose-400 flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5" /> Problematic Implementation
                  </span>
                  <pre className="bg-[#090d16] p-2 rounded text-[11px] font-mono text-rose-200 overflow-x-auto">
                    {selectedDemo.badCode}
                  </pre>
                </div>
              )}

              {selectedDemo.goodCode && (
                <div className="bg-emerald-950/20 border border-emerald-800/30 p-3 rounded-xl space-y-1.5">
                  <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                    <Check className="w-3.5 h-3.5" /> Optimized Implementation
                  </span>
                  <pre className="bg-[#090d16] p-2 rounded text-[11px] font-mono text-emerald-200 overflow-x-auto">
                    {selectedDemo.goodCode}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Step-by-Step Visualizer & Architectural Explanation */}
        <div className="col-span-5 flex flex-col gap-4">
          {/* Visualizer Frame */}
          {steps.length > 0 && (
            <div className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b] space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  Interactive Step Visualizer ({activeStep + 1} / {steps.length})
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setActiveStep(0)}
                    className="p-1 hover:bg-[#1e293b] rounded text-[#94a3b8] hover:text-white"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setActiveStep((prev) => Math.min(steps.length - 1, prev + 1))}
                    disabled={activeStep >= steps.length - 1}
                    className="px-2 py-1 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded text-xs font-semibold flex items-center gap-1"
                  >
                    Next Step <SkipForward className="w-3 h-3" />
                  </button>
                </div>
              </div>

              {currentStep && (
                <div className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b] space-y-2">
                  <p className="text-xs text-cyan-300 font-medium">{currentStep.description}</p>
                  <pre className="bg-[#1e293b]/60 p-2 rounded text-[11px] font-mono text-[#e2e8f0] overflow-x-auto">
                    {JSON.stringify(currentStep.state, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* Structural Explanation */}
          <div className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b] space-y-3 flex-1">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">Engineering Breakdown</h4>
            
            <div className="space-y-2 text-xs">
              <div className="bg-[#1e293b]/60 p-2.5 rounded border border-[#334155]">
                <span className="font-bold text-cyan-300 block mb-0.5">When to Use</span>
                <p className="text-[#94a3b8]">{selectedDemo.explanation.whenToUse}</p>
              </div>

              <div className="bg-[#1e293b]/60 p-2.5 rounded border border-[#334155]">
                <span className="font-bold text-rose-300 block mb-0.5">When NOT to Use</span>
                <p className="text-[#94a3b8]">{selectedDemo.explanation.whenNotToUse}</p>
              </div>

              <div className="flex gap-2">
                <div className="flex-1 bg-[#090d16] p-2.5 rounded border border-[#1e293b] text-center font-mono">
                  <span className="text-[10px] text-[#64748b] block">Time Complexity</span>
                  <span className="text-emerald-400 font-extrabold">{selectedDemo.explanation.complexity.time}</span>
                </div>
                <div className="flex-1 bg-[#090d16] p-2.5 rounded border border-[#1e293b] text-center font-mono">
                  <span className="text-[10px] text-[#64748b] block">Space Complexity</span>
                  <span className="text-indigo-400 font-extrabold">{selectedDemo.explanation.complexity.space}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
