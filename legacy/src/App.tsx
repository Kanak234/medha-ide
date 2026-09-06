import React, { useState, useMemo } from 'react';
import { TopMenuBar } from './components/TopMenuBar';
import { HeaderNavbar } from './components/HeaderNavbar';
import { Sidebar } from './components/Sidebar';
import { FileExplorer } from './components/FileExplorer';
import { SearchPanel } from './components/SearchPanel';
import { DebuggerPanel } from './components/DebuggerPanel';
import { BottomDockPanel } from './components/BottomDockPanel';
import { CodeEditorPanel } from './components/CodeEditorPanel';
import { ComplexityPanel } from './components/ComplexityPanel';
import { QualityScorePanel } from './components/QualityScorePanel';
import { EducationalDemosPanel } from './components/EducationalDemosPanel';
import { BenchmarkingPanel } from './components/BenchmarkingPanel';
import { DatabaseStudioPanel } from './components/DatabaseStudioPanel';
import { GitStudioPanel } from './components/GitStudioPanel';
import { DevOpsPanel } from './components/DevOpsPanel';
import { MobilePreviewPanel } from './components/MobilePreviewPanel';
import { AIAssistantPanel } from './components/AIAssistantPanel';
import { EnvironmentInventoryModal } from './components/EnvironmentInventoryModal';
import { ProjectTemplatesModal } from './components/ProjectTemplatesModal';
import { ExtensionMarketplacePanel } from './components/ExtensionMarketplacePanel';
import { GraphicDesignPanel } from './components/GraphicDesignPanel';
import { LibreOfficeSuitePanel } from './components/LibreOfficeSuitePanel';
import { PhotoEditingPanel } from './components/PhotoEditingPanel';
import { VlcMediaPlayerPanel } from './components/VlcMediaPlayerPanel';
import { GameEnginePanel } from './components/GameEnginePanel';
import { IntegratedBrowserPanel } from './components/IntegratedBrowserPanel';
import { EditionsModal } from './components/EditionsModal';
import { AboutModal } from './components/AboutModal';
import { SubsystemsPanel } from './components/SubsystemsPanel';
import { CommandPalette, CommandPaletteAction } from './components/CommandPalette';
import { defaultSessionManager } from './services/sessionManager';

import { scanSystemEnvironment } from './services/envScanner';
import { analyzeCodeComplexity } from './services/complexityAnalyzer';
import { evaluateCodeQuality } from './services/codeQualityAnalyzer';
import { executeVaishnaviOrchestration, CompilerDiagnostic } from './services/vaishnaviEngine';
import { defaultTerminalBridge } from './services/terminalBridge';
import { defaultDebuggerEngine } from './services/debuggerEngine';
import { DEMO_PROJECTS, DemoProject } from './services/demoProjects';
import { IDEEdition } from './services/editionsEngine';
import { FileItem, EditorTab, SupportedLanguage } from './types';
import { Play, Bug, Search, Terminal as TerminalIcon, Sparkles, FolderOpen, Moon } from 'lucide-react';

export function App() {
  // Software Edition & Theme state
  const [currentEdition, setCurrentEdition] = useState<IDEEdition>('ultimate');
  const [isEditionsOpen, setIsEditionsOpen] = useState<boolean>(false);
  const [isAboutOpen, setIsAboutOpen] = useState<boolean>(false);
  const [currentTheme, setCurrentTheme] = useState<string>('dark');
  const [isPaletteOpen, setIsPaletteOpen] = useState<boolean>(false);

  // Build & Compiler Configuration State
  const [buildConfig, setBuildConfig] = useState<'Debug' | 'Release'>('Debug');
  const [selectedCompiler, setSelectedCompiler] = useState<string>('g++');

  // System inventory state
  const [inventory] = useState(() => scanSystemEnvironment());
  const [isInventoryOpen, setIsInventoryOpen] = useState(false);
  const [isTemplatesOpen, setIsTemplatesOpen] = useState(false);

  // Active view & drawer state
  const [activeView, setActiveView] = useState<string>('editor');
  const [activeDrawer, setActiveDrawer] = useState<string>('explorer');
  const [isAiOpen, setIsAiOpen] = useState<boolean>(true);

  // Diagnostics state
  const [diagnostics, setDiagnostics] = useState<CompilerDiagnostic[]>([]);
  const [compilerOutputMsg, setCompilerOutputMsg] = useState<string>('');

  // Default workspace files
  const [files, setFiles] = useState<FileItem[]>(() => DEMO_PROJECTS[0].files);

  // Editor tabs state
  const [tabs, setTabs] = useState<EditorTab[]>(() => [
    {
      id: 'tab-cpp-main',
      fileId: 'cpp-1',
      title: 'main.cpp',
      path: '/cpp-algo-project/main.cpp',
      content: DEMO_PROJECTS[0].files[0].content || '',
      language: 'cpp',
      isDirty: false
    }
  ]);
  const [activeTabId, setActiveTabId] = useState<string>('tab-cpp-main');

  // Terminal state
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    'MEDHĀ IDE v1.0.0 (메ध IDE) Autonomous Offline AI Engine initialized.',
    'Created by: Kanak Prabhakar | Primary Lead: Kanak Prabhakar (Conceived 2022)',
    'Software Edition: Ultimate Complete Offline Bundle (9.2 GB capability)',
    'Workspace isolated to /home/kanak/Desktop/ide',
    'Hardware detected: Linux x86_64 | 8 CPU Cores | GCC 15.2 | Python 3.14 | Node.js v22',
    'System ready. Knowledge -> Intelligence -> Creation'
  ]);

  // Current active tab object
  const activeTab = useMemo(() => tabs.find(t => t.id === activeTabId), [tabs, activeTabId]);

  // Real-time Static Analysis & Complexity computation
  const complexityResult = useMemo(() => {
    if (!activeTab) return analyzeCodeComplexity('', 'typescript');
    return analyzeCodeComplexity(activeTab.content, activeTab.language);
  }, [activeTab?.content, activeTab?.language]);

  // Real-time Code Quality Audit computation
  const qualityResult = useMemo(() => {
    if (!activeTab) return evaluateCodeQuality('', 'typescript');
    return evaluateCodeQuality(activeTab.content, activeTab.language);
  }, [activeTab?.content, activeTab?.language]);

  // Code Change Handler
  const handleCodeChange = (tabId: string, newContent: string) => {
    setTabs(prev => prev.map(tab => tab.id === tabId ? { ...tab, content: newContent, isDirty: true } : tab));
  };

  // Select file from Explorer
  const handleSelectFile = (file: FileItem) => {
    if (file.type === 'directory') return;
    const existingTab = tabs.find(t => t.fileId === file.id);
    if (existingTab) {
      setActiveTabId(existingTab.id);
    } else {
      const newTab: EditorTab = {
        id: `tab-${file.id}`,
        fileId: file.id,
        title: file.name,
        path: file.path,
        content: file.content || '',
        language: file.language || 'typescript',
        isDirty: false
      };
      setTabs(prev => [...prev, newTab]);
      setActiveTabId(newTab.id);
    }
    setActiveView('editor');
  };

  // Create new file
  const handleCreateFile = (name: string, language: SupportedLanguage) => {
    const newFile: FileItem = {
      id: `file-${Date.now()}`,
      name,
      path: `/${name}`,
      type: 'file',
      language,
      content: language === 'python' ? `# New Python script\ndef main():\n    print("Hello from MEDHĀ-IDE")\n\nif __name__ == "__main__":\n    main()` :
               language === 'cpp' ? `// New C++ source\n#include <iostream>\n\nint main() {\n    std::cout << "Hello C++" << std::endl;\n    return 0;\n}` :
               `// New TypeScript file\nexport function run() {\n  console.log("Hello from MEDHĀ-IDE");\n}`
    };

    setFiles(prev => [...prev, newFile]);
    handleSelectFile(newFile);
  };

  // Close tab
  const handleCloseTab = (tabId: string) => {
    const updated = tabs.filter(t => t.id !== tabId);
    setTabs(updated);
    if (activeTabId === tabId && updated.length > 0) {
      setActiveTabId(updated[updated.length - 1].id);
    }
  };

  // Load Demo Project Template
  const handleLoadDemoProject = (project: DemoProject) => {
    setFiles(project.files);
    const newTabs: EditorTab[] = project.files.map(f => ({
      id: `tab-${f.id}`,
      fileId: f.id,
      title: f.name,
      path: f.path,
      content: f.content || '',
      language: f.language || 'typescript',
      isDirty: false
    }));
    setTabs(newTabs);
    if (newTabs.length > 0) {
      setActiveTabId(newTabs[0].id);
    }
    setActiveView('editor');
    setTerminalLogs(prev => [...prev, `Loaded template project: ${project.name}`]);
  };

  // Run Code Command Execution (VAISHNAVĪ Engine Pipeline)
  const handleRunCode = async () => {
    if (!activeTab) return;
    setTerminalLogs(prev => [...prev, `[VAISHNAVĪ ENGINE] Orchestrating compilation & execution of ${activeTab.title} (${activeTab.language.toUpperCase()})...`]);

    const res = await executeVaishnaviOrchestration(
      activeTab.content,
      activeTab.language,
      activeTab.title
    );

    setDiagnostics(res.diagnostics);
    setCompilerOutputMsg(res.compilerOutput);

    const logs: string[] = [
      `[${res.toolchain.compilerName}] Status: ${res.toolchain.status} (${res.toolchain.version})`,
      res.compilerOutput
    ];

    if (res.stdout) {
      logs.push(`--- STDOUT Output ---`);
      logs.push(res.stdout);
    }

    if (res.stderr) {
      logs.push(`--- STDERR Error Log ---`);
      logs.push(res.stderr);
    }

    logs.push(`Program execution completed with exit code ${res.exitCode} (${res.executionTimeMs} ms).`);
    setTerminalLogs(prev => [...prev, ...logs]);
  };

  // Execute manual Terminal Command
  const handleExecuteCommand = async (cmd: string) => {
    const termRes = await defaultTerminalBridge.executeCommand(
      cmd,
      activeTab?.content,
      activeTab?.language || 'typescript',
      activeTab?.title || 'main'
    );
    setTerminalLogs(prev => [...prev, `kanak@medha-ide:~/Desktop/ide$ ${cmd}`, ...termRes.output]);
  };

  // Select Diagnostic Item & Jump to Line
  const handleSelectDiagnostic = (file: string, line: number, column: number) => {
    if (!activeTab) return;
    setTabs(prev => prev.map(tab => tab.id === activeTab.id ? { ...tab, cursorLine: line, cursorColumn: column } : tab));
  };

  // Dynamic Theme CSS class helper
  const themeCssClass = 
    currentTheme === 'light' ? 'bg-slate-100 text-slate-900' :
    currentTheme === 'high-contrast' ? 'bg-black text-white' :
    currentTheme === 'cyberpunk' ? 'bg-[#090014] text-fuchsia-100' :
    currentTheme === 'solarized' ? 'bg-[#002b36] text-[#839496]' :
    'bg-[#090d16] text-[#e2e8f0]';

  return (
    <div className={`flex flex-col h-screen w-screen overflow-hidden select-none ${themeCssClass}`}>
      {/* Top Application Desktop Ribbon Menu */}
      <TopMenuBar
        currentEdition={currentEdition}
        onOpenEditionsModal={() => setIsEditionsOpen(true)}
        onOpenAbout={() => setIsAboutOpen(true)}
        onOpenInventory={() => setIsInventoryOpen(true)}
        onOpenTemplates={() => setIsTemplatesOpen(true)}
        onRunCode={handleRunCode}
        onStartDebug={() => {
          if (activeTab) {
            defaultDebuggerEngine.startDebugging(activeTab.title, activeTab.language);
            setActiveDrawer('debugger');
          }
        }}
        buildConfig={buildConfig}
        setBuildConfig={setBuildConfig}
        selectedCompiler={selectedCompiler}
        setSelectedCompiler={setSelectedCompiler}
        inventory={inventory}
        isAiOpen={isAiOpen}
        setIsAiOpen={setIsAiOpen}
        setActiveDrawer={setActiveDrawer}
        setActiveView={setActiveView}
      />

      {/* Primary IDE Header Navbar */}
      <HeaderNavbar
        activeView={activeView}
        setActiveView={setActiveView}
        inventory={inventory}
        onOpenInventory={() => setIsInventoryOpen(true)}
        onOpenTemplates={() => setIsTemplatesOpen(true)}
        onOpenAbout={() => setIsAboutOpen(true)}
        onRunCode={handleRunCode}
        isAiOpen={isAiOpen}
        setIsAiOpen={setIsAiOpen}
        currentEdition={currentEdition}
        onOpenEditionsModal={() => setIsEditionsOpen(true)}
        currentTheme={currentTheme}
        onChangeTheme={setCurrentTheme}
      />

      {/* Main Workspace Layout Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Vertical Icon Launcher Sidebar */}
        <Sidebar
          activeDrawer={activeDrawer}
          setActiveDrawer={(drawer) => {
            setActiveDrawer(drawer);
            if (drawer === 'extensions') {
              setActiveView('extensions');
            } else if (activeView === 'extensions' && drawer !== 'extensions') {
              setActiveView('editor');
            }
          }}
        />

        {/* Dynamic Secondary Drawers */}
        {activeDrawer === 'explorer' && activeView !== 'extensions' && (
          <FileExplorer
            files={files}
            onSelectFile={handleSelectFile}
            activeFileId={activeTab?.fileId}
            onCreateFile={handleCreateFile}
          />
        )}

        {activeDrawer === 'search' && (
          <SearchPanel
            files={files}
            onSelectFileMatch={(file, line) => {
              handleSelectFile(file);
              if (activeTab) handleSelectDiagnostic(file.name, line, 1);
            }}
          />
        )}

        {activeDrawer === 'debugger' && (
          <DebuggerPanel
            activeFile={activeTab?.title}
            activeLanguage={activeTab?.language}
            onSelectLine={(line) => {
              if (activeTab) handleSelectDiagnostic(activeTab.title, line, 1);
            }}
          />
        )}

        {/* Center Main View Area */}
        <div className="flex-1 flex flex-col overflow-hidden bg-[#090d16]/80">
          {activeView === 'editor' && (
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="flex-1 flex overflow-hidden">
                <CodeEditorPanel
                  tabs={tabs}
                  activeTabId={activeTabId}
                  onSelectTab={setActiveTabId}
                  onCloseTab={handleCloseTab}
                  onCodeChange={handleCodeChange}
                  onOptimizeCode={() => setIsAiOpen(true)}
                  onExplainCode={() => setIsAiOpen(true)}
                  onSecurityAudit={() => setIsAiOpen(true)}
                />

                {/* Right Dockable Panel: Complexity Engine & Quality Audit */}
                <div className="flex">
                  <ComplexityPanel complexity={complexityResult} />
                  <QualityScorePanel
                    quality={qualityResult}
                    onApplyOptimization={(optCode) => {
                      if (activeTab) handleCodeChange(activeTab.id, optCode);
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {activeView === 'learning' && <EducationalDemosPanel />}
          {activeView === 'benchmark' && <BenchmarkingPanel />}
          {activeView === 'database' && <DatabaseStudioPanel />}
          {(activeView === 'office' || activeDrawer === 'office') && <LibreOfficeSuitePanel />}
          {(activeView === 'graphic' || activeDrawer === 'graphic') && <GraphicDesignPanel />}
          {(activeView === 'photo' || activeDrawer === 'photo') && <PhotoEditingPanel />}
          {(activeView === 'media' || activeDrawer === 'media') && <VlcMediaPlayerPanel />}
          {(activeView === 'game' || activeDrawer === 'game') && <GameEnginePanel />}
          {(activeView === 'browser' || activeDrawer === 'browser') && <IntegratedBrowserPanel />}
          {activeView === 'git' && <GitStudioPanel />}
          {activeView === 'devops' && <DevOpsPanel />}
          {activeView === 'mobile' && <MobilePreviewPanel />}
          {activeView === 'extensions' && <ExtensionMarketplacePanel />}
          {(activeView === 'subsystems' || activeDrawer === 'subsystems') && <SubsystemsPanel />}

          {/* Bottom Dock Container: Terminal, Problems, Build Output, Debug Console, Test Runner */}
          <BottomDockPanel
            logs={terminalLogs}
            onClearLogs={() => setTerminalLogs([])}
            onExecuteCommand={handleExecuteCommand}
            diagnostics={diagnostics}
            onSelectDiagnostic={handleSelectDiagnostic}
            compilerOutputMsg={compilerOutputMsg}
            toolchainStatus={activeTab ? activeTab.language.toUpperCase() : undefined}
          />
        </div>

        {/* Right AI Assistant Drawer Panel */}
        {isAiOpen && (
          <AIAssistantPanel
            activeCode={activeTab?.content}
            activeLanguage={activeTab?.language}
            onApplySnippet={(snippetCode) => {
              if (activeTab) handleCodeChange(activeTab.id, snippetCode);
            }}
          />
        )}
      </div>

      {/* Modals */}
      {isInventoryOpen && (
        <EnvironmentInventoryModal
          inventory={inventory}
          onClose={() => setIsInventoryOpen(false)}
        />
      )}

      {isTemplatesOpen && (
        <ProjectTemplatesModal
          onLoadProject={handleLoadDemoProject}
          onClose={() => setIsTemplatesOpen(false)}
        />
      )}

      <EditionsModal
        isOpen={isEditionsOpen}
        onClose={() => setIsEditionsOpen(false)}
        currentEdition={currentEdition}
        onSelectEdition={(ed) => {
          setCurrentEdition(ed);
          setTerminalLogs(prev => [...prev, `Switched IDE Edition to: ${ed.toUpperCase()}`]);
        }}
      />

      <AboutModal
        isOpen={isAboutOpen}
        onClose={() => setIsAboutOpen(false)}
      />

      <CommandPalette
        isOpen={isPaletteOpen}
        onClose={() => setIsPaletteOpen(false)}
        actions={[
          {
            id: 'cmd-run',
            title: 'Run Project (VAISHNAVĪ Toolchain)',
            category: 'Build & Execution',
            shortcut: 'Ctrl+F5',
            icon: <Play className="w-4 h-4" />,
            perform: handleRunCode
          },
          {
            id: 'cmd-debug',
            title: 'Start Debugging (GDB / LLDB)',
            category: 'Debugger',
            shortcut: 'F5',
            icon: <Bug className="w-4 h-4" />,
            perform: () => {
              if (activeTab) {
                defaultDebuggerEngine.startDebugging(activeTab.title, activeTab.language);
                setActiveDrawer('debugger');
              }
            }
          },
          {
            id: 'cmd-search',
            title: 'Search in Workspace Files',
            category: 'Search & Replace',
            shortcut: 'Ctrl+Shift+F',
            icon: <Search className="w-4 h-4" />,
            perform: () => setActiveDrawer('search')
          },
          {
            id: 'cmd-ai',
            title: 'Toggle AI Assistant Panel',
            category: 'AI Subsystems',
            icon: <Sparkles className="w-4 h-4" />,
            perform: () => setIsAiOpen(!isAiOpen)
          },
          {
            id: 'cmd-templates',
            title: 'Open Starter Project Templates',
            category: 'Project Explorer',
            shortcut: 'Ctrl+N',
            icon: <FolderOpen className="w-4 h-4" />,
            perform: () => setIsTemplatesOpen(true)
          }
        ]}
      />
    </div>
  );
}
