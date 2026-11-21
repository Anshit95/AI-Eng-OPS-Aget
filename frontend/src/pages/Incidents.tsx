import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Incident } from '../types';
import { AlertTriangle, Plus, Search, RefreshCw, Bot, ArrowRight } from 'lucide-react';

export const Incidents: React.FC = () => {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newSeverity, setNewSeverity] = useState('P2');
  const [newServiceId, setNewServiceId] = useState(1);
  const [services, setServices] = useState<any[]>([]);

  const loadIncidents = async () => {
    setLoading(true);
    try {
      const data = await api.getIncidents(statusFilter || undefined, severityFilter || undefined);
      setIncidents(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIncidents();
    api.getServices().then(setServices).catch(() => {});
  }, [severityFilter, statusFilter]);

  const handleCreateIncident = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createIncident({
        title: newTitle,
        service_id: Number(newServiceId),
        severity: newSeverity
      });
      setShowCreateModal(false);
      setNewTitle('');
      loadIncidents();
    } catch (e: any) {
      alert("Error: " + e.message);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Incident Operations & Triage</h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">Real-time incident queue, P0-P3 severity tracking, and automated investigation</p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-300 font-mono focus:outline-none"
          >
            <option value="">All Severities</option>
            <option value="P0">P0 (Critical Outage)</option>
            <option value="P1">P1 (Major Degradation)</option>
            <option value="P2">P2 (Moderate Impact)</option>
            <option value="P3">P3 (Minor)</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-300 font-mono focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="TRIGGERED">TRIGGERED</option>
            <option value="INVESTIGATING">INVESTIGATING</option>
            <option value="RESOLVED">RESOLVED</option>
          </select>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Declare Incident
          </button>

          <button
            onClick={loadIncidents}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-mono uppercase tracking-wider">
            <tr>
              <th className="py-3 px-4">Severity</th>
              <th className="py-3 px-4">Incident #</th>
              <th className="py-3 px-4">Service</th>
              <th className="py-3 px-6">Summary</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Triggered</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {incidents.map((inc) => (
              <tr key={inc.id} className="hover:bg-slate-800/40 transition">
                <td className="py-3 px-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                    inc.severity === 'P0' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40 animate-pulse' :
                    inc.severity === 'P1' ? 'bg-amber-500/20 text-amber-400 border-amber-500/40' :
                    inc.severity === 'P2' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40' :
                    'bg-slate-800 text-slate-400 border-slate-700'
                  }`}>
                    {inc.severity}
                  </span>
                </td>
                <td className="py-3 px-4 font-bold text-white">{inc.incident_number}</td>
                <td className="py-3 px-4 text-slate-300">{inc.service_slug}</td>
                <td className="py-3 px-6 font-sans text-slate-200 max-w-md truncate">{inc.title}</td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] ${
                    inc.status === 'TRIGGERED' ? 'bg-rose-500/20 text-rose-300' :
                    inc.status === 'INVESTIGATING' ? 'bg-indigo-500/20 text-indigo-300' :
                    'bg-emerald-500/20 text-emerald-300'
                  }`}>
                    {inc.status}
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-400 text-[11px]">
                  {new Date(inc.triggered_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </td>
                <td className="py-3 px-4 text-right space-x-2">
                  <Link
                    to={`/investigation?incident_id=${inc.id}`}
                    className="inline-flex items-center gap-1 px-2.5 py-1 bg-indigo-600/30 hover:bg-indigo-600 text-indigo-300 hover:text-white rounded-lg text-[11px] font-medium transition border border-indigo-500/30"
                  >
                    <Bot className="w-3.5 h-3.5" />
                    Investigate
                  </Link>
                  <Link
                    to={`/incidents/${inc.id}`}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-[11px] transition"
                  >
                    Details
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create Incident Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
            <h2 className="text-base font-bold text-white mb-4">Declare Operational Incident</h2>
            <form onSubmit={handleCreateIncident} className="space-y-4">
              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1">Incident Summary</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                  placeholder="e.g. Latency degradation on checkout API"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1">Impacted Service</label>
                <select
                  value={newServiceId}
                  onChange={(e) => setNewServiceId(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                >
                  {services.map((s) => (
                    <option key={s.id} value={s.id}>{s.name} ({s.tier})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1">Initial Severity</label>
                <select
                  value={newSeverity}
                  onChange={(e) => setNewSeverity(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                >
                  <option value="P0">P0 - Critical Outage</option>
                  <option value="P1">P1 - Major Impact</option>
                  <option value="P2">P2 - Moderate Impact</option>
                  <option value="P3">P3 - Minor Issue</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/30 transition"
                >
                  Create Incident
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
