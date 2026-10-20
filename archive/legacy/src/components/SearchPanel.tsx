import React, { useState } from 'react';
import { Search, ChevronRight, FileCode, SlidersHorizontal, ArrowRightLeft } from 'lucide-react';
import { FileItem } from '../types';

interface SearchResultMatch {
  fileId: string;
  fileName: string;
  filePath: string;
  lineNumber: number;
  lineContent: string;
}

interface SearchPanelProps {
  files: FileItem[];
  onSelectFileMatch: (file: FileItem, line: number) => void;
}

export const SearchPanel: React.FC<SearchPanelProps> = ({ files, onSelectFileMatch }) => {
  const [query, setQuery] = useState('');
  const [replaceQuery, setReplaceQuery] = useState('');
  const [isReplaceOpen, setIsReplaceOpen] = useState(false);
  const [caseSensitive, setCaseSensitive] = useState(false);

  const getFileMatches = (): SearchResultMatch[] => {
    if (!query.trim()) return [];

    const matches: SearchResultMatch[] = [];
    const searchTarget = caseSensitive ? query : query.toLowerCase();

    const flattenFiles = (items: FileItem[]) => {
      items.forEach(item => {
        if (item.type === 'directory' && item.children) {
          flattenFiles(item.children);
        } else if (item.type === 'file' && item.content) {
          const lines = item.content.split('\n');
          lines.forEach((lineText, idx) => {
            const lineTarget = caseSensitive ? lineText : lineText.toLowerCase();
            if (lineTarget.includes(searchTarget)) {
              matches.push({
                fileId: item.id,
                fileName: item.name,
                filePath: item.path,
                lineNumber: idx + 1,
                lineContent: lineText.trim()
              });
            }
          });
        }
      });
    };

    flattenFiles(files);
    return matches;
  };

  const matches = getFileMatches();

  return (
    <div className="w-80 bg-[#0f172a] border-r border-[#1e293b] flex flex-col h-full select-none text-xs text-slate-300">
      {/* Search Header */}
      <div className="p-3 border-b border-[#1e293b] flex items-center justify-between bg-[#0b101d]">
        <span className="font-bold text-[11px] uppercase tracking-wider text-slate-200 flex items-center gap-1.5">
          <Search className="w-3.5 h-3.5 text-cyan-400" />
          Search & Replace in Workspace
        </span>
        <button
          onClick={() => setIsReplaceOpen(!isReplaceOpen)}
          className={`p-1 rounded transition-colors ${isReplaceOpen ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400 hover:text-white'}`}
          title="Toggle Replace"
        >
          <ArrowRightLeft className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Input controls */}
      <div className="p-3 space-y-2 border-b border-[#1e293b] bg-[#090d16]">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search matching text (e.g. main, struct)..."
            className="w-full bg-[#0f172a] border border-[#334155] rounded px-2.5 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 font-mono"
          />
        </div>

        {isReplaceOpen && (
          <div className="relative">
            <input
              type="text"
              value={replaceQuery}
              onChange={(e) => setReplaceQuery(e.target.value)}
              placeholder="Replace with..."
              className="w-full bg-[#0f172a] border border-[#334155] rounded px-2.5 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-400 font-mono"
            />
          </div>
        )}

        <div className="flex items-center gap-2 text-[10px] text-slate-400 pt-1">
          <button
            onClick={() => setCaseSensitive(!caseSensitive)}
            className={`px-1.5 py-0.5 rounded border transition-colors ${caseSensitive ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400 font-bold' : 'border-[#334155]'}`}
          >
            Aa Case Match
          </button>
        </div>
      </div>

      {/* Search Results */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {!query.trim() ? (
          <div className="p-4 text-center text-slate-500 text-[11px]">
            Type a query above to perform real workspace symbol & text search.
          </div>
        ) : matches.length === 0 ? (
          <div className="p-4 text-center text-slate-500 text-[11px]">
            No results found matching '{query}'.
          </div>
        ) : (
          <div>
            <div className="px-2 py-1 text-[10px] uppercase font-bold text-slate-400 mb-1">
              Found {matches.length} matches across workspace
            </div>
            {matches.map((m, idx) => (
              <div
                key={idx}
                onClick={() => {
                  const targetFile = files.find(f => f.id === m.fileId || f.path === m.filePath);
                  if (targetFile) onSelectFileMatch(targetFile, m.lineNumber);
                }}
                className="p-2 rounded border border-[#1e293b] bg-[#1e293b]/30 hover:bg-[#1e293b] cursor-pointer transition-colors space-y-1"
              >
                <div className="flex items-center justify-between text-[11px] text-cyan-300 font-medium font-mono">
                  <div className="flex items-center gap-1.5">
                    <FileCode className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{m.fileName}</span>
                  </div>
                  <span className="text-[10px] text-slate-400">Line {m.lineNumber}</span>
                </div>
                <div className="text-[10px] font-mono text-slate-300 truncate bg-[#090d16] p-1 rounded">
                  {m.lineContent}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
