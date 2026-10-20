import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('MEDHĀ Standalone Desktop Application Launcher E2E Tests', () => {
  const workspaceDir = path.resolve(__dirname, '../../../');
  const packageScriptPath = path.join(workspaceDir, 'scripts/package-release.ts');
  const mainJsPath = path.join(workspaceDir, 'main.js');

  it('main.js process entry point exists for native desktop execution', () => {
    expect(fs.existsSync(mainJsPath)).toBe(true);
    const mainJsContent = fs.readFileSync(mainJsPath, 'utf-8');
    expect(mainJsContent).toContain("import { app, BrowserWindow, Menu, ipcMain } from 'electron';");
    expect(mainJsContent).toContain("mainWindow.loadFile(indexPath);");
  });

  it('package-release.ts generates start.sh without browser or HTTP server dependencies', () => {
    expect(fs.existsSync(packageScriptPath)).toBe(true);
    const scriptContent = fs.readFileSync(packageScriptPath, 'utf-8');
    
    // Must NOT contain web browser or localhost launchers
    expect(scriptContent).not.toContain('xdg-open "http://localhost');
    expect(scriptContent).not.toContain('kde-open5 "http://localhost');
    expect(scriptContent).not.toContain('sensible-browser "http://localhost');
    expect(scriptContent).not.toContain('python3 -m http.server');
    expect(scriptContent).not.toContain('npx serve');
    expect(scriptContent).not.toContain('xdg-open "file://');

    // MUST contain native Electron executable invocation
    expect(scriptContent).toContain('exec electron "$DIR/main.js" "$@"');
  });
});
