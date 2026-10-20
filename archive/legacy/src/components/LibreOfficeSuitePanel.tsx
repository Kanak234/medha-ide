import React, { useState } from 'react';
import { FileText, Table, Presentation, Calculator, Download, Play, Plus, Trash2, FileCode, Check, Bold, Italic, List, AlignLeft } from 'lucide-react';
import { INITIAL_CALC_DATA, INITIAL_IMPRESS_SLIDES, evaluateCalcFormula } from '../services/officeEngine';
import { LibreOfficeAppType, OfficeSpreadsheetCell, OfficePresentationSlide } from '../types';

export const LibreOfficeSuitePanel: React.FC = () => {
  const [activeApp, setActiveApp] = useState<LibreOfficeAppType>('writer');

  // Writer State
  const [writerText, setWriterText] = useState<string>(
    `# MEDHĀ-IDE Project Executive Documentation\n\n` +
    `## Executive Summary\n` +
    `MEDHĀ-IDE is an autonomous, offline-first, multi-platform AI Integrated Development Environment built for high-performance engineering workflows.\n\n` +
    `### Key Open-Source Capabilities\n` +
    `- **Multi-Language Compiler Suite**: Native GCC 15, Python 3.14, Node.js 22, OpenJDK 21, Rust 1.84.\n` +
    `- **Polyglot Database Studio**: Oracle 23c, PostgreSQL 16, MySQL 8.4, MongoDB 7.0, SQLite 3.\n` +
    `- **LibreOffice Suite Integration**: 100% Open Source document, spreadsheet, presentation, and formula processing.\n` +
    `- **Cyber Security Tooling**: Native Nmap, Wireshark, Metasploit, Burp Suite, Hydra, and Nikto penetration testing frameworks.`
  );

  // Calc State
  const [calcCells, setCalcCells] = useState<OfficeSpreadsheetCell[]>(INITIAL_CALC_DATA);
  const [selectedCell, setSelectedCell] = useState<{ row: number; col: number }>({ row: 1, col: 0 });
  const [formulaInput, setFormulaInput] = useState<string>('');

  // Impress State
  const [slides, setSlides] = useState<OfficePresentationSlide[]>(INITIAL_IMPRESS_SLIDES);
  const [activeSlideId, setActiveSlideId] = useState<string>('slide-1');
  const [isPresenting, setIsPresenting] = useState<boolean>(false);

  // Math State
  const [mathFormula, setMathFormula] = useState<string>(
    `f(x) = \\int_{-\\infty}^{\\infty} \\hat{f}(\\xi) e^{2\\pi i x \\xi} d\\xi`
  );

  const activeSlide = slides.find(s => s.id === activeSlideId) || slides[0];

  const handleCellChange = (row: number, col: number, value: string) => {
    setCalcCells(prev => {
      const existingIdx = prev.findIndex(c => c.row === row && c.col === col);
      if (existingIdx >= 0) {
        const copy = [...prev];
        copy[existingIdx] = { ...copy[existingIdx], value };
        return copy;
      }
      return [...prev, { row, col, value }];
    });
  };

  const handleExportFile = (extension: string) => {
    let content = '';
    let mime = 'text/plain';

    if (activeApp === 'writer') {
      content = writerText;
      mime = 'text/markdown';
    } else if (activeApp === 'calc') {
      content = calcCells.map(c => `${c.row},${c.col},"${c.value}"`).join('\n');
      mime = 'text/csv';
    } else if (activeApp === 'impress') {
      content = JSON.stringify(slides, null, 2);
      mime = 'application/json';
    } else {
      content = mathFormula;
    }

    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `libreoffice_${activeApp}_document.${extension}`;
    a.click();
  };

  return (
    <div className="flex-1 bg-[#090d16] flex flex-col h-full overflow-hidden select-none">
      {/* Top Suite Toolbar */}
      <div className="h-11 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <span className="font-bold text-xs uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-emerald-400" /> LibreOffice Productivity Suite
          </span>

          <div className="flex items-center gap-1 bg-[#1e293b] p-0.5 rounded-lg border border-[#334155]">
            <button
              onClick={() => setActiveApp('writer')}
              className={`px-3 py-1 text-xs font-semibold rounded-md flex items-center gap-1.5 transition-all ${
                activeApp === 'writer' ? 'bg-emerald-600 text-white shadow' : 'text-[#94a3b8] hover:text-white'
              }`}
            >
              <FileText className="w-3.5 h-3.5" /> Writer (Doc)
            </button>
            <button
              onClick={() => setActiveApp('calc')}
              className={`px-3 py-1 text-xs font-semibold rounded-md flex items-center gap-1.5 transition-all ${
                activeApp === 'calc' ? 'bg-emerald-600 text-white shadow' : 'text-[#94a3b8] hover:text-white'
              }`}
            >
              <Table className="w-3.5 h-3.5" /> Calc (Sheet)
            </button>
            <button
              onClick={() => setActiveApp('impress')}
              className={`px-3 py-1 text-xs font-semibold rounded-md flex items-center gap-1.5 transition-all ${
                activeApp === 'impress' ? 'bg-emerald-600 text-white shadow' : 'text-[#94a3b8] hover:text-white'
              }`}
            >
              <Presentation className="w-3.5 h-3.5" /> Impress (Slides)
            </button>
            <button
              onClick={() => setActiveApp('math')}
              className={`px-3 py-1 text-xs font-semibold rounded-md flex items-center gap-1.5 transition-all ${
                activeApp === 'math' ? 'bg-emerald-600 text-white shadow' : 'text-[#94a3b8] hover:text-white'
              }`}
            >
              <Calculator className="w-3.5 h-3.5" /> Math (Formula)
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {activeApp === 'impress' && (
            <button
              onClick={() => setIsPresenting(!isPresenting)}
              className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold flex items-center gap-1 shadow"
            >
              <Play className="w-3.5 h-3.5 fill-current" /> {isPresenting ? 'Exit Slideshow' : 'Start Slideshow'}
            </button>
          )}

          <button
            onClick={() => handleExportFile(activeApp === 'writer' ? 'odt' : (activeApp === 'calc' ? 'ods' : 'odp'))}
            className="px-3 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-emerald-300 rounded-lg text-xs font-bold flex items-center gap-1 border border-[#334155]"
          >
            <Download className="w-3.5 h-3.5" /> Export OpenDocument (.odt/.ods)
          </button>
        </div>
      </div>

      {/* Main Workspace Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* 1. LIBREOFFICE WRITER (DOCUMENT EDITOR) */}
        {activeApp === 'writer' && (
          <div className="flex-1 flex flex-col bg-[#090d16] p-4 overflow-hidden">
            {/* Formatting Toolbar */}
            <div className="h-9 bg-[#0f172a] border border-[#1e293b] rounded-t-xl flex items-center px-3 gap-2 text-slate-300 text-xs">
              <button className="p-1 hover:bg-[#1e293b] rounded"><Bold className="w-3.5 h-3.5" /></button>
              <button className="p-1 hover:bg-[#1e293b] rounded"><Italic className="w-3.5 h-3.5" /></button>
              <div className="h-4 w-[1px] bg-[#334155]" />
              <button className="p-1 hover:bg-[#1e293b] rounded"><AlignLeft className="w-3.5 h-3.5" /></button>
              <button className="p-1 hover:bg-[#1e293b] rounded"><List className="w-3.5 h-3.5" /></button>
              <div className="h-4 w-[1px] bg-[#334155]" />
              <span className="text-[11px] text-[#64748b]">LibreOffice Writer v24.2 OpenDocument Text</span>
            </div>

            <textarea
              value={writerText}
              onChange={(e) => setWriterText(e.target.value)}
              className="flex-1 bg-[#0d1322] border-x border-b border-[#1e293b] rounded-b-xl p-6 font-mono text-sm text-[#e2e8f0] focus:outline-none leading-relaxed resize-none"
            />

            <div className="h-6 flex items-center justify-between text-[11px] font-mono text-[#64748b] pt-2 px-1">
              <span>Words: {writerText.split(/\s+/).length} | Characters: {writerText.length}</span>
              <span>Format: OpenDocument Text (ODT / Markdown)</span>
            </div>
          </div>
        )}

        {/* 2. LIBREOFFICE CALC (SPREADSHEET EDITOR) */}
        {activeApp === 'calc' && (
          <div className="flex-1 flex flex-col bg-[#090d16] p-4 overflow-hidden">
            {/* Formula Bar */}
            <div className="h-9 bg-[#0f172a] border border-[#1e293b] rounded-t-xl flex items-center px-3 gap-2">
              <span className="font-mono text-xs text-emerald-400 font-bold">f(x)</span>
              <input
                type="text"
                placeholder="Enter cell formula (e.g. =SUM(D2:D4))"
                value={formulaInput}
                onChange={(e) => setFormulaInput(e.target.value)}
                className="flex-1 bg-[#090d16] border border-[#334155] rounded px-2 py-0.5 font-mono text-xs text-white focus:outline-none"
              />
            </div>

            {/* Grid Table */}
            <div className="flex-1 bg-[#0d1322] border-x border-b border-[#1e293b] rounded-b-xl overflow-auto p-4">
              <table className="w-full border-collapse font-mono text-xs">
                <thead>
                  <tr className="bg-[#0f172a] text-slate-400">
                    <th className="border border-[#1e293b] p-2 w-12 text-center">#</th>
                    <th className="border border-[#1e293b] p-2 text-left">A</th>
                    <th className="border border-[#1e293b] p-2 text-left">B</th>
                    <th className="border border-[#1e293b] p-2 text-left">C</th>
                    <th className="border border-[#1e293b] p-2 text-left">D</th>
                  </tr>
                </thead>
                <tbody>
                  {[0, 1, 2, 3, 4].map((r) => (
                    <tr key={r} className="hover:bg-[#1e293b]/20">
                      <td className="border border-[#1e293b] p-2 bg-[#0f172a] text-[#64748b] text-center font-bold">{r + 1}</td>
                      {[0, 1, 2, 3].map((c) => {
                        const cell = calcCells.find(item => item.row === r && item.col === c);
                        const isHeader = r === 0;
                        return (
                          <td key={c} className={`border border-[#1e293b] p-1 ${isHeader ? 'bg-[#151f32] font-bold text-emerald-300' : 'text-slate-200'}`}>
                            <input
                              type="text"
                              value={cell?.value || ''}
                              onChange={(e) => handleCellChange(r, c, e.target.value)}
                              className="w-full bg-transparent border-none text-xs focus:outline-none focus:bg-indigo-950/40 rounded px-1"
                            />
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 3. LIBREOFFICE IMPRESS (PRESENTATION BUILDER) */}
        {activeApp === 'impress' && (
          <div className="flex-1 flex bg-[#090d16] p-4 overflow-hidden gap-4">
            {/* Slide Navigation Sidebar */}
            <div className="w-56 bg-[#0f172a] border border-[#1e293b] rounded-xl p-3 flex flex-col space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-[#1e293b] pb-2">
                Presentation Slides
              </span>
              {slides.map((s, idx) => (
                <div
                  key={s.id}
                  onClick={() => setActiveSlideId(s.id)}
                  className={`p-2.5 rounded-lg cursor-pointer text-xs border transition-all ${
                    activeSlideId === s.id
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-semibold'
                      : 'bg-[#1e293b]/40 text-[#94a3b8] border-[#334155]/40 hover:text-white'
                  }`}
                >
                  <div className="font-bold">Slide {idx + 1}</div>
                  <div className="truncate text-[11px] text-slate-400">{s.title}</div>
                </div>
              ))}
            </div>

            {/* Slide Stage Viewport */}
            <div className="flex-1 bg-[#0d1322] border border-[#1e293b] rounded-xl flex items-center justify-center p-8 relative overflow-hidden">
              <div className="w-full max-w-xl bg-[#0f172a] border border-[#334155] rounded-2xl p-8 shadow-2xl space-y-4">
                <h1 className="text-2xl font-extrabold text-emerald-400 tracking-tight">{activeSlide.title}</h1>
                {activeSlide.subtitle && <p className="text-sm font-medium text-slate-400">{activeSlide.subtitle}</p>}
                <ul className="space-y-2 text-sm text-slate-200 pt-2">
                  {activeSlide.content.map((item, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* 4. LIBREOFFICE MATH (EQUATION EDITOR) */}
        {activeApp === 'math' && (
          <div className="flex-1 flex flex-col bg-[#090d16] p-4 overflow-hidden gap-4">
            <div className="flex-1 flex gap-4">
              <div className="flex-1 bg-[#0f172a] border border-[#1e293b] rounded-xl p-4 flex flex-col space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">LaTeX / MathML Formula Input</span>
                <textarea
                  value={mathFormula}
                  onChange={(e) => setMathFormula(e.target.value)}
                  className="flex-1 bg-[#090d16] border border-[#334155] rounded-lg p-3 font-mono text-sm text-emerald-300 focus:outline-none resize-none"
                />
              </div>

              <div className="flex-1 bg-[#0d1322] border border-[#1e293b] rounded-xl p-6 flex flex-col items-center justify-center space-y-4">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Rendered Scientific Equation</span>
                <div className="p-6 bg-[#0f172a] rounded-xl border border-[#334155] text-xl font-mono text-white text-center shadow-xl">
                  {mathFormula}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
