import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';

export default function DashboardView() {
  const [data, setData] = useState(null);
  const [stats, setStats] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  // Trigger state
  const [triggerProduct, setTriggerProduct] = useState('Groww');
  const [triggerWeek, setTriggerWeek] = useState('2024-W20');
  const [triggerStatus, setTriggerStatus] = useState('');

  useEffect(() => {
    Promise.all([
      fetch('/api/insights').then(res => res.json()),
      fetch('/api/stats').then(res => res.json()),
      fetch('/api/config').then(res => res.json())
    ]).then(([insightsData, statsData, configData]) => {
      setData(insightsData);
      setStats(statsData);
      setConfig(configData);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  const handleTrigger = async (e) => {
    e.preventDefault();
    setTriggerStatus('Starting pipeline...');
    try {
      const res = await fetch('/api/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product: triggerProduct, week: triggerWeek })
      });
      const resData = await res.json();
      setTriggerStatus(resData.message || 'Pipeline started!');
      setTimeout(() => setTriggerStatus(''), 5000);
    } catch(err) {
      setTriggerStatus('Failed to start pipeline');
    }
  };

  if (loading) return <div className="loading">Loading insights...</div>;

  const validInsights = data ? data.filter(i => i.theme && !i.theme.startsWith('Error')).sort((a,b) => b.review_count - a.review_count) : [];
  
  const totalReviews = stats?.total || 0;
  const numThemes = validInsights.length;
  const avgRating = stats?.average || 0;
  
  // Recharts data for BarChart
  const themeData = validInsights.map(i => ({
    name: i.theme.substring(0, 15) + (i.theme.length > 15 ? '...' : ''),
    reviews: i.review_count || 0
  }));

  return (
    <div className="dashboard-grid">
      {/* 1. Trigger & Artifacts Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
        <div className="card">
          <h3 className="section-title">🚀 RUN PIPELINE</h3>
          <form onSubmit={handleTrigger} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', gap: '12px' }}>
              <input type="text" value={triggerProduct} onChange={e => setTriggerProduct(e.target.value)} placeholder="Product (e.g. Groww)" style={{ padding: '8px', borderRadius: '4px', border: '1px solid #334155', background: '#1e293b', color: 'white', flex: 1 }}/>
              <input type="text" value={triggerWeek} onChange={e => setTriggerWeek(e.target.value)} placeholder="Week (e.g. 2024-W20)" style={{ padding: '8px', borderRadius: '4px', border: '1px solid #334155', background: '#1e293b', color: 'white', flex: 1 }}/>
            </div>
            <button type="submit" style={{ padding: '10px', background: '#6366f1', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Trigger Pulse</button>
            {triggerStatus && <div style={{ color: '#4ade80', fontSize: '0.9rem' }}>{triggerStatus}</div>}
          </form>
        </div>

        <div className="card">
          <h3 className="section-title">📄 ARTIFACTS</h3>
          <p style={{ color: '#cbd5e1', marginBottom: '16px' }}>View the full generated Weekly Review Pulse report in Google Docs.</p>
          {config?.google_doc_id ? (
            <a href={`https://docs.google.com/document/d/${config.google_doc_id}/edit`} target="_blank" rel="noreferrer" style={{ display: 'inline-block', padding: '10px 16px', background: '#10b981', color: 'white', textDecoration: 'none', borderRadius: '4px', fontWeight: 'bold' }}>
              Open Google Doc
            </a>
          ) : (
            <p style={{ color: '#f87171' }}>Google Doc ID not configured.</p>
          )}
        </div>
      </div>

      {/* 2. Key Insights (5 fields) */}
      <div className="kpi-row" style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
        <div className="card kpi-card">
          <h3 style={{ color: '#60a5fa' }}>{triggerProduct}</h3>
          <p>Product</p>
        </div>
        <div className="card kpi-card">
          <h3 style={{ color: '#a78bfa' }}>{triggerWeek}</h3>
          <p>Timeline</p>
        </div>
        <div className="card kpi-card">
          <h3 style={{ color: '#34d399' }}>{totalReviews}</h3>
          <p>Reviews Analysed</p>
        </div>
        <div className="card kpi-card">
          <h3 style={{ color: '#f472b6' }}>{avgRating}★</h3>
          <p>Avg Rating</p>
        </div>
        <div className="card kpi-card">
          <h3 style={{ color: '#fbbf24' }}>{numThemes}</h3>
          <p>Top Themes</p>
        </div>
      </div>

      {/* 3. Charts & Visuals */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginTop: '24px' }}>
        <div className="card">
          <h3 className="section-title">🎭 SENTIMENT DISTRIBUTION</h3>
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={stats?.sentiment || []} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                  {stats?.sentiment?.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: 'white' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 className="section-title">📊 THEME FREQUENCY</h3>
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer>
              <BarChart data={themeData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis dataKey="name" type="category" width={120} stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: 'white' }} />
                <Bar dataKey="reviews" fill="#818cf8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 4. Action Ideas */}
      <div className="card" style={{ marginTop: '24px' }}>
        <h3 className="section-title">🚀 STRATEGIC ACTION IDEAS</h3>
        {validInsights.filter(i => i.action_ideas && i.action_ideas.length > 0).slice(0,3).map((insight, idx) => {
          const colors = ['green', 'orange', 'purple'];
          const color = colors[idx % colors.length];
          return (
            <div key={idx} className="action-item">
              <div className={`action-number ${color}`}>{idx + 1}</div>
              <div className="action-text">
                <h5 style={{color: `var(--accent-${color})`}}>{insight.theme}</h5>
                <p>{insight.action_ideas[0]}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
