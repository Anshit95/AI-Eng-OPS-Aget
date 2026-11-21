import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Bot, CheckCircle2, Shield, Cpu, RefreshCw } from 'lucide-react';

export const AgentActivity: React.FC = () => {
  const [status, setStatus] = useState<any | null>(null);
  const [investigations, setInvestigations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getAgentStatus(), api.getInvestigations()])
      .then(([sData, invData]) => {
        setStatus(sData);
        setInvestigations(invData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <Bot className="w-6 h-6 text-indigo-400" />
          Google ADK & Gemini Agent Observability
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-mono">
          Model configuration, least-privilege tool execution traces, and AI safety boundary controls
        </p>
      </div>

      {/* Agent Status Card */}
      {status && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <h2 className="text-sm font-bold text-white font-mono flex items-center gap-2">
              <Cpu className="w-4 h-4 text-indigo-400" />
              Runtime Orchestrator Configuration
            </h2>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1.5 border-b border-slate-800">
                <span className="text-slate-400">Agent Status:</span>
                <span className="text-emerald-400 font-bold">{status.status}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-800">
                <span className="text-slate-400">Orchestrator:</span>
                <span className="text-white">{status.orchestrator}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-800">
                <span className="text-slate-400">Reasoning Model:</span>
                <span className="text-indigo-400 font-bold">{status.model}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-800">
                <span className="text-slate-400">Embeddings Engine:</span>
                <span className="text-indigo-400">{status.embedding_model}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-400">Execution Mode:</span>
                <span className="text-white">{status.execution_mode}</span>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <h2 className="text-sm font-bold text-white font-mono flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-400" />
              Active AI Safety & Defense Boundaries
            </h2>
            <div className="space-y-3 text-xs font-mono">
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Untrusted Data Isolation: Logs and commits treated as untrusted text</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Least Privilege RBAC: Strict read-only tools for investigations</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Human-In-The-Loop: Consequential actions require explicit approval</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Independent Post-Action Verification: Observes metric recovery</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Historical Investigation Executions */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl p-6 space-y-4">
        <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
          Recorded Investigation Executions ({investigations.length})
        </h2>

        <div className="space-y-3">
          {investigations.map((inv) => (
            <div key={inv.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs font-mono">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <span className="text-indigo-400 font-bold">Investigation #{inv.id}</span>
                  <span className="text-white">Incident: {inv.incident_number}</span>
                  <span className="text-slate-400">({inv.service_name})</span>
                </div>
                <div className="text-[11px] text-slate-400 font-sans line-clamp-1">{inv.summary}</div>
              </div>
              <div className="text-right">
                <div className="text-emerald-400 font-bold">{(inv.confidence_score * 100).toFixed(0)}% Confidence</div>
                <div className="text-[10px] text-slate-500">{new Date(inv.created_at).toLocaleTimeString()}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
