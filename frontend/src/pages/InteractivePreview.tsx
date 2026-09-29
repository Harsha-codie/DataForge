import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api/client';
import { useDataset } from '../context/DatasetContext';
import { 
  Table, 
  ChevronLeft, 
  ChevronRight, 
  Search, 
  Filter, 
  Download,
  Loader2,
  Layers
} from 'lucide-react';

export const InteractivePreview: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { selectedVersionId } = useDataset();
  const [previewData, setPreviewData] = useState<any | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const fetchPreview = async () => {
    if (!id) return;
    setIsLoading(true);
    try {
      const data = await api.getPreview(id, selectedVersionId || undefined, page, pageSize);
      setPreviewData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPreview();
  }, [id, selectedVersionId, page, pageSize]);

  if (isLoading && !previewData) {
    return (
      <div className="p-16 flex flex-col items-center justify-center text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mb-2" />
        <span className="text-xs">Loading tabular preview...</span>
      </div>
    );
  }

  if (!previewData) {
    return <div className="text-slate-400 text-sm">No preview available.</div>;
  }

  // Client-side row search filter on current page
  const filteredRows = previewData.rows.filter((row: any) => {
    if (!searchTerm) return true;
    return Object.values(row).some(
      (val) => val !== null && val !== undefined && String(val).toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  const totalPages = Math.ceil(previewData.total_rows / pageSize);

  return (
    <div className="space-y-4">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Table className="w-6 h-6 text-indigo-400" />
            <span>Interactive Data Grid</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Displaying rows {((page - 1) * pageSize) + 1} - {Math.min(page * pageSize, previewData.total_rows)} of {previewData.total_rows.toLocaleString()}
          </p>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          {/* Search in preview */}
          <div className="relative flex-1 sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search current page..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Page size select */}
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(1);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value={25}>25 rows</option>
            <option value={50}>50 rows</option>
            <option value={100}>100 rows</option>
            <option value={200}>200 rows</option>
          </select>
        </div>
      </div>

      {/* Grid Container */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto max-h-[600px] no-scrollbar">
          <table className="w-full text-left border-collapse text-xs">
            <thead className="sticky top-0 z-20 bg-slate-900/95 backdrop-blur border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3 font-semibold text-slate-500 text-[10px] uppercase w-12 text-center border-r border-slate-800/60">
                  #
                </th>
                {previewData.columns.map((col: string) => (
                  <th
                    key={col}
                    className="py-2.5 px-3 font-semibold text-slate-300 text-xs border-r border-slate-800/60 whitespace-nowrap min-w-[140px]"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="truncate">{col}</span>
                      <span className="text-[9px] font-mono uppercase px-1 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">
                        {previewData.column_types[col] || 'any'}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {filteredRows.map((row: any, rIdx: number) => {
                const rowIndex = ((page - 1) * pageSize) + rIdx + 1;
                return (
                  <tr key={rIdx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2 px-3 text-slate-500 text-[10px] text-center bg-slate-950/40 border-r border-slate-800/60">
                      {rowIndex}
                    </td>
                    {previewData.columns.map((col: string) => {
                      const val = row[col];
                      const isNull = val === null || val === undefined;
                      return (
                        <td
                          key={col}
                          className={`py-2 px-3 border-r border-slate-800/60 whitespace-nowrap max-w-[240px] truncate ${
                            isNull ? 'bg-rose-950/20 text-rose-400 italic' : 'text-slate-200'
                          }`}
                        >
                          {isNull ? 'null' : String(val)}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-3 bg-slate-900/80 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>
            Page <span className="font-semibold text-white">{page}</span> of{' '}
            <span className="font-semibold text-white">{totalPages || 1}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1.5 rounded-md bg-slate-800 hover:bg-slate-700 disabled:opacity-30 disabled:pointer-events-none text-slate-300"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1.5 rounded-md bg-slate-800 hover:bg-slate-700 disabled:opacity-30 disabled:pointer-events-none text-slate-300"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
