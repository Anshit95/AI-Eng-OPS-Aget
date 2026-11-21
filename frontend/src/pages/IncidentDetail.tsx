import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Incident } from '../types';
import { AlertOctagon, Bot, ArrowLeft, Clock, User, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const IncidentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      api.getIncident(Number(id))
        .then(setIncident)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) {
    return <div className="text-center py-16 text-slate-400 font-mono text-sm">Loading incident details...</div>;
  }

  if (!incident) {
    return <div className="text-center py-16 text-rose-400 font-mono text-sm">Incident not found</div>;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Back button */}
      <div>
        <Link to="/incidents" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition">
          <ArrowLeft className="w-4 h-4" /> Back to Incidents
        </Link>
      </div>

      {/* Incident Header */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className={`px-2.5 py-0.5 rounded text-xs font-bold border ${
              incident.severity === 'P0' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40 animate-pulse' :
              incident.severity === 'P1' ? 'bg-amber-500/20 text-amber-400 border-amber-500/40' :
              'bg-yellow-500/20 text-yellow-400 border-yellow-500/40'
            }`}>
              {incident.severity}
            </span>
            <span className="text-sm font-mono font-bold text-slate-400">{incident.incident_number}</span>
            <span className="text-xs font-mono text-indigo-400">service: {incident.service_slug}</span>
          </div>
          <h1 className="text-xl font-bold text-white">{incident.title}</h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">{incident.description}</p>
        </div>

        <div>
          <Link
            to={`/investigation?incident_id=${incident.id}`}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/30 transition"
          >
            <Bot className="w-4 h-4" />
            AI Root-Cause Investigation
          </Link>
        </div>
      </div>

      {/* Timeline Section */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800">
        <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
          <Clock className="w-4 h-4 text-indigo-400" />
          Incident Event Timeline
        </h2>

        <div className="space-y-4">
          {incident.timeline.map((t) => (
            <div key={t.id} className="relative pl-6 pb-2 border-l border-slate-800 last:border-l-0">
              <div className={`absolute -left-1.5 top-0.5 h-3 w-3 rounded-full border-2 border-slate-900 ${
                t.entry_type === 'ALERT' ? 'bg-rose-500' :
                t.entry_type === 'ACTION_EXECUTED' ? 'bg-emerald-400' :
                t.entry_type === 'INVESTIGATION_NOTE' ? 'bg-indigo-400' : 'bg-slate-500'
              }`} />
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold text-slate-200">{t.title}</div>
                <div className="text-[10px] font-mono text-slate-500">{new Date(t.timestamp).toLocaleString()}</div>
              </div>
              <div className="text-xs text-slate-400 mt-1 font-mono">{t.description}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
