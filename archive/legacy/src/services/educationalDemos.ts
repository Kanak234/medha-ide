import { EducationalDemo } from '../types';

export const EDUCATIONAL_DEMOS: EducationalDemo[] = [
  {
    id: 'if-else-if-demo',
    category: 'Control Flow',
    title: 'Conditional Branching: if / else-if / else',
    subtitle: 'Evaluating multi-condition decisions and short-circuit evaluation',
    description: 'Demonstrates sequential condition evaluation, short-circuit boolean logic, and branching performance.',
    language: 'javascript',
    code: `// Multi-condition grade evaluator
function evaluateGrade(score) {
  if (score >= 90) {
    return 'A - Outstanding';
  } else if (score >= 80) {
    return 'B - Excellent';
  } else if (score >= 70) {
    return 'C - Good';
  } else if (score >= 60) {
    return 'D - Satisfactory';
  } else {
    return 'F - Needs Improvement';
  }
}`,
    badCode: `// Bad: Unnecessary nested conditions & non-short-circuiting
function evaluateGradeBad(score) {
  if (score >= 90) {
    return 'A';
  } else {
    if (score >= 80) {
      if (score < 90) {
        return 'B';
      }
    }
    // Messy nesting increases cyclomatic complexity to 6!
  }
}`,
    goodCode: `// Good: Guard clauses or direct ordered evaluation
function evaluateGradeGood(score) {
  if (score < 0 || score > 100) return 'Invalid Score';
  if (score >= 90) return 'A';
  if (score >= 80) return 'B';
  if (score >= 70) return 'C';
  return 'F';
}`,
    explanation: {
      whenToUse: 'Use when evaluating non-contiguous ranges (e.g. score >= 90), complex boolean formulas, or non-integral expressions.',
      whenNotToUse: 'Do not use when checking a single integer or enum variable against multiple distinct constants—use switch/case instead.',
      executionFlow: [
        'Evaluates condition score >= 90 first.',
        'If true, executes branch A and immediately exits (short-circuits remaining checks).',
        'If false, proceeds down the chain sequentially.'
      ],
      advantages: [
        'Flexible expression support',
        'Early return prevents unnecessary checks',
        'Supports range comparisons (>, <, >=, <=)'
      ],
      disadvantages: [
        'Sequential O(n) condition evaluation if many branches exist',
        'Can become hard to read if nested deeply'
      ],
      complexity: {
        time: 'O(1)',
        space: 'O(1)'
      }
    },
    visualizerSteps: [
      { stepIndex: 0, description: 'Input score = 85. Evaluating score >= 90', state: { score: 85, activeBranch: 'if (score >= 90)', result: false }, highlightLine: 3 },
      { stepIndex: 1, description: 'False. Evaluating score >= 80', state: { score: 85, activeBranch: 'else if (score >= 80)', result: true }, highlightLine: 5 },
      { stepIndex: 2, description: 'True! Branch selected: B - Excellent. Return statement executed.', state: { score: 85, activeBranch: 'return B - Excellent', result: 'B - Excellent' }, highlightLine: 6 }
    ]
  },
  {
    id: 'switch-case-demo',
    category: 'Control Flow',
    title: 'Switch / Case vs if-else Chain',
    subtitle: 'Constant-time dispatch tables vs linear condition chains',
    description: 'Compares switch statement jump tables against sequential if/else-if evaluations.',
    language: 'cpp',
    code: `// C++ Switch Statement with Jump Table optimization
enum Status { IDLE, PROCESSING, SUCCESS, FAILED };

const char* getStatusMessage(Status s) {
    switch (s) {
        case IDLE:       return "System ready for input";
        case PROCESSING: return "Task currently in progress";
        case SUCCESS:    return "Task finished successfully";
        case FAILED:     return "Execution encountered error";
        default:         return "Unknown status code";
    }
}`,
    explanation: {
      whenToUse: 'Use when switching on discrete values (integers, enums, characters, strings). Compilers build jump tables for O(1) branch dispatch!',
      whenNotToUse: 'Do not use for relational floating point range comparisons.',
      executionFlow: [
        'Reads discrete value key.',
        'Compiler indexes directly into jump table array.',
        'Jumps instantly to matching case offset in constant time.'
      ],
      advantages: [
        'Extremely fast branch dispatch via compiler jump table',
        'Cleaner, structured code for state machines and enums',
        'Compiler warns on unhandled enum values'
      ],
      disadvantages: [
        'Risk of fall-through if break or return statement is omitted',
        'Only supports discrete constant match keys'
      ],
      complexity: {
        time: 'O(1)',
        space: 'O(1)'
      }
    }
  },
  {
    id: 'for-loop-demo',
    category: 'Control Flow',
    title: 'For Loop & Iterative Indexing',
    subtitle: 'Deterministic counter iteration, index safety, and vectorization',
    description: 'Demonstrates deterministic iteration using for loops over indexed arrays.',
    language: 'typescript',
    code: `// Deterministic for loop array processing
function calculateSum(numbers: number[]): number {
  let sum = 0;
  for (let i = 0; i < numbers.length; i++) {
    sum += numbers[i];
  }
  return sum;
}`,
    explanation: {
      whenToUse: 'Use when the exact number of iterations or range is known beforehand.',
      whenNotToUse: 'Do not use when waiting for arbitrary external events—use while loops instead.',
      executionFlow: [
        'Initializes counter variable i = 0.',
        'Checks loop condition i < numbers.length.',
        'Executes loop body and increments i++.'
      ],
      advantages: [
        'Deterministic execution bound',
        'Supports SIMD vectorization optimizations in compilers'
      ],
      disadvantages: [
        'Off-by-one errors if index bounds are misconfigured'
      ],
      complexity: {
        time: 'O(n)',
        space: 'O(1)'
      }
    }
  },
  {
    id: 'while-loop-deep-dive',
    category: 'Control Flow',
    title: 'While Loop Deep Dive: Proper vs Problematic Usage',
    subtitle: 'Indefinite iteration, streaming input, and safe termination guarantees',
    description: 'Examines while loop execution patterns, termination condition safety, and avoiding infinite loops.',
    language: 'python',
    code: `# Proper While Loop: Reading stream with safe termination condition
def process_data_stream(stream):
    max_reads = 1000  # Safety circuit breaker against infinite loops
    reads = 0
    
    while stream.has_next() and reads < max_reads:
        data = stream.read_chunk()
        process(data)
        reads += 1
        
    return reads`,
    badCode: `# Bad: Missing loop increment or flawed termination condition!
def bad_while_loop(n):
    i = 0
    while i != n:  # Dangerous! If n is negative or floats, loops forever!
        print(i)
        # Forget i += 1 or wrong step size leads to CPU 100% lockup!`,
    goodCode: `# Good: Deterministic bound & explicit loop step
def good_while_loop(n):
    i = 0
    while i < n:
        print(i)
        i += 1`,
    explanation: {
      whenToUse: 'Use when the exact number of iterations is NOT known beforehand (e.g. socket polling, stream reading, user prompt loop).',
      whenNotToUse: 'Do not use when iterating over known ranges or array indices—use for loop or foreach instead.',
      executionFlow: [
        'Checks condition at the top of loop.',
        'If true, executes loop body.',
        'Re-evaluates condition after every iteration until false.'
      ],
      advantages: [
        'Handles unknown event counts',
        'Clean expression of polling states'
      ],
      disadvantages: [
        'Risk of infinite loop if state mutated incorrectly inside loop body'
      ],
      complexity: {
        time: 'O(n)',
        space: 'O(1)'
      }
    }
  },
  {
    id: 'do-while-loop-demo',
    category: 'Control Flow',
    title: 'Do-While Loop: Guaranteed Minimum Execution',
    subtitle: 'Post-test conditional loop evaluating condition after first iteration',
    description: 'Demonstrates do-while loops ensuring the body executes at least once regardless of initial condition state.',
    language: 'cpp',
    code: `// C++ Do-While Loop for Interactive Input Validation
#include <iostream>

void promptUserUntilValid() {
    int input;
    do {
        std::cout << "Enter a positive integer (> 0): ";
        std::cin >> input;
    } while (input <= 0); // Condition checked AFTER body execution
    
    std::cout << "Valid input received: " << input << std::endl;
}`,
    explanation: {
      whenToUse: 'Use when the body MUST execute at least once before checking the condition (e.g. user prompts, menu selection).',
      whenNotToUse: 'Do not use if zero execution is required when condition is initially false.',
      executionFlow: [
        'Executes body statements unconditionally on 1st run.',
        'Evaluates condition at bottom of loop.',
        'Repeats if condition is true.'
      ],
      advantages: [
        'Guarantees at least 1 execution pass',
        'Eliminates duplicate initialization code before loop'
      ],
      disadvantages: [
        'Can execute unintended side effects if initial state is invalid'
      ],
      complexity: {
        time: 'O(n)',
        space: 'O(1)'
      }
    }
  },
  {
    id: 'recursion-demo',
    category: 'Control Flow',
    title: 'Recursion & Call Stack Dynamics',
    subtitle: 'Base cases, recursive reduction, stack frame allocation, and tail-call optimization',
    description: 'Visualizes recursive function calls, call stack depth, and base case guard conditions.',
    language: 'python',
    code: `# Recursive Factorial Computation
def factorial(n: int) -> int:
    # Base Case Guard
    if n <= 1:
        return 1
    # Recursive Case
    return n * factorial(n - 1)`,
    badCode: `# Bad: Missing Base Case leads to StackOverflow / RecursionError!
def infinite_recursion(n):
    return n * infinite_recursion(n - 1)  # Never terminates!`,
    goodCode: `# Good: Explicit Base Case + Tail-Call Optimization style
def factorial_tail(n: int, accumulator: int = 1) -> int:
    if n <= 1:
        return accumulator
    return factorial_tail(n - 1, n * accumulator)`,
    explanation: {
      whenToUse: 'Use for self-similar problem decomposition like tree traversals, graph DFS, and divide-and-conquer.',
      whenNotToUse: 'Avoid deep recursion in non-tail-optimized languages due to stack overflow risk.',
      executionFlow: [
        'Pushes stack frame for call factorial(n).',
        'Checks base case guard n <= 1.',
        'Recursively invokes factorial(n-1) until base case is reached, then unwinds stack.'
      ],
      advantages: [
        'Elegant expression of recursive data structures (Trees/Graphs)',
        'Simplifies divide-and-conquer logic'
      ],
      disadvantages: [
        'O(n) call stack space overhead',
        'Risk of Stack Overflow'
      ],
      complexity: {
        time: 'O(n)',
        space: 'O(n)'
      }
    }
  },
  {
    id: 'binary-search-vs-linear',
    category: 'Algorithms',
    title: 'Binary Search O(log n) vs Linear Search O(n)',
    subtitle: 'Divide-and-conquer logarithmic scaling vs linear scanning',
    description: 'Visually compares searching elements in sorted datasets using O(log n) binary search against O(n) linear scanning.',
    language: 'typescript',
    code: `// Binary Search O(log n) on Sorted Array
function binarySearch(arr: number[], target: number): number {
  let low = 0;
  let high = arr.length - 1;

  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    if (arr[mid] === target) return mid; // Target found!
    if (arr[mid] < target) {
      low = mid + 1;  // Discard left half
    } else {
      high = mid - 1; // Discard right half
    }
  }

  return -1; // Target absent
}`,
    badCode: `// Linear Search O(n) - Inspects every single element sequentially
function linearSearch(arr: number[], target: number): number {
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] === target) return i;
  }
  return -1;
}`,
    goodCode: `// Binary search O(log n) - Requires sorted array
// Reduces 1,000,000 items to at most 20 comparisons!`,
    explanation: {
      whenToUse: 'Use Binary Search on sorted datasets! For 1,000,000 elements, linear search takes 1,000,000 operations while binary search takes only 20!',
      whenNotToUse: 'Do not use on unsorted arrays unless doing multiple queries (where sorting once O(n log n) pays off).',
      executionFlow: [
        'Calculates midpoint index mid = (low + high) / 2.',
        'Compares arr[mid] with target.',
        'Eliminates half of remaining search space per step.'
      ],
      advantages: [
        'Logarithmic time complexity O(log n)',
        'Extremely fast for massive datasets'
      ],
      disadvantages: [
        'Requires data to be sorted first'
      ],
      complexity: {
        time: 'O(log n)',
        space: 'O(1)'
      }
    },
    visualizerSteps: [
      { stepIndex: 0, description: 'Sorted Array: [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]. Target = 23.', state: { low: 0, high: 9, mid: 4, midVal: 16, target: 23, action: '16 < 23 -> Discard left half [2..16]' }, highlightLine: 6 },
      { stepIndex: 1, description: 'Adjust bounds: low = 5, high = 9. Mid = 7 (val = 56).', state: { low: 5, high: 9, mid: 7, midVal: 56, target: 23, action: '56 > 23 -> Discard right half [56..91]' }, highlightLine: 10 },
      { stepIndex: 2, description: 'Adjust bounds: low = 5, high = 6. Mid = 5 (val = 23).', state: { low: 5, high: 6, mid: 5, midVal: 23, target: 23, action: 'FOUND at index 5!' }, highlightLine: 7 }
    ]
  },
  {
    id: 'quicksort-vs-bubblesort',
    category: 'Algorithms',
    title: 'Quicksort O(n log n) vs Bubble Sort O(n²)',
    subtitle: 'Divide-and-conquer partitioning vs quadratic pairwise swaps',
    description: 'Demonstrates why asymptotic time complexity matters dramatically as dataset size grows.',
    language: 'cpp',
    code: `// Quicksort O(n log n) in-place partitioning algorithm
int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = (low - 1);
    for (int j = low; j <= high - 1; j++) {
        if (arr[j] < pivot) {
            i++;
            std::swap(arr[i], arr[j]);
        }
    }
    std::swap(arr[i + 1], arr[high]);
    return (i + 1);
}

void quickSort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}`,
    explanation: {
      whenToUse: 'Use Quicksort or Mergesort for general sorting. Quicksort has low memory overhead O(log n stack) and high cache locality.',
      whenNotToUse: 'Do not use Bubble Sort in real applications; it executes n² swaps!',
      executionFlow: [
        'Picks pivot element.',
        'Partitions array so elements smaller than pivot go left, larger go right.',
        'Recursively sorts sub-arrays.'
      ],
      advantages: [
        'Average O(n log n) performance',
        'In-place cache-friendly sorting'
      ],
      disadvantages: [
        'Worst case O(n²) if pivot selection is unrandomized on already sorted array'
      ],
      complexity: {
        time: 'O(n log n)',
        space: 'O(log n)'
      }
    }
  }
];
