import React, { useState } from 'react';
import { Palette, Layers, Play, Pause, RotateCcw, Download, Sparkles, Plus, Eye, EyeOff, Film, Type, Square, Circle } from 'lucide-react';
import { INITIAL_GRAPHIC_LAYERS, INITIAL_ANIMATION_KEYFRAMES, generateCssAnimation, exportSvgCanvas } from '../services/graphicEngine';
import { GraphicLayer, AnimationKeyframe } from '../types';

export const GraphicDesignPanel: React.FC = () => {
  const [layers, setLayers] = useState<GraphicLayer[]>(INITIAL_GRAPHIC_LAYERS);
  const [keyframes, setKeyframes] = useState<AnimationKeyframe[]>(INITIAL_ANIMATION_KEYFRAMES);
  const [selectedLayerId, setSelectedLayerId] = useState<string>('layer-1');
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTimeSec, setCurrentTimeSec] = useState<number>(1.0);
  const [activeTab, setActiveTab] = useState<'canvas' | 'animation' | 'css'>('canvas');

  const selectedLayer = layers.find(l => l.id === selectedLayerId) || layers[0];

  const updateLayer = (id: string, updates: Partial<GraphicLayer>) => {
    setLayers(layers.map(l => l.id === id ? { ...l, ...updates } : l));
  };

  const toggleLayerVisibility = (id: string) => {
    setLayers(layers.map(l => l.id === id ? { ...l, visible: !l.visible } : l));
  };

  const addLayer = (type: GraphicLayer['type']) => {
    const newId = `layer-${Date.now()}`;
    const newLayer: GraphicLayer = {
      id: newId,
      name: `${type.charAt(0).toUpperCase() + type.slice(1)} Layer ${layers.length + 1}`,
      type,
      x: 100 + layers.length * 20,
      y: 80 + layers.length * 20,
      width: type === 'ellipse' ? 100 : 200,
      height: type === 'ellipse' ? 100 : 120,
      fill: type === 'text' ? '#38bdf8' : (type === 'ellipse' ? '#f43f5e' : '#10b981'),
      stroke: '#ffffff',
      strokeWidth: 1,
      rotation: 0,
      opacity: 0.9,
      visible: true,
      content: type === 'text' ? 'New Motion Element' : undefined
    };
    setLayers([...layers, newLayer]);
    setSelectedLayerId(newId);
  };

  const handleExportSvg = () => {
    const svgStr = exportSvgCanvas(layers);
    const blob = new Blob([svgStr], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `medha_vector_graphic_${Date.now()}.svg`;
    a.click();
  };

  return (
    <div className="flex-1 bg-[#090d16] flex flex-col h-full overflow-hidden select-none">
      {/* Top Header Controls Bar */}
      <div className="h-11 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <Palette className="w-5 h-5 text-indigo-400" />
          <span className="font-bold text-xs uppercase tracking-wider text-white">Graphic & Motion Studio</span>
          <div className="flex items-center gap-1 bg-[#1e293b] p-0.5 rounded-lg border border-[#334155]">
            <button
              onClick={() => setActiveTab('canvas')}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                activeTab === 'canvas' ? 'bg-indigo-600 text-white shadow' : 'text-[#94a3b8] hover:text-white'
              }`}
            >
              Vector Canvas
            </button>
            <button
              onClick={() => setActiveTab('animation')}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                activeTab === 'animation' ? 'bg-indigo-600 text-white shadow' : 'text-[#94a3b8] hover:text-white'
              }`}
            >
              Motion Keyframes
            </button>
            <button
              onClick={() => setActiveTab('css')}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                activeTab === 'css' ? 'bg-indigo-600 text-white shadow' : 'text-[#94a3b8] hover:text-white'
              }`}
            >
              CSS Animation Code
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all shadow ${
              isPlaying ? 'bg-amber-600 hover:bg-amber-500 text-white' : 'bg-emerald-600 hover:bg-emerald-500 text-white'
            }`}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            {isPlaying ? 'Pause Motion' : 'Play Motion'}
          </button>
          <button
            onClick={handleExportSvg}
            className="px-3 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-cyan-300 rounded-lg text-xs font-bold flex items-center gap-1 border border-[#334155]"
          >
            <Download className="w-3.5 h-3.5" /> Export SVG
          </button>
        </div>
      </div>

      {/* Main Studio Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Layer Inspector Sidebar */}
        <div className="w-64 bg-[#0f172a] border-r border-[#1e293b] flex flex-col p-3 space-y-3">
          <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
            <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-white">
              <Layers className="w-4 h-4 text-indigo-400" /> Graphic Layers
            </span>
            <div className="flex items-center gap-1">
              <button onClick={() => addLayer('rectangle')} className="p-1 hover:bg-[#1e293b] rounded text-slate-300" title="Add Rectangle">
                <Square className="w-3.5 h-3.5 text-emerald-400" />
              </button>
              <button onClick={() => addLayer('ellipse')} className="p-1 hover:bg-[#1e293b] rounded text-slate-300" title="Add Circle">
                <Circle className="w-3.5 h-3.5 text-rose-400" />
              </button>
              <button onClick={() => addLayer('text')} className="p-1 hover:bg-[#1e293b] rounded text-slate-300" title="Add Text">
                <Type className="w-3.5 h-3.5 text-sky-400" />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto space-y-1.5">
            {layers.map((layer) => (
              <div
                key={layer.id}
                onClick={() => setSelectedLayerId(layer.id)}
                className={`p-2 rounded-lg cursor-pointer text-xs flex items-center justify-between border transition-all ${
                  selectedLayerId === layer.id
                    ? 'bg-indigo-500/20 text-indigo-200 border-indigo-500/40 font-semibold'
                    : 'bg-[#1e293b]/40 text-[#94a3b8] border-[#334155]/40 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  {layer.type === 'rectangle' && <Square className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                  {layer.type === 'ellipse' && <Circle className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
                  {layer.type === 'text' && <Type className="w-3.5 h-3.5 text-sky-400 shrink-0" />}
                  <span className="truncate">{layer.name}</span>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleLayerVisibility(layer.id);
                  }}
                  className="hover:text-white p-0.5 text-slate-400"
                >
                  {layer.visible ? <Eye className="w-3.5 h-3.5 text-emerald-400" /> : <EyeOff className="w-3.5 h-3.5 text-slate-500" />}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Center Canvas Viewport */}
        <div className="flex-1 bg-[#060911] flex flex-col overflow-hidden">
          {activeTab === 'canvas' || activeTab === 'animation' ? (
            <div className="flex-1 flex items-center justify-center p-6 overflow-auto relative">
              {/* Graphic Stage Canvas Container */}
              <div className="w-[600px] h-[400px] bg-[#0f172a] rounded-2xl border border-[#334155] shadow-2xl relative overflow-hidden">
                {/* SVG Render Stage */}
                <div
                  dangerouslySetInnerHTML={{ __html: exportSvgCanvas(layers) }}
                  className="w-full h-full"
                />
              </div>
            </div>
          ) : (
            <div className="flex-1 p-4 overflow-auto font-mono text-xs text-indigo-300 bg-[#090d16]">
              <pre className="p-4 bg-[#0f172a] rounded-xl border border-[#1e293b]">
                {generateCssAnimation(layers, keyframes)}
              </pre>
            </div>
          )}

          {/* Bottom Timeline Control Strip */}
          <div className="h-28 bg-[#0f172a] border-t border-[#1e293b] p-3 flex flex-col space-y-2">
            <div className="flex items-center justify-between text-xs text-[#94a3b8]">
              <span className="flex items-center gap-1.5 font-bold text-white uppercase tracking-wider">
                <Film className="w-4 h-4 text-indigo-400" /> Keyframe Motion Timeline (0.0s - 3.0s)
              </span>
              <span className="font-mono text-indigo-300 font-bold">Current Time: {currentTimeSec.toFixed(1)}s</span>
            </div>

            <input
              type="range"
              min="0"
              max="3"
              step="0.1"
              value={currentTimeSec}
              onChange={(e) => setCurrentTimeSec(parseFloat(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer"
            />

            <div className="flex items-center justify-between text-[11px] font-mono text-[#64748b] pt-1">
              <span>0.0s [Start]</span>
              <span>1.0s [Keyframe A]</span>
              <span>2.0s [Keyframe B]</span>
              <span>3.0s [End Loop]</span>
            </div>
          </div>
        </div>

        {/* Right Property Inspector Panel */}
        {selectedLayer && (
          <div className="w-72 bg-[#0f172a] border-l border-[#1e293b] p-4 flex flex-col space-y-4 overflow-y-auto">
            <span className="text-xs font-bold uppercase tracking-wider text-white border-b border-[#1e293b] pb-2">
              Transform & Style Inspector
            </span>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-[10px] uppercase font-bold text-[#64748b]">Layer Name</label>
                <input
                  type="text"
                  value={selectedLayer.name}
                  onChange={(e) => updateLayer(selectedLayer.id, { name: e.target.value })}
                  className="w-full bg-[#090d16] border border-[#334155] rounded p-1.5 text-white font-medium focus:outline-none"
                />
              </div>

              {selectedLayer.type === 'text' && (
                <div>
                  <label className="text-[10px] uppercase font-bold text-[#64748b]">Text Content</label>
                  <input
                    type="text"
                    value={selectedLayer.content || ''}
                    onChange={(e) => updateLayer(selectedLayer.id, { content: e.target.value })}
                    className="w-full bg-[#090d16] border border-[#334155] rounded p-1.5 text-white font-medium focus:outline-none"
                  />
                </div>
              )}

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] uppercase font-bold text-[#64748b]">Position X</label>
                  <input
                    type="number"
                    value={selectedLayer.x}
                    onChange={(e) => updateLayer(selectedLayer.id, { x: parseInt(e.target.value) || 0 })}
                    className="w-full bg-[#090d16] border border-[#334155] rounded p-1.5 text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-[10px] uppercase font-bold text-[#64748b]">Position Y</label>
                  <input
                    type="number"
                    value={selectedLayer.y}
                    onChange={(e) => updateLayer(selectedLayer.id, { y: parseInt(e.target.value) || 0 })}
                    className="w-full bg-[#090d16] border border-[#334155] rounded p-1.5 text-white font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] uppercase font-bold text-[#64748b]">Width</label>
                  <input
                    type="number"
                    value={selectedLayer.width}
                    onChange={(e) => updateLayer(selectedLayer.id, { width: parseInt(e.target.value) || 10 })}
                    className="w-full bg-[#090d16] border border-[#334155] rounded p-1.5 text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-[10px] uppercase font-bold text-[#64748b]">Height</label>
                  <input
                    type="number"
                    value={selectedLayer.height}
                    onChange={(e) => updateLayer(selectedLayer.id, { height: parseInt(e.target.value) || 10 })}
                    className="w-full bg-[#090d16] border border-[#334155] rounded p-1.5 text-white font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-[#64748b]">Fill Color</label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={selectedLayer.fill}
                    onChange={(e) => updateLayer(selectedLayer.id, { fill: e.target.value })}
                    className="w-8 h-8 rounded bg-transparent cursor-pointer border border-[#334155]"
                  />
                  <input
                    type="text"
                    value={selectedLayer.fill}
                    onChange={(e) => updateLayer(selectedLayer.id, { fill: e.target.value })}
                    className="flex-1 bg-[#090d16] border border-[#334155] rounded p-1.5 text-white font-mono uppercase"
                  />
                </div>
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-[#64748b]">Opacity ({selectedLayer.opacity})</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={selectedLayer.opacity}
                  onChange={(e) => updateLayer(selectedLayer.id, { opacity: parseFloat(e.target.value) })}
                  className="w-full accent-indigo-500 cursor-pointer"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
