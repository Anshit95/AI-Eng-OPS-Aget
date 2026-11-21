import React, { useEffect, useState } from 'react';
import { getCurrentUser } from '../services/api';
import { Users, Shield, Database, RefreshCw, Key } from 'lucide-react';

export const UserManagement: React.FC = () => {
  const currentUser = getCurrentUser();

  const usersList = [
    { email: 'admin@nexatech.internal', name: 'Admin User', role: 'Administrator', team: 'Core Platform', permissions: 'Full operational approvals, user admin, root actions' },
    { email: 'lead.engineer@nexatech.internal', name: 'Alex Vance', role: 'Engineer', team: 'Payments & Billing', permissions: 'Investigate incidents, propose rollbacks & restarts' },
    { email: 'sec.analyst@nexatech.internal', name: 'Jordan Reed', role: 'Security Analyst', team: 'Identity & Security', permissions: 'Triage CVEs, rotate credentials, IAM forensics' },
    { email: 'ops.viewer@nexatech.internal', name: 'Taylor Morgan', role: 'Viewer', team: 'Order & Fulfillment', permissions: 'Read-only access to operational dashboards & telemetry' },
    { email: 'svc-deploy-worker@nexatech.internal', name: 'CI Service Account', role: 'Engineer', team: 'Core Platform', permissions: 'Automated CI/CD deployment pipeline execution' }
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <Users className="w-6 h-6 text-indigo-400" />
          Access Control & Simulator Configuration
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-mono">
          Role-Based Access Control (RBAC) directory and NexaTech enterprise simulation settings
        </p>
      </div>

      {/* Current Active Session */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <div>
          <div className="text-xs font-mono text-slate-400">Authenticated Identity</div>
          <div className="text-base font-bold text-white mt-1">{currentUser?.full_name} ({currentUser?.email})</div>
          <div className="text-xs font-mono text-indigo-400 mt-0.5">Assigned Role: {currentUser?.role}</div>
        </div>
        <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-400">
          ✓ Active JWT Session
        </div>
      </div>

      {/* RBAC Users Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <h2 className="text-xs font-bold text-white font-mono uppercase tracking-wider">Enterprise User Directory & Roles</h2>
        </div>

        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-mono uppercase tracking-wider">
            <tr>
              <th className="py-3 px-4">Name</th>
              <th className="py-3 px-4">Email</th>
              <th className="py-3 px-4">Role</th>
              <th className="py-3 px-4">Team</th>
              <th className="py-3 px-4">Permissions Scope</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {usersList.map((u, i) => (
              <tr key={i} className="hover:bg-slate-800/40 transition">
                <td className="py-3 px-4 font-bold text-white">{u.name}</td>
                <td className="py-3 px-4 text-slate-300">{u.email}</td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    u.role === 'Administrator' ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' :
                    u.role === 'Security Analyst' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                    u.role === 'Engineer' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                    'bg-slate-800 text-slate-400'
                  }`}>
                    {u.role}
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-400">{u.team}</td>
                <td className="py-3 px-4 text-slate-400 font-sans text-xs">{u.permissions}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Simulator Management Card */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-white font-mono flex items-center gap-2">
          <Database className="w-4 h-4 text-indigo-400" />
          NexaTech Simulator Controls
        </h2>
        <p className="text-xs text-slate-400 font-sans leading-relaxed">
          The NexaTech Enterprise Simulator produces reproducible telemetry, deployments, logs, CVE vulnerabilities, and IAM activities across Scenarios A through E.
          To re-seed or reset the database cleanly from CLI:
        </p>
        <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-400">
          python -m backend.app.simulator.seed --reset --seed 42
        </div>
      </div>
    </div>
  );
};
