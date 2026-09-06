import { SupportedLanguage, SystemTool } from '../types';

export interface LanguageToolchainInfo {
  language: SupportedLanguage;
  compilerName: string;
  category: 'Compiler' | 'Interpreter' | 'Runtime' | 'Build Tool';
  installed: boolean;
  version: string;
  path: string;
  status: 'INSTALLED' | 'NOT INSTALLED / NOT CONFIGURED';
  command: string;
  defaultFlags: string[];
}

export function detectLanguageToolchain(language: SupportedLanguage): LanguageToolchainInfo {
  const isLinux = typeof navigator !== 'undefined' && navigator.userAgent.includes('Linux');

  switch (language) {
    case 'c':
      return {
        language: 'c',
        compilerName: 'GCC (GNU C Compiler)',
        category: 'Compiler',
        installed: true,
        version: '15.2.0 (Ubuntu Host)',
        path: '/usr/bin/gcc',
        status: 'INSTALLED',
        command: 'gcc',
        defaultFlags: ['-O2', '-Wall', '-std=c17']
      };
    case 'cpp':
      return {
        language: 'cpp',
        compilerName: 'G++ (GNU C++ Compiler)',
        category: 'Compiler',
        installed: true,
        version: '15.2.0 (Ubuntu Host)',
        path: '/usr/bin/g++',
        status: 'INSTALLED',
        command: 'g++',
        defaultFlags: ['-O2', '-Wall', '-std=c++20']
      };
    case 'python':
    case 'jupyter':
      return {
        language: 'python',
        compilerName: 'Python 3 Interpreter',
        category: 'Interpreter',
        installed: true,
        version: '3.14.4 (Ubuntu Host)',
        path: '/usr/bin/python3',
        status: 'INSTALLED',
        command: 'python3',
        defaultFlags: ['-u']
      };
    case 'javascript':
    case 'typescript':
      return {
        language: 'typescript',
        compilerName: 'Node.js V8 Runtime',
        category: 'Runtime',
        installed: true,
        version: 'v22.22.1 (Ubuntu Host)',
        path: '/usr/bin/node',
        status: 'INSTALLED',
        command: 'node',
        defaultFlags: []
      };
    case 'rust':
      return {
        language: 'rust',
        compilerName: 'Rustc Compiler',
        category: 'Compiler',
        installed: true,
        version: '1.84.0 (Cargo Toolchain)',
        path: '/home/kanak/.cargo/bin/rustc',
        status: 'INSTALLED',
        command: 'rustc',
        defaultFlags: ['-O']
      };
    case 'go':
      return {
        language: 'go',
        compilerName: 'Go Compiler Toolchain',
        category: 'Compiler',
        installed: true,
        version: 'go1.22.0 (Ubuntu Host)',
        path: '/usr/local/go/bin/go',
        status: 'INSTALLED',
        command: 'go',
        defaultFlags: ['run']
      };
    case 'java':
      return {
        language: 'java',
        compilerName: 'OpenJDK Javac Compiler',
        category: 'Compiler',
        installed: true,
        version: 'OpenJDK 21.0.2',
        path: '/usr/bin/javac',
        status: 'INSTALLED',
        command: 'javac',
        defaultFlags: []
      };
    default:
      return {
        language,
        compilerName: `${language.toUpperCase()} Toolchain`,
        category: 'Compiler',
        installed: false,
        version: 'N/A',
        path: 'N/A',
        status: 'NOT INSTALLED / NOT CONFIGURED',
        command: 'N/A',
        defaultFlags: []
      };
  }
}

export function getAllSupportedToolchains(): LanguageToolchainInfo[] {
  const languages: SupportedLanguage[] = ['c', 'cpp', 'python', 'typescript', 'rust', 'go', 'java', 'fortran', 'cobol', 'zig'];
  return languages.map(detectLanguageToolchain);
}
