import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api/client';
import { useDataset } from '../context/DatasetContext';
import { 
  GitFork, 
  ArrowRight, 
  Layers, 
  GitBranch, 
  CheckCircle2, 
  Loader2,
  Diff
} from 'lucide-react';

export const LineageComparison: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { versions } = useDataset();
  const [sourceVerId, setSourceVerId] = useState<string>('');
  const [targetVerId, setTargetVerId] = useState<string>('');
  const [comparison, setComparison] = useState<any | null>(null);
  const [isComparing, setIsComparing] = useState(false);

  useEffect(() => {
    if (versions && versions.length >= 2) {
      // Pick first (latest) and second latest
      setTargetVerId(versions[0].id);
      setSourceVerId(versions[1].id);
    } else if (versions && versions.length === 1) {
      setTargetVerId(versions[0].id);
      setSourceVerId(versions[0].id);
    }
  }, [versions]);

  const handleCompare = async () => {
    if (!id || !sourceVerId || !targetVerId) return;
    setIsComparing(true);
    try {
      const data = await api.compareVersions(id, sourceVerId, targetVerId);
      setComparison(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsComparing(false);
    }
  };

  useEffect(() => {
    if (sourceVerId && targetVerId) {
      handleCompare();
    }
  }, [sourceVerId, targetVerId]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <GitFork className="w-6 h-6 text-indigo-400" />
            <span>Dataset Lineage & Version Diff</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Compare two immutable versions to inspect schema modifications, row delta, and null count reductions.
          </p>
        </div>
      </div>

      {/* Version Pickers */}
      <div className="glass-card p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex-1 w-full">
          <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Base Version (Before)
          </label>
          <select
            value={sourceVerId}
            onChange={(e) => setSourceVerId(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500 font-medium"
          >
            {versions.map((v: any) => (
              <option key={v.id} value={v.id}>
                v{v.version_number} - {v.transformation_operation} ({v.row_count} rows, {v.branch_name})
              </option>
            ))}
          </select>
        </div>

        <div className="p-2 rounded-full bg-slate-800 text-slate-400 mt-4 sm:mt-0">
          <ArrowRight className="w-4 h-4" />
        </div>

        <div className="flex-1 w-full">
          <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Target Version (After)
          </label>
          <select
            value={targetVerId}
            onChange={(e) => setTargetVerId(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500 font-medium"
          >
            {versions.map((v: any) => (
              <option key={v.id} value={v.id}>
                v{v.version_number} - {v.transformation_operation} ({v.row_count} rows, {v.branch_name})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Comparison Results */}
      {isComparing ? (
        <div className="p-16 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
          <span>Comparing columnar versions...</span>
        </div>
      ) : comparison ? (
        <div className="space-y-5">
          {/* Summary Box */}
          <div className="glass-card p-5 border-indigo-500/30 bg-indigo-950/20">
            <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-300 mb-1 flex items-center gap-2">
              <Diff className="w-4 h-4" />
              <span>Version Transition Summary</span>
            </h3>
            <p className="text-sm font-semibold text-white leading-relaxed">
              {comparison.summary}
            </p>
          </div>

          {/* Metric Diff Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="glass-card p-4">
              <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">Row Delta</span>
              <div className={`text-2xl font-bold ${comparison.row_count_diff < 0 ? 'text-rose-400' : comparison.row_count_diff > 0 ? 'text-emerald-400' : 'text-slate-300'}`}>
                {comparison.row_count_diff > 0 ? `+${comparison.row_count_diff}` : comparison.row_count_diff}
              </div>
            </div>

            <div className="glass-card p-4">
              <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">Column Delta</span>
              <div className="text-2xl font-bold text-white">
                {comparison.column_count_diff > 0 ? `+${comparison.column_count_diff}` : comparison.column_count_diff}
              </div>
            </div>

            <div className="glass-card p-4">
              <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">Columns Added</span>
              <div className="text-2xl font-bold text-emerald-400">
                {comparison.columns_added?.length || 0}
              </div>
            </div>

            <div className="glass-card p-4">
              <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">Columns Removed</span>
              <div className="text-2xl font-bold text-rose-400">
                {comparison.columns_removed?.length || 0}
              </div>
            </div>
          </div>

          {/* Type Modifications */}
          {comparison.columns_modified && comparison.columns_modified.length > 0 && (
            <div className="glass-card p-5 space-y-3">
              <h3 className="text-sm font-bold text-white">Column Data Type Modifications</h3>
              <div className="divide-y divide-slate-800 text-xs">
                {comparison.columns_modified.map((mod: any) => (
                  <div key={mod.name} className="py-2.5 flex items-center justify-between">
                    <span className="font-mono text-indigo-400 font-bold">{mod.name}</span>
                    <div className="flex items-center gap-2 font-mono">
                      <span className="text-slate-400 px-2 py-0.5 rounded bg-slate-900">{mod.old_type}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                      <span className="text-emerald-400 font-bold px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800/60">{mod.new_type}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Null Reductions */}
          {comparison.null_count_diffs && Object.keys(comparison.null_count_diffs).length > 0 && (
            <div className="glass-card p-5 space-y-3">
              <h3 className="text-sm font-bold text-white">Missing Value Changes</h3>
              <div className="divide-y divide-slate-800 text-xs">
                {Object.entries(comparison.null_count_diffs).map(([col, diff]: [string, any]) => (
                  <div key={col} className="py-2.5 flex items-center justify-between">
                    <span className="font-mono text-slate-300">{col}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-500">
                        {diff.old_nulls} nulls → {diff.new_nulls} nulls
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                        diff.diff < 0 ? 'bg-emerald-950 text-emerald-300' : 'bg-rose-950 text-rose-300'
                      }`}>
                        {diff.diff > 0 ? `+${diff.diff}` : diff.diff}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
};
