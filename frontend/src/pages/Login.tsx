import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, setAuthToken } from '../services/api';
import { Shield, Lock, Mail, ArrowRight, UserCheck } from 'lucide-react';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@nexatech.internal');
  const [password, setPassword] = useState('NexaTech2026!Secure');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await api.login(email, password);
      setAuthToken(data.access_token, data);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = async (demoEmail: string) => {
    setEmail(demoEmail);
    setLoading(true);
    setError(null);
    try {
      const data = await api.login(demoEmail, "NexaTech2026!Secure");
      setAuthToken(data.access_token, data);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-6 selection:bg-indigo-500">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        {/* Glow backdrop */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-24 bg-indigo-500/20 blur-3xl pointer-events-none rounded-full" />

        <div className="flex items-center gap-3 mb-6">
          <div className="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">
            ⚡
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-wide">NexaTech Operations</h1>
            <p className="text-xs text-slate-400 font-mono">AI Engineering & Security Intelligence</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Corporate Email</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full pl-9 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono transition"
                placeholder="name@nexatech.internal"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-9 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono transition"
                placeholder="••••••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition shadow-lg shadow-indigo-600/30 disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'Sign In to Operations Console'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Demo Fast-Login Accounts */}
        <div className="mt-8 pt-6 border-t border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 mb-2.5 flex items-center gap-1.5">
            <UserCheck className="w-3.5 h-3.5 text-indigo-400" />
            <span>1-Click Portfolio Demo Sign In:</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              onClick={() => quickLogin('admin@nexatech.internal')}
              className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-left border border-slate-700/50 transition"
            >
              <div className="font-semibold text-slate-200">Administrator</div>
              <div className="text-[10px] text-slate-400 font-mono">Full action approvals</div>
            </button>
            <button
              onClick={() => quickLogin('lead.engineer@nexatech.internal')}
              className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-left border border-slate-700/50 transition"
            >
              <div className="font-semibold text-slate-200">Lead Engineer</div>
              <div className="text-[10px] text-slate-400 font-mono">Propose rollbacks</div>
            </button>
            <button
              onClick={() => quickLogin('sec.analyst@nexatech.internal')}
              className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-left border border-slate-700/50 transition"
            >
              <div className="font-semibold text-slate-200">Security Analyst</div>
              <div className="text-[10px] text-slate-400 font-mono">IAM & CVE triage</div>
            </button>
            <button
              onClick={() => quickLogin('ops.viewer@nexatech.internal')}
              className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-left border border-slate-700/50 transition"
            >
              <div className="font-semibold text-slate-200">Ops Viewer</div>
              <div className="text-[10px] text-slate-400 font-mono">Read-only metrics</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
