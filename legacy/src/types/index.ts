export type SupportedLanguage = 
  | 'c' | 'cpp' | 'rust' | 'go' | 'zig' | 'd' | 'nim' | 'fortran' | 'cobol'
  | 'java' | 'kotlin' | 'scala' | 'groovy' | 'clojure'
  | 'csharp' | 'fsharp' | 'powershell'
  | 'javascript' | 'typescript' | 'html' | 'css' | 'scss' | 'webassembly'
  | 'python' | 'jupyter'
  | 'swift' | 'dart' | 'flutter' | 'react-native'
  | 'r' | 'julia' | 'haskell' | 'ocaml' | 'erlang' | 'elixir' | 'lisp' | 'prolog'
  | 'sql' | 'postgresql' | 'mysql' | 'sqlite' | 'mongodb' | 'graphql'
  | 'bash' | 'zsh' | 'fish' | 'json' | 'yaml' | 'toml' | 'dockerfile';

export interface FileItem {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'directory';
  language?: SupportedLanguage;
  content?: string;
  children?: FileItem[];
  isExpanded?: boolean;
}

export interface EditorTab {
  id: string;
  fileId: string;
  title: string;
  path: string;
  content: string;
  language: SupportedLanguage;
  isDirty: boolean;
  cursorLine?: number;
  cursorColumn?: number;
}

export interface SystemTool {
  name: string;
  category: 'Compiler' | 'Runtime' | 'Debugger' | 'Build Tool' | 'VCS' | 'Container' | 'Database';
  installed: boolean;
  version?: string;
  path?: string;
  description: string;
}

export interface SystemInventory {
  os: string;
  arch: string;
  cpuCores: number;
  totalRamGB: number;
  availableRamGB: number;
  hasGpu: boolean;
  gpuName?: string;
  tools: SystemTool[];
  lastScannedAt: string;
}

export type BigONotation = 
  | 'O(1)' 
  | 'O(log n)' 
  | 'O(n)' 
  | 'O(n log n)' 
  | 'O(n²)' 
  | 'O(n³)' 
  | 'O(2ⁿ)' 
  | 'O(n!)' 
  | 'O(V + E)' 
  | 'O(n × m)';

export interface ComplexityResult {
  timeComplexity: BigONotation;
  spaceComplexity: BigONotation;
  bestCase: BigONotation;
  averageCase: BigONotation;
  worstCase: BigONotation;
  auxiliarySpace: string;
  confidence: number; // 0 - 100%
  isExact: boolean;
  reasoning: string[];
  loopDepth: number;
  recursiveDepth: number;
  spatialAllocations: string[];
}

export interface CodeSmell {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  type: string;
  line?: number;
  description: string;
  recommendation: string;
}

export interface QualityScore {
  overallScore: number; // 0 - 100
  performanceScore: number;
  readabilityScore: number;
  maintainabilityScore: number;
  securityScore: number;
  complexityGrade: string; // 'A' | 'B' | 'C' | 'D' | 'F'
  smells: CodeSmell[];
  metrics: {
    linesOfCode: number;
    cyclomaticComplexity: number;
    maxNestingDepth: number;
    duplicateBlocks: number;
  };
  summary: string;
  makeItBetter?: {
    originalCode: string;
    optimizedCode: string;
    improvementReason: string;
    timeComplexityBefore: BigONotation;
    timeComplexityAfter: BigONotation;
    spaceComplexityBefore: BigONotation;
    spaceComplexityAfter: BigONotation;
    tradeoffs: string;
  };
}

export interface BenchmarkResult {
  id: string;
  name: string;
  executionTimeMs: number;
  operationsPerSec: number;
  memoryUsedMB: number;
  iterations: number;
  timeComplexity: BigONotation;
  spaceComplexity: BigONotation;
  isWinner?: boolean;
  logs: string[];
}

export interface BenchmarkComparison {
  title: string;
  description: string;
  implementationA: {
    name: string;
    code: string;
    language: SupportedLanguage;
  };
  implementationB: {
    name: string;
    code: string;
    language: SupportedLanguage;
  };
  resultA?: BenchmarkResult;
  resultB?: BenchmarkResult;
  conclusion?: string;
}

export interface EducationalDemo {
  id: string;
  category: 'Control Flow' | 'Data Structures' | 'Algorithms' | 'OOP' | 'Concurrency';
  title: string;
  subtitle: string;
  description: string;
  language: SupportedLanguage;
  code: string;
  badCode?: string;
  goodCode?: string;
  explanation: {
    whenToUse: string;
    whenNotToUse: string;
    executionFlow: string[];
    advantages: string[];
    disadvantages: string[];
    complexity: {
      time: BigONotation;
      space: BigONotation;
    };
  };
  visualizerSteps?: {
    stepIndex: number;
    description: string;
    state: Record<string, any>;
    highlightLine?: number;
  }[];
}

export interface DatabaseSchemaTable {
  name: string;
  columns: { name: string; type: string; isPk?: boolean; isFk?: boolean; nullable?: boolean }[];
  rowCount: number;
}

export interface DatabaseQueryResult {
  columns: string[];
  rows: Record<string, any>[];
  executionTimeMs: number;
  rowCount: number;
  error?: string;
}

export interface GitCommit {
  hash: string;
  shortHash: string;
  author: string;
  date: string;
  message: string;
  branch: string;
}

export interface GitFileStatus {
  path: string;
  status: 'modified' | 'added' | 'deleted' | 'untracked';
  staged: boolean;
}

export interface SecurityVulnerability {
  id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  cwe: string;
  title: string;
  file: string;
  line: number;
  snippet: string;
  description: string;
  remediation: string;
}

export interface AIMessage {
  id: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  codeSnippet?: {
    language: SupportedLanguage;
    code: string;
  };
  verified?: boolean;
}

export interface PluginExtension {
  id: string;
  name: string;
  version: string;
  author: string;
  description: string;
  enabled: boolean;
  category: 'Language' | 'Linter' | 'Theme' | 'Debugger' | 'Database' | 'AI';
}

export interface GraphicLayer {
  id: string;
  name: string;
  type: 'rectangle' | 'ellipse' | 'text' | 'path' | 'vector_icon';
  x: number;
  y: number;
  width: number;
  height: number;
  fill: string;
  stroke: string;
  strokeWidth: number;
  rotation: number;
  opacity: number;
  visible: boolean;
  content?: string;
}

export interface AnimationKeyframe {
  id: string;
  timeSec: number;
  layerId: string;
  property: 'x' | 'y' | 'opacity' | 'rotation' | 'scale';
  value: number;
  easing: 'linear' | 'ease-in-out' | 'cubic-bezier' | 'bounce';
}

export type LibreOfficeAppType = 'writer' | 'calc' | 'impress' | 'math';

export interface OfficeSpreadsheetCell {
  row: number;
  col: number;
  value: string;
  formula?: string;
  format?: 'text' | 'number' | 'currency';
}

export interface OfficePresentationSlide {
  id: string;
  title: string;
  subtitle?: string;
  content: string[];
  layout: 'title' | 'content' | 'split';
}

export interface PhotoFilterSettings {
  brightness: number; // 0 - 200%
  contrast: number;   // 0 - 200%
  saturation: number; // 0 - 200%
  blur: number;       // 0 - 20px
  sepia: number;      // 0 - 100%
  hueRotate: number;  // 0 - 360deg
  grayscale: number;  // 0 - 100%
  invert: number;     // 0 - 100%
}

export interface MediaTrackItem {
  id: string;
  title: string;
  type: 'video' | 'audio';
  durationSec: number;
  url: string;
  artist?: string;
  codec?: string;
  resolution?: string;
}

export interface GameObjectEntity {
  id: string;
  name: string;
  type: 'sprite' | 'mesh3d' | 'light' | 'camera' | 'rigid_body' | 'particle_system';
  x: number;
  y: number;
  z: number;
  scaleX: number;
  scaleY: number;
  scaleZ: number;
  rotationX: number;
  rotationY: number;
  rotationZ: number;
  color: string;
  script?: string;
}

export type NetworkStatus = 'offline' | 'connecting' | 'online' | 'limited';

export type DeviceViewportMode = 'desktop' | 'laptop' | 'tablet' | 'mobile_iphone' | 'mobile_android' | 'custom';

export interface BrowserTabItem {
  id: string;
  title: string;
  url: string;
  isLoading: boolean;
  canGoBack: boolean;
  canGoForward: boolean;
  favicon?: string;
  isSecure: boolean;
  history: string[];
  historyIndex: number;
}

export interface BrowserConsoleEntry {
  id: string;
  type: 'log' | 'info' | 'warn' | 'error';
  message: string;
  timestamp: string;
  sourceFile?: string;
  lineNumber?: number;
}

export interface BrowserNetworkEntry {
  id: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  url: string;
  status: number;
  statusText: string;
  type: 'xhr' | 'fetch' | 'document' | 'script' | 'stylesheet' | 'image';
  durationMs: number;
  sizeBytes: number;
  timestamp: string;
}

export interface BrowserStorageEntry {
  key: string;
  value: string;
  type: 'localStorage' | 'sessionStorage' | 'cookie';
}

export type SubsystemStatus = 'IMPLEMENTED' | 'TESTED' | 'VERIFIED' | 'NOT IMPLEMENTED' | 'NOT VERIFIED';

export interface IntelligentSubsystem {
  id: 'sarasvati' | 'kali' | 'mahalakshmi' | 'vaishnavi';
  name: string;
  sanskritName: string;
  tagline: string;
  role: string;
  status: SubsystemStatus[];
  responsibilities: string[];
  description: string;
}





