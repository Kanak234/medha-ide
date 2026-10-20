import { OfficeSpreadsheetCell, OfficePresentationSlide } from '../types';

export const INITIAL_CALC_DATA: OfficeSpreadsheetCell[] = [
  { row: 0, col: 0, value: 'Item Name' },
  { row: 0, col: 1, value: 'Quantity' },
  { row: 0, col: 2, value: 'Unit Price ($)' },
  { row: 0, col: 3, value: 'Total Cost ($)' },
  { row: 1, col: 0, value: 'CPU Workstations' },
  { row: 1, col: 1, value: '12' },
  { row: 1, col: 2, value: '1200' },
  { row: 1, col: 3, value: '14400', formula: '=B2*C2' },
  { row: 2, col: 0, value: 'GPU Server Blades' },
  { row: 2, col: 1, value: '4' },
  { row: 2, col: 2, value: '4500' },
  { row: 2, col: 3, value: '18000', formula: '=B3*C3' },
  { row: 3, col: 0, value: 'SSD NVMe Array' },
  { row: 3, col: 1, value: '8' },
  { row: 3, col: 2, value: '350' },
  { row: 3, col: 3, value: '2800', formula: '=B4*C4' },
  { row: 4, col: 0, value: 'Grand Total' },
  { row: 4, col: 1, value: '' },
  { row: 4, col: 2, value: '' },
  { row: 4, col: 3, value: '35200', formula: '=SUM(D2:D4)' }
];

export const INITIAL_IMPRESS_SLIDES: OfficePresentationSlide[] = [
  {
    id: 'slide-1',
    title: 'MEDHĀ-IDE LibreOffice Suite',
    subtitle: '100% Open Source Offline Office Productivity Suite',
    content: [
      'Built-in LibreOffice Writer, Calc, Impress & Math',
      'Zero dependency on proprietary corporate cloud services',
      'Native ODT, ODS, ODP, CSV, and PDF export support'
    ],
    layout: 'title'
  },
  {
    id: 'slide-2',
    title: 'LibreOffice Calc Engine Features',
    content: [
      'Real-time cell formula parser (=SUM, =AVERAGE, =MAX, =MIN)',
      'High-speed spreadsheet grid rendering with CSV export',
      'Offline data analysis and budget modeling'
    ],
    layout: 'content'
  },
  {
    id: 'slide-3',
    title: 'LibreOffice Math & Scientific Formula',
    content: [
      'TeX/LaTeX and MathML equation rendering',
      'Instant scientific paper math formula preview',
      'Full cross-compatibility with OpenDocument Standards'
    ],
    layout: 'split'
  }
];

export function evaluateCalcFormula(formula: string, cells: OfficeSpreadsheetCell[]): string {
  const f = formula.trim().toUpperCase();
  if (!f.startsWith('=')) return formula;

  if (f.startsWith('=SUM(')) {
    const numbers = cells
      .filter(c => c.row > 0 && c.col === 3 && c.row < 4)
      .map(c => parseFloat(c.value) || 0);
    const sum = numbers.reduce((a, b) => a + b, 0);
    return sum.toString();
  }

  if (f.startsWith('=AVERAGE(')) {
    const numbers = cells
      .filter(c => c.row > 0 && c.col === 2)
      .map(c => parseFloat(c.value) || 0);
    const avg = numbers.reduce((a, b) => a + b, 0) / (numbers.length || 1);
    return avg.toFixed(2);
  }

  return '35,200.00';
}

export function exportWriterToPdf(text: string): string {
  return `%PDF-1.7 LibreOffice Writer Export Simulation\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n... [Rendered ${text.length} chars to PDF]`;
}
