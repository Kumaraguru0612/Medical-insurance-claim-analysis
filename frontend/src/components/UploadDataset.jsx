import React, { useState, useEffect, useRef } from 'react';
import { 
  UploadCloud, 
  CheckCircle2, 
  AlertCircle, 
  RotateCw, 
  FileSpreadsheet, 
  Database,
  Layers,
  RefreshCw,
  Tag
} from 'lucide-react';
import { uploadDataset, resetDataset, fetchDatasetSummary } from '../services/api';

export default function UploadDataset({ onDatasetChange }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const loadSummary = () => {
    setLoading(true);
    fetchDatasetSummary()
      .then(data => setSummary(data))
      .catch(err => console.error("Summary error:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadSummary();
  }, []);

  const handleFile = async (file) => {
    if (!file) return;
    if (!file.name.endsWith('.csv')) {
      setErrorMessage('Please upload a valid CSV (.csv) file.');
      return;
    }

    setUploading(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const res = await uploadDataset(file);
      setSuccessMessage(`Dataset "${file.name}" uploaded and processed successfully! (${res.total_rows.toLocaleString()} records, ${res.total_columns} columns)`);
      loadSummary();
      if (onDatasetChange) onDatasetChange();
    } catch (err) {
      setErrorMessage(err.message || 'Failed to upload and parse dataset.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleReset = async () => {
    setUploading(true);
    setErrorMessage('');
    setSuccessMessage('');
    try {
      await resetDataset();
      setSuccessMessage('Dataset reset to default canonical dataset (insurance_claims.csv).');
      loadSummary();
      if (onDatasetChange) onDatasetChange();
    } catch (err) {
      setErrorMessage(err.message || 'Failed to reset dataset.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      
      {/* Alert Messages */}
      {successMessage && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Main Drag and Drop Card Matching Fig 3 */}
      <div className="bg-white rounded-3xl p-8 sm:p-12 shadow-sm border border-slate-100 space-y-6">
        
        {/* Dropzone Area */}
        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-3xl p-10 sm:p-16 flex flex-col items-center justify-center text-center transition-all cursor-pointer ${
            isDragOver 
              ? 'border-blue-600 bg-blue-50/50 scale-[1.01]' 
              : 'border-slate-200 bg-slate-50/40 hover:bg-slate-50/80 hover:border-slate-300'
          }`}
          onClick={() => fileInputRef.current?.click()}
        >
          {/* Cloud Upload Icon in Circle */}
          <div className="w-20 h-20 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mb-4 shadow-sm">
            {uploading ? (
              <RotateCw className="w-10 h-10 animate-spin" />
            ) : (
              <UploadCloud className="w-10 h-10" />
            )}
          </div>

          <h3 className="text-base sm:text-lg font-bold text-slate-800 mb-1">
            Drag and drop your CSV file here
          </h3>
          <p className="text-xs text-slate-400 font-medium mb-5">or</p>

          <button
            type="button"
            disabled={uploading}
            onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
            className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-semibold text-xs shadow-md shadow-blue-600/20 transition cursor-pointer"
          >
            {uploading ? 'Processing CSV...' : 'Choose File'}
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={(e) => {
              if (e.target.files?.[0]) handleFile(e.target.files[0]);
            }}
            className="hidden"
          />

          {/* Active / Current File Badge Matching Fig 3 */}
          <div className="mt-8 flex items-center gap-2 text-xs font-mono font-semibold text-slate-700 bg-white px-4 py-2 rounded-xl border border-slate-200 shadow-2xs">
            <span className="text-slate-800">{summary?.file_name || 'insurance_claims.csv'}</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>

        </div>

      </div>

      {/* Dataset Information & Detected Columns */}
      {summary && (
        <div className="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-100 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Database className="w-5 h-5 text-blue-600" />
                Active Dataset Telemetry & Schema
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">Summary of currently loaded insurance claims dataset</p>
            </div>
            
            <button
              onClick={handleReset}
              className="px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-xs flex items-center gap-1.5 transition cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
              Reset to Default Dataset
            </button>
          </div>

          {/* 4 Stats Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-400 font-medium block">Total Records</span>
              <span className="text-xl font-bold text-slate-900 font-mono mt-1 block">
                {summary.total_rows.toLocaleString()}
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-400 font-medium block">Total Columns</span>
              <span className="text-xl font-bold text-slate-900 font-mono mt-1 block">
                {summary.total_columns}
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-400 font-medium block">File Size</span>
              <span className="text-xl font-bold text-slate-900 font-mono mt-1 block">
                {summary.file_size_kb || 50.0} KB
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-400 font-medium block">Status / Validation</span>
              <span className="text-xs font-bold text-emerald-600 mt-2 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Ready & Trained
              </span>
            </div>
          </div>

          {/* Detected Columns Tags */}
          <div>
            <span className="text-xs font-semibold text-slate-700 block mb-3">
              Detected Dataset Columns:
            </span>
            <div className="flex flex-wrap gap-2">
              {summary.column_names?.map((col, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 rounded-lg bg-blue-50 border border-blue-100 text-blue-700 text-xs font-mono font-medium flex items-center gap-1.5"
                >
                  <Tag className="w-3 h-3 text-blue-500" />
                  {col}
                </span>
              ))}
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
