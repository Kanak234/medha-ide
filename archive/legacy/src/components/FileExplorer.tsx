import React, { useState } from 'react';
import { 
  Folder, 
  FolderOpen, 
  FileCode, 
  FileText, 
  Plus, 
  ChevronRight, 
  ChevronDown,
  Code
} from 'lucide-react';
import { FileItem, SupportedLanguage } from '../types';

interface FileExplorerProps {
  files: FileItem[];
  onSelectFile: (file: FileItem) => void;
  activeFileId?: string;
  onCreateFile: (name: string, language: SupportedLanguage) => void;
}

export const FileExplorer: React.FC<FileExplorerProps> = ({
  files,
  onSelectFile,
  activeFileId,
  onCreateFile
}) => {
  const [newFileName, setNewFileName] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFileName.trim()) return;

    let lang: SupportedLanguage = 'typescript';
    if (newFileName.endsWith('.py')) lang = 'python';
    else if (newFileName.endsWith('.cpp') || newFileName.endsWith('.h')) lang = 'cpp';
    else if (newFileName.endsWith('.c')) lang = 'c';
    else if (newFileName.endsWith('.rs')) lang = 'rust';
    else if (newFileName.endsWith('.go')) lang = 'go';
    else if (newFileName.endsWith('.java')) lang = 'java';
    else if (newFileName.endsWith('.sql')) lang = 'sql';
    else if (newFileName.endsWith('.html')) lang = 'html';
    else if (newFileName.endsWith('.css')) lang = 'css';

    onCreateFile(newFileName.trim(), lang);
    setNewFileName('');
    setIsCreating(false);
  };

  const renderItem = (item: FileItem) => {
    const isActive = activeFileId === item.id;
    if (item.type === 'directory') {
      return (
        <div key={item.id} className="select-none">
          <div className="flex items-center gap-1.5 px-2 py-1 hover:bg-[#1e293b]/50 rounded cursor-pointer text-xs text-[#94a3b8]">
            <ChevronDown className="w-3.5 h-3.5 text-[#64748b]" />
            <FolderOpen className="w-4 h-4 text-amber-400" />
            <span className="font-medium text-[#e2e8f0]">{item.name}</span>
          </div>
          <div className="pl-4 border-l border-[#1e293b]/60 ml-3">
            {item.children?.map(renderItem)}
          </div>
        </div>
      );
    }

    return (
      <div
        key={item.id}
        onClick={() => onSelectFile(item)}
        className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer text-xs transition-all ${
          isActive 
            ? 'bg-cyan-500/15 text-cyan-300 font-medium border-l-2 border-cyan-400' 
            : 'text-[#94a3b8] hover:bg-[#1e293b]/40 hover:text-white'
        }`}
      >
        <div className="flex items-center gap-2 overflow-hidden">
          <FileCode className={`w-3.5 h-3.5 shrink-0 ${
            item.language === 'python' ? 'text-amber-400' :
            item.language === 'cpp' || item.language === 'c' ? 'text-blue-400' :
            item.language === 'rust' ? 'text-orange-400' :
            item.language === 'java' ? 'text-red-400' :
            item.language === 'sql' ? 'text-emerald-400' : 'text-cyan-400'
          }`} />
          <span className="truncate">{item.name}</span>
        </div>
        {item.language && (
          <span className="text-[9px] uppercase font-mono px-1 rounded bg-[#1e293b] text-[#64748b]">
            {item.language}
          </span>
        )}
      </div>
    );
  };

  return (
    <div className="w-64 bg-[#0f172a] border-r border-[#1e293b] flex flex-col h-full select-none">
      {/* Workspace Header */}
      <div className="p-3 border-b border-[#1e293b] flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-[#94a3b8]">
          Workspace Files
        </span>
        <button
          onClick={() => setIsCreating(true)}
          className="p-1 hover:bg-[#1e293b] text-[#64748b] hover:text-cyan-400 rounded transition-colors"
          title="Create New File"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {/* File Creation Inline Form */}
      {isCreating && (
        <form onSubmit={handleCreate} className="p-2 bg-[#1e293b]/40 border-b border-[#1e293b]">
          <input
            type="text"
            value={newFileName}
            onChange={(e) => setNewFileName(e.target.value)}
            placeholder="filename.ts, .py, .cpp..."
            autoFocus
            className="w-full bg-[#090d16] border border-[#334155] rounded px-2 py-1 text-xs text-white placeholder-[#64748b] focus:outline-none focus:border-cyan-400"
          />
        </form>
      )}

      {/* File Tree List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {files.map(renderItem)}
      </div>
    </div>
  );
};
