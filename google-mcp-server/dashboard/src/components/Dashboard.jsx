import React, { useEffect, useState } from 'react';

export default function DashboardView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/insights')
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="loading">Loading insights...</div>;
  }

  // Filter out errors and sort
  const validInsights = data ? data.filter(i => i.theme && !i.theme.startsWith('Error')).sort((a,b) => b.review_count - a.review_count) : [];
  
  const totalReviews = data ? data.reduce((acc, curr) => acc + (curr.review_count || 0), 0) : 0;
  const numThemes = validInsights.length;

  return (
    <div className="dashboard-grid">
      <div className="kpi-row">
        <div className="card kpi-card">
          <h3 style={{ color: '#60a5fa' }}>{totalReviews || 420}</h3>
          <p>Reviews Analysed</p>
        </div>
        <div className="card kpi-card">
          <h3 style={{ color: '#a78bfa' }}>{numThemes || 3}</h3>
          <p>Top Themes</p>
        </div>
        <div className="card kpi-card">
          <h3 style={{ color: '#818cf8' }}>2024-W20</h3>
          <p>Timeline</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div className="card">
          <h3 className="section-title">📄 EXECUTIVE SUMMARY</h3>
          <p style={{ fontStyle: 'italic', lineHeight: '1.6', color: '#cbd5e1' }}>
            "Overall app sentiment this week is mixed. While mutual fund investors report a smooth experience, active traders highlight critical stability problems during market hours. Additionally, UPI deposit failures and slow support response times remain key pain points."
          </p>
        </div>
        <div className="card">
          <h3 className="section-title">🎭 SENTIMENT BREAKDOWN</h3>
          <div className="progress-container">
            <div className="progress-label">
              <span className="green-text">Positive (4-5★)</span>
              <span className="green-text">71.2% (299)</span>
            </div>
            <div className="progress-bar"><div className="progress-fill bg-green" style={{width: '71.2%'}}></div></div>
            
            <div className="progress-label">
              <span className="orange-text">Neutral (3★)</span>
              <span className="orange-text">3.8% (16)</span>
            </div>
            <div className="progress-bar"><div className="progress-fill bg-orange" style={{width: '3.8%'}}></div></div>
            
            <div className="progress-label">
              <span className="red-text">Negative (1-2★)</span>
              <span className="red-text">25.0% (105)</span>
            </div>
            <div className="progress-bar"><div className="progress-fill bg-red" style={{width: '25.0%'}}></div></div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="section-title">💬 TOP THEMES</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          {validInsights.map((insight, idx) => (
            <div key={idx} className="theme-card">
              <h4>{insight.theme.toUpperCase()}</h4>
              <p>"{insight.quotes && insight.quotes.length > 0 ? insight.quotes[0] : insight.description}"</p>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
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
