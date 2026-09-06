import React from 'react';
import { X, Check, ShieldCheck, Zap, Layers } from 'lucide-react';
import { EDITIONS_CONFIG, IDEEdition } from '../services/editionsEngine';

interface EditionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentEdition: IDEEdition;
  onSelectEdition: (edition: IDEEdition) => void;
}

export const EditionsModal: React.FC<EditionsModalProps> = ({
  isOpen,
  onClose,
  currentEdition,
  onSelectEdition
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-[#0f172a] border border-slate-700 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-semibold text-slate-100">MEDHĀ-IDE Software Editions & Capabilities</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-md transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          <div className="text-center max-w-2xl mx-auto">
            <h3 className="text-lg font-bold text-slate-100">Choose Your Offline Development Edition</h3>
            <p className="text-xs text-slate-400 mt-1">
              Switching editions adjusts active feature sets, system toolchain integrations, and UI modules instantly.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(Object.keys(EDITIONS_CONFIG) as IDEEdition[]).map(edKey => {
              const ed = EDITIONS_CONFIG[edKey];
              const isCurrent = currentEdition === edKey;
              return (
                <div
                  key={edKey}
                  className={`flex flex-col justify-between p-4 rounded-xl border transition-all ${
                    isCurrent
                      ? 'bg-slate-900 border-indigo-500 shadow-lg shadow-indigo-500/10 ring-1 ring-indigo-500'
                      : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${ed.badgeColor}`}>
                        {ed.name}
                      </span>
                      {isCurrent && (
                        <span className="text-[10px] font-medium text-indigo-400 flex items-center gap-1">
                          <Check className="w-3 h-3" /> Active
                        </span>
                      )}
                    </div>
                    <p className="text-xs font-medium text-slate-200 mt-2">{ed.tagline}</p>
                    <div className="text-[10px] text-slate-400 mt-2 font-mono bg-slate-950/60 p-1.5 rounded border border-slate-800">
                      Target Size: {ed.bundleSizeEstimate}
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-2">
                      {ed.features.map((feat, i) => (
                        <div key={i} className="flex items-start gap-1.5 text-[11px] text-slate-300">
                          <ShieldCheck className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                          <span>{feat}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      onSelectEdition(edKey);
                      onClose();
                    }}
                    disabled={isCurrent}
                    className={`w-full mt-5 py-2 px-3 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
                      isCurrent
                        ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/50 cursor-default'
                        : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-md'
                    }`}
                  >
                    {isCurrent ? 'Currently Active' : <><Zap className="w-3.5 h-3.5" /> Switch to {ed.name}</>}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
