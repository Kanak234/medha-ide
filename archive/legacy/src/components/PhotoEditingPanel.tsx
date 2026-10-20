import React, { useState } from 'react';
import { Image, Sliders, Download, RefreshCw, Sun, Contrast, Droplets, Eye, Sparkles, Layers } from 'lucide-react';
import { DEFAULT_PHOTO_FILTERS, getCssFilterString } from '../services/photoEngine';
import { PhotoFilterSettings } from '../types';

export const PhotoEditingPanel: React.FC = () => {
  const [filters, setFilters] = useState<PhotoFilterSettings>(DEFAULT_PHOTO_FILTERS);
  const [activePreset, setActivePreset] = useState<string>('normal');
  const [sampleImage, setSampleImage] = useState<string>(
    'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80'
  );

  const applyPreset = (preset: string) => {
    setActivePreset(preset);
    if (preset === 'cyberpunk') {
      setFilters({ ...DEFAULT_PHOTO_FILTERS, brightness: 110, contrast: 130, saturation: 160, hueRotate: 190 });
    } else if (preset === 'vintage') {
      setFilters({ ...DEFAULT_PHOTO_FILTERS, brightness: 90, contrast: 110, sepia: 70, grayscale: 20 });
    } else if (preset === 'noir') {
      setFilters({ ...DEFAULT_PHOTO_FILTERS, brightness: 100, contrast: 150, grayscale: 100 });
    } else if (preset === 'vivid') {
      setFilters({ ...DEFAULT_PHOTO_FILTERS, brightness: 105, contrast: 120, saturation: 180 });
    } else {
      setFilters(DEFAULT_PHOTO_FILTERS);
    }
  };

  const handleReset = () => {
    setFilters(DEFAULT_PHOTO_FILTERS);
    setActivePreset('normal');
  };

  return (
    <div className="flex-1 bg-[#090d16] flex flex-col h-full overflow-hidden select-none">
      {/* Header Toolbar */}
      <div className="h-11 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <Image className="w-5 h-5 text-[#f43f5e]" />
          <span className="font-bold text-xs uppercase tracking-wider text-white">Digital Photo & Image Processing Studio</span>
          
          <div className="flex items-center gap-1 bg-[#1e293b] p-0.5 rounded-lg border border-[#334155]">
            {['normal', 'cyberpunk', 'vivid', 'vintage', 'noir'].map((preset) => (
              <button
                key={preset}
                onClick={() => applyPreset(preset)}
                className={`px-2.5 py-1 text-[11px] font-bold capitalize rounded-md transition-all ${
                  activePreset === preset ? 'bg-[#f43f5e] text-white shadow' : 'text-[#94a3b8] hover:text-white'
                }`}
              >
                {preset}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            className="px-3 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-slate-300 rounded-lg text-xs font-bold flex items-center gap-1 border border-[#334155]"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Reset Filters
          </button>
        </div>
      </div>

      {/* Main Workspace Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Main Image Stage */}
        <div className="flex-1 bg-[#060911] flex items-center justify-center p-8 overflow-auto relative">
          <div className="relative max-w-3xl max-h-[500px] rounded-2xl overflow-hidden border-2 border-[#334155] shadow-2xl">
            <img
              src={sampleImage}
              alt="Photo Processing Canvas"
              style={{ filter: getCssFilterString(filters) }}
              className="w-full h-full object-cover transition-all duration-200"
            />
          </div>
        </div>

        {/* Right Adjustments & Controls Panel */}
        <div className="w-80 bg-[#0f172a] border-l border-[#1e293b] p-4 flex flex-col space-y-4 overflow-y-auto">
          <span className="text-xs font-bold uppercase tracking-wider text-white border-b border-[#1e293b] pb-2 flex items-center gap-1.5">
            <Sliders className="w-4 h-4 text-[#f43f5e]" /> Color & Light Adjustments
          </span>

          <div className="space-y-4 text-xs">
            <div>
              <div className="flex items-center justify-between text-slate-300 font-bold mb-1">
                <span className="flex items-center gap-1"><Sun className="w-3.5 h-3.5 text-amber-400" /> Brightness</span>
                <span className="font-mono text-amber-400">{filters.brightness}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="200"
                value={filters.brightness}
                onChange={(e) => setFilters({ ...filters, brightness: parseInt(e.target.value) })}
                className="w-full accent-[#f43f5e] cursor-pointer"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-slate-300 font-bold mb-1">
                <span className="flex items-center gap-1"><Contrast className="w-3.5 h-3.5 text-sky-400" /> Contrast</span>
                <span className="font-mono text-sky-400">{filters.contrast}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="200"
                value={filters.contrast}
                onChange={(e) => setFilters({ ...filters, contrast: parseInt(e.target.value) })}
                className="w-full accent-[#f43f5e] cursor-pointer"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-slate-300 font-bold mb-1">
                <span className="flex items-center gap-1"><Droplets className="w-3.5 h-3.5 text-emerald-400" /> Saturation</span>
                <span className="font-mono text-emerald-400">{filters.saturation}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="200"
                value={filters.saturation}
                onChange={(e) => setFilters({ ...filters, saturation: parseInt(e.target.value) })}
                className="w-full accent-[#f43f5e] cursor-pointer"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-slate-300 font-bold mb-1">
                <span>Blur Radius</span>
                <span className="font-mono text-indigo-300">{filters.blur}px</span>
              </div>
              <input
                type="range"
                min="0"
                max="20"
                value={filters.blur}
                onChange={(e) => setFilters({ ...filters, blur: parseInt(e.target.value) })}
                className="w-full accent-[#f43f5e] cursor-pointer"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-slate-300 font-bold mb-1">
                <span>Hue Rotation</span>
                <span className="font-mono text-purple-300">{filters.hueRotate}°</span>
              </div>
              <input
                type="range"
                min="0"
                max="360"
                value={filters.hueRotate}
                onChange={(e) => setFilters({ ...filters, hueRotate: parseInt(e.target.value) })}
                className="w-full accent-[#f43f5e] cursor-pointer"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-slate-300 font-bold mb-1">
                <span>Sepia Filter</span>
                <span className="font-mono text-amber-200">{filters.sepia}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={filters.sepia}
                onChange={(e) => setFilters({ ...filters, sepia: parseInt(e.target.value) })}
                className="w-full accent-[#f43f5e] cursor-pointer"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
