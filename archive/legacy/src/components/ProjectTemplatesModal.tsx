import React from 'react';
import { FolderOpen, X, Code2, ArrowRight } from 'lucide-react';
import { DEMO_PROJECTS, DemoProject } from '../services/demoProjects';

interface ProjectTemplatesModalProps {
  onLoadProject: (project: DemoProject) => void;
  onClose: () => void;
}

export const ProjectTemplatesModal: React.FC<ProjectTemplatesModalProps> = ({ onLoadProject, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-6 z-50 select-none">
      <div className="bg-[#0f172a] border border-[#334155] rounded-2xl w-full max-w-2xl flex flex-col overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-[#1e293b] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FolderOpen className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">Load Demo Project Template</h3>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-[#1e293b] text-[#64748b] hover:text-white rounded">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 space-y-3 max-h-[70vh] overflow-y-auto">
          {DEMO_PROJECTS.map((proj) => (
            <div
              key={proj.id}
              onClick={() => {
                onLoadProject(proj);
                onClose();
              }}
              className="p-4 bg-[#090d16] hover:bg-[#1e293b]/60 rounded-xl border border-[#1e293b] hover:border-cyan-500/40 cursor-pointer transition-all flex items-center justify-between group"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Code2 className="w-4 h-4 text-cyan-400" />
                  <span className="text-xs font-bold text-white group-hover:text-cyan-300">{proj.name}</span>
                  <span className="text-[9px] uppercase font-mono px-2 py-0.5 rounded bg-[#1e293b] text-purple-300 border border-purple-500/30">
                    {proj.category}
                  </span>
                </div>
                <p className="text-xs text-[#94a3b8]">{proj.description}</p>
              </div>
              <ArrowRight className="w-4 h-4 text-[#64748b] group-hover:text-cyan-400 transition-colors" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
