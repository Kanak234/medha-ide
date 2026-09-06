import { describe, it, expect } from 'vitest';
import { analyzeCodeComplexity } from '../complexityAnalyzer';
import { evaluateCodeQuality } from '../codeQualityAnalyzer';
import { runSecurityAudit, KALI_PARROT_PENTEST_TOOLS } from '../securityAuditor';
import { executeSqlQuery, exportToCsv, SUPPORTED_DATABASES, SAMPLE_DATABASE_TABLES } from '../databaseEngine';
import { EDITIONS_CONFIG, ALL_IDE_FEATURES, isFeatureAvailable } from '../editionsEngine';
import { extensionEngine } from '../extensionEngine';
import { performOfflineRAGSearch, processAIQuery } from '../aiAssistantEngine';
import { EDUCATIONAL_DEMOS } from '../educationalDemos';
import { getAllSubsystems, getSubsystemById } from '../subsystemsEngine';
import { detectNetworkStatus, validateSecurityOrigin } from '../networkEngine';
import { exportSvgCanvas, generateCssAnimation, INITIAL_GRAPHIC_LAYERS, INITIAL_ANIMATION_KEYFRAMES } from '../graphicEngine';
import { DEFAULT_PHOTO_FILTERS, getCssFilterString } from '../photoEngine';
import { generateGameCodeScript, INITIAL_GAME_ENTITIES } from '../gameEngine';
import { scanSystemEnvironment } from '../envScanner';

describe('MEDHĀ-IDE 101/101 Core Engine Comprehensive Test Suite', () => {

  // ==========================================
  // 1. Complexity Analyzer Subsystem (Tests 1-15)
  // ==========================================
  describe('1. AST Complexity Analyzer Engine', () => {
    it('Test 01: should derive O(1) time complexity for simple arithmetic statements', () => {
      const res = analyzeCodeComplexity('function add(a, b) { return a + b; }', 'typescript');
      expect(res.timeComplexity).toBe('O(1)');
      expect(res.spaceComplexity).toBe('O(1)');
    });

    it('Test 02: should detect O(n) linear loop complexity for standard for-loops', () => {
      const code = `function sum(arr) {
        let s = 0;
        for (let i = 0; i < arr.length; i++) { s += arr[i]; }
        return s;
      }`;
      const res = analyzeCodeComplexity(code, 'typescript');
      expect(res.timeComplexity).toBe('O(n)');
    });

    it('Test 03: should detect O(n²) quadratic complexity for nested double loops', () => {
      const code = `function bubbleSort(arr) {
        for (let i = 0; i < arr.length; i++) {
          for (let j = 0; j < arr.length; j++) {
            if (arr[i] < arr[j]) { let tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp; }
          }
        }
      }`;
      const res = analyzeCodeComplexity(code, 'typescript');
      expect(res.timeComplexity).toBe('O(n²)');
    });

    it('Test 04: should detect O(n³) cubic complexity for triple nested loops', () => {
      const code = `function matrixMultiply(A, B, C) {
        for (let i = 0; i < n; i++) {
          for (let j = 0; j < n; j++) {
            for (let k = 0; k < n; k++) {
              C[i][j] += A[i][k] * B[k][j];
            }
          }
        }
      }`;
      const res = analyzeCodeComplexity(code, 'typescript');
      expect(res.timeComplexity).toBe('O(n³)');
    });

    it('Test 05: should detect O(log n) logarithmic complexity for binary halving while loops', () => {
      const code = `function binaryPartition(n) {
        let count = 0;
        while (n > 1) {
          n /= 2;
          count++;
        }
        return count;
      }`;
      const res = analyzeCodeComplexity(code, 'javascript');
      expect(res.timeComplexity).toBe('O(log n)');
    });

    it('Test 06: should detect O(n log n) linearithmic complexity for divide and conquer recursion', () => {
      const code = `function mergeSort(arr) {
        if (arr.length <= 1) return arr;
        let mid = arr.length / 2;
        return mergeSort(arr.slice(0, mid));
      }`;
      const res = analyzeCodeComplexity(code, 'typescript');
      expect(res.timeComplexity).toBe('O(n log n)');
      expect(res.spaceComplexity).toBe('O(log n)');
    });

    it('Test 07: should detect O(2ⁿ) exponential complexity for un-memoized recursive calls', () => {
      const code = `function fib(n) {
        if (n <= 1) return n;
        return fib(n - 1) + fib(n - 2);
      }`;
      const res = analyzeCodeComplexity(code, 'javascript');
      expect(res.timeComplexity).toBe('O(2ⁿ)');
      expect(res.spaceComplexity).toBe('O(n)');
    });

    it('Test 08: should identify linear spatial allocations O(n)', () => {
      const code = `function createBuffer(n) {
        let buf = new Array(n);
        for (let i = 0; i < n; i++) { buf.push(i); }
        return buf;
      }`;
      const res = analyzeCodeComplexity(code, 'typescript');
      expect(res.spaceComplexity).toBe('O(n)');
    });

    it('Test 09: should identify 2D matrix quadratic spatial allocations O(n²)', () => {
      const code = `function createMatrix(n) {
        vector<vector<int>> grid(n, vector<int>(n));
        return grid;
      }`;
      const res = analyzeCodeComplexity(code, 'cpp');
      expect(res.spaceComplexity).toBe('O(n²)');
    });

    it('Test 10: should parse Python code loops correctly', () => {
      const code = `def process_list(items):
    total = 0
    for item in items:
        total += item
    return total`;
      const res = analyzeCodeComplexity(code, 'python');
      expect(res.timeComplexity).toBe('O(n)');
    });

    it('Test 11: should parse C++ code loops correctly', () => {
      const code = `int calculate(int n) {
        int sum = 0;
        for(int i = 0; i < n; ++i) { sum += i; }
        return sum;
      }`;
      const res = analyzeCodeComplexity(code, 'cpp');
      expect(res.timeComplexity).toBe('O(n)');
    });

    it('Test 12: should parse Rust code loops correctly', () => {
      const code = `fn compute(n: usize) -> usize {
        let mut total = 0;
        for i in 0..n { total += i; }
        total
      }`;
      const res = analyzeCodeComplexity(code, 'rust');
      expect(res.timeComplexity).toBe('O(n)');
    });

    it('Test 13: should handle empty code strings gracefully defaulting to O(1)', () => {
      const res = analyzeCodeComplexity('', 'typescript');
      expect(res.timeComplexity).toBe('O(1)');
      expect(res.spaceComplexity).toBe('O(1)');
    });

    it('Test 14: should ignore comment lines in complexity calculation', () => {
      const code = `// for (let i=0; i<n; i++) { for (let j=0; j<n; j++) {} }
      function simple() { return 42; }`;
      const res = analyzeCodeComplexity(code, 'typescript');
      expect(res.timeComplexity).toBe('O(1)');
    });

    it('Test 15: should provide exact confidence score and reasoning list', () => {
      const res = analyzeCodeComplexity('function test() {}', 'typescript');
      expect(res.confidence).toBe(95);
      expect(res.isExact).toBe(false);
      expect(res.reasoning.length).toBeGreaterThan(0);
    });
  });

  // ==========================================
  // 2. Code Quality & Refactoring Engine (Tests 16-30)
  // ==========================================
  describe('2. Code Quality & Refactoring Engine', () => {
    it('Test 16: should compute overall code quality score between 0 and 100', () => {
      const quality = evaluateCodeQuality('function demo() { return 1; }', 'typescript');
      expect(quality.overallScore).toBeGreaterThanOrEqual(0);
      expect(quality.overallScore).toBeLessThanOrEqual(100);
    });

    it('Test 17: should detect Deep Nesting smell when nesting depth exceeds threshold', () => {
      const deepCode = `function deep() {
        if (a) {
          if (b) {
            if (c) {
              if (d) {
                return true;
              }
            }
          }
        }
      }`;
      const quality = evaluateCodeQuality(deepCode, 'typescript');
      expect(quality.smells.some(s => s.type === 'Deep Nesting')).toBe(true);
    });

    it('Test 18: should detect Magic Number smell for hardcoded constants', () => {
      const code = `function calc(val) { return val * 86400; }`;
      const quality = evaluateCodeQuality(code, 'typescript');
      expect(quality.smells.some(s => s.type === 'Magic Number')).toBe(true);
    });

    it('Test 19: should detect Long Line smell when line length exceeds 120 characters', () => {
      const longLine = `const descriptiveVariable = "This is an extraordinarily long string literal designed specifically to exceed the maximum line width threshold of 120 characters for testing.";`;
      const quality = evaluateCodeQuality(longLine, 'typescript');
      expect(quality.smells.some(s => s.type === 'Long Line')).toBe(true);
    });

    it('Test 20: should detect Security Risk smell for dangerous eval/exec calls', () => {
      const code = `function run(codeStr) { eval(codeStr); }`;
      const quality = evaluateCodeQuality(code, 'typescript');
      expect(quality.smells.some(s => s.type === 'Security Risk')).toBe(true);
    });

    it('Test 21: should generate Make It Better refactoring for quadratic O(n²) loops', () => {
      const code = `function findDuplicates(arr) {
        let res = [];
        for(let i=0; i<arr.length; i++) {
          for(let j=i+1; j<arr.length; j++) {
            if(arr[i] === arr[j]) res.push(arr[i]);
          }
        }
        return res;
      }`;
      const quality = evaluateCodeQuality(code, 'typescript');
      expect(quality.makeItBetter).toBeDefined();
      expect(quality.makeItBetter?.timeComplexityBefore).toBe('O(n²)');
      expect(quality.makeItBetter?.timeComplexityAfter).toBe('O(n)');
    });

    it('Test 22: should generate Make It Better guard-clause refactoring for deep nesting', () => {
      const code = `function check(user) {\n  if (user) {\n    if (user.active) {\n      if (user.role === 'admin') {\n        return execute(user);\n      }\n    }\n  }\n}`;
      const quality = evaluateCodeQuality(code, 'typescript');
      expect(quality.makeItBetter).toBeDefined();
      expect(quality.makeItBetter?.improvementReason.toLowerCase()).toContain('guard clauses');
    });

    it('Test 23: should assign grade A for high quality clean code', () => {
      const quality = evaluateCodeQuality('function cleanAdd(a: number, b: number): number { return a + b; }', 'typescript');
      expect(quality.complexityGrade).toBe('A');
    });

    it('Test 24: should return metrics with accurate lines of code count', () => {
      const code = `line 1\nline 2\nline 3\nline 4\nline 5`;
      const quality = evaluateCodeQuality(code, 'typescript');
      expect(quality.metrics.linesOfCode).toBe(5);
    });

    it('Test 25: should penalize readability score for excessive nesting', () => {
      const cleanQ = evaluateCodeQuality('function f() { return 1; }', 'typescript');
      const nestedCode = `function f() {\n  if(a) {\n    if(b) {\n      if(c) {\n        if(d) {\n          return 1;\n        }\n      }\n    }\n  }\n}`;
      const nestedQ = evaluateCodeQuality(nestedCode, 'typescript');
      expect(nestedQ.readabilityScore).toBeLessThan(cleanQ.readabilityScore);
    });

    it('Test 26: should evaluate Python code quality accurately', () => {
      const pyCode = `def test_func(arr):
    for i in range(len(arr)):
        for j in range(len(arr)):
            print(arr[i], arr[j])`;
      const quality = evaluateCodeQuality(pyCode, 'python');
      expect(quality.overallScore).toBeGreaterThan(0);
      expect(quality.makeItBetter).toBeDefined();
    });

    it('Test 27: should evaluate C++ code quality accurately', () => {
      const cppCode = `int getValue() { return 42; }`;
      const quality = evaluateCodeQuality(cppCode, 'cpp');
      expect(quality.complexityGrade).toBe('A');
    });

    it('Test 28: should include tradeoff explanation in Make It Better output', () => {
      const code = `function dup(a) { for(let i=0;i<a.length;i++) { for(let j=0;j<a.length;j++) {} } }`;
      const quality = evaluateCodeQuality(code, 'typescript');
      expect(quality.makeItBetter?.tradeoffs).toBeDefined();
      expect(quality.makeItBetter?.tradeoffs.length).toBeGreaterThan(10);
    });

    it('Test 29: should calculate cyclomatic complexity based on conditional statements', () => {
      const complexCode = `function test(a, b, c) {
        if (a) { } else if (b) { } while(c) { }
      }`;
      const quality = evaluateCodeQuality(complexCode, 'typescript');
      expect(quality.metrics.cyclomaticComplexity).toBeGreaterThan(1);
    });

    it('Test 30: should return a non-empty summary string', () => {
      const quality = evaluateCodeQuality('let x = 10;', 'typescript');
      expect(quality.summary).toBeDefined();
      expect(quality.summary.length).toBeGreaterThan(10);
    });
  });

  // ==========================================
  // 3. Security Auditor & Threat Detection (Tests 31-45)
  // ==========================================
  describe('3. Security Auditor & Threat Detector (KĀLĪ Engine)', () => {
    it('Test 31: should detect CWE-798 Hardcoded Plaintext Secrets and API Keys', () => {
      const code = `const api_key = "secret_1234567890123456";`;
      const vulns = runSecurityAudit(code, 'config.ts', 'typescript');
      expect(vulns.some(v => v.cwe === 'CWE-798')).toBe(true);
      expect(vulns[0].severity).toBe('CRITICAL');
    });

    it('Test 32: should detect CWE-89 SQL Injection vulnerabilities', () => {
      const code = `const query = "SELECT * FROM users WHERE id = '" + req.query.id + "'";`;
      const vulns = runSecurityAudit(code, 'db.ts', 'typescript');
      expect(vulns.some(v => v.cwe === 'CWE-89')).toBe(true);
      expect(vulns[0].severity).toBe('CRITICAL');
    });

    it('Test 33: should detect CWE-78 Command Injection in child_process exec', () => {
      const code = `const { exec } = require('child_process'); exec("ping " + req.query.host);`;
      const vulns = runSecurityAudit(code, 'shell.ts', 'typescript');
      expect(vulns.some(v => v.cwe === 'CWE-78')).toBe(true);
      expect(vulns[0].severity).toBe('HIGH');
    });

    it('Test 34: should detect CWE-22 Path Traversal vulnerabilities', () => {
      const code = `fs.readFile(path.join('/tmp', req.query.filename), 'utf8');`;
      const vulns = runSecurityAudit(code, 'file.ts', 'typescript');
      expect(vulns.some(v => v.cwe === 'CWE-22')).toBe(true);
      expect(vulns[0].severity).toBe('HIGH');
    });

    it('Test 35: should detect CWE-120 C/C++ Unbounded String Copy (Buffer Overflow)', () => {
      const code = `char buf[64]; strcpy(buf, input_str);`;
      const vulns = runSecurityAudit(code, 'main.cpp', 'cpp');
      expect(vulns.some(v => v.cwe === 'CWE-120')).toBe(true);
      expect(vulns[0].severity).toBe('HIGH');
    });

    it('Test 36: should report zero vulnerabilities for secure, clean code', () => {
      const code = `function safeAdd(a: number, b: number): number { return a + b; }`;
      const vulns = runSecurityAudit(code, 'safe.ts', 'typescript');
      expect(vulns.length).toBe(0);
    });

    it('Test 37: should pinpoint exact line numbers for security findings', () => {
      const code = `// Line 1\n// Line 2\nconst bearer = "bearer_secret_1234567890";`;
      const vulns = runSecurityAudit(code, 'app.ts', 'typescript');
      expect(vulns[0].line).toBe(3);
    });

    it('Test 38: should provide actionable remediation guidance for all vulnerabilities', () => {
      const code = `const secret = "password_1234567890";`;
      const vulns = runSecurityAudit(code, 'auth.ts', 'typescript');
      expect(vulns[0].remediation.length).toBeGreaterThan(15);
    });

    it('Test 39: should detect multiple vulnerabilities in a single file', () => {
      const code = `const secret = "password_1234567890";\nconst q = "SELECT * FROM users WHERE u = '" + param + "'";`;
      const vulns = runSecurityAudit(code, 'vulnerable.ts', 'typescript');
      expect(vulns.length).toBe(2);
    });

    it('Test 40: should scan Python code for hardcoded secrets', () => {
      const code = `auth_token = "secret_1234567890123456"`;
      const vulns = runSecurityAudit(code, 'main.py', 'python');
      expect(vulns.length).toBe(1);
    });

    it('Test 41: should scan C++ code for unsafe sprintf calls', () => {
      const code = `char out[32]; sprintf(out, "%s", user_input);`;
      const vulns = runSecurityAudit(code, 'app.cpp', 'cpp');
      expect(vulns.some(v => v.cwe === 'CWE-120')).toBe(true);
    });

    it('Test 42: should verify presence of pentest tools inventory', () => {
      expect(KALI_PARROT_PENTEST_TOOLS.length).toBeGreaterThanOrEqual(8);
    });

    it('Test 43: should verify Nmap recon tool definition', () => {
      const nmap = KALI_PARROT_PENTEST_TOOLS.find(t => t.id === 'nmap');
      expect(nmap).toBeDefined();
      expect(nmap?.installed).toBe(true);
    });

    it('Test 44: should verify Wireshark packet sniffer tool definition', () => {
      const wireshark = KALI_PARROT_PENTEST_TOOLS.find(t => t.id === 'wireshark');
      expect(wireshark).toBeDefined();
      expect(wireshark?.category).toBe('Packet Sniffer');
    });

    it('Test 45: should verify Metasploit framework tool definition', () => {
      const msf = KALI_PARROT_PENTEST_TOOLS.find(t => t.id === 'metasploit');
      expect(msf).toBeDefined();
      expect(msf?.category).toBe('Exploit Framework');
    });
  });

  // ==========================================
  // 4. Polyglot Database Studio Engine (Tests 46-55)
  // ==========================================
  describe('4. Polyglot Database Studio Engine', () => {
    it('Test 46: should execute SELECT queries on users table returning mock rows', () => {
      const res = executeSqlQuery('SELECT * FROM users;', 'sqlite');
      expect(res.rowCount).toBe(5);
      expect(res.columns).toContain('username');
      expect(res.rows[0].username).toBe('alex_dev');
    });

    it('Test 47: should execute SELECT queries on projects table returning mock rows', () => {
      const res = executeSqlQuery('SELECT * FROM projects;', 'postgresql');
      expect(res.rowCount).toBe(3);
      expect(res.columns).toContain('title');
      expect(res.rows[0].title).toBe('Autonomous-AI-IDE');
    });

    it('Test 48: should return MongoDB JSON document structures for NoSQL queries', () => {
      const res = executeSqlQuery('db.users.find()', 'mongodb');
      expect(res.rowCount).toBe(3);
      expect(res.columns).toContain('_id');
      expect(res.columns).toContain('document_JSON');
    });

    it('Test 49: should execute generic SQL statements returning success confirmation', () => {
      const res = executeSqlQuery('CREATE TABLE test (id INT);', 'mysql');
      expect(res.rowCount).toBe(1);
      expect(res.rows[0].status).toBe('SUCCESS');
    });

    it('Test 50: should measure execution time in milliseconds', () => {
      const res = executeSqlQuery('SELECT 1;', 'sqlite');
      expect(res.executionTimeMs).toBeGreaterThan(0);
    });

    it('Test 51: should export database result sets to valid CSV format', () => {
      const cols = ['id', 'name'];
      const rows = [{ id: 1, name: 'Alice' }, { id: 2, name: 'Bob' }];
      const csv = exportToCsv(cols, rows);
      expect(csv).toBe('id,name\n1,"Alice"\n2,"Bob"');
    });

    it('Test 52: should verify supported database engines count (5 engines)', () => {
      expect(SUPPORTED_DATABASES.length).toBe(5);
    });

    it('Test 53: should verify PostgreSQL engine default port 5432', () => {
      const pg = SUPPORTED_DATABASES.find(d => d.type === 'postgresql');
      expect(pg?.defaultPort).toBe(5432);
    });

    it('Test 54: should verify sample database schema tables count (3 tables)', () => {
      expect(SAMPLE_DATABASE_TABLES.length).toBe(3);
      expect(SAMPLE_DATABASE_TABLES[0].name).toBe('users');
    });

    it('Test 55: should handle empty/null cell values in CSV export', () => {
      const cols = ['id', 'val'];
      const rows = [{ id: 1, val: null }];
      const csv = exportToCsv(cols, rows);
      expect(csv).toBe('id,val\n1,""');
    });
  });

  // ==========================================
  // 5. Software Editions & Feature Matrix (Tests 56-68)
  // ==========================================
  describe('5. Software Editions & Feature Matrix', () => {
    it('Test 56: should verify Community Edition configuration metadata', () => {
      expect(EDITIONS_CONFIG.community.name).toBe('Community Edition');
      expect(EDITIONS_CONFIG.community.bundleSizeEstimate).toContain('1.5 GB');
    });

    it('Test 57: should verify Professional Edition configuration metadata', () => {
      expect(EDITIONS_CONFIG.professional.name).toBe('Professional Edition');
      expect(EDITIONS_CONFIG.professional.bundleSizeEstimate).toContain('4.8 GB');
    });

    it('Test 58: should verify Ultimate Edition configuration metadata', () => {
      expect(EDITIONS_CONFIG.ultimate.name).toBe('Ultimate Edition');
      expect(EDITIONS_CONFIG.ultimate.bundleSizeEstimate).toContain('9.2 GB');
    });

    it('Test 59: should verify code editor is available in all editions', () => {
      expect(isFeatureAvailable('editor', 'community')).toBe(true);
      expect(isFeatureAvailable('editor', 'professional')).toBe(true);
      expect(isFeatureAvailable('editor', 'ultimate')).toBe(true);
    });

    it('Test 60: should verify benchmarking feature availability', () => {
      expect(isFeatureAvailable('benchmarking', 'community')).toBe(false);
      expect(isFeatureAvailable('benchmarking', 'professional')).toBe(true);
      expect(isFeatureAvailable('benchmarking', 'ultimate')).toBe(true);
    });

    it('Test 61: should verify database studio feature availability', () => {
      expect(isFeatureAvailable('database', 'community')).toBe(false);
      expect(isFeatureAvailable('database', 'professional')).toBe(true);
      expect(isFeatureAvailable('database', 'ultimate')).toBe(true);
    });

    it('Test 62: should verify mobile simulator availability only in Ultimate edition', () => {
      expect(isFeatureAvailable('mobile', 'community')).toBe(false);
      expect(isFeatureAvailable('mobile', 'professional')).toBe(false);
      expect(isFeatureAvailable('mobile', 'ultimate')).toBe(true);
    });

    it('Test 63: should verify extension marketplace availability only in Ultimate edition', () => {
      expect(isFeatureAvailable('extensions', 'community')).toBe(false);
      expect(isFeatureAvailable('extensions', 'professional')).toBe(false);
      expect(isFeatureAvailable('extensions', 'ultimate')).toBe(true);
    });

    it('Test 64: should verify offline RAG vector indexer availability only in Ultimate edition', () => {
      expect(isFeatureAvailable('rag_ai', 'community')).toBe(false);
      expect(isFeatureAvailable('rag_ai', 'professional')).toBe(false);
      expect(isFeatureAvailable('rag_ai', 'ultimate')).toBe(true);
    });

    it('Test 65: should verify feature matrix total features count (12 features)', () => {
      expect(ALL_IDE_FEATURES.length).toBe(12);
    });

    it('Test 66: should return true for un-registered feature IDs as default fallback', () => {
      expect(isFeatureAvailable('non_existent_feature', 'community')).toBe(true);
    });

    it('Test 67: should check target audiences in edition configurations', () => {
      expect(EDITIONS_CONFIG.community.targetAudience).toContain('Students');
      expect(EDITIONS_CONFIG.professional.targetAudience).toContain('Full-stack');
      expect(EDITIONS_CONFIG.ultimate.targetAudience).toContain('Architects');
    });

    it('Test 68: should verify badge color styles in edition configurations', () => {
      expect(EDITIONS_CONFIG.community.badgeColor).toContain('emerald');
      expect(EDITIONS_CONFIG.professional.badgeColor).toContain('cyan');
      expect(EDITIONS_CONFIG.ultimate.badgeColor).toContain('purple');
    });
  });

  // ==========================================
  // 6. Extension Marketplace Engine (Tests 69-75)
  // ==========================================
  describe('6. Extension Marketplace Engine', () => {
    it('Test 69: should return initial list of extensions', () => {
      const all = extensionEngine.getAllExtensions();
      expect(all.length).toBeGreaterThanOrEqual(6);
    });

    it('Test 70: should search extensions by exact title', () => {
      const res = extensionEngine.searchExtensions('Pyright');
      expect(res.length).toBe(1);
      expect(res[0].id).toBe('ext-pyright');
    });

    it('Test 71: should search extensions by category key', () => {
      const res = extensionEngine.searchExtensions('AI');
      expect(res.length).toBeGreaterThan(0);
      expect(res.some(e => e.category === 'AI')).toBe(true);
    });

    it('Test 72: should return all extensions when search query is empty', () => {
      const res = extensionEngine.searchExtensions('');
      expect(res.length).toBe(extensionEngine.getAllExtensions().length);
    });

    it('Test 73: should install an uninstalled extension by ID', () => {
      const res = extensionEngine.installExtension('ext-rust-analyzer');
      expect(res).toBe(true);
      const ext = extensionEngine.getAllExtensions().find(e => e.id === 'ext-rust-analyzer');
      expect(ext?.installed).toBe(true);
    });

    it('Test 74: should uninstall an installed extension by ID', () => {
      const res = extensionEngine.uninstallExtension('ext-pyright');
      expect(res).toBe(true);
      const ext = extensionEngine.getAllExtensions().find(e => e.id === 'ext-pyright');
      expect(ext?.installed).toBe(false);
    });

    it('Test 75: should return false when installing a non-existent extension ID', () => {
      const res = extensionEngine.installExtension('invalid-id-xyz');
      expect(res).toBe(false);
    });
  });

  // ==========================================
  // 7. Offline RAG & AI Assistant Engine (Tests 76-85)
  // ==========================================
  describe('7. Offline RAG & AI Assistant Engine (SARASVATĪ Engine)', () => {
    it('Test 76: should perform offline vector RAG search matching query terms', () => {
      const results = performOfflineRAGSearch('python GIL');
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].title).toContain('GIL');
    });

    it('Test 77: should sort RAG search results descending by similarity score', () => {
      const results = performOfflineRAGSearch('C++ STL map');
      expect(results[0].similarityScore).toBeGreaterThanOrEqual(results[1].similarityScore);
    });

    it('Test 78: should cap RAG search maximum similarity score at 98%', () => {
      const results = performOfflineRAGSearch('python standard library GIL epoll');
      expect(results[0].similarityScore).toBeLessThanOrEqual(0.98);
    });

    it('Test 79: should process AI query with RAG search keyword', () => {
      const msg = processAIQuery('search knowledge for Rust lifetimes');
      expect(msg.content).toContain('Offline Local RAG Vector Search Results');
    });

    it('Test 80: should process AI query with code explanation keyword', () => {
      const msg = processAIQuery('explain how this code works', 'let x = 10;', 'typescript');
      expect(msg.content).toContain('Code Explanation');
      expect(msg.content).toContain('Complexity Breakdown');
    });

    it('Test 81: should prompt for file when explain keyword is used without code', () => {
      const msg = processAIQuery('explain this code');
      expect(msg.content).toContain('Please open a file');
    });

    it('Test 82: should process AI query with optimize/refactor keyword', () => {
      const code = `function dup(a) { for(let i=0;i<a.length;i++) { for(let j=0;j<a.length;j++) {} } }`;
      const msg = processAIQuery('optimize this code', code, 'typescript');
      expect(msg.content).toContain('Make It Better');
      expect(msg.codeSnippet).toBeDefined();
    });

    it('Test 83: should process AI query with unit test generation keyword for Python', () => {
      const msg = processAIQuery('generate unit test', 'def add(a, b): return a + b', 'python');
      expect(msg.content).toContain('Unit Test Suite Generated');
      expect(msg.codeSnippet?.language).toBe('python');
    });

    it('Test 84: should process AI query with unit test generation keyword for TypeScript', () => {
      const msg = processAIQuery('generate unit test', 'function add(a,b){return a+b;}', 'typescript');
      expect(msg.content).toContain('Unit Test Suite Generated');
      expect(msg.codeSnippet?.language).toBe('typescript');
    });

    it('Test 85: should process AI query with security audit keyword', () => {
      const msg = processAIQuery('security audit', 'const secret = "password_1234567890"', 'typescript');
      expect(msg.content).toContain('Security Audit Results');
    });
  });

  // ==========================================
  // 8. Educational Demos Visualizer (Tests 86-90)
  // ==========================================
  describe('8. Educational Algorithmic Demos Engine', () => {
    it('Test 86: should contain at least 8 educational algorithmic demos', () => {
      expect(EDUCATIONAL_DEMOS.length).toBeGreaterThanOrEqual(8);
    });

    it('Test 87: should verify presence of all core control flow demos', () => {
      const ids = EDUCATIONAL_DEMOS.map(d => d.id);
      expect(ids).toContain('if-else-if-demo');
      expect(ids).toContain('switch-case-demo');
      expect(ids).toContain('for-loop-demo');
      expect(ids).toContain('while-loop-deep-dive');
      expect(ids).toContain('do-while-loop-demo');
      expect(ids).toContain('recursion-demo');
    });

    it('Test 88: should verify presence of core algorithm demos', () => {
      const ids = EDUCATIONAL_DEMOS.map(d => d.id);
      expect(ids).toContain('binary-search-vs-linear');
      expect(ids).toContain('quicksort-vs-bubblesort');
    });

    it('Test 89: should include step-by-step visualizer definitions in binary search demo', () => {
      const bs = EDUCATIONAL_DEMOS.find(d => d.id === 'binary-search-vs-linear');
      expect(bs?.visualizerSteps).toBeDefined();
      expect(bs?.visualizerSteps?.length).toBeGreaterThan(0);
    });

    it('Test 90: should include execution flow and complexity metadata in all demos', () => {
      EDUCATIONAL_DEMOS.forEach(demo => {
        expect(demo.explanation.executionFlow.length).toBeGreaterThan(0);
        expect(demo.explanation.complexity.time).toBeDefined();
        expect(demo.explanation.complexity.space).toBeDefined();
      });
    });
  });

  // ==========================================
  // 9. Intelligent Subsystems Architecture (Tests 91-95)
  // ==========================================
  describe('9. Intelligent Subsystems Architecture', () => {
    it('Test 91: should verify all 4 specialized intelligent subsystems exist', () => {
      const subsystems = getAllSubsystems();
      expect(subsystems.length).toBe(4);
    });

    it('Test 92: should verify Sanskrit engine names (Sarasvatī, Kālī, Mahālakṣmī, Vaishnavī)', () => {
      const names = getAllSubsystems().map(s => s.name);
      expect(names).toContain('SARASVATĪ');
      expect(names).toContain('KĀLĪ');
      expect(names).toContain('MAHĀLAKṢMĪ');
      expect(names).toContain('VAISHNAVĪ');
    });

    it('Test 93: should verify all subsystems are marked IMPLEMENTED, TESTED, VERIFIED', () => {
      getAllSubsystems().forEach(sub => {
        expect(sub.status).toEqual(['IMPLEMENTED', 'TESTED', 'VERIFIED']);
      });
    });

    it('Test 94: should retrieve specific subsystem by ID', () => {
      const sub = getSubsystemById('sarasvati');
      expect(sub).toBeDefined();
      expect(sub?.tagline).toBe('Knowledge & Learning Engine');
    });

    it('Test 95: should verify non-empty responsibilities list for all subsystems', () => {
      getAllSubsystems().forEach(sub => {
        expect(sub.responsibilities.length).toBeGreaterThan(5);
      });
    });
  });

  // ==========================================
  // 10. Cross-Platform Utilities & Studios (Tests 96-100)
  // ==========================================
  describe('10. Cross-Platform Utilities & Studio Engines', () => {
    it('Test 96: should detect network status and offline capabilities', () => {
      const diag = detectNetworkStatus();
      expect(diag.isOfflineCapable).toBe(true);
      expect(diag.activeInterfaces).toContain('lo');
    });

    it('Test 97: should validate security origin for localhost vs remote URLs', () => {
      const localRes = validateSecurityOrigin('http://localhost:5173');
      expect(localRes.isSecure).toBe(true);
      expect(localRes.isLocalhost).toBe(true);

      const insecureRes = validateSecurityOrigin('http://example-plain.com');
      expect(insecureRes.isSecure).toBe(false);
      expect(insecureRes.warning).toContain('Unencrypted');
    });

    it('Test 98: should render SVG graphic canvas from graphic layers', () => {
      const svg = exportSvgCanvas(INITIAL_GRAPHIC_LAYERS);
      expect(svg).toContain('<svg');
      expect(svg).toContain('MEDHĀ Motion & Graphic Studio');
    });

    it('Test 99: should generate valid CSS filter string for photo editing', () => {
      const cssFilter = getCssFilterString(DEFAULT_PHOTO_FILTERS);
      expect(cssFilter).toContain('brightness(100%)');
      expect(cssFilter).toContain('blur(0px)');
    });

    it('Test 100: should generate valid 2D/3D game engine script bundle', () => {
      const gameScript = generateGameCodeScript(INITIAL_GAME_ENTITIES);
      expect(gameScript).toContain('MEDHĀEngineGame');
      expect(gameScript).toContain('this.isRunning = false;');
    });

    it('Test 101: should scan local hardware environment and report system compiler toolchains', () => {
      const env = scanSystemEnvironment();
      expect(env.os).toBeDefined();
      expect(env.cpuCores).toBeGreaterThan(0);
      expect(env.tools.length).toBeGreaterThan(0);
      expect(env.tools.some(t => t.category === 'Compiler')).toBe(true);
    });
  });
});
