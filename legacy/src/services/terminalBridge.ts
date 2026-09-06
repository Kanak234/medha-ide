import { SupportedLanguage } from '../types';
import { executeVaishnaviOrchestration, BuildAndRunResult } from './vaishnaviEngine';

export interface TerminalExecutionResult {
  command: string;
  output: string[];
  exitCode: number;
  newCwd?: string;
}

export class IntegratedTerminalBridge {
  private cwd: string = '/home/kanak/Desktop/ide';

  getCwd(): string {
    return this.cwd;
  }

  async executeCommand(
    inputCommand: string,
    activeCode?: string,
    activeLanguage: SupportedLanguage = 'typescript',
    activeFileName: string = 'main'
  ): Promise<TerminalExecutionResult> {
    const rawCmd = inputCommand.trim();
    if (!rawCmd) return { command: '', output: [], exitCode: 0 };

    const parts = rawCmd.split(/\s+/);
    const mainCmd = parts[0].toLowerCase();

    // 1. Navigation / Shell Builtins
    if (mainCmd === 'pwd') {
      return { command: rawCmd, output: [this.cwd], exitCode: 0 };
    }

    if (mainCmd === 'cd') {
      const target = parts[1] || '/home/kanak/Desktop/ide';
      if (target === '..') {
        this.cwd = '/home/kanak/Desktop';
      } else if (target.startsWith('/')) {
        this.cwd = target;
      } else {
        this.cwd = `${this.cwd}/${target}`.replace(/\/+/g, '/');
      }
      return { command: rawCmd, output: [`Changed directory to ${this.cwd}`], exitCode: 0, newCwd: this.cwd };
    }

    if (mainCmd === 'ls') {
      return {
        command: rawCmd,
        output: [
          'src/               public/            package.json',
          'vite.config.ts     tsconfig.json      README.md',
          'medha.project.json node_modules/      dist/'
        ],
        exitCode: 0
      };
    }

    if (mainCmd === 'clear') {
      return { command: rawCmd, output: [], exitCode: 0 };
    }

    if (mainCmd === 'whoami') {
      return { command: rawCmd, output: ['kanak (MEDHĀ Lead Architect)'], exitCode: 0 };
    }

    if (mainCmd === 'uname' || rawCmd.includes('uname -a')) {
      return { command: rawCmd, output: ['Linux medha-desktop 6.8.0-45-generic #45-Ubuntu SMP PREEMPT_DYNAMIC x86_64 GNU/Linux'], exitCode: 0 };
    }

    // 2. Version checks (gcc --version, python3 --version, etc)
    if (rawCmd.includes('--version') || rawCmd.includes('-v')) {
      if (mainCmd === 'gcc' || mainCmd === 'g++') {
        return { command: rawCmd, output: [`${mainCmd} (Ubuntu 15.2.0-1ubuntu1) 15.2.0`], exitCode: 0 };
      }
      if (mainCmd === 'python3' || mainCmd === 'python') {
        return { command: rawCmd, output: ['Python 3.14.4 (Ubuntu Host)'], exitCode: 0 };
      }
      if (mainCmd === 'node') {
        return { command: rawCmd, output: ['v22.22.1'], exitCode: 0 };
      }
    }

    // 3. Build & Execution Toolchain Directives (gcc, g++, python3, node, cargo, go)
    if (['gcc', 'g++', 'clang', 'clang++', 'python3', 'python', 'node', 'ts-node', 'cargo', 'go', 'javac', 'java'].includes(mainCmd)) {
      const lang: SupportedLanguage = 
        mainCmd === 'gcc' || mainCmd === 'clang' ? 'c' :
        mainCmd === 'g++' || mainCmd === 'clang++' ? 'cpp' :
        mainCmd.startsWith('python') ? 'python' :
        mainCmd === 'cargo' ? 'rust' :
        mainCmd === 'go' ? 'go' :
        mainCmd.startsWith('java') ? 'java' : 'typescript';

      const buildRes: BuildAndRunResult = await executeVaishnaviOrchestration(
        activeCode || `// Sample ${lang.toUpperCase()} source\n#include <stdio.h>\nint main() { printf("Hello from ${lang.toUpperCase()}\\n"); return 0; }`,
        lang,
        activeFileName
      );

      const logs: string[] = [];
      logs.push(`[$] ${rawCmd}`);
      logs.push(`[${buildRes.toolchain.compilerName}] Toolchain Path: ${buildRes.toolchain.path}`);
      logs.push(buildRes.compilerOutput);

      if (buildRes.stdout) {
        logs.push(`--- STDOUT Output ---`);
        logs.push(buildRes.stdout);
      }

      if (buildRes.stderr) {
        logs.push(`--- STDERR Error Log ---`);
        logs.push(buildRes.stderr);
      }

      logs.push(`Process finished with exit code ${buildRes.exitCode} (${buildRes.executionTimeMs} ms)`);
      return { command: rawCmd, output: logs, exitCode: buildRes.exitCode };
    }

    // 4. Fallback execution
    return {
      command: rawCmd,
      output: [
        `Command '${mainCmd}' executed in isolated workspace terminal session.`,
        `Output: Exit code 0.`
      ],
      exitCode: 0
    };
  }
}

export const defaultTerminalBridge = new IntegratedTerminalBridge();
