import React, { useState, useEffect } from 'react';
import { 
  BarChart2, 
  TrendingUp, 
  RotateCw, 
  Layers, 
  Users, 
  Building2,
  PieChart as PieIcon,
  Filter
} from 'lucide-react';
import { fetchAnalysisData } from '../services/api';
import { formatINR, formatCompactINR } from '../config/currency';

export default function DataAnalysis() {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchAnalysisData()
      .then(res => setAnalysisData(res))
      .catch(err => console.error("Analysis data fetch error:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !analysisData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-slate-400">
        <RotateCw className="w-8 h-8 animate-spin text-blue-600 mb-3" />
        <p className="text-sm font-medium">Computing Insurance Claim Visualizations...</p>
      </div>
    );
  }

  const diseaseData = analysisData.disease_category_analysis || [];
  const monthlyData = analysisData.monthly_trend || [];
  const genderData = analysisData.gender_analysis || [];
  const hospitalData = analysisData.hospital_type_analysis || [];

  // Disease category chart max value for scaling
  const maxDiseaseAmt = 200000;

  // Monthly dual-axis scaling
  const maxMonthlyCount = 1000;
  const maxMonthlyLakhs = 40;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      
      {/* 1. Fig 5: Claim Amount Analysis by Disease Category */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-100 space-y-6">
        <div>
          <h3 className="text-lg font-bold text-slate-900">
            Claim Amount Analysis by Disease Category
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Average claim amount for each disease category
          </p>
        </div>

        {/* Disease Category Multi-Colored Bar Chart Matching Fig 5 */}
        <div className="py-4">
          <div className="relative h-72 w-full">
            
            {/* Y-Axis Label */}
            <div className="absolute -left-12 top-1/2 -translate-y-1/2 -rotate-90 text-[11px] font-semibold text-slate-500 tracking-wider">
              Average Claim Amount (₹)
            </div>

            {/* Background Grid Lines and Y-Axis Values */}
            <div className="absolute inset-0 flex flex-col justify-between text-[11px] font-mono text-slate-400 pl-16 pr-4">
              {[200000, 150000, 100000, 50000, 0].map((val, idx) => (
                <div key={idx} className="flex items-center gap-2 w-full">
                  <span className="w-14 text-right shrink-0">{val.toLocaleString()}</span>
                  <div className="h-px bg-slate-100 flex-1"></div>
                </div>
              ))}
            </div>

            {/* Vertical Multi-Colored Bars */}
            <div className="absolute inset-0 pl-32 pr-8 pt-6 pb-6 flex items-end justify-between gap-2 sm:gap-6">
              {diseaseData.map((item, idx) => {
                const heightPct = Math.min(100, Math.max(10, (item.avg_amount / maxDiseaseAmt) * 100));
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center h-full justify-end group">
                    {/* Top Value Label */}
                    <span className="text-[11px] font-bold font-mono text-slate-800 mb-1.5 opacity-90 group-hover:scale-110 transition">
                      ₹{Math.round(item.avg_amount).toLocaleString()}
                    </span>

                    {/* Bar */}
                    <div
                      className="w-full max-w-[52px] rounded-t-lg transition-all duration-300 hover:opacity-90 shadow-xs cursor-pointer"
                      style={{
                        height: `${heightPct}%`,
                        backgroundColor: item.color || '#3b82f6'
                      }}
                    ></div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* X-Axis Category Labels */}
          <div className="flex justify-between text-[11px] font-semibold text-slate-600 pl-32 pr-8 pt-3 border-t border-slate-200">
            {diseaseData.map((item, idx) => (
              <span key={idx} className="flex-1 text-center truncate">
                {item.short_label || item.category}
              </span>
            ))}
          </div>
          
          <div className="text-center text-xs font-semibold text-slate-500 mt-2">
            Disease Category
          </div>
        </div>

      </div>

      {/* 2. Fig 6: Monthly Claim Trend Analysis (Dual Axis Combo Chart) */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-100 space-y-6">
        
        {/* Header & Legend */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900">
              Monthly Claim Trend Analysis
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Total claim amount and number of claims per month
            </p>
          </div>

          {/* Dual-Axis Legend Matching Fig 6 */}
          <div className="flex items-center gap-6 text-xs font-semibold">
            <div className="flex items-center gap-2 text-slate-700">
              <span className="w-3.5 h-3.5 rounded bg-blue-500 shrink-0"></span>
              <span>Number of Claims</span>
            </div>
            <div className="flex items-center gap-2 text-rose-600">
              <span className="w-3.5 h-3.5 rounded-full bg-rose-500 shrink-0 flex items-center justify-center">
                <span className="w-1.5 h-1.5 rounded-full bg-white"></span>
              </span>
              <span>Total Claim Amount (₹ in lakhs)</span>
            </div>
          </div>
        </div>

        {/* Dual Axis Chart Area */}
        <div className="py-4">
          <div className="relative h-72 w-full">
            
            {/* Left Y-Axis Label (Number of Claims) */}
            <div className="absolute -left-10 top-1/2 -translate-y-1/2 -rotate-90 text-[11px] font-semibold text-slate-500 tracking-wider">
              Number of Claims
            </div>

            {/* Right Y-Axis Label (Total Claim Amount) */}
            <div className="absolute -right-12 top-1/2 -translate-y-1/2 rotate-90 text-[11px] font-semibold text-rose-500 tracking-wider">
              Total Claim Amount (₹ in lakhs)
            </div>

            {/* Left Grid & Values (0 to 1000) */}
            <div className="absolute inset-0 flex flex-col justify-between text-[11px] font-mono text-slate-400 pl-12 pr-12">
              {[1000, 800, 600, 400, 200, 0].map((val, idx) => {
                const rightVal = Math.round((val / 1000) * maxMonthlyLakhs);
                return (
                  <div key={idx} className="flex items-center justify-between w-full">
                    <span className="w-10 text-right shrink-0">{val}</span>
                    <div className="h-px bg-slate-100 flex-1 mx-3"></div>
                    <span className="w-8 text-left text-rose-500 shrink-0">{rightVal}</span>
                  </div>
                );
              })}
            </div>

            {/* Blue Vertical Bars (Number of Claims) */}
            <div className="absolute inset-0 pl-24 pr-24 pt-4 pb-6 flex items-end justify-between gap-1 sm:gap-4">
              {monthlyData.map((m, idx) => {
                const heightPct = Math.min(100, Math.max(8, (m.claims_count / maxMonthlyCount) * 100));
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center h-full justify-end">
                    <div
                      className="w-full max-w-[28px] bg-blue-500 rounded-t transition-all duration-300 hover:bg-blue-600"
                      style={{ height: `${heightPct}%` }}
                    ></div>
                  </div>
                );
              })}
            </div>

            {/* Red Overlay Polyline (Total Claim Amount in Lakhs) */}
            <svg 
              className="absolute inset-0 pl-24 pr-24 pt-4 pb-6 w-full h-full overflow-visible pointer-events-none"
              viewBox={`0 0 ${monthlyData.length * 40} 100`}
              preserveAspectRatio="none"
            >
              {monthlyData.length > 0 && (
                <polyline
                  fill="none"
                  stroke="#ef4444"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  points={monthlyData.map((m, idx) => {
                    const x = (idx + 0.5) * 40;
                    const y = 92 - (m.total_amount_lakhs / maxMonthlyLakhs) * 85;
                    return `${x},${y}`;
                  }).join(' ')}
                />
              )}

              {/* Red Circular Dots */}
              {monthlyData.map((m, idx) => {
                const x = (idx + 0.5) * 40;
                const y = 92 - (m.total_amount_lakhs / maxMonthlyLakhs) * 85;
                return (
                  <circle
                    key={idx}
                    cx={x}
                    cy={y}
                    r="4.5"
                    fill="#ef4444"
                    stroke="#ffffff"
                    strokeWidth="2"
                  />
                );
              })}
            </svg>

          </div>

          {/* X-Axis Month Labels */}
          <div className="flex justify-between text-[11px] font-medium text-slate-600 pl-24 pr-24 pt-2 border-t border-slate-200">
            {monthlyData.map((m, idx) => (
              <span key={idx} className="flex-1 text-center">{m.month}</span>
            ))}
          </div>

          <div className="text-center text-xs font-semibold text-slate-500 mt-2">
            Month
          </div>
        </div>

      </div>

      {/* 3. Comparative Demographic & Hospital Type Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Gender Comparison */}
        <div className="bg-white rounded-3xl p-6 sm:p-7 shadow-sm border border-slate-100 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Users className="w-4 h-4 text-blue-600" />
              Claim Amount by Gender
            </h4>
            <span className="text-xs text-slate-400 font-medium">Male vs Female</span>
          </div>

          <div className="space-y-4 pt-2">
            {genderData.map((g, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-800">{g.gender} ({g.claims_count.toLocaleString()} claims)</span>
                  <span className="text-blue-600 font-mono">Avg: {g.formatted_avg}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                  <div 
                    className="bg-blue-600 h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, (g.avg_amount / 120000) * 100)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Hospital Type Comparison */}
        <div className="bg-white rounded-3xl p-6 sm:p-7 shadow-sm border border-slate-100 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-emerald-600" />
              Average Claim Amount by Hospital Type
            </h4>
            <span className="text-xs text-slate-400 font-medium">Provider Type</span>
          </div>

          <div className="space-y-4 pt-2">
            {hospitalData.map((h, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-800">{h.hospital_type} ({h.claims_count.toLocaleString()} claims)</span>
                  <span className="text-emerald-600 font-mono">Avg: {h.formatted_avg}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                  <div 
                    className="bg-emerald-600 h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, (h.avg_amount / 120000) * 100)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
