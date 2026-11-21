import React, { useEffect, useState } from 'react';
import { api, getCurrentUser } from '../services/api';
import { ActionRequest } from '../types';
import { CheckSquare, ShieldCheck, CheckCircle2, XCircle, Play, RefreshCw, AlertTriangle } from 'lucide-react';

export const ApprovalQueue: React.FC = () => {
  const [actions, setActions] = useState<ActionRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const user = getCurrentUser();

  const loadActions = async () => {
    setLoading(true);
    try {
      const data = await api.getActions();
      setActions(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActions();
  }, []);

  const handleApprove = async (id: number, approved: boolean) => {
    try {
      await api.approveAction(id, approved);
      loadActions();
    } catch (e: any) {
      alert("Approval error: " + e.message);
    }
  };

  const handleExecute = async (id: number) => {
    try {
      await api.executeAction(id);
      loadActions();
    } catch (e: any) {
      alert("Execution error: " + e.message);
    }
  };

  const isAdmin = user?.role === 'Administrator';
  const isEngineerOrAdmin = user?.role === 'Administrator' || user?.role === 'Engineer';

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <CheckSquare className="w-6 h-6 text-indigo-400" />
            Controlled Remediation Approval Queue
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Explicit Lifecycle: Proposed → Pending Approval → Approved → Executing → Verified
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-xs font-mono px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400">
            Current Role: <span className="text-indigo-400 font-bold">{user?.role || 'Viewer'}</span>
          </div>
          <button
            onClick={loadActions}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Action Requests Feed */}
      <div className="space-y-4">
        {actions.length === 0 && (
          <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-2xl text-slate-500 font-mono text-xs">
            No action requests in queue.
          </div>
        )}

        {actions.map((act) => (
          <div key={act.id} className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-xl">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold font-mono border ${
                  act.status === 'VERIFIED' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40' :
                  act.status === 'APPROVED' ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/40' :
                  act.status === 'PENDING_APPROVAL' ? 'bg-amber-500/20 text-amber-400 border-amber-500/40 animate-pulse' :
                  act.status === 'REJECTED' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40' :
                  'bg-slate-800 text-slate-400 border-slate-700'
                }`}>
                  {act.status}
                </span>
                <span className="text-xs font-bold text-white font-mono">{act.action_type}</span>
                <span className="text-xs text-indigo-400 font-mono">→ {act.target_resource}</span>
              </div>

              <div className="text-[11px] font-mono text-slate-400">
                Requested by: <span className="text-slate-200">{act.requested_by_email}</span> at {new Date(act.created_at).toLocaleTimeString()}
              </div>
            </div>

            {/* Action Parameters */}
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono flex items-center justify-between">
              <div className="text-slate-400">
                Parameters: <span className="text-slate-200">{JSON.stringify(act.parameters)}</span>
              </div>
              {act.approved_by_email && (
                <div className="text-emerald-400">
                  Approved by: {act.approved_by_email}
                </div>
              )}
            </div>

            {/* Execution & Verification Output */}
            {act.verification_result && (
              <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 font-mono">
                  <CheckCircle2 className="w-4 h-4" />
                  Independent Post-Action Verification Passed
                </div>
                <div className="text-xs font-mono text-slate-300">
                  Health Check: <span className="text-emerald-400 font-bold">{act.verification_result.health_check_status || 'HEALTHY'}</span>
                  {act.verification_result.metrics_observed && (
                    <span className="ml-3 text-slate-400">
                      • Post-Rollback Error Rate: <span className="text-emerald-300">{act.verification_result.metrics_observed.error_rate_post}%</span>
                      • p99 Latency: <span className="text-emerald-300">{act.verification_result.metrics_observed.latency_p99_post_ms}ms</span>
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Action Controls */}
            <div className="flex items-center justify-end gap-3 pt-2">
              {act.status === 'PENDING_APPROVAL' && (
                <>
                  {isAdmin ? (
                    <>
                      <button
                        onClick={() => handleApprove(act.id, false)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-600/20 hover:bg-rose-600 text-rose-300 hover:text-white rounded-xl text-xs font-semibold transition border border-rose-500/30"
                      >
                        <XCircle className="w-4 h-4" /> Reject Action
                      </button>
                      <button
                        onClick={() => handleApprove(act.id, true)}
                        className="flex items-center gap-1.5 px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition shadow-lg shadow-indigo-600/30"
                      >
                        <ShieldCheck className="w-4 h-4" /> Approve Action (Admin)
                      </button>
                    </>
                  ) : (
                    <div className="text-[11px] text-amber-400 font-mono flex items-center gap-1">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      Requires Administrator role to approve (Use quick switcher in sidebar)
                    </div>
                  )}
                </>
              )}

              {act.status === 'APPROVED' && isEngineerOrAdmin && (
                <button
                  onClick={() => handleExecute(act.id)}
                  className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition shadow-lg shadow-emerald-600/30 font-mono"
                >
                  <Play className="w-4 h-4" /> Execute Action & Verify Outcome
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
