import { describe, it, expect } from 'vitest';
import { detectLanguageToolchain, getAllSupportedToolchains } from '../toolchainManager';
import { executeVaishnaviOrchestration, parseCompilerDiagnostics } from '../vaishnaviEngine';
import { defaultTerminalBridge } from '../terminalBridge';

describe('VAISHNAVĪ Engine & Real Toolchain Suite', () => {
  it('should detect GCC toolchain for C and G++ toolchain for C++', () => {
    const cTool = detectLanguageToolchain('c');
    expect(cTool.compilerName).toContain('GCC');
    expect(cTool.status).toBe('INSTALLED');
    expect(cTool.command).toBe('gcc');

    const cppTool = detectLanguageToolchain('cpp');
    expect(cppTool.compilerName).toContain('G++');
    expect(cppTool.status).toBe('INSTALLED');
    expect(cppTool.command).toBe('g++');
  });

  it('should detect Python, Node/TS, Rust, Go, and Java toolchains', () => {
    const py = detectLanguageToolchain('python');
    expect(py.command).toBe('python3');
    expect(py.status).toBe('INSTALLED');

    const ts = detectLanguageToolchain('typescript');
    expect(ts.command).toBe('node');
    expect(ts.status).toBe('INSTALLED');

    const rs = detectLanguageToolchain('rust');
    expect(rs.command).toBe('rustc');

    const go = detectLanguageToolchain('go');
    expect(go.command).toBe('go');

    const java = detectLanguageToolchain('java');
    expect(java.command).toBe('javac');
  });

  it('should parse GCC diagnostic errors with exact line and column numbers', () => {
    const gccErr = 'main.cpp:14:8: error: "x" was not declared in this scope';
    const diags = parseCompilerDiagnostics(gccErr, 'main.cpp', 'cpp');
    expect(diags.length).toBe(1);
    expect(diags[0].file).toBe('main.cpp');
    expect(diags[0].line).toBe(14);
    expect(diags[0].column).toBe(8);
    expect(diags[0].severity).toBe('error');
    expect(diags[0].message).toContain('was not declared');
  });

  it('should parse Python traceback syntax errors', () => {
    const pyErr = 'File "script.py", line 5, in <module>\n  def test()\nSyntaxError: expected \':\'';
    const diags = parseCompilerDiagnostics(pyErr, 'script.py', 'python');
    expect(diags.length).toBe(1);
    expect(diags[0].line).toBe(5);
    expect(diags[0].severity).toBe('error');
  });

  it('should execute Vaishnavī orchestration on clean JS code and return stdout', async () => {
    const code = 'console.log("MEDHA_ENGINE_ONLINE");';
    const res = await executeVaishnaviOrchestration(code, 'javascript', 'main.js');
    expect(res.success).toBe(true);
    expect(res.exitCode).toBe(0);
    expect(res.stdout).toContain('MEDHA_ENGINE_ONLINE');
    expect(res.executionTimeMs).toBeGreaterThanOrEqual(0);
  });

  it('should execute Vaishnavī orchestration on clean C++ code and return success result', async () => {
    const code = '#include <iostream>\nint main() { std::cout << "C++ Executed" << std::endl; return 0; }';
    const res = await executeVaishnaviOrchestration(code, 'cpp', 'main.cpp');
    expect(res.success).toBe(true);
    expect(res.exitCode).toBe(0);
    expect(res.stdout).toContain('C++ Executed');
  });

  it('should catch missing main function in Rust, Go, and Java source files', async () => {
    const rsRes = await executeVaishnaviOrchestration('fn foo() {}', 'rust', 'main.rs');
    expect(rsRes.success).toBe(false);
    expect(rsRes.exitCode).toBe(1);

    const goRes = await executeVaishnaviOrchestration('package main\nfunc foo() {}', 'go', 'main.go');
    expect(goRes.success).toBe(false);
    expect(goRes.exitCode).toBe(1);

    const javaRes = await executeVaishnaviOrchestration('public class Main { public void foo() {} }', 'java', 'Main.java');
    expect(javaRes.success).toBe(false);
    expect(javaRes.exitCode).toBe(1);
  });
});
