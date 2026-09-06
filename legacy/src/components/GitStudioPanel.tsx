import React, { useState } from 'react';
import { GitBranch, GitCommit as GitCommitIcon, CheckSquare, Square, RefreshCw, CheckCircle2 } from 'lucide-react';
import { INITIAL_GIT_COMMITS, INITIAL_GIT_FILES, createGitCommit } from '../services/gitEngine';
import { GitCommit, GitFileStatus } from '../types';

export const GitStudioPanel: React.FC = () => {
  const [commits, setCommits] = useState<GitCommit[]>(INITIAL_GIT_COMMITS);
  const [files, setFiles] = useState<GitFileStatus[]>(INITIAL_GIT_FILES);
  const [commitMessage, setCommitMessage] = useState('');
  const [notification, setNotification] = useState<string | null>(null);

  const toggleStage = (path: string) => {
    setFiles(files.map(f => f.path === path ? { ...f, staged: !f.staged } : f));
  };

  const handleCommit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!commitMessage.trim()) return;

    const stagedFiles = files.filter(f => f.staged);
    if (stagedFiles.length === 0) {
      setNotification('No staged files selected for commit. Click files to stage them.');
      setTimeout(() => setNotification(null), 3000);
      return;
    }

    const newCommit = createGitCommit(commitMessage, stagedFiles);
    setCommits([newCommit, ...commits]);
    setFiles(files.filter(f => !f.staged));
    setCommitMessage('');
    setNotification(`Created Git Commit [${newCommit.shortHash}] "${newCommit.message}"`);
    setTimeout(() => setNotification(null), 4000);
  };

  return (
    <div className="flex-1 bg-[#090d16] flex h-full overflow-hidden select-none p-4 gap-4">
      {/* Commit & File Staging Panel */}
      <div className="w-80 bg-[#0f172a] rounded-xl border border-[#1e293b] flex flex-col p-4 space-y-4">
        <div className="flex items-center gap-2 border-b border-[#1e293b] pb-3">
          <GitBranch className="w-4 h-4 text-emerald-400" />
          <span className="font-bold text-xs uppercase tracking-wider text-white">Source Control (Git)</span>
        </div>

        {notification && (
          <div className="p-2 bg-emerald-950/60 border border-emerald-800/50 rounded-lg text-emerald-300 text-[11px] font-mono flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>{notification}</span>
          </div>
        )}

        <form onSubmit={handleCommit} className="space-y-2">
          <textarea
            value={commitMessage}
            onChange={(e) => setCommitMessage(e.target.value)}
            placeholder="Commit message (e.g. feat: refactor Big-O engine)..."
            rows={2}
            className="w-full bg-[#090d16] border border-[#334155] rounded-lg p-2 font-mono text-xs text-white placeholder-[#64748b] focus:outline-none focus:border-emerald-400"
          />
          <button
            type="submit"
            className="w-full py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-bold shadow"
          >
            Commit Staged Changes
          </button>
        </form>

        <div className="flex-1 overflow-y-auto space-y-2">
          <span className="text-[10px] font-bold uppercase text-[#64748b] block">Changed Files ({files.length})</span>
          {files.map((file) => (
            <div
              key={file.path}
              onClick={() => toggleStage(file.path)}
              className="flex items-center justify-between p-2 bg-[#1e293b]/40 hover:bg-[#1e293b] rounded cursor-pointer text-xs"
            >
              <div className="flex items-center gap-2 overflow-hidden">
                {file.staged ? <CheckSquare className="w-4 h-4 text-emerald-400" /> : <Square className="w-4 h-4 text-[#64748b]" />}
                <span className="truncate text-[#e2e8f0] font-mono text-[11px]">{file.path.split('/').pop()}</span>
              </div>
              <span className="text-[10px] uppercase font-mono px-1 rounded bg-[#090d16] text-amber-400">
                {file.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Graphical Commit Log Graph */}
      <div className="flex-1 bg-[#0f172a] rounded-xl border border-[#1e293b] flex flex-col p-4 space-y-3">
        <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
          <span className="text-xs font-bold text-white uppercase tracking-wider">Visual Commit History Graph</span>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800/40">
            Branch: main (HEAD)
          </span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-3">
          {commits.map((c) => (
            <div key={c.hash} className="flex items-start gap-3 p-3 bg-[#090d16] rounded-xl border border-[#1e293b]">
              <div className="p-2 rounded-full bg-emerald-500/20 text-emerald-400 mt-0.5">
                <GitCommitIcon className="w-4 h-4" />
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#e2e8f0]">{c.message}</span>
                  <span className="text-[10px] font-mono text-cyan-400">{c.shortHash}</span>
                </div>
                <div className="flex items-center gap-3 text-[10px] text-[#64748b]">
                  <span>{c.author}</span>
                  <span>•</span>
                  <span>{c.date}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
