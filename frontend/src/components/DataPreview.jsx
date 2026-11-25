import React, { useState, useEffect } from 'react';
import { 
  Search, 
  RotateCw, 
  ChevronLeft, 
  ChevronRight, 
  ArrowUpDown, 
  Filter, 
  FileSpreadsheet,
  Download
} from 'lucide-react';
import { fetchDatasetRecords } from '../services/api';
import { formatINR } from '../config/currency';

export default function DataPreview() {
  const [recordsData, setRecordsData] = useState({ records: [], total_records: 0, total_pages: 1, page: 1 });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('id');
  const [sortDir, setSortDir] = useState('asc');

  const loadRecords = () => {
    setLoading(true);
    fetchDatasetRecords({
      page,
      per_page: perPage,
      search,
      sort_by: sortBy,
      sort_dir: sortDir,
      claim_status: statusFilter
    })
      .then(data => setRecordsData(data))
      .catch(err => console.error("Records error:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadRecords();
  }, [page, perPage, search, sortBy, sortDir, statusFilter]);

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortDir('asc');
    }
    setPage(1);
  };

  const getStatusBadge = (status) => {
    const s = String(status).toLowerCase();
    if (s === 'approved') {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/80">
          Approved
        </span>
      );
    } else if (s === 'rejected') {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200/80">
          Rejected
        </span>
      );
    } else {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200/80">
          Pending
        </span>
      );
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      
      {/* Table Container Card Matching Fig 4 */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-100 space-y-5">
        
        {/* Search and Filters Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-4 border-b border-slate-100">
          
          {/* Search Box */}
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search diagnosis, policy, status..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs sm:text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
            />
          </div>

          {/* Right Controls (Status filter & Per page) */}
          <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
            
            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-blue-500 cursor-pointer"
            >
              <option value="all">Status: All</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="pending">Pending</option>
            </select>

            {/* Per Page Selector */}
            <select
              value={perPage}
              onChange={(e) => {
                setPerPage(Number(e.target.value));
                setPage(1);
              }}
              className="px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-blue-500 cursor-pointer"
            >
              <option value={10}>Show 10</option>
              <option value={25}>Show 25</option>
              <option value={50}>Show 50</option>
              <option value={100}>Show 100</option>
            </select>

          </div>

        </div>

        {/* Data Table */}
        <div className="overflow-x-auto rounded-2xl border border-slate-100">
          <table className="w-full text-left text-xs sm:text-sm text-slate-700">
            <thead className="bg-slate-50 text-slate-500 font-semibold text-xs border-b border-slate-200/80 select-none">
              <tr>
                <th onClick={() => handleSort('id')} className="py-3.5 px-4 cursor-pointer hover:text-slate-900">
                  <div className="flex items-center gap-1.5 font-bold">ID <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" /></div>
                </th>
                <th onClick={() => handleSort('age')} className="py-3.5 px-4 cursor-pointer hover:text-slate-900">
                  <div className="flex items-center gap-1.5 font-bold">Age <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" /></div>
                </th>
                <th onClick={() => handleSort('gender')} className="py-3.5 px-4 cursor-pointer hover:text-slate-900">
                  <div className="flex items-center gap-1.5 font-bold">Gender <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" /></div>
                </th>
                <th onClick={() => handleSort('policy_type')} className="py-3.5 px-4 cursor-pointer hover:text-slate-900">
                  <div className="flex items-center gap-1.5 font-bold">Policy_Type <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" /></div>
                </th>
                <th onClick={() => handleSort('claim_amount')} className="py-3.5 px-4 cursor-pointer hover:text-slate-900">
                  <div className="flex items-center gap-1.5 font-bold">Claim_Amount <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" /></div>
                </th>
                <th className="py-3.5 px-4 font-bold">Claim_Status</th>
                <th className="py-3.5 px-4 font-bold">Diagnosis</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-400">
                    <RotateCw className="w-6 h-6 animate-spin mx-auto text-blue-600 mb-2" />
                    Fetching dataset records...
                  </td>
                </tr>
              ) : recordsData.records.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-400">
                    No records found matching your query.
                  </td>
                </tr>
              ) : (
                recordsData.records.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-600">
                      {r.id}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">
                      {r.age}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">
                      {r.gender}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">
                      {r.policy_type}
                    </td>
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-900">
                      {r.claim_amount.toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4">
                      {getStatusBadge(r.claim_status)}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-800">
                      {r.diagnosis}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 text-xs text-slate-500">
          <div>
            Showing <strong className="text-slate-800">{recordsData.records.length}</strong> of <strong className="text-slate-800">{recordsData.total_records.toLocaleString()}</strong> total records
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page <= 1}
              className="px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 disabled:opacity-40 hover:bg-slate-100 transition cursor-pointer flex items-center gap-1"
            >
              <ChevronLeft className="w-3.5 h-3.5" /> Previous
            </button>
            <span className="px-3 py-1.5 rounded-lg bg-blue-50 border border-blue-100 text-blue-700 font-mono font-bold">
              Page {recordsData.page} of {recordsData.total_pages}
            </span>
            <button
              onClick={() => setPage(Math.min(recordsData.total_pages, page + 1))}
              disabled={page >= recordsData.total_pages}
              className="px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 disabled:opacity-40 hover:bg-slate-100 transition cursor-pointer flex items-center gap-1"
            >
              Next <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

      </div>

    </div>
  );
}
