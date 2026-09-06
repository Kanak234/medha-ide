import { GitCommit, GitFileStatus } from '../types';

export const INITIAL_GIT_COMMITS: GitCommit[] = [
  {
    hash: 'a1b2c3d4e5f6789012345678901234567890abcd',
    shortHash: 'a1b2c3d',
    author: 'Kanak <kanak@medhaide.io>',
    date: '2026-08-20 20:15:00',
    message: 'feat(core): implement autonomous offline AI IDE engine with AST complexity parser',
    branch: 'main'
  },
  {
    hash: 'b2c3d4e5f6789012345678901234567890abcdef',
    shortHash: 'b2c3d4e',
    author: 'Kanak <kanak@medhaide.io>',
    date: '2026-08-20 18:40:00',
    message: 'feat(demos): add Big-O time and space complexity educational interactive visualizer',
    branch: 'main'
  },
  {
    hash: 'c3d4e5f6789012345678901234567890abcdef01',
    shortHash: 'c3d4e5f',
    author: 'Kanak <kanak@medhaide.io>',
    date: '2026-08-20 16:10:00',
    message: 'init: create workspace structure with strict filesystem sandbox security boundaries',
    branch: 'main'
  }
];

export const INITIAL_GIT_FILES: GitFileStatus[] = [
  { path: 'src/services/complexityAnalyzer.ts', status: 'modified', staged: true },
  { path: 'src/services/codeQualityAnalyzer.ts', status: 'modified', staged: true },
  { path: 'src/components/EducationalDemosPanel.tsx', status: 'added', staged: false },
  { path: 'src/components/BenchmarkingPanel.tsx', status: 'added', staged: false }
];

export function createGitCommit(message: string, stagedFiles: GitFileStatus[], branch: string = 'main'): GitCommit {
  const hashRaw = Array.from({ length: 40 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
  return {
    hash: hashRaw,
    shortHash: hashRaw.substring(0, 7),
    author: 'Kanak Prabhakar <kanak@medhaide.dev>',
    date: new Date().toISOString().replace('T', ' ').substring(0, 19),
    message: message.trim(),
    branch
  };
}

