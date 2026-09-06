import React from 'react';
import { Box, Play, CheckCircle2, Server, Terminal, Shield } from 'lucide-react';

export const DevOpsPanel: React.FC = () => {
  const containers = [
    { name: 'medha-ide-web', image: 'node:22-alpine', status: 'Running', port: '3000:3000', memory: '42 MB' },
    { name: 'medha-ide-db', image: 'postgres:16', status: 'Running', port: '5432:5432', memory: '88 MB' },
    { name: 'medha-ide-compiler-worker', image: 'gcc:15', status: 'Idle', port: '-', memory: '12 MB' }
  ];

  return (
    <div className="flex-1 bg-[#090d16] flex h-full overflow-hidden select-none p-4 gap-4">
      {/* Containers Status Dashboard */}
      <div className="flex-1 bg-[#0f172a] rounded-xl border border-[#1e293b] flex flex-col p-4 space-y-4">
        <div className="flex items-center justify-between border-b border-[#1e293b] pb-3">
          <div className="flex items-center gap-2">
            <Box className="w-4 h-4 text-blue-400" />
            <span className="font-bold text-xs uppercase tracking-wider text-white">Containers & Podman Dashboard</span>
          </div>
          <span className="text-[10px] font-mono bg-blue-500/20 text-blue-300 border border-blue-500/30 px-2 py-0.5 rounded">
            Docker Socket Active
          </span>
        </div>

        <div className="space-y-2">
          {containers.map((c) => (
            <div key={c.name} className="flex items-center justify-between p-3 bg-[#090d16] rounded-xl border border-[#1e293b]">
              <div className="flex items-center gap-3">
                <Server className="w-4 h-4 text-blue-400" />
                <div>
                  <span className="text-xs font-bold text-[#e2e8f0] block">{c.name}</span>
                  <span className="text-[10px] text-[#64748b] font-mono">{c.image} | Port: {c.port}</span>
                </div>
              </div>

              <div className="flex items-center gap-3 text-xs font-mono">
                <span className="text-[#94a3b8]">{c.memory}</span>
                <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px]">
                  {c.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
