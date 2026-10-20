import { SecurityVulnerability, SupportedLanguage } from '../types';

export interface SecurityPentestTool {
  id: string;
  name: string;
  category: 'Network Recon' | 'Packet Sniffer' | 'Exploit Framework' | 'Web Proxy' | 'Password Cracker' | 'Wireless Pentest';
  installed: boolean;
  version: string;
  description: string;
}

export const KALI_PARROT_PENTEST_TOOLS: SecurityPentestTool[] = [
  { id: 'nmap', name: 'Nmap / Ncat', category: 'Network Recon', installed: true, version: '7.95', description: 'Network exploration, port scanner & service/OS detection engine' },
  { id: 'wireshark', name: 'Wireshark / TShark', category: 'Packet Sniffer', installed: true, version: '4.2.3', description: 'Network packet analyzer & pcap packet inspection' },
  { id: 'metasploit', name: 'Metasploit Framework (MSF)', category: 'Exploit Framework', installed: true, version: '6.4.1', description: 'Penetration testing & vulnerability exploitation payload generator' },
  { id: 'burpsuite', name: 'Burp Suite Proxy', category: 'Web Proxy', installed: true, version: '2024.2', description: 'Web application security scanner & HTTP request intercepting proxy' },
  { id: 'john', name: 'John the Ripper & Hashcat', category: 'Password Cracker', installed: true, version: '1.9.0', description: 'High-speed offline password hash auditing tool' },
  { id: 'hydra', name: 'THC Hydra', category: 'Password Cracker', installed: true, version: '9.5', description: 'Fast network logon brute-forcer for SSH, FTP, RDP, HTTP' },
  { id: 'aircrack', name: 'Aircrack-ng Suite', category: 'Wireless Pentest', installed: true, version: '1.7', description: 'Wi-Fi 802.11 WPA/WPA2/WPA3 network security auditing tool' },
  { id: 'nikto', name: 'Nikto Web Scanner', category: 'Network Recon', installed: true, version: '2.5.0', description: 'Comprehensive web server vulnerability & CGI scanner' }
];

export function runSecurityAudit(code: string, path: string, language: SupportedLanguage): SecurityVulnerability[] {
  const vulnerabilities: SecurityVulnerability[] = [];
  const lines = code.split('\n');

  lines.forEach((line, idx) => {
    const lineNum = idx + 1;
    const trimmed = line.trim();

    // 1. Hardcoded Secret / API Key Detection
    if (/(?:api_key|secret|password|bearer|auth_token)\s*[:=]\s*["'][A-Za-z0-9_\-]{16,}["']/i.test(trimmed)) {
      vulnerabilities.push({
        id: `sec-secret-${lineNum}`,
        severity: 'CRITICAL',
        cwe: 'CWE-798',
        title: 'Hardcoded Plaintext Credentials / Secret Token',
        file: path,
        line: lineNum,
        snippet: trimmed,
        description: 'Hardcoded secret token or password detected in source code. Exposing API keys in source repositories enables unauthorized access and credential leaks.',
        remediation: 'Move secrets to encrypted environment variables or standard .env configuration managed outside VCS.'
      });
    }

    // 2. SQL Injection Vulnerability
    if (/(?:SELECT|INSERT|UPDATE|DELETE).*\+.*(?:req\.query|req\.body|user_input|param)/i.test(trimmed) || /format\(.*SELECT/i.test(trimmed)) {
      vulnerabilities.push({
        id: `sec-sqli-${lineNum}`,
        severity: 'CRITICAL',
        cwe: 'CWE-89',
        title: 'SQL Injection (SQLi) Vulnerability',
        file: path,
        line: lineNum,
        snippet: trimmed,
        description: 'Dynamic SQL query built via string concatenation with un-sanitized user input. Attackers can execute arbitrary SQL statements to exfiltrate or mutate database contents.',
        remediation: 'Use parameterized queries or Object-Relational Mapping (ORM) query builders.'
      });
    }

    // 3. Command Injection / Unsafe Shell Execution
    if (/(?:child_process\.exec|os\.system|eval\(|exec\(|system\()/i.test(trimmed) && !trimmed.includes('// safe')) {
      vulnerabilities.push({
        id: `sec-cmdi-${lineNum}`,
        severity: 'HIGH',
        cwe: 'CWE-78',
        title: 'Command Injection / Unsafe Shell Invocation',
        file: path,
        line: lineNum,
        snippet: trimmed,
        description: 'Direct invocation of system shell via exec() or system(). If argument contains user-controllable input, command injection leads to remote code execution.',
        remediation: 'Use child_process.execFile() or spawn() with explicit string array parameters avoiding shell evaluation.'
      });
    }

    // 4. Path Traversal Vulnerability
    if (/(?:fs\.readFile|open\(|fopen\().*req\.|path\.join\(.*req\./i.test(trimmed)) {
      vulnerabilities.push({
        id: `sec-path-${lineNum}`,
        severity: 'HIGH',
        cwe: 'CWE-22',
        title: 'Path Traversal (Arbitrary File Access)',
        file: path,
        line: lineNum,
        snippet: trimmed,
        description: 'File path constructed directly from user input without canonicalization checks. Attackers can supply ../ sequences to read sensitive system files.',
        remediation: 'Sanitize file paths with path.basename() and verify target remains inside designated WORKSPACE boundary.'
      });
    }

    // 5. Dangerous C/C++ Buffer Overflow Functions
    if ((language === 'c' || language === 'cpp') && /\b(strcpy|strcat|gets|sprintf)\b/.test(trimmed)) {
      vulnerabilities.push({
        id: `sec-buffer-${lineNum}`,
        severity: 'HIGH',
        cwe: 'CWE-120',
        title: 'Unbounded String Copy (Buffer Overflow Risk)',
        file: path,
        line: lineNum,
        snippet: trimmed,
        description: `Use of unsafe function '${trimmed.match(/\b(strcpy|strcat|gets|sprintf)\b/)?.[1]}' without buffer length boundary checks.`,
        remediation: 'Replace with bounded variants like strncpy, strncat, or snprintf.'
      });
    }
  });

  return vulnerabilities;
}

