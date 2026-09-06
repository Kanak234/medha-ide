import React, { useState } from 'react';
import { Package, Search, CheckCircle, Download, Shield, Info, Star } from 'lucide-react';
import { extensionEngine, IDEExtension } from '../services/extensionEngine';

export const ExtensionMarketplacePanel: React.FC = () => {
  const [extensions, setExtensions] = useState<IDEExtension[]>(extensionEngine.getAllExtensions());
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedExtension, setSelectedExtension] = useState<IDEExtension | null>(extensions[0] || null);

  const handleSearch = (q: string) => {
    setSearchQuery(q);
    setExtensions(extensionEngine.searchExtensions(q));
  };

  const toggleInstall = (id: string, currentlyInstalled: boolean) => {
    if (currentlyInstalled) {
      extensionEngine.uninstallExtension(id);
    } else {
      extensionEngine.installExtension(id);
    }
    const updated = extensionEngine.getAllExtensions();
    setExtensions(updated);
    if (selectedExtension?.id === id) {
      const refreshed = updated.find(e => e.id === id) || null;
      setSelectedExtension(refreshed);
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0f172a]/90 text-slate-200">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
        <div className="flex items-center gap-2">
          <Package className="w-5 h-5 text-indigo-400" />
          <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider">Extension Marketplace & Plugins</h2>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
          Offline Verified Plugins
        </span>
      </div>

      {/* Content split */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Extension List */}
        <div className="w-1/2 border-r border-slate-800 flex flex-col">
          <div className="p-3 border-b border-slate-800">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search extensions, tools, linters..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-md text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-slate-800/60">
            {extensions.map(ext => (
              <div
                key={ext.id}
                onClick={() => setSelectedExtension(ext)}
                className={`p-3 cursor-pointer transition-colors flex items-start gap-3 ${
                  selectedExtension?.id === ext.id ? 'bg-indigo-600/15 border-l-2 border-indigo-500' : 'hover:bg-slate-800/40'
                }`}
              >
                <div className="text-2xl p-1 bg-slate-900 rounded border border-slate-800">{ext.icon}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-medium text-slate-100 truncate">{ext.name}</h3>
                    {ext.installed && (
                      <span className="text-[10px] text-emerald-400 flex items-center gap-1 font-mono">
                        <CheckCircle className="w-3 h-3" /> Installed
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400 truncate mt-0.5">{ext.description}</p>
                  <div className="flex items-center gap-3 text-[10px] text-slate-500 mt-1">
                    <span>{ext.publisher}</span>
                    <span>v{ext.version}</span>
                    <span className="flex items-center gap-0.5 text-amber-400"><Star className="w-2.5 h-2.5 fill-current" /> {ext.rating}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Selected Extension Detail */}
        <div className="w-1/2 p-4 overflow-y-auto bg-slate-900/30">
          {selectedExtension ? (
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="text-4xl p-2 bg-slate-900 border border-slate-800 rounded-lg">{selectedExtension.icon}</div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-slate-100">{selectedExtension.name}</h3>
                  <p className="text-xs text-slate-400 mt-0.5">Publisher: <span className="text-indigo-400">{selectedExtension.publisher}</span></p>
                  <div className="flex items-center gap-2 mt-2">
                    <button
                      onClick={() => toggleInstall(selectedExtension.id, selectedExtension.installed)}
                      className={`px-3 py-1 text-xs font-medium rounded border transition-all flex items-center gap-1.5 ${
                        selectedExtension.installed
                          ? 'bg-rose-500/10 text-rose-400 border-rose-500/30 hover:bg-rose-500/20'
                          : 'bg-indigo-600 text-white border-indigo-500 hover:bg-indigo-500'
                      }`}
                    >
                      {selectedExtension.installed ? (
                        <>Uninstall Extension</>
                      ) : (
                        <><Download className="w-3.5 h-3.5" /> Install (Offline Bundle)</>
                      )}
                    </button>
                    <span className="text-xs text-slate-400 flex items-center gap-1">
                      <Download className="w-3 h-3" /> {selectedExtension.downloads.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              <div className="border-t border-slate-800 pt-3">
                <h4 className="text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1">
                  <Info className="w-3.5 h-3.5 text-indigo-400" /> Overview
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-2.5 rounded border border-slate-800/80">
                  {selectedExtension.description}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-slate-950/60 p-2 rounded border border-slate-800/80">
                  <span className="text-slate-400 block text-[10px]">License</span>
                  <span className="font-mono text-slate-200">{selectedExtension.license}</span>
                </div>
                <div className="bg-slate-950/60 p-2 rounded border border-slate-800/80">
                  <span className="text-slate-400 block text-[10px]">Category</span>
                  <span className="text-slate-200">{selectedExtension.category}</span>
                </div>
              </div>

              <div className="border-t border-slate-800 pt-3">
                <h4 className="text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1">
                  <Shield className="w-3.5 h-3.5 text-emerald-400" /> Security & Declared Permissions
                </h4>
                {selectedExtension.permissions.length > 0 ? (
                  <ul className="space-y-1">
                    {selectedExtension.permissions.map((perm, i) => (
                      <li key={i} className="text-[11px] font-mono text-emerald-300 bg-emerald-950/20 px-2 py-0.5 rounded border border-emerald-800/40">
                        ✓ {perm}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400 italic">No special system permissions requested.</p>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-500 text-xs">
              Select an extension to inspect details and permissions.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
