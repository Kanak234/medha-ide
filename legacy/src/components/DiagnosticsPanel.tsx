import React from 'react';
import { AlertTriangle, AlertCircle, Info, ChevronRight, CheckCircle2 } from 'lucide-react';
import { CompilerDiagnostic } from '../services/vaishnaviEngine';

interface DiagnosticsPanelProps {
  diagnostics: CompilerDiagnostic[];
  onSelectDiagnostic?: (file: string, line: number, column: number) => void;
  compilerOutput?: string;
  toolchainStatus?: string;
}

export const DiagnosticsPanel: React.FC<DiagnosticsPanelProps> = ({
  diagnostics,
  onSelectDiagnostic,
  compilerOutput,
  toolchainStatus
}) => {
  const errorsCount = diagnostics.filter(d => d.severity === 'error').length;
  const warningsCount = diagnostics.filter(d => d.severity === 'warning').length;

  return (
    <div className="bg-[#0b101d] border-t border-[#1e293b] flex flex-col font-mono text-xs select-none min-h-[160px] max-h-[300px]">
      {/* Header Bar */}
      <div className="h-8 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between px-3">
        <div className="flex items-center gap-3">
          <span className="font-bold text-[11px] uppercase tracking-wider text-slate-200 flex items-center gap-1.5">
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
            Problems / Compiler Diagnostics
          </span>
          <div className="flex items-center gap-2 text-[10px]">
            <span className={`px-2 py-0.5 rounded font-bold ${errorsCount > 0 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' : 'bg-slate-800 text-slate-400'}`}>
              {errorsCount} Errors
            </span>
            <span className={`px-2 py-0.5 rounded font-bold ${warningsCount > 0 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-slate-800 text-slate-400'}`}>
              {warningsCount} Warnings
            </span>
          </div>
        </div>

        {toolchainStatus && (
          <div className="text-[10px] text-cyan-400 font-sans font-medium flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Toolchain: {toolchainStatus}
          </div>
        )}
      </div>

      {/* Diagnostics List & Output */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {diagnostics.length === 0 ? (
          <div className="p-4 text-center text-slate-500 flex flex-col items-center justify-center gap-1.5">
            <CheckCircle2 className="w-5 h-5 text-emerald-400/70" />
            <span className="text-[11px] text-slate-400 font-sans">No compile errors or diagnostic warnings detected in workspace.</span>
            {compilerOutput && (
              <pre className="mt-2 p-2 bg-[#060911] border border-[#1e293b] rounded text-[10px] text-slate-300 max-w-full overflow-x-auto text-left">
                {compilerOutput}
              </pre>
            )}
          </div>
        ) : (
          diagnostics.map((diag) => (
            <div
              key={diag.id}
              onClick={() => onSelectDiagnostic?.(diag.file, diag.line, diag.column)}
              className={`p-2 rounded border flex items-start justify-between gap-3 cursor-pointer transition-colors ${
                diag.severity === 'error'
                  ? 'bg-rose-950/20 border-rose-800/40 hover:bg-rose-950/40 text-rose-200'
                  : diag.severity === 'warning'
                  ? 'bg-amber-950/20 border-amber-800/40 hover:bg-amber-950/40 text-amber-200'
                  : 'bg-slate-900 border-slate-700 hover:bg-slate-800 text-slate-300'
              }`}
            >
              <div className="flex items-start gap-2 flex-1">
                {diag.severity === 'error' ? (
                  <AlertCircle className="w-4 h-4 text-rose-400 mt-0.5 flex-shrink-0" />
                ) : diag.severity === 'warning' ? (
                  <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                ) : (
                  <Info className="w-4 h-4 text-sky-400 mt-0.5 flex-shrink-0" />
                )}
                <div>
                  <div className="font-semibold text-[11px] leading-tight">{diag.message}</div>
                  <div className="text-[10px] opacity-75 font-sans mt-0.5">
                    Source: <span className="font-mono text-cyan-300">{diag.file}</span> (Line {diag.line}, Col {diag.column})
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-1 text-[10px] opacity-60 hover:opacity-100 text-cyan-400 font-sans">
                Jump to line <ChevronRight className="w-3 h-3" />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
