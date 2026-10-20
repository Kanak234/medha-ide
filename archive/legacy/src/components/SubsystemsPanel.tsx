import React from 'react';
import { Cpu, BookOpen, Shield, Zap, Workflow, CheckCircle, Heart, Lock, AlertTriangle } from 'lucide-react';
import { INTELLIGENT_SUBSYSTEMS } from '../services/subsystemsEngine';

export const SubsystemsPanel: React.FC = () => {
  const getSubsystemIcon = (id: string) => {
    switch (id) {
      case 'sarasvati':
        return <BookOpen className="w-6 h-6 text-cyan-400" />;
      case 'kali':
        return <Shield className="w-6 h-6 text-rose-400" />;
      case 'mahalakshmi':
        return <Zap className="w-6 h-6 text-amber-400" />;
      case 'vaishnavi':
        return <Workflow className="w-6 h-6 text-emerald-400" />;
      default:
        return <Cpu className="w-6 h-6 text-purple-400" />;
    }
  };

  return (
    <div className="flex-1 bg-[#090d16] flex flex-col h-full overflow-y-auto select-none p-6 space-y-6 text-[#e2e8f0]">
      {/* Header Banner */}
      <div className="bg-[#0f172a] p-5 rounded-2xl border border-[#1e293b] flex items-center justify-between shadow-xl">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gradient-to-br from-cyan-500 via-indigo-600 to-purple-600 rounded-xl text-white shadow-lg shadow-cyan-500/20">
            <Cpu className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-lg font-extrabold text-white flex items-center gap-2">
              MEDHĀ Intelligent Subsystem Architecture <span className="text-cyan-400 font-normal">मेधा IDE</span>
            </h1>
            <p className="text-xs text-[#94a3b8] font-mono mt-0.5">
              Central Intelligence Orchestrating Specialized Technical Engines
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-3 py-1 bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 rounded-full font-bold">
            Creator: Kanak Prabhakar
          </span>
          <span className="px-3 py-1 bg-purple-500/10 text-purple-300 border border-purple-500/30 rounded-full font-bold">
            Inception: 2022
          </span>
        </div>
      </div>

      {/* ASCII System Architecture Diagram Block */}
      <div className="bg-[#0f172a] p-5 rounded-2xl border border-[#1e293b] space-y-3 shadow-lg">
        <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono">
            Conceptual Subsystem Topology
          </span>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800/40 font-bold">
            Verified Operational
          </span>
        </div>

        <pre className="p-4 bg-[#05080f] rounded-xl border border-[#1e293b] font-mono text-xs text-cyan-300 overflow-x-auto leading-tight">
{`                    MEDHĀ IDE
                        |
                MEDHĀ Intelligence
                        |
       ┌────────────────┼────────────────┐
       │                │                │
   SARASVATĪ          KĀLĪ        MAHĀLAKṢMĪ
   Knowledge         Security      Performance
       │                │                │
       └────────────────┼────────────────┘
                        │
                    VAISHNAVĪ
                  Orchestration
                        │
               Developer Workspace`}
        </pre>
      </div>

      {/* Grid of 4 Intelligent Subsystems */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {INTELLIGENT_SUBSYSTEMS.map((sub) => (
          <div
            key={sub.id}
            className="bg-[#0f172a] rounded-2xl border border-[#1e293b] p-5 flex flex-col justify-between space-y-4 hover:border-cyan-500/40 transition-all shadow-lg"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between border-b border-[#1e293b] pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-[#090d16] border border-[#1e293b] rounded-xl">
                    {getSubsystemIcon(sub.id)}
                  </div>
                  <div>
                    <h3 className="text-sm font-extrabold text-white flex items-center gap-2">
                      {sub.name} <span className="text-cyan-400 font-normal">({sub.sanskritName})</span>
                    </h3>
                    <p className="text-[11px] text-[#94a3b8] font-mono">{sub.tagline}</p>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-1">
                  {sub.status.map((st) => (
                    <span
                      key={st}
                      className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1"
                    >
                      <CheckCircle className="w-2.5 h-2.5" />
                      {st}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-[10px] uppercase font-bold text-[#64748b] tracking-wider block font-mono">Role & Description</span>
                <p className="text-xs font-semibold text-cyan-300 mt-0.5">{sub.role}</p>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed">{sub.description}</p>
              </div>

              <div>
                <span className="text-[10px] uppercase font-bold text-[#64748b] tracking-wider block font-mono mb-1.5">
                  Core Responsibilities ({sub.responsibilities.length})
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {sub.responsibilities.map((resp) => (
                    <span
                      key={resp}
                      className="text-[10px] font-mono bg-[#090d16] text-slate-300 px-2 py-1 rounded-md border border-[#1e293b]"
                    >
                      • {resp}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {sub.id === 'kali' && (
              <div className="p-2.5 bg-rose-950/20 border border-rose-800/30 rounded-xl flex items-center gap-2 text-[11px] text-rose-300 font-mono">
                <Lock className="w-4 h-4 shrink-0 text-rose-400" />
                <span>Defensive Security Design: Threat detection & workspace boundary enforcement.</span>
              </div>
            )}

            {sub.id === 'mahalakshmi' && (
              <div className="p-2.5 bg-amber-950/20 border border-amber-800/30 rounded-xl flex items-center gap-2 text-[11px] text-amber-300 font-mono">
                <Zap className="w-4 h-4 shrink-0 text-amber-400" />
                <span>Zero Benchmarking Fabrication: Real execution measurement telemetry.</span>
              </div>
            )}

            {sub.id === 'vaishnavi' && (
              <div className="p-2.5 bg-emerald-950/20 border border-emerald-800/30 rounded-xl flex items-center gap-2 text-[11px] text-emerald-300 font-mono">
                <Workflow className="w-4 h-4 shrink-0 text-emerald-400" />
                <span>Workspace Boundary Protection: NEVER DELETE USER FILES policy strictly active.</span>
              </div>
            )}

            {sub.id === 'sarasvati' && (
              <div className="p-2.5 bg-cyan-950/20 border border-cyan-800/30 rounded-xl flex items-center gap-2 text-[11px] text-cyan-300 font-mono">
                <BookOpen className="w-4 h-4 shrink-0 text-cyan-400" />
                <span>Offline Developer Knowledge Base & RAG Indexing active.</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Dedication Banner */}
      <div className="bg-gradient-to-r from-rose-950/40 via-[#0f172a] to-purple-950/40 p-5 rounded-2xl border border-rose-800/40 shadow-xl space-y-2">
        <div className="flex items-center gap-2 border-b border-rose-800/30 pb-2">
          <Heart className="w-5 h-5 text-rose-400" />
          <h2 className="text-sm font-extrabold text-rose-200 uppercase tracking-wider">
            Personal Dedication by Kanak Prabhakar
          </h2>
        </div>

        <p className="text-sm italic text-slate-200 leading-relaxed font-serif pt-1">
          &quot;MEDHĀ IDE is a work of dedication by Kanak Prabhakar, inspired by gratitude, knowledge, strength, creativity, learning and the people and spiritual figures who hold deep personal meaning in his life.
          <br /><br />
          This project is dedicated to Maa Vaishno, Maa Kali, Maa Saraswati, my mother, my girlfriend, and my sister.&quot;
        </p>

        <div className="pt-2 border-t border-[#1e293b] flex items-center justify-between text-[11px] text-[#94a3b8] font-mono">
          <span>Sole Technical Creator & Primary Lead: Kanak Prabhakar</span>
          <span>Knowledge → Intelligence → Creation</span>
        </div>
      </div>
    </div>
  );
};
