import React, { useState } from 'react';
import { Smartphone, Monitor, RotateCw, Download, Play, Shield } from 'lucide-react';

export const MobilePreviewPanel: React.FC = () => {
  const [device, setDevice] = useState<'android' | 'ios' | 'desktop'>('android');
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>('portrait');

  return (
    <div className="flex-1 bg-[#090d16] flex flex-col h-full overflow-hidden select-none p-4 items-center justify-between">
      {/* Device Toolbar */}
      <div className="w-full bg-[#0f172a] p-3 rounded-xl border border-[#1e293b] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Smartphone className="w-4 h-4 text-rose-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">Mobile & Web Live Device Simulator</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setDevice('android')}
            className={`px-3 py-1 rounded text-xs font-semibold ${device === 'android' ? 'bg-rose-600 text-white' : 'bg-[#1e293b] text-[#94a3b8]'}`}
          >
            Android (Pixel 8)
          </button>
          <button
            onClick={() => setDevice('ios')}
            className={`px-3 py-1 rounded text-xs font-semibold ${device === 'ios' ? 'bg-rose-600 text-white' : 'bg-[#1e293b] text-[#94a3b8]'}`}
          >
            iOS (iPhone 15 Pro)
          </button>
          <button
            onClick={() => setDevice('desktop')}
            className={`px-3 py-1 rounded text-xs font-semibold ${device === 'desktop' ? 'bg-rose-600 text-white' : 'bg-[#1e293b] text-[#94a3b8]'}`}
          >
            Responsive Web
          </button>

          <button
            onClick={() => setOrientation(orientation === 'portrait' ? 'landscape' : 'portrait')}
            className="p-1.5 bg-[#1e293b] text-[#94a3b8] hover:text-white rounded"
            title="Rotate Screen Orientation"
          >
            <RotateCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Device Display Frame */}
      <div className={`my-auto bg-[#0f172a] border-4 border-[#334155] rounded-3xl overflow-hidden shadow-2xl transition-all flex flex-col ${
        device === 'desktop' ? 'w-full max-w-3xl h-[420px]' :
        orientation === 'portrait' ? 'w-[320px] h-[540px]' : 'w-[540px] h-[320px]'
      }`}>
        {/* Device Notch / Bar */}
        <div className="h-6 bg-[#1e293b] flex items-center justify-center">
          <div className="w-16 h-2 bg-[#334155] rounded-full"></div>
        </div>

        {/* Device Content Frame */}
        <div className="flex-1 bg-[#090d16] p-4 text-center flex flex-col items-center justify-center space-y-3">
          <Smartphone className="w-12 h-12 text-rose-500/40 animate-pulse" />
          <h3 className="text-sm font-bold text-white">Flutter / React Native Mobile Application Running</h3>
          <p className="text-xs text-[#94a3b8] max-w-xs">
            Hot Reload Active. Executing inside local Android APK simulation sandbox.
          </p>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-mono">
              60 FPS | Debug Mode
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
