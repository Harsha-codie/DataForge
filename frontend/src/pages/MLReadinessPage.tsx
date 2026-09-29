import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';
import { useDataset } from '../context/DatasetContext';
import { 
  Sparkles, 
  Target, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Wand2, 
  ArrowRight, 
  ShieldAlert,
  Loader2,
  Info
} from 'lucide-react';

export const MLReadinessPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { selectedVersionId } = useDataset();
  const [columns, setColumns] = useState<string[]>([]);
  const [taskType, setTaskType] = useState<string>('classification');
  const [targetColumn, setTargetColumn] = useState<string>('churn');
  const [report, setReport] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      if (!id) return;
      try {
        const prev = await api.getPreview(id, selectedVersionId || undefined, 1, 1);
        setColumns(prev.columns || []);
        if (prev.columns && prev.columns.includes('churn')) {
          setTargetColumn('churn');
        } else if (prev.columns && prev.columns.length > 0) {
          setTargetColumn(prev.columns[prev.columns.length - 1]);
        }
      } catch (err) {
        console.error(err);
      }
    };
    init();
  }, [id, selectedVersionId]);

  const runEvaluation = async () => {
    if (!id) return;
    setIsLoading(true);
    try {
      const data = await api.evaluateMLReadiness(id, {
        version_id: selectedVersionId,
        task_type: taskType,
        target_column: targetColumn || undefined,
      });
      setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (id && targetColumn) {
      runEvaluation();
    }
  }, [id, selectedVersionId, taskType, targetColumn]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-indigo-400" />
            <span>ML Readiness & Leakage Assessment</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Evaluates target distribution, high-cardinality ID leakage, and feature missingness for supervised modeling.
          </p>
        </div>
      </div>

      {/* Configuration Controls */}
      <div className="glass-card p-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Intended Machine Learning Task
            </label>
            <select
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500 font-medium"
            >
              <option value="classification">Classification (Binary or Multi-Class)</option>
              <option value="regression">Regression (Continuous Numeric)</option>
              <option value="clustering">Clustering / Unsupervised</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Target Prediction Column (Y)
            </label>
            <select
              value={targetColumn}
              onChange={(e) => setTargetColumn(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono font-medium"
            >
              <option value="">No target (Unsupervised)</option>
              {columns.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Readiness Report Banner */}
      {isLoading ? (
        <div className="p-16 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
          <span>Evaluating dataset against machine learning requirements...</span>
        </div>
      ) : report ? (
        <div className="space-y-6">
          <div className={`glass-card p-6 border ${
            report.overall_status === 'ready'
              ? 'border-emerald-500/30 bg-emerald-950/20'
              : report.overall_status === 'needs_attention'
              ? 'border-amber-500/30 bg-amber-950/20'
              : 'border-rose-500/30 bg-rose-950/20'
          }`}>
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div className="flex items-center gap-3">
                {report.overall_status === 'ready' ? (
                  <CheckCircle2 className="w-9 h-9 text-emerald-400 shrink-0" />
                ) : report.overall_status === 'needs_attention' ? (
                  <AlertTriangle className="w-9 h-9 text-amber-400 shrink-0" />
                ) : (
                  <XCircle className="w-9 h-9 text-rose-400 shrink-0" />
                )}
                <div>
                  <h3 className="text-lg font-bold text-white uppercase tracking-tight">
                    Readiness: {report.overall_status.replace('_', ' ')}
                  </h3>
                  <p className="text-xs text-slate-300 mt-0.5">
                    Target column: <span className="font-mono text-indigo-300">{report.target_column || 'None'}</span> • Task: {report.task_type}
                  </p>
                </div>
              </div>

              <div className="text-right">
                <div className="text-3xl font-black text-white">
                  {report.readiness_score}<span className="text-sm font-normal text-slate-400">/100</span>
                </div>
                <div className="text-[10px] text-slate-400">Readiness Score</div>
              </div>
            </div>
          </div>

          {/* Actionable Preprocessing Recommendations */}
          {report.recommendations && report.recommendations.length > 0 && (
            <div className="glass-card p-5 space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Wand2 className="w-4 h-4 text-indigo-400" />
                <span>Recommended ML Preprocessing Pipeline</span>
              </h3>
              <div className="space-y-2">
                {report.recommendations.map((rec: any) => (
                  <div
                    key={rec.step}
                    className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-indigo-600/30 text-indigo-400 font-bold flex items-center justify-center text-[10px]">
                          {rec.step}
                        </span>
                        <span className="font-bold text-slate-200">{rec.title}</span>
                      </div>
                      <p className="text-slate-400 text-[11px] pl-7">{rec.description}</p>
                    </div>

                    <Link
                      to={`/datasets/${id}/transform`}
                      className="shrink-0 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold flex items-center gap-1.5 text-xs self-start sm:self-auto"
                    >
                      <span>Configure</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Findings */}
          {report.findings && report.findings.length > 0 && (
            <div className="glass-card p-5 space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-400" />
                <span>Detailed Findings & Leakage Risks</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {report.findings.map((f: any, idx: number) => (
                  <div key={idx} className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1 text-xs">
                    <div className="flex items-center justify-between gap-2">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        f.severity === 'critical' ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-amber-950 text-amber-300 border border-amber-800'
                      }`}>
                        {f.severity}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500 uppercase">{f.category}</span>
                    </div>
                    <div className="font-bold text-slate-200">{f.issue}</div>
                    <p className="text-[11px] text-slate-400 leading-relaxed">{f.explanation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Disclaimers & Ethics */}
          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-400 space-y-1.5">
            <div className="flex items-center gap-2 font-semibold text-slate-300">
              <Info className="w-4 h-4 text-indigo-400" />
              <span>Model Readiness Disclaimer</span>
            </div>
            <p className="text-[11px] leading-relaxed">
              Passing automated ML readiness checks does not guarantee high model predictive performance or universal suitability.
              DataForge verifies structural integrity, missingness limits, type encodings, and apparent ID leakage. Continuous
              validation during feature engineering and out-of-sample testing remains essential.
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
};
