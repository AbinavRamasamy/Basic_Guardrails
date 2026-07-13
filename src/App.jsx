import React, { useState } from 'react';
import { Shield, ShieldAlert, ShieldCheck, AlertCircle, FileText, Send, Sparkles, Terminal, Code, Info } from 'lucide-react';

function App() {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [showInstructions, setShowInstructions] = useState(false);

  const presets = [
    { label: 'Safe Input', text: 'Hello, this is a friendly request to process some data.' },
    { label: 'Keyword Blocker (sudo)', text: 'I need sudo access to execute root privileges.' },
    { label: 'Length Constraint (>100)', text: 'This text is deliberately padded to exceed the one hundred character boundary limit. It has excessive words that will trip the length guardrail.' },
    { label: 'Format Constraint (< >)', text: 'Is it okay to use <html> tags here?' },
    { label: 'Sensitive Leak (SSN & CC)', text: 'My SSN is 123-45-6789 and my card number is 4111-2222-3333-4444.' },
  ];

  const handleValidation = async (text) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });
      if (!response.ok) {
        throw new Error('API server returned an error.');
      }
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    handleValidation(inputText);
  };

  const applyPreset = (text) => {
    setInputText(text);
    handleValidation(text);
  };

  return (
    <div>
      <header className="app-header">
        <h1 className="app-title">
          <Shield size={38} color="#3b82f6" /> Basic Guardrails Portal
        </h1>
        <p className="app-subtitle">FastAPI + React input validation sandbox running basic query guardrails</p>
      </header>

      {/* Info Block explaining the Guardrails */}
      <section style={{ 
        background: 'var(--bg-panel)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '20px',
        marginBottom: '24px',
        fontSize: '0.9rem',
        lineHeight: '1.5'
      }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: 'white' }}>
          <Info size={18} style={{ color: '#3b82f6' }} /> Active Guardrails in this App
        </h3>
        <ul style={{ paddingLeft: '20px', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <li><strong>Prohibited Keyword Blocker:</strong> A basic word filter implemented via substring matching. Scans the input string for forbidden administration keywords (`admin`, `root`, `sudo`, `hack`, `override`) and immediately halts processing if found.</li>
          <li><strong>Input Constraints Rail:</strong> Built-in structural validator using FastAPI's routing parameters. Rejects any inputs that exceed 100 characters in length or contain HTML/JSX brackets ([, ], &lt;, &gt;) to prevent injection or buffer issues.</li>
          <li><strong>Sensitive Pattern Leak Blocker:</strong> A regular expression pattern detector. Identifies standard formatting signatures of Social Security Numbers (SSN) and Credit Card numbers (CC), redacting them from the final string while flagging the request.</li>
        </ul>
        
        <button 
          className="submit-btn" 
          style={{ 
            marginTop: '16px',
            background: 'transparent',
            border: '1px solid var(--border-color)',
            fontSize: '0.85rem',
            padding: '6px 12px',
            boxShadow: 'none'
          }}
          onClick={() => setShowInstructions(!showInstructions)}
        >
          <Code size={14} /> {showInstructions ? 'Hide Run Code' : 'Show Run Code'}
        </button>

        {showInstructions && (
          <div style={{ 
            marginTop: '16px', 
            background: '#0a0c10', 
            padding: '16px', 
            borderRadius: '12px',
            fontFamily: 'monospace',
            fontSize: '0.8rem',
            border: '1px solid var(--border-color)',
            overflowX: 'auto'
          }}>
            <p style={{ color: '#38bdf8', marginBottom: '8px' }}># 1. Install dependencies</p>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>pip install -r requirements.txt<br />npm install</p>
            
            <p style={{ color: '#38bdf8', marginBottom: '8px' }}># 2. Run backend server (from the app folder)</p>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>uvicorn api.index:app --reload --port 8000</p>
            
            <p style={{ color: '#38bdf8', marginBottom: '8px' }}># 3. Run React frontend dev server</p>
            <p style={{ color: 'var(--text-secondary)' }}>npm run dev</p>
          </div>
        )}
      </section>

      <main className="main-card">
        {/* Presets */}
        <div style={{ marginBottom: '24px' }}>
          <p className="input-label" style={{ marginBottom: '10px' }}>Test Presets</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {presets.map((preset, index) => (
              <button
                key={index}
                className="submit-btn"
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  boxShadow: 'none',
                  fontSize: '0.85rem',
                  padding: '8px 16px',
                }}
                onClick={() => applyPreset(preset.text)}
              >
                <Sparkles size={14} style={{ color: '#3b82f6' }} /> {preset.label}
              </button>
            ))}
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="input-section">
          <label className="input-label" htmlFor="guardrail-input">Raw Text Input</label>
          <div className="input-container">
            <textarea
              id="guardrail-input"
              className="text-input"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your query or click a test preset above..."
            />
          </div>
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Validating...' : 'Run Flow'} <Send size={16} />
          </button>
        </form>

        {error && (
          <div style={{ display: 'flex', gap: '8px', color: 'var(--error-color)', padding: '16px', borderRadius: '12px', background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.1)', marginBottom: '32px' }}>
            <AlertCircle size={20} /> <strong>Error:</strong> {error}
          </div>
        )}

        {/* Guardrails Status Pipeline */}
        <div>
          <h2 className="pipeline-title">
            <FileText size={20} style={{ color: '#3b82f6' }} /> Validation Pipeline
          </h2>
          
          <div className="pipeline-container">
            {/* Rail 1 */}
            <div className={`rail-card ${results ? (results.keyword_rail.passed ? 'passed' : 'failed') : ''}`}>
              <div className="rail-info">
                <span className="rail-name">Prohibited Keyword Blocker</span>
                <span className="rail-desc">Blocks inputs containing system commands or credentials (admin, root, sudo, hack, override)</span>
                {results && !results.keyword_rail.passed && (
                  <span style={{ color: 'var(--error-color)', fontSize: '0.85rem', marginTop: '6px' }}>
                    🚨 {results.keyword_rail.message}
                  </span>
                )}
              </div>
              <div className={`rail-badge ${results ? (results.keyword_rail.passed ? 'pass' : 'fail') : ''}`}>
                {results ? (
                  results.keyword_rail.passed ? (
                    <><ShieldCheck size={16} /> Pass</>
                  ) : (
                    <><ShieldAlert size={16} /> Blocked</>
                  )
                ) : (
                  'Inactive'
                )}
              </div>
            </div>

            {/* Rail 2 */}
            <div className={`rail-card ${results ? (results.constraint_rail.passed ? 'passed' : 'failed') : ''}`}>
              <div className="rail-info">
                <span className="rail-name">Input Constraints Rail</span>
                <span className="rail-desc">Enforces length limitation (max 100 characters) and blocks HTML special characters (&lt;, &gt;, [, ])</span>
                {results && !results.constraint_rail.passed && (
                  <span style={{ color: 'var(--error-color)', fontSize: '0.85rem', marginTop: '6px' }}>
                    🚨 {results.constraint_rail.message}
                  </span>
                )}
              </div>
              <div className={`rail-badge ${results ? (results.constraint_rail.passed ? 'pass' : 'fail') : ''}`}>
                {results ? (
                  results.constraint_rail.passed ? (
                    <><ShieldCheck size={16} /> Pass</>
                  ) : (
                    <><ShieldAlert size={16} /> Blocked</>
                  )
                ) : (
                  'Inactive'
                )}
              </div>
            </div>

            {/* Rail 3 */}
            <div className={`rail-card ${results ? (results.leak_rail.passed ? 'passed' : 'failed') : ''}`}>
              <div className="rail-info">
                <span className="rail-name">Sensitive Pattern Leak Blocker</span>
                <span className="rail-desc">Detects and redacts Credit Card numbers or Social Security Numbers (SSN)</span>
                {results && !results.leak_rail.passed && (
                  <span style={{ color: 'var(--error-color)', fontSize: '0.85rem', marginTop: '6px' }}>
                    🚨 {results.leak_rail.message}
                  </span>
                )}
              </div>
              <div className={`rail-badge ${results ? (results.leak_rail.passed ? 'pass' : 'fail') : ''}`}>
                {results ? (
                  results.leak_rail.passed ? (
                    <><ShieldCheck size={16} /> Pass</>
                  ) : (
                    <><ShieldAlert size={16} /> Flagged</>
                  )
                ) : (
                  'Inactive'
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Final Result Panel */}
        {results && (
          <div className="result-section">
            <div className="result-header">
              <h3 className="result-title">Pipeline Output</h3>
              <div className={`status-indicator ${results.overall_passed ? 'success' : 'error'}`}>
                {results.overall_passed ? (
                  <><ShieldCheck size={22} /> FLOW COMPLETED</>
                ) : (
                  <><ShieldAlert size={22} /> FLOW BLOCKED</>
                )}
              </div>
            </div>
            <div className="result-box">
              {results.overall_passed ? (
                <div>
                  <p style={{ color: 'var(--text-secondary)', marginBottom: '8px' }}>Processed string:</p>
                  <p style={{ fontSize: '1.1rem', wordBreak: 'break-all' }}>{results.leak_rail.redacted_text}</p>
                </div>
              ) : (
                <div>
                  <p style={{ color: 'var(--error-color)', fontWeight: 600, marginBottom: '6px' }}>The request was halted by the guardrails:</p>
                  <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {!results.keyword_rail.passed && <li><strong>Keyword Blocker:</strong> {results.keyword_rail.message}</li>}
                    {!results.constraint_rail.passed && <li><strong>Input Constraint:</strong> {results.constraint_rail.message}</li>}
                    {!results.leak_rail.passed && <li><strong>Sensitive Leak Blocker:</strong> {results.leak_rail.message} (Redacted preview: <em>{results.leak_rail.redacted_text}</em>)</li>}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
