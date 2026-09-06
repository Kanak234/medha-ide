import React, { useState, useRef } from 'react';
import { 
  Globe, 
  ArrowLeft, 
  ArrowRight, 
  RotateCw, 
  Lock, 
  Plus, 
  X, 
  Smartphone, 
  Tablet, 
  Monitor, 
  Terminal, 
  Activity, 
  Database, 
  Code2, 
  Camera, 
  Sparkles, 
  ShieldAlert, 
  Wifi, 
  WifiOff, 
  Laptop
} from 'lucide-react';
import { 
  DEFAULT_BROWSER_TABS, 
  DEVICE_VIEWPORT_MAP, 
  INITIAL_CONSOLE_LOGS, 
  INITIAL_NETWORK_LOGS, 
  INITIAL_STORAGE_ITEMS,
  detectLocalDevServers
} from '../services/browserEngine';
import { detectNetworkStatus, validateSecurityOrigin } from '../services/networkEngine';
import { BrowserTabItem, BrowserConsoleEntry, BrowserNetworkEntry, BrowserStorageEntry, DeviceViewportMode } from '../types';

interface IntegratedBrowserPanelProps {
  onSendErrorToAi?: (errorMsg: string) => void;
}

export const IntegratedBrowserPanel: React.FC<IntegratedBrowserPanelProps> = ({ onSendErrorToAi }) => {
  // Tabs & Navigation State
  const [tabs, setTabs] = useState<BrowserTabItem[]>(DEFAULT_BROWSER_TABS);
  const [activeTabId, setActiveTabId] = useState<string>('tab-local-dev');
  const [urlInput, setUrlInput] = useState<string>('http://localhost:5173/');

  // Viewport & DevTools State
  const [viewportMode, setViewportMode] = useState<DeviceViewportMode>('desktop');
  const [activeDevTool, setActiveDevTool] = useState<'console' | 'elements' | 'network' | 'storage'>('console');
  const [consoleLogs, setConsoleLogs] = useState<BrowserConsoleEntry[]>(INITIAL_CONSOLE_LOGS);
  const [networkLogs] = useState<BrowserNetworkEntry[]>(INITIAL_NETWORK_LOGS);
  const [storageItems] = useState<BrowserStorageEntry[]>(INITIAL_STORAGE_ITEMS);
  const [consoleInput, setConsoleInput] = useState<string>('');

  // Network Engine State
  const networkState = detectNetworkStatus();
  const activeTab = tabs.find(t => t.id === activeTabId) || tabs[0];
  const securityInfo = validateSecurityOrigin(activeTab.url);
  const viewportSpec = DEVICE_VIEWPORT_MAP[viewportMode];

  // Navigate URL
  const handleNavigate = (targetUrl: string) => {
    let formatted = targetUrl.trim();
    if (!formatted.startsWith('http://') && !formatted.startsWith('https://')) {
      formatted = `http://${formatted}`;
    }

    setUrlInput(formatted);
    setTabs(tabs.map(t => {
      if (t.id === activeTabId) {
        const newHistory = [...t.history.slice(0, t.historyIndex + 1), formatted];
        return {
          ...t,
          url: formatted,
          title: formatted.replace('http://', '').replace('https://', ''),
          history: newHistory,
          historyIndex: newHistory.length - 1,
          canGoBack: newHistory.length > 1
        };
      }
      return t;
    }));
  };

  // Tab Controls
  const handleAddTab = () => {
    const newId = `tab-${Date.now()}`;
    const newTab: BrowserTabItem = {
      id: newId,
      title: 'New Tab',
      url: 'http://localhost:5173/',
      isLoading: false,
      canGoBack: false,
      canGoForward: false,
      favicon: '🌐',
      isSecure: true,
      history: ['http://localhost:5173/'],
      historyIndex: 0
    };
    setTabs([...tabs, newTab]);
    setActiveTabId(newId);
    setUrlInput('http://localhost:5173/');
  };

  const handleCloseTab = (tabId: string) => {
    const updated = tabs.filter(t => t.id !== tabId);
    if (updated.length > 0) {
      setTabs(updated);
      if (activeTabId === tabId) {
        setActiveTabId(updated[updated.length - 1].id);
        setUrlInput(updated[updated.length - 1].url);
      }
    }
  };

  // Console Commands
  const handleRunConsoleCommand = () => {
    if (!consoleInput.trim()) return;
    const newEntry: BrowserConsoleEntry = {
      id: `c-${Date.now()}`,
      type: 'log',
      message: `> ${consoleInput}`,
      timestamp: new Date().toLocaleTimeString(),
      sourceFile: 'REPL'
    };
    let evalOutput: BrowserConsoleEntry;
    try {
      evalOutput = {
        id: `c-${Date.now() + 1}`,
        type: 'info',
        message: `< undefined`,
        timestamp: new Date().toLocaleTimeString(),
        sourceFile: 'REPL'
      };
    } catch (err: any) {
      evalOutput = {
        id: `c-${Date.now() + 1}`,
        type: 'error',
        message: `Uncaught Error: ${err.message}`,
        timestamp: new Date().toLocaleTimeString(),
        sourceFile: 'REPL'
      };
    }
    setConsoleLogs(prev => [...prev, newEntry, evalOutput]);
    setConsoleInput('');
  };

  return (
    <div className="flex-1 bg-[#090d16] flex flex-col h-full overflow-hidden select-none">
      {/* 1. TOP BROWSER TAB BAR */}
      <div className="h-10 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between px-2 overflow-x-auto select-none">
        <div className="flex items-center gap-1">
          {tabs.map((tab) => {
            const isActive = tab.id === activeTabId;
            return (
              <div
                key={tab.id}
                onClick={() => {
                  setActiveTabId(tab.id);
                  setUrlInput(tab.url);
                }}
                className={`flex items-center gap-2 px-3 py-1 text-xs rounded-t-lg cursor-pointer border-t-2 transition-all ${
                  isActive
                    ? 'bg-[#090d16] text-cyan-300 border-cyan-400 font-medium shadow-sm'
                    : 'text-[#64748b] border-transparent hover:text-[#e2e8f0] hover:bg-[#1e293b]/40'
                }`}
              >
                <span>{tab.favicon || '🌐'}</span>
                <span className="max-w-[140px] truncate">{tab.title}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleCloseTab(tab.id);
                  }}
                  className="hover:text-rose-400 p-0.5 rounded text-slate-500"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            );
          })}

          <button
            onClick={handleAddTab}
            className="p-1 text-slate-400 hover:text-white hover:bg-[#1e293b] rounded transition-colors"
            title="New Browser Tab"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>

        {/* Network Connectivity Status Badge */}
        <div className="flex items-center gap-2">
          <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-bold border ${
            networkState.status === 'online'
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
          }`}>
            {networkState.status === 'online' ? <Wifi className="w-3 h-3 text-emerald-400" /> : <WifiOff className="w-3 h-3 text-rose-400" />}
            <span>{networkState.status === 'online' ? 'Online' : 'Offline Mode'}</span>
          </div>
        </div>
      </div>

      {/* 2. BROWSER NAVIGATION BAR & URL INPUT */}
      <div className="h-11 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between px-3 gap-2">
        <div className="flex items-center gap-1">
          <button className="p-1.5 text-slate-400 hover:text-white hover:bg-[#1e293b] rounded" title="Back">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <button className="p-1.5 text-slate-400 hover:text-white hover:bg-[#1e293b] rounded" title="Forward">
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleNavigate(activeTab.url)}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-[#1e293b] rounded"
            title="Reload"
          >
            <RotateCw className="w-4 h-4" />
          </button>
        </div>

        {/* URL Address Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleNavigate(urlInput);
          }}
          className="flex-1 max-w-2xl flex items-center gap-2 bg-[#090d16] border border-[#334155] rounded-lg px-3 py-1 text-xs text-white"
        >
          {securityInfo.isSecure ? (
            <span title="Secure Encrypted Origin"><Lock className="w-3.5 h-3.5 text-emerald-400 shrink-0" /></span>
          ) : (
            <span title="Unencrypted Plaintext HTTP"><ShieldAlert className="w-3.5 h-3.5 text-amber-400 shrink-0" /></span>
          )}

          <input
            type="text"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            className="flex-1 bg-transparent font-mono text-xs text-cyan-200 focus:outline-none"
            placeholder="Enter URL (e.g. http://localhost:5173/)"
          />
        </form>

        {/* Viewport Device Emulation Controls */}
        <div className="flex items-center gap-1 bg-[#1e293b] p-0.5 rounded-lg border border-[#334155]">
          <button
            onClick={() => setViewportMode('desktop')}
            className={`p-1.5 rounded transition-all ${viewportMode === 'desktop' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            title="Desktop (1920x1080)"
          >
            <Monitor className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setViewportMode('laptop')}
            className={`p-1.5 rounded transition-all ${viewportMode === 'laptop' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            title="Laptop (1366x768)"
          >
            <Laptop className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setViewportMode('tablet')}
            className={`p-1.5 rounded transition-all ${viewportMode === 'tablet' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            title="Tablet (768x1024)"
          >
            <Tablet className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setViewportMode('mobile_iphone')}
            className={`p-1.5 rounded transition-all ${viewportMode === 'mobile_iphone' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            title="Mobile (375x812)"
          >
            <Smartphone className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 3. MAIN WEB VIEWPORT STAGE */}
      <div className="flex-1 bg-[#060911] flex flex-col items-center justify-center p-4 overflow-hidden relative">
        <div
          style={{
            width: viewportMode === 'desktop' ? '100%' : `${viewportSpec.width}px`,
            height: viewportMode === 'desktop' ? '100%' : `${viewportSpec.height}px`,
            maxHeight: '100%'
          }}
          className="bg-[#0f172a] rounded-xl border border-[#334155] shadow-2xl overflow-hidden flex flex-col transition-all duration-300 relative"
        >
          {/* Web App Preview Render Container */}
          {activeTab.url.includes('localhost:5173') ? (
            <div className="flex-1 p-6 flex flex-col items-center justify-center text-center bg-[#090d16] text-[#e2e8f0]">
              <div className="w-16 h-16 rounded-2xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center mb-4">
                <Globe className="w-8 h-8 text-cyan-400 animate-pulse" />
              </div>
              <h2 className="text-xl font-bold text-white mb-1">MEDHĀ Localhost Development App</h2>
              <p className="text-xs text-slate-400 max-w-md mb-4">
                Running live on <code className="text-cyan-300 font-mono">http://localhost:5173/</code> with HMR Hot Module Reload & React 19 fast refresh.
              </p>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-[11px] font-bold border border-emerald-500/30">
                  HTTP 200 OK
                </span>
                <span className="px-2.5 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-[11px] font-bold border border-indigo-500/30">
                  Viewport: {viewportSpec.name}
                </span>
              </div>
            </div>
          ) : (
            <iframe
              src={activeTab.url}
              title={activeTab.title}
              className="w-full h-full border-none bg-white"
            />
          )}
        </div>
      </div>

      {/* 4. DEVELOPER TOOLS DOCKER (BOTTOM PANEL) */}
      <div className="h-44 bg-[#0f172a] border-t border-[#1e293b] flex flex-col overflow-hidden">
        {/* DevTools Tab Bar */}
        <div className="h-8 bg-[#0d1322] border-b border-[#1e293b] flex items-center justify-between px-3 select-none">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setActiveDevTool('console')}
              className={`px-3 py-1 text-xs font-semibold rounded-t-md flex items-center gap-1.5 transition-all ${
                activeDevTool === 'console' ? 'bg-[#0f172a] text-cyan-300 border-t-2 border-cyan-400' : 'text-[#64748b] hover:text-white'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" /> Console ({consoleLogs.length})
            </button>
            <button
              onClick={() => setActiveDevTool('elements')}
              className={`px-3 py-1 text-xs font-semibold rounded-t-md flex items-center gap-1.5 transition-all ${
                activeDevTool === 'elements' ? 'bg-[#0f172a] text-cyan-300 border-t-2 border-cyan-400' : 'text-[#64748b] hover:text-white'
              }`}
            >
              <Code2 className="w-3.5 h-3.5" /> Elements DOM
            </button>
            <button
              onClick={() => setActiveDevTool('network')}
              className={`px-3 py-1 text-xs font-semibold rounded-t-md flex items-center gap-1.5 transition-all ${
                activeDevTool === 'network' ? 'bg-[#0f172a] text-cyan-300 border-t-2 border-cyan-400' : 'text-[#64748b] hover:text-white'
              }`}
            >
              <Activity className="w-3.5 h-3.5" /> Network ({networkLogs.length})
            </button>
            <button
              onClick={() => setActiveDevTool('storage')}
              className={`px-3 py-1 text-xs font-semibold rounded-t-md flex items-center gap-1.5 transition-all ${
                activeDevTool === 'storage' ? 'bg-[#0f172a] text-cyan-300 border-t-2 border-cyan-400' : 'text-[#64748b] hover:text-white'
              }`}
            >
              <Database className="w-3.5 h-3.5" /> Application Storage
            </button>
          </div>
        </div>

        {/* DevTools Tab Content */}
        <div className="flex-1 p-2 font-mono text-xs overflow-y-auto bg-[#090d16]">
          {/* Console Tab */}
          {activeDevTool === 'console' && (
            <div className="flex flex-col h-full">
              <div className="flex-1 space-y-1 overflow-y-auto">
                {consoleLogs.map((log) => (
                  <div key={log.id} className="flex items-center justify-between text-[11px] hover:bg-[#1e293b]/40 px-2 py-0.5 rounded">
                    <div className="flex items-center gap-2 truncate">
                      <span className="text-[#64748b]">{log.timestamp}</span>
                      <span className={`font-semibold ${
                        log.type === 'error' ? 'text-rose-400' : (log.type === 'warn' ? 'text-amber-300' : 'text-slate-200')
                      }`}>
                        {log.message}
                      </span>
                    </div>

                    {log.type === 'error' && onSendErrorToAi && (
                      <button
                        onClick={() => onSendErrorToAi(log.message)}
                        className="px-2 py-0.5 bg-purple-950/80 hover:bg-purple-900 text-purple-300 rounded text-[10px] font-bold border border-purple-800/40 flex items-center gap-1 shrink-0"
                      >
                        <Sparkles className="w-3 h-3 text-purple-300" /> Diagnose with AI
                      </button>
                    )}
                  </div>
                ))}
              </div>

              <div className="pt-2 border-t border-[#1e293b] flex items-center gap-2">
                <span className="text-cyan-400 font-bold">&gt;</span>
                <input
                  type="text"
                  placeholder="Execute JavaScript in Browser REPL..."
                  value={consoleInput}
                  onChange={(e) => setConsoleInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleRunConsoleCommand()}
                  className="flex-1 bg-[#0f172a] border border-[#334155] rounded px-2 py-1 text-xs text-white focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* Network Tab */}
          {activeDevTool === 'network' && (
            <table className="w-full border-collapse text-[11px]">
              <thead>
                <tr className="bg-[#0f172a] text-[#64748b]">
                  <th className="p-1 text-left">Method</th>
                  <th className="p-1 text-left">URL</th>
                  <th className="p-1 text-left">Status</th>
                  <th className="p-1 text-left">Type</th>
                  <th className="p-1 text-right">Time</th>
                  <th className="p-1 text-right">Size</th>
                </tr>
              </thead>
              <tbody>
                {networkLogs.map((req) => (
                  <tr key={req.id} className="border-b border-[#1e293b]/40 hover:bg-[#1e293b]/30 text-slate-300">
                    <td className="p-1 font-bold text-cyan-400">{req.method}</td>
                    <td className="p-1 truncate max-w-xs">{req.url}</td>
                    <td className="p-1 font-bold text-emerald-400">{req.status} {req.statusText}</td>
                    <td className="p-1 text-slate-400">{req.type}</td>
                    <td className="p-1 text-right text-indigo-300">{req.durationMs} ms</td>
                    <td className="p-1 text-right text-slate-400">{(req.sizeBytes / 1024).toFixed(1)} KB</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {/* Storage Tab */}
          {activeDevTool === 'storage' && (
            <table className="w-full border-collapse text-[11px]">
              <thead>
                <tr className="bg-[#0f172a] text-[#64748b]">
                  <th className="p-1 text-left">Key</th>
                  <th className="p-1 text-left">Value</th>
                  <th className="p-1 text-left">Storage Type</th>
                </tr>
              </thead>
              <tbody>
                {storageItems.map((item, idx) => (
                  <tr key={idx} className="border-b border-[#1e293b]/40 hover:bg-[#1e293b]/30 text-slate-300">
                    <td className="p-1 font-bold text-amber-300">{item.key}</td>
                    <td className="p-1 font-mono text-slate-200">{item.value}</td>
                    <td className="p-1 text-indigo-400">{item.type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {/* DOM Elements Inspector Tab */}
          {activeDevTool === 'elements' && (
            <div className="text-[#94a3b8] space-y-1 font-mono">
              <div>&lt;<span className="text-rose-400">html</span> <span className="text-amber-300">lang</span>=<span className="text-emerald-300">"en"</span>&gt;</div>
              <div className="pl-4">&lt;<span className="text-rose-400">head</span>&gt; ... &lt;/<span className="text-rose-400">head</span>&gt;</div>
              <div className="pl-4">&lt;<span className="text-rose-400">body</span> <span className="text-amber-300">class</span>=<span className="text-emerald-300">"bg-slate-900 text-white"</span>&gt;</div>
              <div className="pl-8">&lt;<span className="text-rose-400">div</span> <span className="text-amber-300">id</span>=<span className="text-emerald-300">"root"</span>&gt;</div>
              <div className="pl-12 text-cyan-300">&lt;!-- MEDHĀ IDE Web App React 19 Root --&gt;</div>
              <div className="pl-8">&lt;/<span className="text-rose-400">div</span>&gt;</div>
              <div className="pl-4">&lt;/<span className="text-rose-400">body</span>&gt;</div>
              <div>&lt;/<span className="text-rose-400">html</span>&gt;</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
