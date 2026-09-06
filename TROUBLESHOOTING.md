# TROUBLESHOOTING.md — MEDHĀ-IDE Diagnostics & Troubleshooting Guide

This guide provides solutions for common issues, toolchain setup, offline AI indexing, and platform-specific installer verification.

---

## 1. System Inventory & Toolchain Discovery Issues

### Symptom: Compilers (GCC/Clang/Python) marked as "Not Found" in Header
- **Cause**: Toolchain binaries are installed in non-standard PATH locations.
- **Solution**:
  1. Open the Integrated Terminal (`Ctrl+\``) in MEDHĀ-IDE.
  2. Verify command availability: `gcc --version` or `python3 --version`.
  3. Click **Cores | RAM** in the top navigation bar to trigger an instant re-scan.

---

## 2. Big-O Complexity Analysis & Static Scanner Diagnostics

### Symptom: Time complexity reported as $O(1)$ for custom functions
- **Cause**: Heuristic AST parser requires standard loop keywords (`for`, `while`, `do-while`, or recursive call identifiers).
- **Solution**: Ensure your function uses explicit loop counters or recursion. Use the "Make It Better" button to view auto-generated linear implementations.

---

## 3. Database Studio & SQL WASM Query Errors

### Symptom: Query fails with "Table not found"
- **Cause**: The in-browser SQLite memory instance initializes with default schema tables: `users`, `orders`, `products`.
- **Solution**: Run `SELECT name FROM sqlite_master WHERE type='table';` in the Database Studio to view active tables, or execute `CREATE TABLE ...`.

---

## 4. Platform Installer Verification

### Ubuntu / Kubuntu Debian Package Installation:
```bash
# Option A: Using absolute path (Works from any terminal working directory)
sudo dpkg -i /home/kanak/Desktop/ide/release/linux/kubuntu/medha-ide-professional_1.0.0_amd64.deb

# Option B: Navigate to project workspace directory first
cd /home/kanak/Desktop/ide
sudo dpkg -i release/linux/kubuntu/medha-ide-professional_1.0.0_amd64.deb
```

### Troubleshooting Launch Issues on Kubuntu / Linux:
- **Symptom**: Installed `.deb` package does not appear in KDE Application Launcher or fails to open upon click.
- **Root Cause & Fix**:
  1. **Desktop Entry**: Version 1.0.0 packaging now registers `/usr/share/applications/medha-ide-pro.desktop` into the KDE Plasma menu system.
  2. **Terminal Launcher**: Added `/usr/bin/medha-ide-pro` entry point executable for instant terminal launch.
  3. **Auto-Server Launch**: `start.sh` automatically provisions a dynamic local offline HTTP server on `http://localhost:5173+` (via Python3/Node) and triggers `xdg-open` / `kde-open5`.
- **Manual Command Launch**: Run `medha-ide-pro` or `/usr/local/bin/medha-ide-pro/start.sh` directly in terminal.

---

## 5. Security & Isolation Guarantee
MEDHĀ-IDE operates under strict workspace boundary protection. It never executes `rm` commands, never modifies files outside `/home/kanak/Desktop/ide/`, and requires zero internet connectivity for local analysis.

