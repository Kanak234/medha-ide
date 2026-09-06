import React, { useState } from 'react';
import { Database, Play, Table, Download, Server, CheckCircle2 } from 'lucide-react';
import { SAMPLE_DATABASE_TABLES, SUPPORTED_DATABASES, DatabaseType, executeSqlQuery, exportToCsv } from '../services/databaseEngine';
import { DatabaseQueryResult } from '../types';

export const DatabaseStudioPanel: React.FC = () => {
  const [selectedDb, setSelectedDb] = useState<DatabaseType>('sqlite');
  const [query, setQuery] = useState('SELECT * FROM users ORDER BY created_at DESC;');
  const [result, setResult] = useState<DatabaseQueryResult | null>(() => executeSqlQuery('SELECT * FROM users;', 'sqlite'));
  const [activeTable, setActiveTable] = useState('users');

  const activeDbInfo = SUPPORTED_DATABASES.find(db => db.type === selectedDb) || SUPPORTED_DATABASES[4];

  const handleDbChange = (type: DatabaseType) => {
    setSelectedDb(type);
    if (type === 'mongodb') {
      setQuery('db.users.find({ active: true });');
    } else if (type === 'oracle') {
      setQuery('SELECT * FROM users WHERE ROWNUM <= 10;');
    } else {
      setQuery('SELECT * FROM users ORDER BY created_at DESC;');
    }
    setResult(executeSqlQuery(query, type));
  };

  const handleRunQuery = () => {
    const res = executeSqlQuery(query, selectedDb);
    setResult(res);
  };

  const handleExportCsv = () => {
    if (!result) return;
    const csvContent = exportToCsv(result.columns, result.rows);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedDb}_query_result_${Date.now()}.csv`;
    a.click();
  };

  return (
    <div className="flex-1 bg-[#090d16] flex h-full overflow-hidden select-none">
      {/* Schema Browser Sidebar */}
      <div className="w-72 bg-[#0f172a] border-r border-[#1e293b] flex flex-col p-3 space-y-3">
        <div className="flex items-center gap-2 border-b border-[#1e293b] pb-2">
          <Database className="w-4 h-4 text-indigo-400" />
          <span className="font-bold text-xs uppercase tracking-wider text-white">Database Explorer</span>
        </div>

        {/* Database Connection Selector */}
        <div className="space-y-1.5">
          <label className="text-[10px] font-bold uppercase tracking-wider text-[#64748b]">Select Active Engine:</label>
          <select
            value={selectedDb}
            onChange={(e) => handleDbChange(e.target.value as DatabaseType)}
            className="w-full bg-[#090d16] border border-[#334155] rounded-lg p-2 text-xs font-semibold text-white focus:outline-none focus:border-indigo-400"
          >
            {SUPPORTED_DATABASES.map((db) => (
              <option key={db.type} value={db.type}>
                {db.label}
              </option>
            ))}
          </select>
        </div>

        <div className="p-2.5 rounded-lg bg-[#090d16] border border-[#1e293b] flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <Server className={`w-3.5 h-3.5 ${activeDbInfo.iconColor}`} />
            <span className="text-[11px] font-medium text-slate-300">{activeDbInfo.defaultDb}</span>
          </div>
          <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" /> Connected
          </span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-2 pt-2 border-t border-[#1e293b]">
          <span className="text-[10px] font-bold uppercase text-[#64748b]">Schema Tables / Collections</span>
          {SAMPLE_DATABASE_TABLES.map((table) => (
            <div
              key={table.name}
              onClick={() => {
                setActiveTable(table.name);
                const q = selectedDb === 'mongodb' ? `db.${table.name}.find();` : `SELECT * FROM ${table.name};`;
                setQuery(q);
                setResult(executeSqlQuery(q, selectedDb));
              }}
              className={`p-2 rounded-lg cursor-pointer text-xs transition-all border ${
                activeTable === table.name
                  ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40 font-semibold'
                  : 'bg-[#1e293b]/40 text-[#94a3b8] border-[#334155]/40 hover:text-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <Table className="w-3.5 h-3.5 text-indigo-400" />
                  {table.name}
                </span>
                <span className="text-[10px] font-mono text-[#64748b]">{table.rowCount} records</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Query Execution & Results Workspace */}
      <div className="flex-1 flex flex-col overflow-hidden p-4 space-y-4">
        {/* SQL / Mongo Query Editor */}
        <div className="bg-[#0f172a] p-3 rounded-xl border border-[#1e293b] space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                {selectedDb === 'mongodb' ? 'NoSQL Query Console' : 'SQL Query Editor'}
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase">
                {selectedDb}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleExportCsv}
                className="px-2.5 py-1 bg-[#1e293b] hover:bg-[#334155] text-cyan-300 rounded text-xs font-medium flex items-center gap-1"
              >
                <Download className="w-3.5 h-3.5" /> Export CSV
              </button>
              <button
                onClick={handleRunQuery}
                className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-bold flex items-center gap-1 shadow"
              >
                <Play className="w-3.5 h-3.5 fill-current" /> Execute Query
              </button>
            </div>
          </div>

          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={3}
            className="w-full bg-[#090d16] border border-[#334155] rounded-lg p-2.5 font-mono text-xs text-indigo-200 focus:outline-none focus:border-indigo-400"
          />
        </div>

        {/* Results Table */}
        {result && (
          <div className="flex-1 bg-[#0f172a] rounded-xl border border-[#1e293b] flex flex-col overflow-hidden">
            <div className="p-3 border-b border-[#1e293b] flex items-center justify-between">
              <span className="text-xs font-semibold text-[#94a3b8]">
                Result Set ({result.rowCount} records returned in {result.executionTimeMs} ms)
              </span>
            </div>

            <div className="flex-1 overflow-auto p-2">
              <table className="w-full text-left text-xs font-mono border-collapse">
                <thead>
                  <tr className="border-b border-[#1e293b] text-[#64748b]">
                    {result.columns.map((col) => (
                      <th key={col} className="p-2 font-bold uppercase">{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e293b]/40">
                  {result.rows.map((row, idx) => (
                    <tr key={idx} className="hover:bg-[#1e293b]/40 text-[#e2e8f0]">
                      {result.columns.map((col) => (
                        <td key={col} className="p-2">{String(row[col] ?? '')}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

