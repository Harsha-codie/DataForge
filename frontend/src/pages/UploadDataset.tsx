import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { 
  UploadCloud, 
  FileSpreadsheet, 
  FileText, 
  AlertCircle, 
  CheckCircle2, 
  Sparkles, 
  Loader2,
  FileCheck
} from 'lucide-react';

export const UploadDataset: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      if (!name) {
        setName(selectedFile.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' '));
      }
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      setFile(droppedFile);
      if (!name) {
        setName(droppedFile.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' '));
      }
      setError(null);
    }
  };

  // Quick Load Sample Dataset helper
  const handleLoadSample = async () => {
    try {
      setIsUploading(true);
      setUploadProgress('Loading sample dirty customer churn dataset...');
      // Fetch the sample CSV directly
      const sampleCsv = `customer_id,name,age,gender,tenure_months,signup_date,monthly_charges,total_charges,contract_type,payment_method,churn
CUST-001,Alice Smith,34,Female,12,2023-01-15,65.5,786.0,Month-to-month,Credit Card,No
CUST-002,Bob Johnson,45,Male,24,2022-03-20,89.0,2136.0,One year,Bank Transfer,No
CUST-003,Carol White,29,Female,3,2023-11-05,45.2,135.6,Month-to-month,Electronic Check,Yes
CUST-004,David Brown,,Male,18,2022-08-12,70.0,1260.0,One year,Credit Card,No
CUST-005,Emma Wilson,52,Female,36,2021-05-30,110.5,3978.0,Two year,Credit Card,No
CUST-006,Frank Miller,38,Male,6,2023-07-22,55.0,330.0,Month-to-month,Mailed Check,Yes
CUST-007,Grace Davis,61,Female,48,2020-02-14,95.2,4569.6,Two year,Bank Transfer,No
CUST-008,Henry Taylor,24,Male,1,2024-01-08,30.0,30.0,Month-to-month,Electronic Check,Yes
CUST-009,Ivy Anderson,42,Female,15,2022-10-18,80.5,1207.5,Month-to-month,Credit Card,No
CUST-010,Jack Thomas,31,Male,9,2023-04-25,60.0,540.0,Month-to-month,Electronic Check,No
CUST-003,Carol White,29,Female,3,2023-11-05,45.2,135.6,Month-to-month,Electronic Check,Yes
CUST-011,Karen Martinez,49,Female,28,2021-12-10,102.3,unknown,One year,Credit Card,No
CUST-012,Leo Robinson,73,Male,999,2023-09-01,75.0,75000.0,Month-to-month,Electronic Check,Yes
CUST-013,Mia Clark,22,Female,4,2023-10-11,40.0,160.0,Month-to-month,Mailed Check,No
CUST-014,Noah Rodriguez,,Male,14,2022-11-19,85.5,1197.0,One year,Credit Card,No
CUST-015,Olivia Lewis,36,Female,22,2022-04-03,92.0,$2024.00,Month-to-month,Bank Transfer,Yes
CUST-016,Paul Lee,41,Male,0,2024-02-01,25.0,,Month-to-month,Mailed Check,No
CUST-017,Quinn Walker,27,Female,8,2023-06-14,68.0,544.0,Month-to-month,Electronic Check,No
CUST-018,Ryan Hall,58,Male,40,2020-09-27,105.0,4200.0,Two year,Credit Card,No
CUST-019,Sophia Allen,33,Female,11,2023-02-18,72.5,797.5,Month-to-month,Credit Card,Yes
CUST-007,Grace Davis,61,Female,48,2020-02-14,95.2,4569.6,Two year,Bank Transfer,No
CUST-020,Thomas Young,47,Male,30,2021-08-09,88.0,2640.0,One year,Bank Transfer,No
CUST-021,Uma Patel,30,Female,7,2023-07-15,50.0,350.0,Month-to-month,Electronic Check,No
CUST-022,Victor King,65,Male,60,2019-01-10,115.0,15000.0,Two year,Credit Card,No
CUST-023,Wendy Scott,26,Female,2,2023-12-01,35.0,70.0,Month-to-month,Mailed Check,Yes
CUST-024,Xavier Green,39,Male,19,2022-07-04,78.5,1491.5,One year,Electronic Check,No
CUST-025,Yara Baker,50,Female,33,2021-04-12,98.0,3234.0,Two year,Credit Card,No
CUST-026,Zack Nelson,28,Male,5,2023-08-20,48.0,240.0,Month-to-month,Electronic Check,Yes
CUST-027,Amber Bell,35,Female,13,2023-01-28,71.0,923.0,Month-to-month,Credit Card,No
CUST-028,Brian Adams,43,Male,26,2022-01-14,84.0,2184.0,One year,Bank Transfer,No`;

      const sampleBlob = new Blob([sampleCsv], { type: 'text/csv' });
      const sampleFileObj = new File([sampleBlob], 'dirty_customer_churn.csv', { type: 'text/csv' });
      
      const formData = new FormData();
      formData.append('file', sampleFileObj);
      formData.append('name', 'Sample Customer Churn (Flawed Data)');
      formData.append('description', 'Demo dataset containing missing values, duplicates, mixed types, and outliers for acceptance testing.');

      const result = await api.uploadDataset(formData);
      navigate(`/datasets/${result.id}/profiling`);
    } catch (err: any) {
      setError(err.message || 'Failed to upload sample dataset.');
    } finally {
      setIsUploading(false);
      setUploadProgress(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a dataset file to upload.');
      return;
    }

    setIsUploading(true);
    setUploadProgress('Uploading and extracting schema metadata with Polars...');
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    if (name) formData.append('name', name);
    if (description) formData.append('description', description);

    try {
      const result = await api.uploadDataset(formData);
      setUploadProgress('Dataset uploaded! Redirecting to profiling report...');
      setTimeout(() => {
        navigate(`/datasets/${result.id}/profiling`);
      }, 500);
    } catch (err: any) {
      setError(err.message || 'Upload failed. Please verify file format.');
      setIsUploading(false);
      setUploadProgress(null);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Upload New Dataset</h1>
        <p className="text-sm text-slate-400 mt-1">
          Supports CSV, Parquet, JSON, and XLSX. Files are stored as immutable baseline versions.
        </p>
      </div>

      {/* Quick Load Sample Banner */}
      <div className="glass-card p-4 border-indigo-500/30 bg-indigo-950/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/30 flex items-center justify-center text-indigo-400 shrink-0">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-white">Need a test dataset right now?</div>
            <div className="text-[11px] text-slate-300">
              Load our built-in benchmark dataset with missing values, duplicate rows, mixed types, and outliers.
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={handleLoadSample}
          disabled={isUploading}
          className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold whitespace-nowrap transition-all shadow-md shadow-indigo-600/20"
        >
          {isUploading ? 'Loading...' : 'Load Sample Churn Data'}
        </button>
      </div>

      {error && (
        <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="glass-card p-6 space-y-5">
        {/* Dropzone */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
            file
              ? 'border-indigo-500 bg-indigo-950/20'
              : 'border-slate-700 hover:border-slate-500 bg-slate-900/50'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".csv,.parquet,.json,.xlsx,.xls,.txt"
            className="hidden"
          />

          {file ? (
            <div className="space-y-2">
              <div className="w-12 h-12 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/40 flex items-center justify-center mx-auto">
                <FileCheck className="w-6 h-6" />
              </div>
              <div className="font-semibold text-white text-sm">{file.name}</div>
              <div className="text-xs text-slate-400">
                {(file.size / 1024).toFixed(1)} KB • Click or drag to replace
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="w-12 h-12 rounded-xl bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
                <UploadCloud className="w-6 h-6" />
              </div>
              <div className="text-sm font-semibold text-white">
                Drag and drop your file here, or <span className="text-indigo-400">browse</span>
              </div>
              <div className="text-xs text-slate-500">
                CSV, Parquet, JSON, XLSX up to 500MB
              </div>
            </div>
          )}
        </div>

        {/* Metadata Inputs */}
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Dataset Name
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Q3 Customer Churn"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Description (Optional)
            </label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Source, business purpose, or preprocessing notes..."
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>
        </div>

        {/* Submit */}
        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={!file || isUploading}
            className="px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold flex items-center gap-2 shadow-lg shadow-indigo-600/25 transition-all"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>{uploadProgress || 'Processing...'}</span>
              </>
            ) : (
              <>
                <UploadCloud className="w-4 h-4" />
                <span>Upload & Begin Profiling</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
