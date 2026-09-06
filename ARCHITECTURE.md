# MEDHĀ IDE — Technical Architecture & System Design

## 🏛️ System Overview

**MEDHĀ IDE** (मेधा IDE) is an autonomous, offline-first, multi-platform development environment conceived in **2022** and led by **Kanak Prabhakar**.

```
+-----------------------------------------------------------------------------------+
|                                  MEDHĀ IDE CORE                                   |
+-----------------------------------------------------------------------------------+
|                            MEDHĀ Intelligence Layer                                |
|  ┌───────────────────┬───────────────────┬───────────────────┬─────────────────┐  |
|  │  SARASVATĪ Engine │    KĀLĪ Engine    │ MAHĀLAKṢMĪ Engine │ VAISHNAVĪ Engine│  |
|  │ Knowledge & RAG   │ Security & Audit  │ Perf & Big-O      │ Autonomous Exec │  |
|  └───────────────────┴───────────────────┴───────────────────┴─────────────────┘  |
+-----------------------------------------------------------------------------------+
|  Header Navbar  |  Sidebar  |  Code Editor (Monaco)  |  Complexity & Quality Dock |
+-----------------+-----------+------------------------+----------------------------+
|  Integrated     | Database  | LibreOffice            | Graphic & Motion Studio    |
|  Dev Browser    | Studio    | Productivity Suite     | Photo & VLC Media Player   |
+-----------------+-----------+------------------------+----------------------------+
|  2D/3D Game     | DevOps &  | Security Auditor       | Benchmarking Studio        |
|  Engine Studio  | Docker    | & Pentest Suite        | & Educational Demos        |
+-----------------------------------------------------------------------------------+
|                     Offline Local AI & Vector RAG Engine                          |
+-----------------------------------------------------------------------------------+
|                     Sandboxed Execution & Terminal Engine                         |
+-----------------------------------------------------------------------------------+
```

---

## 👤 Creator & Leadership
- **Created by**: Kanak Prabhakar
- **Primary Creator & Lead**: Kanak Prabhakar
- **Inception Year**: 2022

---

## 🕊️ Personal Dedication

> **"MEDHĀ IDE is dedicated by Kanak Prabhakar to Maa Vaishno, Maa Kali, Maa Saraswati, his mother, his girlfriend, and his sister, as an expression of gratitude, inspiration, love, knowledge, strength and dedication."**

---

## 🏛️ Intelligent Subsystems Architecture

MEDHĀ serves as the central intelligence coordination layer directing four specialized, transparent, secular technical subsystems:

```
                    MEDHĀ IDE
                        |
                MEDHĀ Intelligence
                        |
       ┌────────────────┼────────────────┐
       │                │                │
   SARASVATĪ          KĀLĪ        MAHĀLAKṢMĪ
   Knowledge         Security      Performance
       │                │                │
       └────────────────┼────────────────┘
                        │
                    VAISHNAVĪ
                  Orchestration
                        │
               Developer Workspace
```

### Specialized Intelligent Subsystems Summary

1. **SARASVATĪ (सरस्वती) — Knowledge, Learning & Developer Intelligence Engine**
   - Focus: RAG indexing, offline documentation libraries, code comprehension, AST symbol lookup, step-by-step tutorials.
   - Status: `IMPLEMENTED` | `TESTED` | `VERIFIED`

2. **KĀLĪ (काली) — Security, Threat Detection & Defensive Analysis Engine**
   - Focus: OWASP Top 10 static security auditing, vulnerability detection, secret detection, workspace isolation enforcement (`/home/kanak/Desktop/ide`).
   - Safety Policy: `NEVER DELETE USER FILES`.
   - Status: `IMPLEMENTED` | `TESTED` | `VERIFIED`

3. **MAHĀLAKṢMĪ (महालक्ष्मी) — Performance, Resource & Efficiency Engine**
   - Focus: AST algorithmic complexity parser ($O(1)$, $O(\log n)$, $O(n)$, $O(n^2)$), micro-benchmarking, memory profiling, CPU execution-time analysis.
   - Status: `IMPLEMENTED` | `TESTED` | `VERIFIED`

4. **VAISHNAVĪ (वैष्णवी) — Autonomous Execution & Orchestration Engine**
   - Focus: Build orchestration, compiler toolchain execution, test runner automation, dev-server hot-reloading, release packaging workflows.
   - Safety Policy: Operations are confined strictly within workspace boundaries (`WORKSPACE ONLY`).
   - Status: `IMPLEMENTED` | `TESTED` | `VERIFIED`

---

## 🔧 Core Architectural Components

1. **Monaco Code Editor & Multi-Keymap Engine**:
   - Integrated Monaco Editor with support for C++, Python, Rust, Go, Java, TypeScript, Bash, JSON, YAML.
   - Dynamic keymap mode selector (VS Code, Vim with modal state, Nano, JetBrains).

2. **Integrated Development Browser**:
   - Multi-tab browser environment with dev-server auto-detection (`localhost:5173`).
   - Full DevTools Suite (Console REPL, Elements DOM inspector, Network request logger, Storage inspector).
   - Responsive device emulator (Desktop, Laptop, Tablet, iPhone 15 Pro, Android).

3. **Offline AI & Vector RAG Engine**:
   - Zero internet requirement. Local vector index over offline developer documentation.

4. **Polyglot Database Studio**:
   - Native runners for Oracle 23c, PostgreSQL 16, MySQL 8.4, MongoDB 7.0, and SQLite 3.

5. **Open-Source LibreOffice Suite**:
   - Built-in LibreOffice Writer, Calc, Impress, and Math formula equation editor.

6. **Creative & Motion Media Studios**:
   - Graphic & Motion Studio (SVG export & CSS keyframe generator).
   - Digital Photo Processing Studio (Image filter color grading).
   - VLC Media Player Studio (4K/60FPS video playback & codec inspector).
   - 2D/3D Game Development Engine (WebGL scene viewport & Godot/Unity code script exporter).

7. **Static Security Auditor**:
   - OWASP Top 10 static security scanner & penetration testing tool definitions (Nmap, Metasploit, Burp Suite, Hydra, Wireshark, Nikto).
