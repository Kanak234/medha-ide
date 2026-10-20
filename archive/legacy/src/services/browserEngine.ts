import { BrowserTabItem, BrowserConsoleEntry, BrowserNetworkEntry, BrowserStorageEntry, DeviceViewportMode } from '../types';

export const DEFAULT_BROWSER_TABS: BrowserTabItem[] = [
  {
    id: 'tab-local-dev',
    title: 'MEDHĀ IDE Web App (Localhost Preview)',
    url: 'http://localhost:5173/',
    isLoading: false,
    canGoBack: false,
    canGoForward: false,
    favicon: '⚡',
    isSecure: true,
    history: ['http://localhost:5173/'],
    historyIndex: 0
  },
  {
    id: 'tab-[#docs]',
    title: 'React & TypeScript Developer Docs',
    url: 'http://localhost:5173/docs/react-ts',
    isLoading: false,
    canGoBack: false,
    canGoForward: false,
    favicon: '📘',
    isSecure: true,
    history: ['http://localhost:5173/docs/react-ts'],
    historyIndex: 0
  }
];

export const DEVICE_VIEWPORT_MAP: Record<DeviceViewportMode, { width: number; height: number; name: string }> = {
  desktop: { width: 1920, height: 1080, name: 'Desktop (1920x1080)' },
  laptop: { width: 1366, height: 768, name: 'Laptop (1366x768)' },
  tablet: { width: 768, height: 1024, name: 'iPad / Tablet (768x1024)' },
  mobile_iphone: { width: 375, height: 812, name: 'iPhone 15 Pro (375x812)' },
  mobile_android: { width: 360, height: 800, name: 'Android Pixel (360x800)' },
  custom: { width: 1200, height: 800, name: 'Custom Viewport' }
};

export const INITIAL_CONSOLE_LOGS: BrowserConsoleEntry[] = [
  { id: 'c-1', type: 'info', message: '[Vite v6.4.3] dev server running at http://localhost:5173/', timestamp: '03:30:12', sourceFile: 'vite:client' },
  { id: 'c-2', type: 'log', message: 'MEDHĀ Integrated Browser Engine initialized in WASM Sandbox.', timestamp: '03:30:13', sourceFile: 'browserEngine.ts' },
  { id: 'c-3', type: 'warn', message: '[React] Fast Refresh enabled for Hot Module Replacement (HMR).', timestamp: '03:30:14', sourceFile: 'react-dom' },
  { id: 'c-4', type: 'info', message: 'GET /api/v1/health status 200 OK (1.2ms)', timestamp: '03:30:15', sourceFile: 'fetch' }
];

export const INITIAL_NETWORK_LOGS: BrowserNetworkEntry[] = [
  { id: 'n-1', method: 'GET', url: 'http://localhost:5173/', status: 200, statusText: 'OK', type: 'document', durationMs: 4.2, sizeBytes: 1240, timestamp: '03:30:12' },
  { id: 'n-2', method: 'GET', url: 'http://localhost:5173/assets/index.css', status: 200, statusText: 'OK', type: 'stylesheet', durationMs: 2.1, sizeBytes: 54100, timestamp: '03:30:13' },
  { id: 'n-3', method: 'GET', url: 'http://localhost:5173/assets/index.js', status: 200, statusText: 'OK', type: 'script', durationMs: 12.8, sizeBytes: 354800, timestamp: '03:30:13' },
  { id: 'n-4', method: 'GET', url: 'http://localhost:5173/api/v1/health', status: 200, statusText: 'OK', type: 'fetch', durationMs: 1.2, sizeBytes: 84, timestamp: '03:30:15' }
];

export const INITIAL_STORAGE_ITEMS: BrowserStorageEntry[] = [
  { key: 'medha_theme', value: 'dark', type: 'localStorage' },
  { key: 'medha_edition', value: 'ultimate', type: 'localStorage' },
  { key: 'session_token', value: 'offline_token_8a92f', type: 'sessionStorage' }
];

export function detectLocalDevServers(): string[] {
  return [
    'http://localhost:5173/ (Vite Dev Server)',
    'http://localhost:3000/ (React / Next.js)',
    'http://localhost:8080/ (Vue / Spring Boot)',
    'http://127.0.0.1:8000/ (Python Fast-API / Django)'
  ];
}
