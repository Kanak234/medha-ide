import { BigONotation, ComplexityResult, SupportedLanguage } from '../types';

export function analyzeCodeComplexity(code: string, language: SupportedLanguage): ComplexityResult {
  const lines = code.split('\n').map(l => l.trim()).filter(l => l.length > 0 && !l.startsWith('//') && !l.startsWith('#'));
  const cleanCode = lines.join(' ');

  let maxLoopDepth = 0;
  let currentLoopDepth = 0;
  let hasLogarithmicLoop = false;
  let hasRecursiveCall = false;
  let hasQuadraticAllocation = false;
  let hasLinearAllocation = false;
  const reasoning: string[] = [];
  const spatialAllocations: string[] = [];

  // Function signature detection for recursion
  const functionMatch = code.match(/(?:function|def|int|void|auto|let|const|fn)\s+([a-zA-Z0-9_]+)\s*\(/);
  const functionName = functionMatch ? functionMatch[1] : null;

  if (functionName) {
    const callCount = (code.match(new RegExp(`\\b${functionName}\\b`, 'g')) || []).length;
    if (callCount > 1) { // 1 for definition, >1 means recursive calls inside body
      hasRecursiveCall = true;
      reasoning.push(`Recursive call to '${functionName}' detected inside function body.`);
    }
  }

  // Analyze loops and control structures
  const loopRegex = /(?:for|while)\s*\(|for\s+[a-zA-Z0-9_]+\s+in\b|while\b/g;
  const matches = [...cleanCode.matchAll(loopRegex)];

  // Simple AST block depth tracker
  let currentDepth = 0;
  for (let i = 0; i < code.length; i++) {
    const char = code[i];
    if (char === '{' || code.substring(i).startsWith(':')) {
      currentDepth++;
    } else if (char === '}') {
      currentDepth = Math.max(0, currentDepth - 1);
    }
  }

  // Detect loop patterns
  if (cleanCode.includes('for') || cleanCode.includes('while')) {
    // Check logarithmic pattern like i /= 2, i *= 2, binary search shift >> 1, mid = (low + high) / 2
    if (cleanCode.includes('/=') || cleanCode.includes('*=') || cleanCode.includes('>>') || cleanCode.includes('<<') || cleanCode.includes('/ 2') || cleanCode.includes('low + high')) {
      hasLogarithmicLoop = true;
      reasoning.push('Logarithmic loop condition detected (problem space halved per iteration e.g. i /= 2 or binary partition).');
    }

    // Count nested loops
    const forCount = (cleanCode.match(/\bfor\b/g) || []).length;
    const whileCount = (cleanCode.match(/\bwhile\b/g) || []).length;
    const totalLoops = forCount + whileCount;

    // Check if loops are nested or sequential
    const isNested = cleanCode.match(/(?:for|while).*[\{\:]\s*(?:for|while)/s) !== null;

    if (isNested) {
      maxLoopDepth = Math.min(3, Math.max(2, totalLoops));
      reasoning.push(`Nested loop structure found (${totalLoops} loop iterations executed within nested scopes).`);
    } else if (totalLoops > 0) {
      maxLoopDepth = 1;
      reasoning.push(`Sequential loop structure detected (${totalLoops} linear iterations over input size n).`);
    }
  } else {
    reasoning.push('No loop or recursion construct found. Execution executes in constant time O(1).');
  }

  // Spatial Allocation Check
  if (cleanCode.match(/new\s+(?:Array|int|double|Object|vector|ArrayList)\[.*\]|\[\s*0\s*\]\s*\*\s*n|\.push\(|\.append\(/)) {
    hasLinearAllocation = true;
    spatialAllocations.push('Dynamic array/list allocation proportional to input size n.');
    reasoning.push('Auxiliary memory allocated dynamically based on input size n.');
  }

  if (cleanCode.match(/\[\s*\[.*\]\s*\]|new\s+int\[.*\]\[.*\]|vector<vector/)) {
    hasQuadraticAllocation = true;
    spatialAllocations.push('2D matrix/grid structure allocation size n × n.');
    reasoning.push('2D matrix data structure allocated in memory.');
  }

  // Time Complexity Determination
  let timeComplexity: BigONotation = 'O(1)';
  let spaceComplexity: BigONotation = 'O(1)';
  let bestCase: BigONotation = 'O(1)';
  let averageCase: BigONotation = 'O(1)';
  let worstCase: BigONotation = 'O(1)';
  let auxiliarySpace = 'O(1)';

  if (hasRecursiveCall) {
    if (hasLogarithmicLoop || cleanCode.includes('/ 2')) {
      timeComplexity = 'O(n log n)';
      worstCase = 'O(n log n)';
      averageCase = 'O(n log n)';
      bestCase = 'O(n log n)';
      spaceComplexity = 'O(log n)';
      auxiliarySpace = 'O(log n) call stack space';
      reasoning.push('Divide and conquer recursive call tree of height log(n) with n operations per level yields O(n log n).');
    } else {
      timeComplexity = 'O(2ⁿ)';
      worstCase = 'O(2ⁿ)';
      averageCase = 'O(2ⁿ)';
      bestCase = 'O(1)';
      spaceComplexity = 'O(n)';
      auxiliarySpace = 'O(n) call stack frame depth';
      reasoning.push('Un-memoized branching recursive call tree generates exponential work O(2^n).');
    }
  } else if (hasLogarithmicLoop) {
    if (maxLoopDepth <= 1) {
      timeComplexity = 'O(log n)';
      worstCase = 'O(log n)';
      averageCase = 'O(log n)';
      bestCase = 'O(1)';
    } else {
      timeComplexity = 'O(n log n)';
      worstCase = 'O(n log n)';
      averageCase = 'O(n log n)';
      bestCase = 'O(log n)';
    }
    reasoning.push('Loop boundary cut logarithmically on every step yielding log(n) operations.');
  } else if (maxLoopDepth === 1) {
    timeComplexity = 'O(n)';
    worstCase = 'O(n)';
    averageCase = 'O(n)';
    bestCase = 'O(1)';
    reasoning.push('Single linear loop iterates n times from start to end condition.');
  } else if (maxLoopDepth === 2) {
    timeComplexity = 'O(n²)';
    worstCase = 'O(n²)';
    averageCase = 'O(n²)';
    bestCase = 'O(n)';
    reasoning.push('Outer loop executes n times; inner loop executes up to n times → n × n = n² total operations.');
  } else if (maxLoopDepth >= 3) {
    timeComplexity = 'O(n³)';
    worstCase = 'O(n³)';
    averageCase = 'O(n³)';
    bestCase = 'O(n²)';
    reasoning.push('Triple nested loop structure detected → cubic complexity O(n³).');
  }

  // Space Complexity Determination
  if (hasQuadraticAllocation) {
    spaceComplexity = 'O(n²)';
    auxiliarySpace = 'O(n²) dynamic grid memory';
  } else if (hasLinearAllocation) {
    spaceComplexity = 'O(n)';
    auxiliarySpace = 'O(n) auxiliary list/buffer';
  }

  return {
    timeComplexity,
    spaceComplexity,
    bestCase,
    averageCase,
    worstCase,
    auxiliarySpace,
    confidence: 95,
    isExact: false,
    reasoning,
    loopDepth: maxLoopDepth,
    recursiveDepth: hasRecursiveCall ? 1 : 0,
    spatialAllocations
  };
}
