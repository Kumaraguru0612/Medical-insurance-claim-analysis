import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import Dashboard from './components/Dashboard';
import UploadDataset from './components/UploadDataset';
import DataPreview from './components/DataPreview';
import DataAnalysis from './components/DataAnalysis';
import ClaimPrediction from './components/ClaimPrediction';
import AnalysisReport from './components/AnalysisReport';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    try {
      const savedAuth = localStorage.getItem('mediclaim_auth_state');
      return savedAuth === 'true';
    } catch {
      return false;
    }
  });

  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('mediclaim_user');
      return savedUser ? JSON.parse(savedUser) : { username: 'admin', name: 'Administrator', role: 'Claims Officer' };
    } catch {
      return { username: 'admin', name: 'Administrator', role: 'Claims Officer' };
    }
  });

  const [activeTab, setActiveTab] = useState('dashboard');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleLoginSuccess = (user) => {
    setIsAuthenticated(true);
    setCurrentUser(user);
    localStorage.setItem('mediclaim_auth_state', 'true');
    localStorage.setItem('mediclaim_user', JSON.stringify(user));
    setActiveTab('dashboard');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('mediclaim_auth_state');
    setActiveTab('dashboard');
  };

  const handleDatasetChange = () => {
    setRefreshKey(prev => prev + 1);
  };

  // If not authenticated, render Login Page (Fig 1)
  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  // Authenticated Shell (Fig 2 - 8)
  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex font-sans antialiased">
      
      {/* Left Navy Sidebar Matching Screenshot */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onLogout={handleLogout} 
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen overflow-x-hidden">
        
        {/* Top Header Bar */}
        <Topbar 
          activeTab={activeTab} 
          user={currentUser} 
        />

        {/* Page View Container */}
        <main className="flex-1 p-6 sm:p-8 lg:p-10 max-w-7xl w-full">
          
          {activeTab === 'dashboard' && (
            <Dashboard key={refreshKey} />
          )}

          {activeTab === 'upload' && (
            <UploadDataset onDatasetChange={handleDatasetChange} />
          )}

          {activeTab === 'preview' && (
            <DataPreview key={refreshKey} />
          )}

          {activeTab === 'analysis' && (
            <DataAnalysis key={refreshKey} />
          )}

          {activeTab === 'prediction' && (
            <ClaimPrediction key={refreshKey} />
          )}

          {activeTab === 'reports' && (
            <AnalysisReport key={refreshKey} />
          )}

        </main>

        {/* Subtle Footer */}
        <footer className="border-t border-slate-200/80 bg-white py-4 px-8 text-center text-xs text-slate-400 print:hidden">
          Medical Insurance Claim Analysis System &copy; {new Date().getFullYear()} &bull; Professional Edition
        </footer>

      </div>

    </div>
  );
}
