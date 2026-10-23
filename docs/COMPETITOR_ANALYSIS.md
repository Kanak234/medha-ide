# MEDHĀ v2 vs C-Lite IDE and other student IDEs

Sources checked on 2026-10-23: C-Lite IDE README (github.com/17NitinRaj06/C-Lite-IDE, v1.0.0, 1 star).
Rows for other IDEs are well-known public facts; items marked *(unverified)* were not re-checked this week.

| Feature | C-Lite 1.0 | Turbo C++ 3 | Dev-C++ | Code::Blocks | VS Code | MEDHĀ 2.0 |
|---|---|---|---|---|---|---|
| Platforms | Windows 10/11 | DOS (DOSBox) | Windows | Win/Linux/mac | Win/Linux/mac | **Windows + Linux** |
| Bundled compiler | MinGW.org GCC **6.3.0, 32-bit** | Borland | TDM-GCC *(unverified version)* | optional MinGW | none | **current 64-bit GCC (WinLibs) + JDK 25 + Python** |
| Languages | C, C++ | C, C++ | C, C++ | C, C++ | any (extensions) | **C, C++, Java, Python** (+JS) |
| graphics.h / conio.h | yes (Windows GDI) | native | no | no | no | **yes, Windows *and* Linux** (PRABHA runtime) |
| Old Turbo code (`void main`, `iostream.h`) | partly | native | no | no | no | **runs unchanged + Modernize with explanations** |
| Debugger | no | yes | yes (gdb) | yes | extension | **GDB + debugpy** |
| Autocomplete / go-to-definition | no | no | basic | basic | yes | **clangd / pylsp** |
| Beginner error explanations | no | no | no | no | no | **English + Hinglish** |
| Crash explanation (segfault, ÷0) | no | no | no | no | no | **yes** |
| Security scan of student code | no | no | no | no | extensions | **yes (CWE, offline)** |
| DSA / memory visualizer | no | no | no | no | extensions | **yes** |
| Git | no | no | no | plugin | yes | **yes** |
| Distribution | NSIS .exe from GitHub (unsigned) | — | SourceForge | website | Store/website | **Microsoft Store (Microsoft-signed, auto-update) + Snap Store** |
| Lab examples | some | — | — | — | — | **32 Turbo graphics + 24 C/C++/Java/Python** |

## Where C-Lite is ahead (and our answer)
1. **Already installed in the university labs.** → Store link = one click, no admin password; ask HOD to pilot.
2. **Small and light** (Tkinter + 32-bit GCC). → MEDHĀ is bigger (JDK + Python bundled). Mitigation: lean MSIX, report its real size in the CI log.
3. **Simple, one window.** → MEDHĀ has many docks; Command Palette (Ctrl+Shift+P) and a Turbo screen that opens only when needed.

## Where MEDHĀ wins
Modern 64-bit compiler, Linux support, Java+Python, debugger, LSP, explanations, Store distribution.
