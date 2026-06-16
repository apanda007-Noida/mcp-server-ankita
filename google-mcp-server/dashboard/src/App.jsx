import React, { useState } from 'react';
import DashboardView from './components/Dashboard';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h2>LIP5</h2>
          <p>App Store Pulse · Groww</p>
        </div>
        <nav className="sidebar-nav">
          <button 
            className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            ⚡ Dashboard
          </button>
          <button 
            className={`nav-btn ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            📄 History
          </button>
          <button 
            className={`nav-btn ${activeTab === 'logs' ? 'active' : ''}`}
            onClick={() => setActiveTab('logs')}
          >
            🖥️ Logs
          </button>
        </nav>
      </aside>
      <main className="main-content">
        <header className="top-header">
          <div className="header-titles">
            <h1>Dashboard</h1>
            <p>Review Analyser · Groww</p>
          </div>
          <div className="status-badge">
            <span className="dot"></span>
            ✓ Done
          </div>
        </header>
        <div className="view-container">
          {activeTab === 'dashboard' && <DashboardView />}
          {activeTab === 'history' && <div className="placeholder-view">History View (Coming Soon)</div>}
          {activeTab === 'logs' && <div className="placeholder-view">Logs View (Coming Soon)</div>}
        </div>
      </main>
    </div>
  );
}

export default App;
