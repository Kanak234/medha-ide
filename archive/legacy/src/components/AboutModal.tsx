import React from 'react';
import { X, Code2, ShieldCheck, Cpu, Layers, Sparkles, Heart, BookOpen, Shield, Zap, Workflow, CheckCircle2 } from 'lucide-react';
import { INTELLIGENT_SUBSYSTEMS } from '../services/subsystemsEngine';

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AboutModal: React.FC<AboutModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const getSubsystemIcon = (id: string) => {
    switch (id) {
      case 'sarasvati':
        return <BookOpen className="w-4 h-4 text-cyan-400" />;
      case 'kali':
        return <Shield className="w-4 h-4 text-rose-400" />;
      case 'mahalakshmi':
        return <Zap className="w-4 h-4 text-amber-400" />;
      case 'vaishnavi':
        return <Workflow className="w-4 h-4 text-emerald-400" />;
      default:
        return <Cpu className="w-4 h-4 text-purple-400" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 select-none">
      <div className="bg-[#0f172a] border border-[#334155] w-full max-w-3xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="h-14 bg-gradient-to-r from-cyan-950/80 via-[#0f172a] to-purple-950/80 px-6 flex items-center justify-between border-b border-[#1e293b] shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Code2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-base font-extrabold tracking-wide text-white flex items-center gap-2">
                MEDHĀ IDE <span className="text-cyan-400 font-normal"> मेधा IDE</span>
              </h2>
              <p className="text-[11px] text-[#94a3b8] font-mono">v1.0.0 Autonomous Offline AI-Powered IDE</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-[#1e293b] rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body Content */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1 text-xs leading-relaxed text-[#e2e8f0]">
          {/* Official Creator & Vision Block */}
          <div className="bg-[#090d16] border border-[#1e293b] rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
              <span className="font-bold text-xs uppercase tracking-wider text-cyan-400">Official Creator & Project Leadership</span>
              <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 font-mono text-[10px] font-bold border border-cyan-500/30">
                Vision Conceived: 2022
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 font-mono">
              <div>
                <span className="text-[#64748b] block text-[10px] uppercase font-bold">Created By</span>
                <span className="text-white font-bold text-sm">Kanak Prabhakar</span>
              </div>
              <div>
                <span className="text-[#64748b] block text-[10px] uppercase font-bold">Primary Creator & Lead</span>
                <span className="text-cyan-300 font-bold text-sm">Kanak Prabhakar</span>
              </div>
            </div>

            <p className="text-[#94a3b8] text-[11px] leading-relaxed pt-1">
              <strong>MEDHĀ IDE</strong> has evolved through continuous day-by-day research, development, experimentation, testing, debugging, and refinement. The project is part of a larger vision for intelligent, secure, accessible, offline-first and developer-focused technology.
            </p>
          </div>

          {/* Product Philosophy */}
          <div className="space-y-2">
            <h3 className="font-bold text-xs uppercase tracking-wider text-purple-400">Central Intelligence & Meaning</h3>
            <p className="text-slate-300">
              <strong>MEDHĀ — मेधा</strong> represents intelligence, understanding, knowledge, reasoning, learning, and coordination. MEDHĀ serves as the central intelligence layer coordinating specialized internal subsystems.
            </p>

            <div className="p-3 bg-purple-950/30 border border-purple-800/40 rounded-xl text-center font-mono font-bold text-purple-200 tracking-wider">
              Knowledge → Intelligence → Creation
            </div>
          </div>

          {/* Intelligent Subsystems Section */}
          <div className="space-y-3">
            <h3 className="font-bold text-xs uppercase tracking-wider text-cyan-400 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>Intelligent Subsystem Architecture</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {INTELLIGENT_SUBSYSTEMS.map((sub) => (
                <div key={sub.id} className="bg-[#090d16] border border-[#1e293b] rounded-xl p-3 space-y-2 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between border-b border-[#1e293b] pb-1.5">
                      <div className="flex items-center gap-2">
                        {getSubsystemIcon(sub.id)}
                        <span className="font-bold text-xs text-white">{sub.name} <span className="text-[#94a3b8] font-normal">({sub.sanskritName})</span></span>
                      </div>
                      <div className="flex items-center gap-1">
                        {sub.status.map((st) => (
                          <span key={st} className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                            {st}
                          </span>
                        ))}
                      </div>
                    </div>
                    <p className="text-[11px] font-semibold text-cyan-300 mt-1.5">{sub.role}</p>
                    <p className="text-[11px] text-[#94a3b8] mt-1 leading-snug">{sub.description}</p>
                  </div>

                  <div className="pt-2 border-t border-[#1e293b]/60 flex flex-wrap gap-1">
                    {sub.responsibilities.slice(0, 5).map((resp) => (
                      <span key={resp} className="text-[9px] font-mono bg-[#1e293b]/60 text-slate-300 px-1.5 py-0.5 rounded">
                        {resp}
                      </span>
                    ))}
                    {sub.responsibilities.length > 5 && (
                      <span className="text-[9px] font-mono text-[#64748b] px-1 py-0.5">
                        +{sub.responsibilities.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Respectful Personal Dedication Block */}
          <div className="bg-gradient-to-r from-rose-950/30 via-[#090d16] to-purple-950/30 border border-rose-800/40 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2 border-b border-rose-800/30 pb-2">
              <Heart className="w-4 h-4 text-rose-400 shrink-0" />
              <span className="font-bold text-xs uppercase tracking-wider text-rose-300">Personal Dedication</span>
            </div>

            <p className="text-slate-200 text-xs italic leading-relaxed pt-1">
              &quot;MEDHĀ IDE is dedicated by Kanak Prabhakar to Maa Vaishno, Maa Kali, Maa Saraswati, his mother, his girlfriend, and his sister, as an expression of gratitude, inspiration, love, knowledge, strength and dedication.&quot;
            </p>

            <div className="text-[10px] text-[#94a3b8] pt-1 border-t border-[#1e293b] font-mono">
              Note: This dedication represents personal inspiration and gratitude by Kanak Prabhakar. Technical creator & lead remains strictly Kanak Prabhakar.
            </div>
          </div>

          {/* R&D Information */}
          <div className="bg-[#090d16] border border-[#1e293b] rounded-xl p-4 space-y-2">
            <h3 className="font-bold text-xs uppercase tracking-wider text-emerald-400">Reported R&D & Development Investment</h3>
            <div className="text-lg font-extrabold font-mono text-emerald-300">₹50,000 INR</div>
            <p className="text-[#94a3b8] text-[11px] leading-relaxed">
              This amount represents the reported investment toward research, development, building and integrating the IDE architecture, development infrastructure, testing, and open-source adaptation by Kanak Prabhakar across his organisation.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="h-12 bg-[#0d1322] border-t border-[#1e293b] px-6 flex items-center justify-between text-[11px] text-[#64748b] shrink-0">
          <span>Official Creator & Lead: Kanak Prabhakar</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-white rounded-lg font-bold transition-all"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
