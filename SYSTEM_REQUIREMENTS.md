# SYSTEM_REQUIREMENTS.md

## Hardware & Operating System Requirements for MEDHĀ-IDE

MEDHĀ-IDE operates completely offline-first with self-contained compilers, runtimes, and local static analysis engines.

---

## 1. Operating System Compatibility
- **Linux**: Ubuntu 20.04+, Kubuntu 22.04+, Debian 11+, Fedora 38+, RHEL 9+, Arch Linux.
- **Windows**: Windows 10 / 11 (x64 / ARM64).
- **macOS**: macOS 12 Monterey or newer (Apple Silicon M1/M2/M3/M4 & Intel x86_64).
- **Android**: Android 10+ (via Web-view container / Termux engine).
- **Web Browsers**: Chrome 110+, Firefox 115+, Safari 17+, Edge 110+.

---

## 2. Hardware Specifications

| Specification Tier | Community Edition | Professional Edition | Ultimate Complete Edition |
| :--- | :--- | :--- | :--- |
| **CPU** | 2 Cores (x86_64 / ARM64) | 4 Cores | 8+ Cores (Multithreaded) |
| **System RAM** | 4 GB | 8 GB | 16 GB+ |
| **Disk Storage** | 2.5 GB Free Space | 6.0 GB Free Space | 12.0 GB+ Free Space |
| **GPU / Acceleration** | Optional | WebGL 2.0 supported | WebGL 2.0 / WebGPU for AI vector search |
| **Network** | Offline-First (No internet required) | Offline-First | Offline-First |

---

## 3. Bundled Runtimes & Toolchain Detection
MEDHĀ-IDE automatically integrates with host toolchains if present:
- **C/C++**: GCC 15+, Clang 18+, GDB 16+
- **Python**: Python 3.10 – 3.14+
- **JavaScript / Node.js**: Node.js v20 – v22+
- **Java**: OpenJDK 17 – 21+
- **Rust**: Rustc 1.80+
- **Go**: Go 1.22+
- **Databases**: SQLite WASM, PostgreSQL client libs, MySQL drivers.
