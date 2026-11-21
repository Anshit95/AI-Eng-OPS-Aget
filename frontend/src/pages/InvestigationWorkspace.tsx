import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Investigation, Incident } from '../types';
import {
  Bot, CheckCircle2, AlertOctagon, ArrowRight, ShieldAlert,
  Search, RefreshCw, FileText, GitCommit, ChevronRight, Play
} from 'lucide-react';

export const InvestigationWorkspace: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<number>(1);
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [toolTrace, setToolTrace] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionProposed, setActionProposed] = useState(false);

  useEffect(() => {
    api.getIncidents().then((data) => {
      setIncidents(data);
      const incIdParam = searchParams.get('incident_id');
      if (incIdParam) {
        setSelectedIncidentId(Number(incIdParam));
      } else if (data.length > 0) {
        setSelectedIncidentId(data[0].id);
      }
    }).catch(console.error);
  }, [searchParams]);

  const runInvestigation = async () => {
    setLoading(true);
    setActionProposed(false);
    try {
      const res = await api.runInvestigation(selectedIncidentId);
      setInvestigation(res);
      setToolTrace(res.tool_trace || []);
    } catch (e: any) {
      alert("Investigation failed: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const proposeAction = async (rec: any) => {
    try {
      await api.proposeAction({
        action_type: rec.action_type,
        target_resource: rec.target_resource,
        parameters: rec.parameters,
        incident_id: selectedIncidentId
      });
      setActionProposed(true);
      setTimeout(() => navigate('/approvals'), 1200);
    } catch (e: any) {
      alert("Failed to propose action: " + e.message);
    }
  };

  const selectedIncident = incidents.find(i => i.id === selectedIncidentId);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Workspace Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Bot className="w-6 h-6 text-indigo-400" />
            AI Operations Investigation Workspace
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Tool-Using Google ADK & Gemini Multi-Step Investigation Engine
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedIncidentId}
            onChange={(e) => setSelectedIncidentId(Number(e.target.value))}
            className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500"
          >
            {incidents.map((inc) => (
              <option key={inc.id} value={inc.id}>
                [{inc.severity}] {inc.incident_number}: {inc.service_slug}
              </option>
            ))}
          </select>

          <button
            onClick={runInvestigation}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
          >
            <Play className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Investigating...' : 'Run Agent Investigation'}
          </button>
        </div>
      </div>

      {/* Target Incident Context Card */}
      {selectedIncident && (
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-3">
            <span className={`px-2 py-0.5 rounded font-bold border ${
              selectedIncident.severity === 'P0' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40' : 'bg-amber-500/20 text-amber-400 border-amber-500/40'
            }`}>
              {selectedIncident.severity}
            </span>
            <span className="text-white font-bold">{selectedIncident.incident_number}</span>
            <span className="text-slate-400">({selectedIncident.service_slug})</span>
            <span className="text-slate-300 font-sans truncate max-w-lg">{selectedIncident.title}</span>
          </div>
          <div className="text-slate-400">
            Triggered: {new Date(selectedIncident.triggered_at).toLocaleTimeString()}
          </div>
        </div>
      )}

      {/* Visual Tool Trace Sequence */}
      {toolTrace.length > 0 && (
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs font-semibold text-slate-300 mb-3 flex items-center justify-between font-mono">
            <span>Orchestration Tool Execution Trace (Step 1 → {toolTrace.length})</span>
            <span className="text-emerald-400 text-[11px]">✓ Verified Least-Privilege Tools</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2 text-[11px] font-mono">
            {toolTrace.map((t, idx) => (
              <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="text-indigo-400 font-bold mb-1">Step {t.step}</div>
                  <div className="text-slate-300 font-semibold truncate">{t.tool}</div>
                </div>
                <div className="mt-2 text-[10px] text-slate-500 truncate">
                  {t.result_summary || `${Object.values(t)[2] || 'OK'}`}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Investigation Results */}
      {investigation && (
        <div className="space-y-6">
          {/* Executive Summary Card */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-indigo-500/30 shadow-xl relative overflow-hidden">
            <div className="flex items-center justify-between mb-3">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 font-bold">
                SYNTHESIZED INVESTIGATION REPORT
              </span>
              <span className="text-xs font-mono text-emerald-400 font-bold">
                Confidence: {(investigation.confidence_score * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-sm text-slate-200 leading-relaxed font-sans">
              {investigation.summary}
            </p>
          </div>

          {/* Root-Cause Hypotheses & Evidence Citations */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Hypotheses Column */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <h2 className="text-sm font-bold text-white font-mono flex items-center gap-2">
                <Search className="w-4 h-4 text-indigo-400" />
                Ranked Root-Cause Hypotheses
              </h2>

              <div className="space-y-3">
                {investigation.root_cause_hypotheses.map((h, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-indigo-400 font-mono">Rank #{h.rank}</span>
                      <span className="text-[11px] font-mono text-emerald-400 font-bold">
                        {(h.confidence * 100).toFixed(0)}% Confidence
                      </span>
                    </div>
                    <div className="text-xs font-bold text-white">{h.title}</div>
                    <p className="text-xs text-slate-400">{h.description}</p>
                    {h.supporting_evidence && (
                      <div className="pt-2 border-t border-slate-900 space-y-1">
                        <div className="text-[10px] text-slate-500 font-mono">Supporting Evidence:</div>
                        {h.supporting_evidence.map((ev, eIdx) => (
                          <div key={eIdx} className="text-[11px] text-slate-300 flex items-start gap-1">
                            <span className="text-indigo-400">•</span>
                            <span>{ev}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Evidence Citations Column */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <h2 className="text-sm font-bold text-white font-mono flex items-center gap-2">
                <FileText className="w-4 h-4 text-indigo-400" />
                Auditable Evidence Citations
              </h2>

              <div className="space-y-3">
                {investigation.evidence_citations.map((c, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono space-y-1">
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        c.source_type === 'DEPLOYMENT' ? 'bg-indigo-500/20 text-indigo-300' :
                        c.source_type === 'APPLICATION_LOG' ? 'bg-rose-500/20 text-rose-300' :
                        c.source_type === 'ML_ANOMALY' ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300'
                      }`}>
                        {c.source_type}
                      </span>
                      <span className="text-slate-500 text-[10px] truncate max-w-xs">{c.reference}</span>
                    </div>
                    <p className="text-slate-300 text-[11px] font-sans pt-1">{c.finding}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recommended Remediation Action */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-emerald-500/30">
            <h2 className="text-sm font-bold text-white font-mono mb-4 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Controlled Remediation Plan
            </h2>

            {actionProposed && (
              <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
                ✓ Remediation Action proposed successfully! Redirecting to Approval Queue...
              </div>
            )}

            <div className="space-y-3">
              {investigation.recommendations.map((rec, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                        ACTION: {rec.action_type}
                      </span>
                      <span className="text-xs font-mono text-slate-300 font-bold">Target: {rec.target_resource}</span>
                      {rec.parameters?.target_version && (
                        <span className="text-xs font-mono text-indigo-400">Target Version: {rec.parameters.target_version}</span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400">{rec.rationale}</p>
                  </div>

                  <div>
                    <button
                      onClick={() => proposeAction(rec)}
                      disabled={actionProposed}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-emerald-600/30 transition whitespace-nowrap"
                    >
                      Propose Controlled Action →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
