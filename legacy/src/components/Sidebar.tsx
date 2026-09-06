import React from 'react';
import { 
  Files, 
  Search, 
  GitBranch, 
  Database, 
  Bug, 
  TestTube, 
  ShieldCheck, 
  GraduationCap, 
  Gauge, 
  Blocks,
  Palette,
  FileText,
  Image,
  Film,
  Gamepad2,
  Globe,
  Cpu,
  Settings
} from 'lucide-react';

interface SidebarProps {
  activeDrawer: string;
  setActiveDrawer: (drawer: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeDrawer, setActiveDrawer }) => {
  const items = [
    { id: 'explorer', label: 'File Explorer', icon: Files },
    { id: 'search', label: 'Global Search', icon: Search },
    { id: 'browser', label: 'Integrated Browser', icon: Globe },
    { id: 'git', label: 'Source Control', icon: GitBranch },
    { id: 'database', label: 'Database Explorer', icon: Database },
    { id: 'office', label: 'LibreOffice Suite', icon: FileText },
    { id: 'graphic', label: 'Graphic & Motion Studio', icon: Palette },
    { id: 'photo', label: 'Photo & Image Studio', icon: Image },
    { id: 'media', label: 'VLC Media Player', icon: Film },
    { id: 'game', label: '2D/3D Game Engine', icon: Gamepad2 },
    { id: 'debugger', label: 'Run & Debug', icon: Bug },
    { id: 'testing', label: 'Test Runner', icon: TestTube },
    { id: 'subsystems', label: 'AI Subsystems', icon: Cpu },
    { id: 'security', label: 'Security Auditor', icon: ShieldCheck },
    { id: 'demos', label: 'Educational Demos', icon: GraduationCap },
    { id: 'benchmark', label: 'Benchmarking Studio', icon: Gauge },
    { id: 'extensions', label: 'Plugin Extensions', icon: Blocks },
  ];

  return (
    <aside className="w-12 bg-[#090d16] border-r border-[#1e293b] flex flex-col items-center py-3 justify-between select-none z-20">
      <div className="flex flex-col gap-2 w-full px-1.5">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = activeDrawer === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveDrawer(item.id)}
              className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all group relative ${
                isActive
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-sm'
                  : 'text-[#64748b] hover:text-[#e2e8f0] hover:bg-[#1e293b]/60'
              }`}
              title={item.label}
            >
              <Icon className="w-4 h-4" />
              {/* Floating Tooltip */}
              <div className="absolute left-12 px-2 py-1 bg-[#1e293b] text-white text-xs rounded font-medium whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 border border-[#334155] shadow-xl">
                {item.label}
              </div>
            </button>
          );
        })}
      </div>

      <button
        onClick={() => setActiveDrawer('settings')}
        className="w-9 h-9 rounded-lg flex items-center justify-center text-[#64748b] hover:text-[#e2e8f0] hover:bg-[#1e293b]/60 transition-all group relative"
        title="Settings & System Configuration"
      >
        <Settings className="w-4 h-4" />
      </button>
    </aside>
  );
};
