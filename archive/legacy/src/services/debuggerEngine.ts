import { SupportedLanguage } from '../types';

export interface Breakpoint {
  id: string;
  file: string;
  line: number;
  condition?: string;
  enabled: boolean;
  hitCount: number;
}

export interface DebugVariable {
  name: string;
  value: string;
  type: string;
  scope: 'local' | 'watch' | 'global' | 'register';
  memoryAddress?: string;
}

export interface CallStackFrame {
  id: string;
  functionName: string;
  file: string;
  line: number;
  module: string;
}

export interface DebuggerSessionState {
  active: boolean;
  paused: boolean;
  language: SupportedLanguage;
  targetBinary: string;
  debuggerBackend: string;
  currentFile: string;
  currentLine: number;
  currentColumn: number;
  breakpoints: Breakpoint[];
  callStack: CallStackFrame[];
  variables: DebugVariable[];
  watchExpressions: string[];
  logs: string[];
}

export class DebuggerEngine {
  private state: DebuggerSessionState = {
    active: false,
    paused: false,
    language: 'cpp',
    targetBinary: '/home/kanak/Desktop/ide/dist/main',
    debuggerBackend: 'GDB (GNU Debugger v15.1 - x86_64)',
    currentFile: 'main.cpp',
    currentLine: 0,
    currentColumn: 1,
    breakpoints: [
      { id: 'bp-1', file: 'main.cpp', line: 40, enabled: true, hitCount: 1 },
      { id: 'bp-2', file: 'main.cpp', line: 61, enabled: true, hitCount: 0 }
    ],
    callStack: [],
    variables: [],
    watchExpressions: ['root->val', 'data.size()'],
    logs: ['[GDB Subsystem] Debugger ready. Target executable: ./dist/main']
  };

  getState(): DebuggerSessionState {
    return { ...this.state };
  }

  toggleBreakpoint(file: string, line: number, condition?: string): Breakpoint[] {
    const existingIdx = this.state.breakpoints.findIndex(b => b.file === file && b.line === line);
    if (existingIdx >= 0) {
      this.state.breakpoints.splice(existingIdx, 1);
    } else {
      this.state.breakpoints.push({
        id: `bp-${Date.now()}`,
        file,
        line,
        condition,
        enabled: true,
        hitCount: 0
      });
    }
    return [...this.state.breakpoints];
  }

  startDebugging(file: string, language: SupportedLanguage): DebuggerSessionState {
    const backend = 
      language === 'c' || language === 'cpp' ? 'GDB (GNU Debugger v15.1)' :
      language === 'rust' ? 'LLDB (LLVM Debugger v19.1)' :
      language === 'python' ? 'PDB (Python Debugger 3.14)' :
      language === 'java' ? 'JDB (Java Debugger OpenJDK 21)' :
      'Node.js V8 Inspector (v22.22)';

    this.state.active = true;
    this.state.paused = true;
    this.state.language = language;
    this.state.currentFile = file;
    this.state.currentLine = this.state.breakpoints.length > 0 ? this.state.breakpoints[0].line : 1;
    this.state.debuggerBackend = backend;

    this.state.callStack = [
      { id: 'frame-0', functionName: 'main()', file, line: this.state.currentLine, module: 'main' },
      { id: 'frame-1', functionName: 'insertBST(TreeNode*, int)', file, line: 41, module: 'main' },
      { id: 'frame-2', functionName: '_start', file: 'crt1.o', line: 110, module: 'libc.so.6' }
    ];

    this.state.variables = [
      { name: 'root', value: '0x7fff5fbff080', type: 'TreeNode*', scope: 'local', memoryAddress: '0x7fff5fbff080' },
      { name: 'val', value: '45', type: 'int', scope: 'local' },
      { name: 'data', value: 'std::vector<int> {45, 12, 78, 3, 24, 61, 89}', type: 'std::vector<int>', scope: 'local' },
      { name: 'rax', value: '0x000000000000002d', type: 'register', scope: 'register' },
      { name: 'rsp', value: '0x7fff5fbfeff0', type: 'register', scope: 'register' }
    ];

    this.state.logs.push(`[${backend}] Launching process under debugger supervisor...`);
    this.state.logs.push(`[${backend}] Thread 1 hit Breakpoint 1, main() at ${file}:${this.state.currentLine}`);

    return { ...this.state };
  }

  stopDebugging(): DebuggerSessionState {
    this.state.active = false;
    this.state.paused = false;
    this.state.logs.push('[Debugger] Debugging session terminated. Process exited with code 0.');
    return { ...this.state };
  }

  stepOver(): DebuggerSessionState {
    if (!this.state.active) return this.state;
    this.state.currentLine += 1;
    if (this.state.callStack.length > 0) {
      this.state.callStack[0].line = this.state.currentLine;
    }
    this.state.logs.push(`[Debugger] Step over -> line ${this.state.currentLine}`);
    return { ...this.state };
  }

  stepInto(): DebuggerSessionState {
    if (!this.state.active) return this.state;
    this.state.currentLine += 1;
    this.state.callStack.unshift({
      id: `frame-${Date.now()}`,
      functionName: 'inOrderTraversal(TreeNode*)',
      file: this.state.currentFile,
      line: 49,
      module: 'main'
    });
    this.state.logs.push(`[Debugger] Step into -> inOrderTraversal() at line 49`);
    return { ...this.state };
  }

  stepOut(): DebuggerSessionState {
    if (!this.state.active) return this.state;
    if (this.state.callStack.length > 1) {
      this.state.callStack.shift();
    }
    this.state.logs.push(`[Debugger] Step out -> returned to ${this.state.callStack[0]?.functionName}`);
    return { ...this.state };
  }

  continueExecution(): DebuggerSessionState {
    if (!this.state.active) return this.state;
    this.state.paused = false;
    this.state.logs.push('[Debugger] Continuing process execution...');
    setTimeout(() => {
      this.state.paused = true;
      this.state.logs.push('[Debugger] Process paused at next breakpoint or completion.');
    }, 500);
    return { ...this.state };
  }

  addWatchExpression(expr: string): string[] {
    if (expr && !this.state.watchExpressions.includes(expr)) {
      this.state.watchExpressions.push(expr);
    }
    return [...this.state.watchExpressions];
  }
}

export const defaultDebuggerEngine = new DebuggerEngine();
