import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  IndianRupee, 
  BarChart2, 
  Users, 
  RotateCw,
  TrendingUp,
  Activity
} from 'lucide-react';
import { fetchDashboardKPIs } from '../services/api';
import { formatINR, formatCompactINR } from '../config/currency';

export default function Dashboard() {
  const [kpis, setKpis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchDashboardKPIs()
      .then(data => setKpis(data))
      .catch(err => console.error("Error fetching dashboard KPIs:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !kpis) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-slate-400">
        <RotateCw className="w-8 h-8 animate-spin text-blue-600 mb-3" />
        <p className="text-sm font-medium">Loading Insurance Claim Analytics...</p>
      </div>
    );
  }

  // Monthly trend data points
  const monthlyTrend = kpis.monthly_trend || [];
  const maxMonthlyClaims = Math.max(...monthlyTrend.map(m => m.claims_count), 1000);

  // Status distribution
  const statusDist = kpis.status_distribution || [
    { name: 'Approved', percentage: 66.2, color: '#2563eb' },
    { name: 'Rejected', percentage: 18.6, color: '#dc2626' },
    { name: 'Pending', percentage: 15.2, color: '#f59e0b' }
  ];

  // SVG Pie calculations
  let accumulatedAngle = 0;
  const pieSlices = statusDist.map(item => {
    const angle = (item.percentage / 100) * 360;
    const startAngle = accumulatedAngle;
    accumulatedAngle += angle;

    const x1 = 100 + 80 * Math.cos((Math.PI * (startAngle - 90)) / 180);
    const y1 = 100 + 80 * Math.sin((Math.PI * (startAngle - 90)) / 180);
    const x2 = 100 + 80 * Math.cos((Math.PI * (accumulatedAngle - 90)) / 180);
    const y2 = 100 + 80 * Math.sin((Math.PI * (accumulatedAngle - 90)) / 180);
    const largeArc = angle > 180 ? 1 : 0;

    const pathData = `M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArc} 1 ${x2} ${y2} Z`;
    return { ...item, pathData };
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      
      {/* 4 Colorful KPI Cards Matching Fig 2 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Card 1: Total Claims (Blue) */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 flex items-center gap-4 transition hover:shadow-md">
          <div className="w-14 h-14 rounded-2xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-600/25 shrink-0">
            <FileText className="w-7 h-7" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-500 block">Total Claims</span>
            <span className="text-2xl sm:text-[26px] font-extrabold text-slate-900 font-mono tracking-tight block mt-0.5">
              {kpis.formatted_total_claims || kpis.total_claims?.toLocaleString()}
            </span>
          </div>
        </div>

        {/* Card 2: Total Claim Amount (Green) */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 flex items-center gap-4 transition hover:shadow-md">
          <div className="w-14 h-14 rounded-2xl bg-emerald-600 flex items-center justify-center text-white shadow-md shadow-emerald-600/25 shrink-0">
            <span className="text-2xl font-black">₹</span>
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-500 block">Total Claim Amount</span>
            <span className="text-2xl sm:text-[26px] font-extrabold text-slate-900 font-mono tracking-tight block mt-0.5">
              {kpis.formatted_total_claim_amount || formatCompactINR(kpis.total_claim_amount)}
            </span>
          </div>
        </div>

        {/* Card 3: Avg Claim Amount (Orange) */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 flex items-center gap-4 transition hover:shadow-md">
          <div className="w-14 h-14 rounded-2xl bg-orange-500 flex items-center justify-center text-white shadow-md shadow-orange-500/25 shrink-0">
            <BarChart2 className="w-7 h-7" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-500 block">Avg Claim Amount</span>
            <span className="text-2xl sm:text-[26px] font-extrabold text-slate-900 font-mono tracking-tight block mt-0.5">
              {kpis.formatted_avg_claim_amount || formatINR(kpis.avg_claim_amount)}
            </span>
          </div>
        </div>

        {/* Card 4: Approved Claims (Purple) */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 flex items-center gap-4 transition hover:shadow-md">
          <div className="w-14 h-14 rounded-2xl bg-purple-600 flex items-center justify-center text-white shadow-md shadow-purple-600/25 shrink-0">
            <Users className="w-7 h-7" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-500 block">Approved Claims</span>
            <span className="text-2xl sm:text-[26px] font-extrabold text-slate-900 font-mono tracking-tight block mt-0.5">
              {kpis.formatted_approved_claims || kpis.approved_claims?.toLocaleString()}
            </span>
          </div>
        </div>

      </div>

      {/* 2 Main Dashboard Charts (Side by Side) Matching Fig 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Chart: Claim Status Distribution (Donut / Pie) */}
        <div className="lg:col-span-5 bg-white rounded-2xl p-6 sm:p-7 shadow-sm border border-slate-100 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Claim Status Distribution
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Percentage breakdown of claims approval status</p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 py-6 my-auto">
            {/* SVG Pie Chart */}
            <div className="relative w-48 h-48 shrink-0">
              <svg viewBox="0 0 200 200" className="w-full h-full transform -rotate-90">
                {pieSlices.map((slice, idx) => (
                  <path
                    key={idx}
                    d={slice.pathData}
                    fill={slice.color}
                    className="transition-all duration-300 hover:opacity-90 cursor-pointer"
                  />
                ))}
              </svg>
            </div>

            {/* Legend on the right */}
            <div className="space-y-3 shrink-0 font-sans">
              {statusDist.map((item, idx) => (
                <div key={idx} className="flex items-center gap-3 text-xs">
                  <span 
                    className="w-3.5 h-3.5 rounded-full shrink-0" 
                    style={{ backgroundColor: item.color }}
                  ></span>
                  <span className="font-medium text-slate-700">
                    {item.name} ({item.percentage}%)
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 text-center text-xs text-slate-400">
            Total verified claims: <strong className="text-slate-700">{kpis.formatted_total_claims}</strong>
          </div>
        </div>

        {/* Right Chart: Monthly Claim Trend (Line Chart with Circular Nodes) */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-6 sm:p-7 shadow-sm border border-slate-100 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Monthly Claim Trend
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Number of insurance claims submitted per calendar month</p>
          </div>

          {/* Line Chart Area */}
          <div className="py-4 my-auto">
            <div className="relative h-56 w-full">
              
              {/* Y-Axis Label */}
              <div className="absolute -left-6 top-1/2 -translate-y-1/2 -rotate-90 text-[10px] font-semibold text-slate-400 tracking-wider">
                Number of Claims
              </div>

              {/* Grid Lines & Labels */}
              <div className="absolute inset-0 flex flex-col justify-between text-[10px] font-mono text-slate-400 pl-6 pr-2">
                {[1000, 800, 600, 400, 200, 0].map((val, idx) => (
                  <div key={idx} className="flex items-center gap-2 w-full">
                    <span className="w-8 text-right shrink-0">{val}</span>
                    <div className="h-px bg-slate-100 flex-1"></div>
                  </div>
                ))}
              </div>

              {/* SVG Line and Points */}
              <svg 
                className="absolute inset-0 pl-16 pr-4 pt-2 pb-6 w-full h-full overflow-visible"
                viewBox={`0 0 ${monthlyTrend.length * 40} 100`}
                preserveAspectRatio="none"
              >
                {/* Polyline */}
                {monthlyTrend.length > 0 && (
                  <polyline
                    fill="none"
                    stroke="#2563eb"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={monthlyTrend.map((m, idx) => {
                      const x = (idx + 0.5) * 40;
                      const y = 90 - (m.claims_count / maxMonthlyClaims) * 80;
                      return `${x},${y}`;
                    }).join(' ')}
                  />
                )}

                {/* Circular Nodes */}
                {monthlyTrend.map((m, idx) => {
                  const x = (idx + 0.5) * 40;
                  const y = 90 - (m.claims_count / maxMonthlyClaims) * 80;
                  return (
                    <g key={idx} className="group cursor-pointer">
                      <circle
                        cx={x}
                        cy={y}
                        r="4"
                        fill="#2563eb"
                        stroke="#ffffff"
                        strokeWidth="2"
                        className="transition duration-200 group-hover:r-6"
                      />
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* X-Axis Month Labels */}
            <div className="flex justify-between text-[11px] font-medium text-slate-500 pl-16 pr-4 pt-2">
              {monthlyTrend.map((m, idx) => (
                <span key={idx} className="text-center">{m.month}</span>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
            <span>Peak Utilization: <strong className="text-slate-700">August / September</strong></span>
            <span>Annual Portfolio Liability: <strong className="text-blue-600 font-mono">{kpis.formatted_total_claim_amount}</strong></span>
          </div>
        </div>

      </div>

    </div>
  );
}
