export interface WorkspaceSessionState {
  lastActiveTabId: string;
  openFiles: string[];
  buildConfig: 'Debug' | 'Release';
  selectedCompiler: string;
  theme: string;
  timestamp: string;
}

const SESSION_KEY = 'medha_ide_session_v1';

export class SessionManager {
  saveSession(state: Partial<WorkspaceSessionState>): void {
    try {
      const current = this.loadSession();
      const updated: WorkspaceSessionState = {
        lastActiveTabId: state.lastActiveTabId ?? current.lastActiveTabId ?? 'tab-cpp-main',
        openFiles: state.openFiles ?? current.openFiles ?? ['/cpp-algo-project/main.cpp'],
        buildConfig: state.buildConfig ?? current.buildConfig ?? 'Debug',
        selectedCompiler: state.selectedCompiler ?? current.selectedCompiler ?? 'g++',
        theme: state.theme ?? current.theme ?? 'dark',
        timestamp: new Date().toISOString()
      };
      localStorage.setItem(SESSION_KEY, JSON.stringify(updated));
    } catch (e) {
      console.warn('[SessionManager] Unable to write workspace session state:', e);
    }
  }

  loadSession(): Partial<WorkspaceSessionState> {
    try {
      const raw = localStorage.getItem(SESSION_KEY);
      if (!raw) return {};
      return JSON.parse(raw);
    } catch (e) {
      return {};
    }
  }
}

export const defaultSessionManager = new SessionManager();
