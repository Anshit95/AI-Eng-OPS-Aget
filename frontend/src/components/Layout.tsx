import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Activity, Server, AlertTriangle, Search, Shield, GitCommit,
  Bot, CheckSquare, FileText, Cpu, BookOpen, Users, LogOut, ChevronRight
} from 'lucide-react';
import { getCurrentUser, clearAuth, api, setAuthToken } from '../services/api';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const user = getCurrentUser();
  const [healthStatus, setHealthStatus] = useState<string>('healthy');

  useEffect(() => {
    api.getHealth()
      .then(res => setHealthStatus(res.status))
      .catch(() => setHealthStatus('degraded'));
  }, []);

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const switchRole = async (email: string) => {
    try {
      const data = await api.login(email, "NexaTech2026!Secure");
      setAuthToken(data.access_token, data);
      window.location.reload();
    } catch (e) {
      alert("Role switch failed: " + e);
    }
  };

  const navItems = [
    { name: 'Overview', path: '/', icon: Activity },
    { name: 'Services', path: '/services', icon: Server },
    { name: 'Incidents', path: '/incidents', icon: AlertTriangle },
    { name: 'AI Investigation', path: '/investigation', icon: Search },
    { name: 'Security Intelligence', path: '/security', icon: Shield },
    { name: 'Deployment Risk', path: '/deployments', icon: GitCommit },
    { name: 'Agent Activity', path: '/agent-activity', icon: Bot },
    { name: 'Approval Queue', path: '/approvals', icon: CheckSquare },
    { name: 'Reports & Postmortems', path: '/reports', icon: FileText },
    { name: 'Model Evaluation', path: '/models', icon: Cpu },
    { name: 'Knowledge Base', path: '/knowledge', icon: BookOpen },
    { name: 'User Management', path: '/settings', icon: Users },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 bg-slate-900 border-r border-slate-800 flex flex-col justify-between">
        <div>
          {/* Brand header */}
          <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
            <div className="h-9 w-9 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">
              ⚡
            </div>
            <div>
              <div className="font-semibold text-sm tracking-wide text-white">NexaTech Ops</div>
              <div className="text-[10px] text-slate-400 font-mono">AI SecOps Agent v1.0</div>
            </div>
          </div>

          {/* Navigation links */}
          <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-14rem)]">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User Card & Logout */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/80">
          <div className="flex items-center justify-between mb-3">
            <div className="overflow-hidden pr-2">
              <div className="text-xs font-medium truncate text-slate-200">{user?.full_name || 'Ops Engineer'}</div>
              <div className="text-[10px] text-indigo-400 font-mono truncate">{user?.role || 'Engineer'}</div>
            </div>
            <button
              onClick={handleLogout}
              title="Logout"
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>

          {/* Quick RBAC Switcher for Reviewer demo */}
          <div className="pt-2 border-t border-slate-800/60">
            <div className="text-[10px] font-mono text-slate-500 mb-1.5 uppercase tracking-wider">Quick RBAC Switch:</div>
            <div className="grid grid-cols-2 gap-1 text-[10px]">
              <button
                onClick={() => switchRole('admin@nexatech.internal')}
                className={`px-1.5 py-1 rounded text-left transition truncate ${user?.role === 'Administrator' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
              >
                👑 Admin
              </button>
              <button
                onClick={() => switchRole('lead.engineer@nexatech.internal')}
                className={`px-1.5 py-1 rounded text-left transition truncate ${user?.role === 'Engineer' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
              >
                🛠️ Engineer
              </button>
              <button
                onClick={() => switchRole('sec.analyst@nexatech.internal')}
                className={`px-1.5 py-1 rounded text-left transition truncate ${user?.role === 'Security Analyst' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
              >
                🛡️ SecOps
              </button>
              <button
                onClick={() => switchRole('ops.viewer@nexatech.internal')}
                className={`px-1.5 py-1 rounded text-left transition truncate ${user?.role === 'Viewer' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
              >
                👁️ Viewer
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-8 flex-shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-xs font-medium text-slate-400">Environment:</span>
            <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              NexaTech Simulated Production
            </span>
          </div>

          <div className="flex items-center gap-4">
            {/* System Status Pill */}
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs">
              <span className={`h-2 w-2 rounded-full ${healthStatus === 'healthy' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
              <span className="text-slate-300 font-mono text-[11px]">System: {healthStatus.toUpperCase()}</span>
            </div>

            <div className="text-xs font-mono text-slate-500">
              PostgreSQL 17 • Isolation Forest • Gemini ADK
            </div>
          </div>
        </header>

        {/* Scrollable Page Body */}
        <main className="flex-1 overflow-y-auto p-8">
          {children}
        </main>
      </div>
    </div>
  );
};
