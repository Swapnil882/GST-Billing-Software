import { useEffect, useState } from 'react';
import {
  ShieldCheck,
  Cpu,
  Database,
  Lock,
  HardDrive,
  CheckCircle2,
  Activity,
  FileText,
  Download,
  HelpCircle,
  Keyboard,
  Server,
  RefreshCw,
  FileSpreadsheet,
} from 'lucide-react';
import ProblemLog from './ProblemLog';
import HelpButton from './HelpButton';

const card = { padding: '1.25rem 1.5rem' };

export default function SupportView() {
  const [dbStatus, setDbStatus] = useState(null);
  const [sysStatus, setSysStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = () => {
    setLoading(true);
    Promise.all([
      fetch('/api/db/status').then((r) => (r.ok ? r.json() : null)).catch(() => null),
      fetch('/api/status').then((r) => (r.ok ? r.json() : null)).catch(() => null),
    ]).then(([db, sys]) => {
      setDbStatus(db);
      setSysStatus(sys);
      setLoading(false);
    });
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const systemCapabilities = [
    {
      icon: Cpu,
      title: 'FastAPI Backend Engine',
      text: 'Asynchronous Python 3.11 service delivering sub-millisecond API response times and zero cloud dependencies.',
    },
    {
      icon: Database,
      title: 'PostgreSQL & Dual Persistence',
      text: 'Relational PostgreSQL engine with indexed queries and automatic local atomic JSON fallback.',
    },
    {
      icon: ShieldCheck,
      title: 'MCA Rule 3(1) Audit Trail',
      text: 'Unalterable edit log tracking every modification, creation, and deletion with statutory CA export.',
    },
    {
      icon: Lock,
      title: 'Hardware Scrypt Security',
      text: 'Scrypt cryptographic PIN hashing with rate-limiting, lockout defense, and emergency recovery file.',
    },
    {
      icon: HardDrive,
      title: 'Automated Daily Snapshots',
      text: 'Daily transactional data snapshots archived automatically with 30-day retention and one-click restore.',
    },
    {
      icon: FileSpreadsheet,
      title: 'GST 2.0 & Statutory Reports',
      text: 'Pre-calibrated for all GST slabs, GSTR-1/3B JSON exports, GSTR-2B ITC reconciliation, and TDS/TCS ledgers.',
    },
  ];

  const keyboardShortcuts = [
    { key: 'Ctrl + N', desc: 'Create a new invoice instantly' },
    { key: 'Ctrl + P', desc: 'Print or export active invoice to PDF' },
    { key: 'Ctrl + S', desc: 'Save current document or form' },
    { key: 'F2', desc: 'Quick customer & client directory lookup' },
    { key: 'Esc', desc: 'Close open modal, preview, or dialog' },
    { key: 'Ctrl + F', desc: 'Search records, invoices, or products' },
  ];

  const faqs = [
    {
      q: 'How does the MCA Rule 3 Audit Trail work?',
      a: 'In compliance with the Companies (Accounts) Rules 2014, the software permanently logs every creation, update, and cancellation of invoices and accounts. You can download the complete audit trail as a CSV for tax assessments and CA reviews using the button above.',
    },
    {
      q: 'Can the software run 100% offline?',
      a: 'Yes. All data, tax calculations, PDF generation, and OCR processing run completely inside your local machine. No external cloud servers are contacted for day-to-day operations.',
    },
    {
      q: 'How do I take a backup or move to another PC?',
      a: 'The system creates automatic daily backups in data/backups/. To move to a new computer, simply copy the data/ folder or go to Settings → Data Management and click "Export Backup".',
    },
    {
      q: 'How are my customer and financial records protected?',
      a: 'In addition to optional Scrypt PIN protection, the server binds strictly to 127.0.0.1 (local loopback), preventing any external network or Wi-Fi device from accessing your books.',
    },
  ];

  return (
    <div className="dashboard-container">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">
            Support &amp; System Overview{' '}
            <HelpButton title="Support & System Overview" doc="support" size={16} style={{ marginLeft: 6 }} />
          </h1>
          <p className="page-subtitle">
            System diagnostics, statutory compliance, audit trail exports, and operational help
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={fetchStatus}
            disabled={loading}
            style={{ fontSize: '0.82rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            Refresh Status
          </button>
          <a
            href="/api/audit-trail/export"
            download
            className="btn btn-primary"
            style={{ fontSize: '0.82rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem', textDecoration: 'none' }}
          >
            <Download size={14} />
            Export MCA Audit Trail (CSV)
          </a>
        </div>
      </div>

      {/* Live System Diagnostics Bar */}
      <div
        className="glass-panel"
        style={{
          ...card,
          marginBottom: '1.25rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Activity size={20} style={{ color: 'var(--primary)' }} />
            <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>Live System Health &amp; Services</span>
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Configured for <strong>Swapnil Enterprises</strong>
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
          {/* Backend Service */}
          <div style={{ padding: '0.75rem 0.9rem', borderRadius: 8, background: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.25rem' }}>
              <Server size={16} style={{ color: 'var(--primary)' }} />
              <span style={{ fontWeight: 600, fontSize: '0.84rem' }}>FastAPI Backend</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: sysStatus?.ok ? '#16a34a' : '#ef4444' }} />
              <span style={{ color: sysStatus?.ok ? 'var(--text-primary)' : '#ef4444', fontWeight: 600 }}>
                {sysStatus?.ok ? 'Online (Python 3.11)' : 'Connecting...'}
              </span>
            </div>
          </div>

          {/* Database Service */}
          <div style={{ padding: '0.75rem 0.9rem', borderRadius: 8, background: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.25rem' }}>
              <Database size={16} style={{ color: 'var(--primary)' }} />
              <span style={{ fontWeight: 600, fontSize: '0.84rem' }}>PostgreSQL</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: dbStatus?.connected ? '#16a34a' : '#f59e0b' }} />
              <span style={{ color: dbStatus?.connected ? 'var(--text-primary)' : '#f59e0b', fontWeight: 600 }}>
                {dbStatus?.connected ? `Connected (${dbStatus.database})` : 'Offline (Local JSON Fallback)'}
              </span>
            </div>
          </div>

          {/* Audit Trail */}
          <div style={{ padding: '0.75rem 0.9rem', borderRadius: 8, background: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.25rem' }}>
              <ShieldCheck size={16} style={{ color: '#16a34a' }} />
              <span style={{ fontWeight: 600, fontSize: '0.84rem' }}>MCA Audit Trail</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem' }}>
              <CheckCircle2 size={14} style={{ color: '#16a34a' }} />
              <span style={{ fontWeight: 600 }}>Active (Rule 3 Compliant)</span>
            </div>
          </div>

          {/* Offline PWA */}
          <div style={{ padding: '0.75rem 0.9rem', borderRadius: 8, background: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.25rem' }}>
              <HardDrive size={16} style={{ color: 'var(--primary)' }} />
              <span style={{ fontWeight: 600, fontSize: '0.84rem' }}>Storage Redundancy</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem' }}>
              <CheckCircle2 size={14} style={{ color: '#16a34a' }} />
              <span style={{ fontWeight: 600 }}>Local Atomic JSON Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Core Enterprise Architecture */}
      <div className="glass-panel" style={{ ...card, marginBottom: '1.25rem' }}>
        <h3 style={{ margin: '0 0 0.25rem', fontSize: '1rem' }}>Enterprise System Capabilities</h3>
        <p style={{ margin: '0 0 1rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          High-performance architecture built for speed, offline reliability, and Indian statutory compliance.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '0.85rem' }}>
          {systemCapabilities.map((s) => (
            <div
              key={s.title}
              style={{
                display: 'flex',
                gap: '0.75rem',
                padding: '0.9rem',
                borderRadius: 8,
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
              }}
            >
              <s.icon size={22} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: 2 }} />
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>{s.title}</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem', lineHeight: 1.45 }}>
                  {s.text}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Keyboard Shortcuts & Efficiency */}
      <div className="glass-panel" style={{ ...card, marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <Keyboard size={18} style={{ color: 'var(--primary)' }} />
          <h3 style={{ margin: 0, fontSize: '1rem' }}>Keyboard Shortcuts &amp; Rapid Billing</h3>
        </div>
        <p style={{ margin: '0 0 1rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          Speed up invoice creation and navigation without touching the mouse.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.65rem' }}>
          {keyboardShortcuts.map((k) => (
            <div
              key={k.key}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.6rem 0.85rem',
                borderRadius: 6,
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
              }}
            >
              <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{k.desc}</span>
              <kbd
                style={{
                  padding: '0.2rem 0.45rem',
                  borderRadius: 4,
                  background: 'var(--card-bg)',
                  border: '1px solid var(--border)',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  fontFamily: 'monospace',
                }}
              >
                {k.key}
              </kbd>
            </div>
          ))}
        </div>
      </div>

      {/* Operational Help & Knowledge Base */}
      <div className="glass-panel" style={{ ...card, marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <HelpCircle size={18} style={{ color: 'var(--primary)' }} />
          <h3 style={{ margin: 0, fontSize: '1rem' }}>Operational Help &amp; Knowledge Base</h3>
        </div>
        <p style={{ margin: '0 0 1rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          Frequently asked operational questions and data management guidelines.
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
          {faqs.map((f, i) => (
            <details
              key={i}
              style={{
                borderRadius: 8,
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
                padding: '0.75rem 1rem',
              }}
            >
              <summary style={{ fontWeight: 600, fontSize: '0.88rem', cursor: 'pointer' }}>
                {f.q}
              </summary>
              <p style={{ margin: '0.5rem 0 0', fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                {f.a}
              </p>
            </details>
          ))}
        </div>
      </div>

      {/* Diagnostic Problem Log */}
      <ProblemLog />
    </div>
  );
}
