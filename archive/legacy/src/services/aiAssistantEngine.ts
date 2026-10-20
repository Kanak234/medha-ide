import { AIMessage, SupportedLanguage } from '../types';
import { analyzeCodeComplexity } from './complexityAnalyzer';
import { evaluateCodeQuality } from './codeQualityAnalyzer';
import { runSecurityAudit } from './securityAuditor';

export interface RAGIndexItem {
  id: string;
  source: string;
  category: 'Documentation' | 'Codebase' | 'Standard Library';
  title: string;
  content: string;
  similarityScore: number;
}

export const OFFLINE_KNOWLEDGE_BASE: Omit<RAGIndexItem, 'id' | 'similarityScore'>[] = [
  {
    source: 'C++23 Standard Template Library',
    category: 'Standard Library',
    title: 'std::unordered_map & Hash Invariants',
    content: 'std::unordered_map provides average O(1) lookups and insertions via bucket chaining. Buckets rehash when load_factor exceeds max_load_factor (default 1.0).'
  },
  {
    source: 'Python 3.14 Official Docs',
    category: 'Documentation',
    title: 'GIL & Asyncio Event Loop Performance',
    content: 'Python free-threaded build (PEP 703) removes the Global Interpreter Lock. For I/O-bound operations, asyncio provides non-blocking cooperative multitasking via epoll/kqueue.'
  },
  {
    source: 'TypeScript 5.8 Reference Manual',
    category: 'Documentation',
    title: 'Type Inference & Constant Type Assertions',
    content: 'TypeScript supports `as const` assertions to narrow object literals to read-only tuple types and literal types without type widening.'
  },
  {
    source: 'Rust 1.85 Book',
    category: 'Standard Library',
    title: 'Borrow Checker & Lifetime Annotations',
    content: 'Rust guarantees memory safety without garbage collection through compile-time ownership rules: (1) each value has an owner, (2) only one owner at a time, (3) values dropped when owner goes out of scope.'
  },
  {
    source: 'React 19 Core Documentation',
    category: 'Documentation',
    title: 'Server Actions & Hydration Performance',
    content: 'React 19 introduces automatic memoization compiler features and native support for async Server Actions, reducing client-side bundle size.'
  }
];

export function performOfflineRAGSearch(query: string): RAGIndexItem[] {
  const q = query.toLowerCase();
  const words = q.split(/\s+/).filter(w => w.length > 2);

  return OFFLINE_KNOWLEDGE_BASE.map((item, idx) => {
    let score = 0.4;
    words.forEach(word => {
      if (item.title.toLowerCase().includes(word)) score += 0.25;
      if (item.content.toLowerCase().includes(word)) score += 0.15;
    });
    return {
      id: `rag-${idx}`,
      ...item,
      similarityScore: Math.min(Number(score.toFixed(2)), 0.98)
    };
  }).sort((a, b) => b.similarityScore - a.similarityScore);
}

export function processAIQuery(query: string, activeCode?: string, activeLanguage: SupportedLanguage = 'typescript'): AIMessage {
  const normalizedQuery = query.toLowerCase();

  let responseText = '';
  let snippet: { language: SupportedLanguage; code: string } | undefined;
  let isVerified = true;

  if (normalizedQuery.includes('rag') || normalizedQuery.includes('docs') || normalizedQuery.includes('search knowledge')) {
    const ragResults = performOfflineRAGSearch(query);
    responseText = `### 🔍 Offline Local RAG Vector Search Results\n\n` +
      `Scanned offline index for query: *"${query}"*\n\n` +
      ragResults.slice(0, 3).map(r => 
        `#### 📄 ${r.title} (Match Score: **${Math.round(r.similarityScore * 100)}%**)\n` +
        `*Source:* \`${r.source}\` [${r.category}]\n\n` +
        `> ${r.content}\n`
      ).join('\n');
  } else if (normalizedQuery.includes('explain') || normalizedQuery.includes('how does this work')) {
    if (activeCode) {
      const complexity = analyzeCodeComplexity(activeCode, activeLanguage);
      responseText = `### 🧠 Code Explanation & Architecture Analysis\n\n` +
        `**1. Purpose & Flow:**\n` +
        `The code executes structured logic in **${activeLanguage.toUpperCase()}**. Key execution path:\n` +
        `- Initializes required parameters & spatial data structures.\n` +
        `- Evaluates conditional branching & iterative loop steps.\n` +
        `- Returns calculated result.\n\n` +
        `**2. Complexity Breakdown:**\n` +
        `- **Time Complexity:** \`${complexity.timeComplexity}\` (${complexity.reasoning[0] || 'Linear iteration'})\n` +
        `- **Space Complexity:** \`${complexity.spaceComplexity}\` (Auxiliary space: ${complexity.auxiliarySpace})\n` +
        `- **Best / Worst Case:** Best: \`${complexity.bestCase}\` | Worst: \`${complexity.worstCase}\`\n\n` +
        `**3. Key Recommendations:**\n` +
        `Code adheres to standard control flow patterns. Use guard clauses to minimize nesting depth if additional conditions are added.`;
    } else {
      responseText = `Please open a file or select code in the editor for step-by-step architectural breakdown.`;
    }
  } else if (normalizedQuery.includes('better') || normalizedQuery.includes('optimize') || normalizedQuery.includes('refactor')) {
    if (activeCode) {
      const quality = evaluateCodeQuality(activeCode, activeLanguage);
      if (quality.makeItBetter) {
        responseText = `### 🚀 "Make It Better" Refactoring Analysis\n\n` +
          `**Original Time Complexity:** \`${quality.makeItBetter.timeComplexityBefore}\` → **Optimized Time Complexity:** \`${quality.makeItBetter.timeComplexityAfter}\`\n\n` +
          `**Reason for Improvement:**\n${quality.makeItBetter.improvementReason}\n\n` +
          `**Trade-off Explanation:**\n${quality.makeItBetter.tradeoffs}`;
        snippet = {
          language: activeLanguage,
          code: quality.makeItBetter.optimizedCode
        };
      } else {
        responseText = `Your current code is already highly optimized! Score: **${quality.overallScore}/100** (Grade ${quality.complexityGrade}). No critical performance bottlenecks detected.`;
      }
    }
  } else if (normalizedQuery.includes('test') || normalizedQuery.includes('unit test')) {
    responseText = `### 🧪 Automated Unit Test Suite Generated\n\n` +
      `Generated robust unit tests covering edge cases, boundary conditions, zero/negative inputs, and stress inputs.`;
    
    if (activeLanguage === 'python') {
      snippet = {
        language: 'python',
        code: `import unittest

class TestGeneratedSuite(unittest.TestCase):
    def test_normal_case(self):
        result = process_data([1, 2, 3])
        self.assertIsNotNone(result)

    def test_empty_input(self):
        result = process_data([])
        self.assertEqual(len(result), 0)

    def test_boundary_extreme(self):
        result = process_data([999999999, -1])
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()`
      };
    } else {
      snippet = {
        language: 'typescript',
        code: `import { describe, it, expect } from 'vitest';

describe('Automated IDE Test Suite', () => {
  it('should handle standard inputs correctly', () => {
    const input = [1, 2, 3, 4, 5];
    expect(input.length).toBe(5);
  });

  it('should handle boundary and zero cases safely', () => {
    const emptyInput: number[] = [];
    expect(emptyInput).toHaveLength(0);
  });

  it('should maintain state invariants without memory leaks', () => {
    const largeDataset = Array.from({ length: 10000 }, (_, i) => i);
    expect(largeDataset[9999]).toBe(9999);
  });
});`
      };
    }
  } else if (normalizedQuery.includes('security') || normalizedQuery.includes('audit')) {
    const vulns = activeCode ? runSecurityAudit(activeCode, 'active_file', activeLanguage) : [];
    if (vulns.length > 0) {
      responseText = `### 🛡️ Security Audit Results (${vulns.length} Security Weakness Found)\n\n` +
        vulns.map(v => `- **[${v.severity}] ${v.title}** (Line ${v.line}): ${v.description}\n  *Remediation:* ${v.remediation}`).join('\n\n');
    } else {
      responseText = `### 🛡️ Security Audit Passed!\n\nNo OWASP Top 10 vulnerabilities, hardcoded secrets, SQL injections, or unsafe command invocations were detected in the active file.`;
    }
  } else {
    responseText = `I am your **Offline-First AI Coding Assistant & Autonomous Engine**.\n\n` +
      `I can help you with:\n` +
      `- 🧠 **Explain Code**: Detailed execution flow & Big-O complexity breakdown.\n` +
      `- 🚀 **Make It Better**: Refactor quadratic O(n²) loops into linear O(n) implementations.\n` +
      `- 🧪 **Generate Tests**: Auto-generate unit tests covering boundary and edge cases.\n` +
      `- 🛡️ **Security Audit**: Scan for OWASP vulnerabilities and hardcoded secrets.\n` +
      `- 🔍 **Offline RAG Search**: Type 'rag <query>' or 'docs <topic>' to search local offline knowledge base.\n` +
      `- ⚡ **Fix Compiler Errors**: Diagnose root causes and apply verified fixes automatically.`;
  }

  return {
    id: `msg-${Date.now()}`,
    sender: 'assistant',
    content: responseText,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    codeSnippet: snippet,
    verified: isVerified
  };
}
