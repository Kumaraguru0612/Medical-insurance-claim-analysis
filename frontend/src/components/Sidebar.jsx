import React from 'react';
import { 
  ShieldCheck, 
  LayoutDashboard, 
  UploadCloud, 
  Table, 
  BarChart2, 
  Sliders, 
  FileText, 
  LogOut 
} from 'lucide-react';

export const navigationItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'upload', label: 'Upload Dataset', icon: UploadCloud },
  { id: 'preview', label: 'Data Preview', icon: Table },
  { id: 'analysis', label: 'Analysis', icon: BarChart2 },
  { id: 'prediction', label: 'Prediction', icon: Sliders },
  { id: 'reports', label: 'Reports', icon: FileText },
];

export default function Sidebar({ activeTab, setActiveTab, onLogout }) {
  return (
    <aside className="w-64 bg-[#0a1128] text-white flex flex-col justify-between shrink-0 min-h-screen border-r border-slate-800/60 select-none">
      
      {/* Top Header Logo */}
      <div>
        <div className="p-6 border-b border-slate-800/60 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-600/30">
            <ShieldCheck className="w-6 h-6" strokeWidth={2.2} />
          </div>
          <div>
            <h1 className="text-sm font-extrabold tracking-tight text-white leading-tight">
              Medical Insurance
            </h1>
            <h2 className="text-xs font-semibold text-slate-300">
              Claim Analysis
            </h2>
          </div>
        </div>

        {/* Navigation Items List */}
        <nav className="p-4 space-y-1.5 mt-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs sm:text-sm font-medium transition-all cursor-pointer ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30 font-semibold'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Logout Button */}
      <div className="p-4 border-t border-slate-800/60">
        <button
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs sm:text-sm font-medium text-slate-400 hover:bg-rose-950/40 hover:text-rose-400 hover:border-rose-900/40 transition cursor-pointer"
        >
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>

    </aside>
  );
}
