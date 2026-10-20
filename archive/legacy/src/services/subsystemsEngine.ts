import { IntelligentSubsystem } from '../types';

export const INTELLIGENT_SUBSYSTEMS: IntelligentSubsystem[] = [
  {
    id: 'sarasvati',
    name: 'SARASVATĪ',
    sanskritName: 'सरस्वती',
    tagline: 'Knowledge & Learning Engine',
    role: 'Knowledge, Learning & Developer Intelligence Engine',
    status: ['IMPLEMENTED', 'TESTED', 'VERIFIED'],
    responsibilities: [
      'code explanation',
      'documentation',
      'offline documentation search',
      'RAG',
      'project knowledge indexing',
      'code comprehension',
      'educational explanations',
      'autocomplete assistance',
      'API documentation',
      'programming tutorials',
      'learning demonstrations',
      'language references',
      'contextual developer assistance'
    ],
    description: 'Sarasvatī helps developers understand WHAT the code does, WHY it works, HOW it works, and HOW it can be improved.'
  },
  {
    id: 'kali',
    name: 'KĀLĪ',
    sanskritName: 'काली',
    tagline: 'Security & Defence Engine',
    role: 'Security, Threat Detection & Defensive Analysis Engine',
    status: ['IMPLEMENTED', 'TESTED', 'VERIFIED'],
    responsibilities: [
      'vulnerability scanning',
      'static security analysis',
      'dependency auditing',
      'secret detection',
      'insecure-code detection',
      'malicious-input analysis',
      'SQL injection detection',
      'XSS detection',
      'command injection detection',
      'path traversal detection',
      'unsafe deserialisation detection',
      'permission analysis',
      'security configuration analysis',
      'workspace-boundary verification',
      'dependency risk analysis'
    ],
    description: 'KĀLĪ is defensive by design. It helps developers identify and fix security problems rather than enabling malicious activity.'
  },
  {
    id: 'mahalakshmi',
    name: 'MAHĀLAKṢMĪ',
    sanskritName: 'महालक्ष्मी',
    tagline: 'Performance & Resource Engine',
    role: 'Performance, Resource & Efficiency Engine',
    status: ['IMPLEMENTED', 'TESTED', 'VERIFIED'],
    responsibilities: [
      'CPU analysis',
      'memory analysis',
      'execution-time measurement',
      'benchmarking',
      'performance profiling',
      'memory optimisation',
      'resource monitoring',
      'performance regression detection',
      'code optimisation',
      'build-performance analysis',
      'application efficiency analysis'
    ],
    description: 'MAHĀLAKṢMĪ compares execution time, memory usage, CPU usage, algorithmic complexity, throughput, and latency from actual real-time execution measurements.'
  },
  {
    id: 'vaishnavi',
    name: 'VAISHNAVĪ',
    sanskritName: 'वैष्णवी',
    tagline: 'Autonomous Execution & Orchestration Engine',
    role: 'Autonomous Development Workflow & Execution Engine',
    status: ['IMPLEMENTED', 'TESTED', 'VERIFIED'],
    responsibilities: [
      'project analysis',
      'build orchestration',
      'compilation',
      'test execution',
      'debugging workflows',
      'dependency management',
      'environment detection',
      'development-server management',
      'browser integration',
      'packaging',
      'installer generation',
      'release workflows',
      'CI/CD assistance',
      'safe automation'
    ],
    description: 'VAISHNAVĪ coordinates development operations while respecting WORKSPACE ONLY restrictions and NEVER DELETE USER FILES protection.'
  }
];

export function getSubsystemById(id: string): IntelligentSubsystem | undefined {
  return INTELLIGENT_SUBSYSTEMS.find(s => s.id === id);
}

export function getAllSubsystems(): IntelligentSubsystem[] {
  return INTELLIGENT_SUBSYSTEMS;
}
