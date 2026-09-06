export interface IDEExtension {
  id: string;
  name: string;
  publisher: string;
  version: string;
  category: 'Language' | 'Theme' | 'Debugger' | 'Database' | 'DevOps' | 'AI' | 'Linter';
  description: string;
  license: string;
  permissions: string[];
  dependencies: string[];
  installed: boolean;
  downloads: number;
  rating: number;
  icon: string;
}

export const INITIAL_EXTENSIONS: IDEExtension[] = [
  {
    id: 'ext-pyright',
    name: 'Python Pyright Language Server',
    publisher: 'Microsoft / Open-Source',
    version: '1.1.350',
    category: 'Language',
    description: 'Fast, offline static type checker and LSP for Python projects.',
    license: 'MIT',
    permissions: ['filesystem:read', 'process:exec'],
    dependencies: [],
    installed: true,
    downloads: 14200,
    rating: 4.9,
    icon: '🐍'
  },
  {
    id: 'ext-clang-tidy',
    name: 'Clang-Tidy C/C++ Static Analyzer',
    publisher: 'LLVM Project',
    version: '18.1.0',
    category: 'Linter',
    description: 'LLVM-based linter tool for identifying C++ code smells and memory bugs.',
    license: 'Apache-2.0 WITH LLVM-exception',
    permissions: ['filesystem:read', 'process:exec'],
    dependencies: [],
    installed: true,
    downloads: 9800,
    rating: 4.8,
    icon: '⚡'
  },
  {
    id: 'ext-rust-analyzer',
    name: 'Rust Analyzer Engine',
    publisher: 'Rust-Lang',
    version: '0.3.1890',
    category: 'Language',
    description: 'Modular compiler frontend for Rust providing completion and diagnostics.',
    license: 'MIT / Apache-2.0',
    permissions: ['filesystem:read', 'process:exec'],
    dependencies: [],
    installed: false,
    downloads: 18500,
    rating: 5.0,
    icon: '🦀'
  },
  {
    id: 'ext-postgres-driver',
    name: 'PostgreSQL Native WebAssembly Connector',
    publisher: 'PostgreSQL Global Development Group',
    version: '16.2.0',
    category: 'Database',
    description: 'In-browser WASM client for connecting and querying PostgreSQL databases offline.',
    license: 'PostgreSQL License',
    permissions: ['network:local', 'filesystem:write'],
    dependencies: [],
    installed: false,
    downloads: 6200,
    rating: 4.7,
    icon: '🐘'
  },
  {
    id: 'ext-cyberpunk-theme',
    name: 'Neon Cyberpunk Theme Pack',
    publisher: 'MEDHĀ Community',
    version: '2.0.1',
    category: 'Theme',
    description: 'Vibrant neon synthwave color palette with high accessibility contrast.',
    license: 'MIT',
    permissions: [],
    dependencies: [],
    installed: false,
    downloads: 24000,
    rating: 4.9,
    icon: '🎨'
  },
  {
    id: 'ext-ollama-bridge',
    name: 'Local Ollama & Llama.cpp AI Bridge',
    publisher: 'MEDHĀ AI Labs',
    version: '1.4.0',
    category: 'AI',
    description: 'Connects MEDHĀ-IDE directly to local GGUF models running via Llama.cpp or Ollama.',
    license: 'MIT',
    permissions: ['network:localhost', 'gpu:access'],
    dependencies: [],
    installed: true,
    downloads: 31000,
    rating: 4.95,
    icon: '🤖'
  }
];

export class ExtensionEngine {
  private extensions: IDEExtension[] = [...INITIAL_EXTENSIONS];

  public getAllExtensions(): IDEExtension[] {
    return [...this.extensions];
  }

  public installExtension(id: string): boolean {
    const ext = this.extensions.find(e => e.id === id);
    if (ext) {
      ext.installed = true;
      return true;
    }
    return false;
  }

  public uninstallExtension(id: string): boolean {
    const ext = this.extensions.find(e => e.id === id);
    if (ext) {
      ext.installed = false;
      return true;
    }
    return false;
  }

  public searchExtensions(query: string): IDEExtension[] {
    const q = query.toLowerCase().trim();
    if (!q) return this.getAllExtensions();
    return this.extensions.filter(
      e => e.name.toLowerCase().includes(q) ||
           e.description.toLowerCase().includes(q) ||
           e.category.toLowerCase().includes(q) ||
           e.publisher.toLowerCase().includes(q)
    );
  }
}

export const extensionEngine = new ExtensionEngine();
