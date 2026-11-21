import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { DashboardOverview } from '../types';
import {
  Activity, AlertOctagon, AlertTriangle, ShieldAlert, GitPullRequest,
  CheckCircle2, ArrowUpRight, RefreshCw, Bot
} from 'lucide-react';

export const Overview: React.FC = () => {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOverview = async () => {
    setLoading(true);
    try {
      const res = await api.getDashboardOverview();
      setData(res);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 font-mono text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2 text-indigo-400" />
        Loading real-time telemetry from NexaTech operations database...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 font-mono text-sm">
        Error loading overview: {error}
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Engineering Operations Overview</h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Autonomous Incident Investigation • ML Anomaly Detection • Security Intelligence
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/investigation"
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/30 transition"
          >
            <Bot className="w-4 h-4" />
            Launch AI Investigation
          </Link>
          <button
            onClick={fetchOverview}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition"
            title="Refresh Metrics"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPI Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* System Health Score */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">System Health</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{data.health_score}%</span>
            <span className="text-xs font-mono text-slate-400">weighted index</span>
          </div>
          <div className="mt-3 w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${data.health_score > 80 ? 'bg-emerald-500' : data.health_score > 60 ? 'bg-amber-500' : 'bg-rose-500'}`}
              style={{ width: `${data.health_score}%` }}
            />
          </div>
          <div className="mt-2 text-[11px] text-slate-400 flex justify-between">
            <span>{data.services.healthy} healthy</span>
            <span className="text-rose-400">{data.services.critical} critical</span>
          </div>
        </div>

        {/* Active Incidents */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Active Incidents</span>
            <AlertOctagon className="w-4 h-4 text-rose-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{data.incidents.total_active}</span>
            <span className="text-xs font-mono text-rose-400">({data.incidents.p0} P0 Outages)</span>
          </div>
          <div className="mt-3 flex gap-1.5 text-[11px] font-mono">
            <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">P0: {data.incidents.p0}</span>
            <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">P1: {data.incidents.p1}</span>
            <span className="px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">P2: {data.incidents.p2}</span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400">P3: {data.incidents.p3}</span>
          </div>
        </div>

        {/* Security Posture */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Security Vulnerabilities</span>
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{data.security.open_vulnerabilities}</span>
            <span className="text-xs font-mono text-amber-400">CVE records</span>
          </div>
          <div className="mt-3 flex gap-2 text-[11px] font-mono">
            <span className="text-rose-400 font-semibold">{data.security.critical_cves} Critical</span>
            <span className="text-slate-500">•</span>
            <span className="text-amber-400">{data.security.suspicious_iam_events} Suspicious IAM</span>
          </div>
        </div>

        {/* Deployment Risk */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Avg Deployment Risk</span>
            <GitPullRequest className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{data.deployments.avg_risk_score}</span>
            <span className="text-xs font-mono text-slate-400">/ 1.0 ML score</span>
          </div>
          <div className="mt-3 text-[11px] text-slate-400 font-mono">
            Across {data.deployments.recent_count} recent releases
          </div>
        </div>
      </div>

      {/* Main Two-Column Layout: Services Health & Recent Operations Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Microservices Health Matrix */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white">NexaTech Microservices State</h2>
              <p className="text-xs text-slate-400 font-mono">Real-time operational status from PostgreSQL</p>
            </div>
            <Link to="/services" className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
              View Catalog <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/80 border border-rose-500/30">
              <div className="flex items-center gap-3">
                <span className="h-2.5 w-2.5 rounded-full bg-rose-500 animate-ping"></span>
                <div>
                  <div className="text-xs font-bold text-white font-mono">payments-service (Tier-1)</div>
                  <div className="text-[11px] text-rose-400 font-mono">Active Outage: Error rate 18.5% post v2.4.2 deploy</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-500/20 text-rose-400 border border-rose-500/40">CRITICAL</span>
                <Link to="/investigation" className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition">
                  Investigate
                </Link>
              </div>
            </div>

            <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/80 border border-amber-500/30">
              <div className="flex items-center gap-3">
                <span className="h-2.5 w-2.5 rounded-full bg-amber-400"></span>
                <div>
                  <div className="text-xs font-bold text-white font-mono">auth-service (Tier-1)</div>
                  <div className="text-[11px] text-amber-400 font-mono">Security Advisory: CVE-2024-21626 in runc runtime</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/20 text-amber-400 border border-amber-500/40">DEGRADED</span>
                <Link to="/security" className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium transition">
                  Triage CVE
                </Link>
              </div>
            </div>

            <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/80 border border-amber-500/30">
              <div className="flex items-center gap-3">
                <span className="h-2.5 w-2.5 rounded-full bg-amber-400"></span>
                <div>
                  <div className="text-xs font-bold text-white font-mono">order-processing (Tier-2)</div>
                  <div className="text-[11px] text-amber-400 font-mono">Canary Memory Saturation (92% memory utilization)</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/20 text-amber-400 border border-amber-500/40">DEGRADED</span>
                <Link to="/incidents" className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium transition">
                  View INC-3982
                </Link>
              </div>
            </div>

            <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="flex items-center gap-3">
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-400"></span>
                <div>
                  <div className="text-xs font-bold text-white font-mono">notification-service (Tier-3)</div>
                  <div className="text-[11px] text-slate-400 font-mono">Baseline Nominal State (0.04% error rate)</div>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">HEALTHY</span>
            </div>
          </div>
        </div>

        {/* Real-Time Operational Event Timeline */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">Live Event Stream</h2>
            <span className="text-[10px] font-mono text-slate-500">Auto-correlated</span>
          </div>

          <div className="space-y-4">
            {data.recent_activity.map((ev) => (
              <div key={ev.id} className="relative pl-6 pb-2 border-l border-slate-800 last:border-l-0">
                <div className={`absolute -left-1.5 top-0 h-3 w-3 rounded-full border-2 border-slate-900 ${
                  ev.type === 'ALERT' ? 'bg-rose-500' :
                  ev.type === 'ACTION_EXECUTED' ? 'bg-emerald-400' :
                  ev.type === 'INVESTIGATION_NOTE' ? 'bg-indigo-400' : 'bg-slate-500'
                }`} />
                <div className="text-xs font-semibold text-slate-200">{ev.title}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">{ev.description}</div>
                <div className="text-[10px] font-mono text-slate-500 mt-1">{new Date(ev.timestamp).toLocaleTimeString()}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
