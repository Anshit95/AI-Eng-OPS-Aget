import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Service } from '../types';
import { Server, ExternalLink, Activity, GitCommit, RefreshCw, X } from 'lucide-react';

export const Services: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [selectedService, setSelectedService] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [tierFilter, setTierFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  const loadServices = async () => {
    setLoading(true);
    try {
      const data = await api.getServices(tierFilter || undefined, statusFilter || undefined);
      setServices(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadServices();
  }, [tierFilter, statusFilter]);

  const viewService = async (slug: string) => {
    try {
      const detail = await api.getServiceDetails(slug);
      setSelectedService(detail);
    } catch (e) {
      alert("Failed to load details: " + e);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header & Filters */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Service Intelligence Catalog</h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">Microservice architecture, deployment versions, and ownership</p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={tierFilter}
            onChange={(e) => setTierFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-300 font-mono focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Tiers</option>
            <option value="Tier-1">Tier-1 (Mission Critical)</option>
            <option value="Tier-2">Tier-2 (Core)</option>
            <option value="Tier-3">Tier-3 (Internal)</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-300 font-mono focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="HEALTHY">HEALTHY</option>
            <option value="DEGRADED">DEGRADED</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>

          <button
            onClick={loadServices}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {services.map((s) => (
          <div
            key={s.id}
            onClick={() => viewService(s.slug)}
            className="p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition cursor-pointer flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                  s.status === 'HEALTHY' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                  s.status === 'DEGRADED' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                  'bg-rose-500/10 text-rose-400 border-rose-500/30'
                }`}>
                  {s.status}
                </span>
                <span className="text-[11px] font-mono text-slate-400">{s.tier}</span>
              </div>

              <h3 className="text-sm font-bold text-white font-mono">{s.name}</h3>
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">{s.description || 'Enterprise microservice'}</p>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 font-mono">
              <div>
                <span className="text-slate-500">Version: </span>
                <span className="text-indigo-400 font-semibold">{s.active_version}</span>
              </div>
              <div className="text-[11px] text-slate-500">
                {s.owner_team_name || 'Core Platform'}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Service Details Drawer / Modal */}
      {selectedService && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex justify-end">
          <div className="w-full max-w-xl bg-slate-900 h-full border-l border-slate-800 p-6 overflow-y-auto space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white font-mono">{selectedService.service.name}</h2>
                <div className="text-xs text-slate-400 font-mono">Active Version: {selectedService.service.active_version} • {selectedService.service.tier}</div>
              </div>
              <button
                onClick={() => setSelectedService(null)}
                className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Microservice Specs */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 grid grid-cols-2 gap-4 text-xs font-mono">
              <div>
                <span className="text-slate-500">Language:</span> <span className="text-white">{selectedService.service.language}</span>
              </div>
              <div>
                <span className="text-slate-500">Framework:</span> <span className="text-white">{selectedService.service.framework}</span>
              </div>
              <div>
                <span className="text-slate-500">Owner Team:</span> <span className="text-white">{selectedService.service.owner_team}</span>
              </div>
              <div>
                <span className="text-slate-500">Repository:</span> <span className="text-indigo-400">{selectedService.service.repo_url}</span>
              </div>
            </div>

            {/* Recent Telemetry Stream */}
            <div>
              <h3 className="text-xs font-semibold text-white uppercase tracking-wider mb-3">Live Telemetry Datapoints</h3>
              <div className="space-y-2">
                {selectedService.metrics_series.slice(-5).map((m: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono grid grid-cols-4 gap-2">
                    <div>
                      <div className="text-[10px] text-slate-500">Error Rate</div>
                      <div className={`font-bold ${m.error_rate > 5 ? 'text-rose-400' : 'text-emerald-400'}`}>{m.error_rate}%</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-slate-500">p99 Latency</div>
                      <div className="text-white">{m.latency_p99}ms</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-slate-500">DB Latency</div>
                      <div className="text-white">{m.db_latency}ms</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-slate-500">CPU Load</div>
                      <div className="text-white">{m.cpu_usage}%</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Releases */}
            <div>
              <h3 className="text-xs font-semibold text-white uppercase tracking-wider mb-3">Recent Releases</h3>
              <div className="space-y-2">
                {selectedService.recent_deployments.map((d: any) => (
                  <div key={d.id} className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-xs font-mono">
                    <div>
                      <div className="text-white font-bold">{d.version} ({d.environment})</div>
                      <div className="text-[10px] text-slate-500">Deployed by {d.deployed_by}</div>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${d.risk_score > 0.5 ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                        Risk: {d.risk_score}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
