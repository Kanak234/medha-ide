export type IDEEdition = 'community' | 'professional' | 'ultimate';

export interface EditionFeature {
  id: string;
  name: string;
  description: string;
  includedIn: IDEEdition[];
}

export interface EditionDetails {
  id: IDEEdition;
  name: string;
  tagline: string;
  targetAudience: string;
  bundleSizeEstimate: string;
  badgeColor: string;
  features: string[];
}

export const EDITIONS_CONFIG: Record<IDEEdition, EditionDetails> = {
  community: {
    id: 'community',
    name: 'Community Edition',
    tagline: 'Essential Offline Development Environment for Students & Open-Source Engineers',
    targetAudience: 'Students, beginners, open-source contributors, general developers',
    bundleSizeEstimate: '~1.5 GB (Minimal Runtime)',
    badgeColor: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
    features: [
      'Monaco Code Editor with Multi-Language Syntax Highlighting',
      'System Toolchain & Hardware Inventory Scanner',
      'AST-based Big-O Time & Space Complexity Analyzer',
      'Code Quality Scoring & "Make It Better" Refactoring Engine',
      'OWASP Static Security Vulnerability Scanner',
      'Interactive Algorithmic Educational Demos',
      'Integrated Terminal Shell & Native Git VCS Dashboard',
      'Offline AI Assistant Engine',
      'Standard Starter Project Templates'
    ]
  },
  professional: {
    id: 'professional',
    name: 'Professional Edition',
    tagline: 'Advanced Full-Stack, Database & DevOps Platform for Enterprise Engineers',
    targetAudience: 'Full-stack engineers, backend developers, database admins, DevOps teams',
    bundleSizeEstimate: '~4.8 GB (Full Dev Stack)',
    badgeColor: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40',
    features: [
      'Everything in Community Edition',
      'Multi-Engine Database Studio (SQLite, PostgreSQL, MySQL WASM)',
      'Docker Container & Kubernetes DevOps Dashboard',
      'Local Algorithmic Benchmarking Studio (Ops/Sec & Latency Profiling)',
      'Advanced Code Intelligence & Language Server Adapters',
      'Expanded Framework Templates (FastAPI, Spring Boot, React, Next.js)',
      'Multi-Tab Split Editor & Multi-Workspace Root Support',
      'Professional High-Contrast & Custom Design Themes'
    ]
  },
  ultimate: {
    id: 'ultimate',
    name: 'Ultimate Edition',
    tagline: 'Maximum Offline AI-Powered Multi-Platform IDE Bundle',
    targetAudience: 'Senior Software Architects, Mobile & Web Engineers, AI/ML Developers',
    bundleSizeEstimate: '~9.2 GB (Complete Offline Ecosystem)',
    badgeColor: 'bg-purple-500/20 text-purple-300 border-purple-500/40',
    features: [
      'Everything in Professional Edition',
      'Local RAG Code Indexer & Vector Embedding Search Engine',
      'Cross-Platform Mobile Simulator & Preview Engine (Android / iOS / Web)',
      'Extension Marketplace & Plugin Architecture Studio',
      'Offline Documentation Library (C++, Python, React, Rust, Go)',
      'Complete Polyglot SDK Bundles (GCC, Python, JDK, Rust, Go, Flutter)',
      'AI Architecture Advisor & Full Project Security Auditor',
      'Multi-Window Workspace & Cloud Sync Protocol Simulation'
    ]
  }
};

export const ALL_IDE_FEATURES: EditionFeature[] = [
  { id: 'editor', name: 'Monaco Editor & Syntax Highlighting', description: 'Core multi-file editor', includedIn: ['community', 'professional', 'ultimate'] },
  { id: 'complexity', name: 'Big-O Complexity Engine', description: 'Theoretical performance calculator', includedIn: ['community', 'professional', 'ultimate'] },
  { id: 'quality', name: 'Quality Score & Refactoring', description: 'Automated code enhancement', includedIn: ['community', 'professional', 'ultimate'] },
  { id: 'educational', name: 'Educational Algorithm Library', description: 'Step-by-step control flow visualizer', includedIn: ['community', 'professional', 'ultimate'] },
  { id: 'git', name: 'Git Version Control Dashboard', description: 'Branch management & commit history', includedIn: ['community', 'professional', 'ultimate'] },
  { id: 'security', name: 'OWASP Security Auditor', description: 'Vulnerability detection', includedIn: ['community', 'professional', 'ultimate'] },
  { id: 'benchmarking', name: 'Benchmarking Studio', description: 'Real measured throughput & latency', includedIn: ['professional', 'ultimate'] },
  { id: 'database', name: 'Database Studio', description: 'SQL execution & schema explorer', includedIn: ['professional', 'ultimate'] },
  { id: 'devops', name: 'DevOps & Container Dashboard', description: 'Docker & Kubernetes monitoring', includedIn: ['professional', 'ultimate'] },
  { id: 'mobile', name: 'Mobile Simulator', description: 'Cross-platform device preview', includedIn: ['ultimate'] },
  { id: 'extensions', name: 'Extension Marketplace', description: 'Pluggable architecture studio', includedIn: ['ultimate'] },
  { id: 'rag_ai', name: 'Offline Vector RAG Indexer', description: 'Local AI semantic search & offline docs', includedIn: ['ultimate'] }
];

export function isFeatureAvailable(featureId: string, currentEdition: IDEEdition): boolean {
  const feat = ALL_IDE_FEATURES.find(f => f.id === featureId);
  if (!feat) return true;
  return feat.includedIn.includes(currentEdition);
}
