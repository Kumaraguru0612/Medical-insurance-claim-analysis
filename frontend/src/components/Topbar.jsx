import React from 'react';
import { Bell, User, ChevronDown } from 'lucide-react';

export default function Topbar({ activeTab, user }) {
  const getHeaderInfo = () => {
    switch (activeTab) {
      case 'upload':
        return { title: 'Upload Dataset', subtitle: 'Upload your insurance claim dataset (CSV format)' };
      case 'preview':
        return { title: 'Dataset Preview', subtitle: 'First 10 records from the uploaded dataset' };
      case 'analysis':
        return { title: 'Data Analysis', subtitle: 'Visual analysis of medical insurance claims' };
      case 'prediction':
        return { title: 'Claim Status Prediction', subtitle: 'Enter patient details to predict claim approval' };
      case 'reports':
        return { title: 'Analysis Report', subtitle: 'Download or view the analysis report' };
      case 'dashboard':
      default:
        return { title: 'Dashboard', subtitle: 'Overview of Insurance Claim Data' };
    }
  };

  const { title, subtitle } = getHeaderInfo();

  return (
    <header className="bg-white border-b border-slate-200/80 px-8 py-5 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      {/* Title & Subtitle */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
          {title}
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 font-normal mt-0.5">
          {subtitle}
        </p>
      </div>

      {/* Right User & Notification Controls */}
      <div className="flex items-center gap-4">
        {/* Notification Bell */}
        <button className="relative p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition cursor-pointer">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full"></span>
        </button>

        {/* User Profile Badge */}
        <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
          <div className="w-9 h-9 rounded-full bg-blue-100 border border-blue-200 text-blue-700 flex items-center justify-center font-bold text-xs">
            <User className="w-4 h-4 text-blue-600" />
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-bold text-slate-800 leading-tight">
              {user?.name || 'Administrator'}
            </div>
            <div className="text-[10px] text-slate-500 font-medium">
              {user?.role || 'Claims Officer'}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
