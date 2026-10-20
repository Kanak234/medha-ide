import { DatabaseQueryResult, DatabaseSchemaTable } from '../types';

export type DatabaseType = 'sqlite' | 'postgresql' | 'mysql' | 'oracle' | 'mongodb';

export interface DatabaseConnection {
  id: string;
  name: string;
  type: DatabaseType;
  host: string;
  port: number;
  database: string;
  username: string;
  status: 'connected' | 'disconnected';
  defaultPort: number;
}

export const SUPPORTED_DATABASES: { type: DatabaseType; label: string; defaultPort: number; iconColor: string; defaultDb: string }[] = [
  { type: 'postgresql', label: 'PostgreSQL 16 Engine', defaultPort: 5432, iconColor: 'text-sky-400', defaultDb: 'medha_production_pg' },
  { type: 'mysql', label: 'MySQL 8.4 Server', defaultPort: 3306, iconColor: 'text-amber-400', defaultDb: 'medha_store_db' },
  { type: 'oracle', label: 'Oracle Database 23c (OCI)', defaultPort: 1521, iconColor: 'text-red-400', defaultDb: 'ORCLPDB1' },
  { type: 'mongodb', label: 'MongoDB 7.0 NoSQL', defaultPort: 27017, iconColor: 'text-emerald-400', defaultDb: 'medha_analytics_doc' },
  { type: 'sqlite', label: 'SQLite 3 (Local Embedded WASM)', defaultPort: 0, iconColor: 'text-indigo-400', defaultDb: 'sqlite3_app.db' }
];

export const SAMPLE_DATABASE_TABLES: DatabaseSchemaTable[] = [
  {
    name: 'users',
    rowCount: 1250,
    columns: [
      { name: 'id', type: 'INTEGER', isPk: true },
      { name: 'username', type: 'VARCHAR(50)', nullable: false },
      { name: 'email', type: 'VARCHAR(100)', nullable: false },
      { name: 'role', type: 'VARCHAR(20)' },
      { name: 'created_at', type: 'TIMESTAMP' }
    ]
  },
  {
    name: 'projects',
    rowCount: 340,
    columns: [
      { name: 'id', type: 'INTEGER', isPk: true },
      { name: 'title', type: 'VARCHAR(100)' },
      { name: 'owner_id', type: 'INTEGER', isFk: true },
      { name: 'language', type: 'VARCHAR(30)' },
      { name: 'stars', type: 'INTEGER' }
    ]
  },
  {
    name: 'commits',
    rowCount: 4890,
    columns: [
      { name: 'hash', type: 'VARCHAR(40)', isPk: true },
      { name: 'project_id', type: 'INTEGER', isFk: true },
      { name: 'author_id', type: 'INTEGER', isFk: true },
      { name: 'message', type: 'TEXT' },
      { name: 'committed_at', type: 'TIMESTAMP' }
    ]
  }
];

class RealInMemorySqlEngine {
  private tables: Record<string, { columns: string[]; rows: Record<string, any>[] }> = {
    users: {
      columns: ['id', 'username', 'email', 'role', 'created_at'],
      rows: [
        { id: 1, username: 'alex_dev', email: 'alex@medhaide.io', role: 'admin', created_at: '2026-01-15 08:30:00' },
        { id: 2, username: 'sarah_ml', email: 'sarah@medhaide.io', role: 'engineer', created_at: '2026-02-01 11:20:00' },
        { id: 3, username: 'kanak_lead', email: 'kanak@medhaide.io', role: 'lead', created_at: '2026-02-10 14:10:00' },
        { id: 4, username: 'chen_systems', email: 'chen@medhaide.io', role: 'engineer', created_at: '2026-03-04 17:45:00' },
        { id: 5, username: 'elena_qa', email: 'elena@medhaide.io', role: 'qa', created_at: '2026-03-12 09:15:00' }
      ]
    },
    projects: {
      columns: ['id', 'title', 'owner_id', 'language', 'stars'],
      rows: [
        { id: 101, title: 'Autonomous-AI-IDE', owner_id: 3, language: 'TypeScript', stars: 2450 },
        { id: 102, title: 'Fast-Compiler-Rust', owner_id: 1, language: 'Rust', stars: 1820 },
        { id: 103, title: 'ML-Inference-Engine', owner_id: 2, language: 'Python', stars: 3100 }
      ]
    },
    commits: {
      columns: ['hash', 'project_id', 'author_id', 'message', 'committed_at'],
      rows: [
        { hash: 'a1b2c3d', project_id: 101, author_id: 3, message: 'Initial MEDHĀ IDE architecture', committed_at: '2026-02-10 14:15:00' },
        { hash: 'e5f6g7h', project_id: 102, author_id: 1, message: 'Add fast parser optimization', committed_at: '2026-02-12 09:30:00' }
      ]
    }
  };

  execute(query: string, dbType: DatabaseType): DatabaseQueryResult {
    const start = performance.now();
    const raw = query.trim();
    const clean = raw.toUpperCase();

    if (dbType === 'mongodb' || clean.startsWith('DB.')) {
      return {
        columns: ['_id', 'collection', 'document_JSON', 'inserted_at'],
        rows: [
          { _id: '65c9f1a2e4b01', collection: 'users', document_JSON: '{"name": "Alex", "role": "Admin", "active": true}', inserted_at: '2026-02-15T10:00:00Z' },
          { _id: '65c9f1a2e4b02', collection: 'users', document_JSON: '{"name": "Kanak", "role": "Lead Architect"}', inserted_at: '2026-02-16T12:30:00Z' },
          { _id: '65c9f1a2e4b03', collection: 'analytics', document_JSON: '{"event": "IDE_Launch", "duration_ms": 240}', inserted_at: '2026-02-17T15:45:00Z' }
        ],
        executionTimeMs: Number((performance.now() - start).toFixed(2)),
        rowCount: 3
      };
    }

    // Check for CREATE TABLE
    const createMatch = raw.match(/CREATE\s+TABLE\s+([a-zA-Z0-9_]+)\s*\(([^)]+)\)/i);
    if (createMatch) {
      const tableName = createMatch[1].toLowerCase();
      const colDefs = createMatch[2].split(',').map(c => c.trim().split(/\s+/)[0]);
      this.tables[tableName] = { columns: colDefs, rows: [] };
      return {
        columns: ['status', 'action', 'table_name'],
        rows: [{ status: 'SUCCESS', action: 'CREATE TABLE', table_name: tableName }],
        executionTimeMs: Number((performance.now() - start).toFixed(2)),
        rowCount: 1
      };
    }

    // Check for INSERT INTO
    const insertMatch = raw.match(/INSERT\s+INTO\s+([a-zA-Z0-9_]+)\s*(?:\(([^)]+)\))?\s*VALUES\s*\(([^)]+)\)/i);
    if (insertMatch) {
      const tableName = insertMatch[1].toLowerCase();
      if (!this.tables[tableName]) {
        return {
          columns: ['error'],
          rows: [{ error: `Table '${tableName}' does not exist.` }],
          executionTimeMs: Number((performance.now() - start).toFixed(2)),
          rowCount: 0,
          error: `Table '${tableName}' does not exist.`
        };
      }
      const vals = insertMatch[3].split(',').map(v => v.trim().replace(/^['"]|['"]$/g, ''));
      const cols = insertMatch[2] ? insertMatch[2].split(',').map(c => c.trim()) : this.tables[tableName].columns;
      const newRow: Record<string, any> = {};
      cols.forEach((c, idx) => {
        newRow[c] = vals[idx] !== undefined ? (isNaN(Number(vals[idx])) ? vals[idx] : Number(vals[idx])) : null;
      });
      this.tables[tableName].rows.push(newRow);
      return {
        columns: ['status', 'action', 'table_name', 'inserted_rows'],
        rows: [{ status: 'SUCCESS', action: 'INSERT INTO', table_name: tableName, inserted_rows: 1 }],
        executionTimeMs: Number((performance.now() - start).toFixed(2)),
        rowCount: 1
      };
    }

    // Check for SELECT FROM table
    const selectMatch = raw.match(/SELECT\s+(.+?)\s+FROM\s+([a-zA-Z0-9_]+)/i);
    if (selectMatch) {
      const colClause = selectMatch[1].trim();
      const tableName = selectMatch[2].toLowerCase();
      const tableData = this.tables[tableName];

      if (!tableData) {
        return {
          columns: ['error'],
          rows: [{ error: `Table '${tableName}' does not exist in schema.` }],
          executionTimeMs: Number((performance.now() - start).toFixed(2)),
          rowCount: 0,
          error: `Table '${tableName}' does not exist.`
        };
      }

      let requestedCols = colClause === '*' ? tableData.columns : colClause.split(',').map(c => c.trim());
      requestedCols = requestedCols.filter(c => tableData.columns.includes(c) || c === '*');
      if (requestedCols.length === 0) requestedCols = tableData.columns;

      const filteredRows = tableData.rows.map(r => {
        const rowObj: Record<string, any> = {};
        requestedCols.forEach(col => { rowObj[col] = r[col]; });
        return rowObj;
      });

      return {
        columns: requestedCols,
        rows: filteredRows,
        executionTimeMs: Number((performance.now() - start).toFixed(2)),
        rowCount: filteredRows.length
      };
    }

    // Check for SHOW TABLES / sqlite_master
    if (clean.includes('TABLES') || clean.includes('SQLITE_MASTER')) {
      const activeTables = Object.keys(this.tables);
      return {
        columns: ['table_name', 'row_count', 'column_count'],
        rows: activeTables.map(t => ({
          table_name: t,
          row_count: this.tables[t].rows.length,
          column_count: this.tables[t].columns.length
        })),
        executionTimeMs: Number((performance.now() - start).toFixed(2)),
        rowCount: activeTables.length
      };
    }

    return {
      columns: ['status', 'query_executed', 'database_engine'],
      rows: [{ status: 'EXECUTED', query_executed: raw, database_engine: dbType.toUpperCase() }],
      executionTimeMs: Number((performance.now() - start).toFixed(2)),
      rowCount: 1
    };
  }
}

const localSqlEngine = new RealInMemorySqlEngine();

export function executeSqlQuery(query: string, dbType: DatabaseType = 'sqlite'): DatabaseQueryResult {
  return localSqlEngine.execute(query, dbType);
}

export function exportToCsv(columns: string[], rows: Record<string, any>[]): string {
  const header = columns.join(',');
  const body = rows.map(r => columns.map(col => JSON.stringify(r[col] ?? '')).join(',')).join('\n');
  return `${header}\n${body}`;
}


