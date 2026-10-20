import React, { useState } from 'react';
import { Gamepad2, Box, Sun, Camera, Play, Pause, Plus, Layers, Code, Sparkles, Move, Zap } from 'lucide-react';
import { INITIAL_GAME_ENTITIES, generateGameCodeScript } from '../services/gameEngine';
import { GameObjectEntity } from '../types';

export const GameEnginePanel: React.FC = () => {
  const [entities, setEntities] = useState<GameObjectEntity[]>(INITIAL_GAME_ENTITIES);
  const [selectedEntityId, setSelectedEntityId] = useState<string>('ent-1');
  const [isGameRunning, setIsGameRunning] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'viewport' | 'code'>('viewport');

  const selectedEntity = entities.find(e => e.id === selectedEntityId) || entities[0];

  const updateEntity = (id: string, updates: Partial<GameObjectEntity>) => {
    setEntities(entities.map(e => e.id === id ? { ...e, ...updates } : e));
  };

  const addEntity = (type: GameObjectEntity['type']) => {
    const newId = `ent-${Date.now()}`;
    const newEntity: GameObjectEntity = {
      id: newId,
      name: `New ${type.charAt(0).toUpperCase() + type.slice(1)} Object`,
      type,
      x: 0,
      y: 1,
      z: 0,
      scaleX: 1,
      scaleY: 1,
      scaleZ: 1,
      rotationX: 0,
      rotationY: 0,
      rotationZ: 0,
      color: type === 'light' ? '#fbbf24' : (type === 'camera' ? '#818cf8' : '#34d399')
    };
    setEntities([...entities, newEntity]);
    setSelectedEntityId(newId);
  };

  return (
    <div className="flex-1 bg-[#090d16] flex flex-col h-full overflow-hidden select-none">
      {/* Top Game Engine Header */}
      <div className="h-11 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <Gamepad2 className="w-5 h-5 text-cyan-400" />
          <span className="font-bold text-xs uppercase tracking-wider text-white">MEDHĀ 2D/3D Game Engine Studio</span>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30">
            Godot & Unity Native Core API
          </span>

          <div className="flex items-center gap-1 bg-[#1e293b] p-0.5 rounded-lg border border-[#334155] ml-4">
            <button
              onClick={() => setActiveTab('viewport')}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                activeTab === 'viewport' ? 'bg-cyan-600 text-white shadow' : 'text-[#94a3b8] hover:text-white'
              }`}
            >
              3D Viewport
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                activeTab === 'code' ? 'bg-cyan-600 text-white shadow' : 'text-[#94a3b8] hover:text-white'
              }`}
            >
              Generated Game Code
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsGameRunning(!isGameRunning)}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all shadow ${
              isGameRunning ? 'bg-amber-600 hover:bg-amber-500 text-white' : 'bg-cyan-600 hover:bg-cyan-500 text-white'
            }`}
          >
            {isGameRunning ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            {isGameRunning ? 'Pause Engine (60 FPS)' : 'Play Game Test'}
          </button>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Entity Hierarchy Tree */}
        <div className="w-64 bg-[#0f172a] border-r border-[#1e293b] p-3 flex flex-col space-y-2">
          <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-cyan-400" /> Scene Hierarchy
            </span>
            <button onClick={() => addEntity('sprite')} className="p-1 hover:bg-[#1e293b] rounded text-cyan-400" title="Add Entity">
              <Plus className="w-4 h-4" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-1">
            {entities.map((entity) => (
              <div
                key={entity.id}
                onClick={() => setSelectedEntityId(entity.id)}
                className={`p-2 rounded-lg cursor-pointer text-xs flex items-center justify-between border transition-all ${
                  selectedEntityId === entity.id
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-semibold'
                    : 'bg-[#1e293b]/40 text-[#94a3b8] border-[#334155]/40 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  {entity.type === 'light' && <Sun className="w-3.5 h-3.5 text-amber-400 shrink-0" />}
                  {entity.type === 'camera' && <Camera className="w-3.5 h-3.5 text-indigo-400 shrink-0" />}
                  {entity.type === 'rigid_body' && <Box className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                  {entity.type === 'sprite' && <Gamepad2 className="w-3.5 h-3.5 text-cyan-400 shrink-0" />}
                  {entity.type === 'particle_system' && <Zap className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
                  <span className="truncate">{entity.name}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Center Viewport Stage */}
        <div className="flex-1 bg-[#060911] flex flex-col overflow-hidden">
          {activeTab === 'viewport' ? (
            <div className="flex-1 flex items-center justify-center p-6 relative overflow-hidden">
              {/* Grid 3D Canvas Stage */}
              <div className="w-[640px] h-[440px] bg-[#0c1322] rounded-2xl border border-[#334155] shadow-2xl relative overflow-hidden flex items-center justify-center">
                {/* Simulated 3D Grid Axis */}
                <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-40" />

                {/* Rendered Entities */}
                {entities.map((entity) => (
                  <div
                    key={entity.id}
                    style={{
                      position: 'absolute',
                      left: `calc(50% + ${entity.x * 30}px)`,
                      top: `calc(50% - ${entity.y * 30}px)`,
                      transform: `rotate(${entity.rotationZ}deg) scale(${entity.scaleX})`,
                      backgroundColor: entity.color,
                      width: entity.type === 'rigid_body' ? '120px' : '48px',
                      height: entity.type === 'rigid_body' ? '16px' : '48px',
                      borderRadius: entity.type === 'camera' || entity.type === 'light' ? '9999px' : '8px',
                      boxShadow: selectedEntityId === entity.id ? '0 0 15px #38bdf8' : 'none'
                    }}
                    className="flex items-center justify-center text-[10px] font-mono font-bold text-slate-950 shadow-lg cursor-pointer transition-all"
                    onClick={() => setSelectedEntityId(entity.id)}
                  >
                    {entity.name.split(' ')[0]}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex-1 p-4 overflow-auto font-mono text-xs text-cyan-300 bg-[#090d16]">
              <pre className="p-4 bg-[#0f172a] rounded-xl border border-[#1e293b]">
                {generateGameCodeScript(entities)}
              </pre>
            </div>
          )}
        </div>

        {/* Right Inspector Drawer */}
        {selectedEntity && (
          <div className="w-72 bg-[#0f172a] border-l border-[#1e293b] p-4 flex flex-col space-y-4 overflow-y-auto">
            <span className="text-xs font-bold uppercase tracking-wider text-white border-b border-[#1e293b] pb-2">
              Transform & Component Inspector
            </span>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-[10px] uppercase font-bold text-[#64748b]">Entity Name</label>
                <input
                  type="text"
                  value={selectedEntity.name}
                  onChange={(e) => updateEntity(selectedEntity.id, { name: e.target.value })}
                  className="w-full bg-[#090d16] border border-[#334155] rounded p-1.5 text-white font-medium focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-3 gap-1.5">
                <div>
                  <label className="text-[10px] uppercase font-bold text-[#64748b]">Pos X</label>
                  <input
                    type="number"
                    value={selectedEntity.x}
                    onChange={(e) => updateEntity(selectedEntity.id, { x: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-[#090d16] border border-[#334155] rounded p-1 text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-[10px] uppercase font-bold text-[#64748b]">Pos Y</label>
                  <input
                    type="number"
                    value={selectedEntity.y}
                    onChange={(e) => updateEntity(selectedEntity.id, { y: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-[#090d16] border border-[#334155] rounded p-1 text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-[10px] uppercase font-bold text-[#64748b]">Pos Z</label>
                  <input
                    type="number"
                    value={selectedEntity.z}
                    onChange={(e) => updateEntity(selectedEntity.id, { z: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-[#090d16] border border-[#334155] rounded p-1 text-white font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-[#64748b]">Material Color</label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={selectedEntity.color}
                    onChange={(e) => updateEntity(selectedEntity.id, { color: e.target.value })}
                    className="w-8 h-8 rounded bg-transparent cursor-pointer border border-[#334155]"
                  />
                  <input
                    type="text"
                    value={selectedEntity.color}
                    onChange={(e) => updateEntity(selectedEntity.id, { color: e.target.value })}
                    className="flex-1 bg-[#090d16] border border-[#334155] rounded p-1.5 text-white font-mono uppercase"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
