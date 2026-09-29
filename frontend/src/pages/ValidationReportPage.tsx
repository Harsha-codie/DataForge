import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';
import { useDataset } from '../context/DatasetContext';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  RefreshCw, 
  ShieldCheck, 
  ArrowRight,
  Loader2
} from 'lucide-react';

export const ValidationReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { selectedVersionId } = useDataset();
  const [report, setReport] = useState<any | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  const fetchValidation = async () => {
    if (!id) return;
    setIsValidating(true);
    try {
      const data = await api.getValidationReport(id, selectedVersionId || undefined);
      setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsValidating(false);
    }
  };

  useEffect(() => {
    fetchValidation();
  }, [id, selectedVersionId]);

  if (isValidating && !report) {
    return (
      <div className="p-16 flex flex-col items-center justify-center text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mb-2" />
        <span className="text-xs">Evaluating data invariants and quality rules...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <CheckCircle2 className="w-6 h-6 text-indigo-400" />
            <span>Dataset Validation Report</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Automated verification of dataset invariants, data consistency, and missingness tolerances.
          </p>
        </div>
        <button
          onClick={fetchValidation}
          disabled={isValidating}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Re-validate Dataset</span>
        </button>
      </div>

      {/* Status Banner */}
      {report && (
        <div className={`glass-card p-6 border ${
          report.overall_status === 'passed'
            ? 'border-emerald-500/30 bg-emerald-950/20'
            : report.overall_status === 'warning'
            ? 'border-amber-500/30 bg-amber-950/20'
            : 'border-rose-500/30 bg-rose-950/20'
        }`}>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center gap-3">
              {report.overall_status === 'passed' ? (
                <CheckCircle2 className="w-8 h-8 text-emerald-400 shrink-0" />
              ) : report.overall_status === 'warning' ? (
                <AlertTriangle className="w-8 h-8 text-amber-400 shrink-0" />
              ) : (
                <XCircle className="w-8 h-8 text-rose-400 shrink-0" />
              )}
              <div>
                <h3 className="text-lg font-bold text-white capitalize">
                  Overall Validation: {report.overall_status}
                </h3>
                <p className="text-xs text-slate-300 mt-0.5">
                  {report.overall_status === 'passed'
                    ? 'All checked invariants and data quality rules passed cleanly.'
                    : `${report.violations_count} invariant violations detected.`}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 text-xs">
              <div className="bg-slate-900/70 px-3 py-1.5 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Rules Checked</span>
                <span className="font-bold text-white text-sm">{report.rules_checked?.length || 0}</span>
              </div>
              <div className="bg-slate-900/70 px-3 py-1.5 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Violations</span>
                <span className="font-bold text-rose-400 text-sm">{report.violations_count}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Rules Checked Pill List */}
      {report && (
        <div className="glass-card p-4 space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Rules Evaluated
          </div>
          <div className="flex flex-wrap gap-2">
            {report.rules_checked?.map((r: string) => (
              <span
                key={r}
                className="px-2.5 py-1 rounded-md text-xs font-mono bg-slate-900 border border-slate-800 text-slate-300"
              >
                {r}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Issues Feed */}
      {report && report.issues && report.issues.length > 0 ? (
        <div className="glass-card p-5 space-y-3">
          <h3 className="text-sm font-bold text-white">Detected Invariant Violations</h3>
          <div className="space-y-2">
            {report.issues.map((issue: any, idx: number) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      issue.severity === 'critical' ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-amber-950 text-amber-300 border border-amber-800'
                    }`}>
                      {issue.severity}
                    </span>
                    <span className="font-bold text-slate-200">{issue.rule}</span>
                    {issue.column && (
                      <span className="font-mono text-indigo-400 bg-indigo-950/40 px-1.5 py-0.2 rounded text-[11px]">
                        {issue.column}
                      </span>
                    )}
                  </div>
                  <p className="text-slate-300">{issue.message}</p>
                </div>

                <Link
                  to={`/datasets/${id}/transform`}
                  className="shrink-0 px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1 self-start sm:self-auto"
                >
                  <span>Resolve</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="glass-card p-12 text-center text-slate-400 text-xs">
          Zero invariant violations detected for this version.
        </div>
      )}
    </div>
  );
};
