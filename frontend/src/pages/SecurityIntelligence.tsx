import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { SecurityFinding, IAMEvent } from '../types';
import { Shield, ShieldAlert, AlertTriangle, Key, RefreshCw, CheckCircle2, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const SecurityIntelligence: React.FC = () => {
  const navigate = useNavigate();
  const [findings, setFindings] = useState<SecurityFinding[]>([]);
  const [iamEvents, setIamEvents] = useState<IAMEvent[]>([]);
  const [loading, setLoading] = useState(true);

  const loadSecurity = async () => {
    setLoading(true);
    try {
      const [fData, iamData] = await Promise.all([
        api.getSecurityFindings(),
        api.getIAMEvents(false)
      ]);
      setFindings(fData);
      setIamEvents(iamData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSecurity();
  }, []);

  const remediateVulnerability = async (f: SecurityFinding) => {
    try {
      await api.proposeAction({
        action_type: "APPLY_HOTFIX",
        target_resource: f.service_name || "auth-service",
        parameters: { cve_id: f.cve_id, fixed_version: f.fixed_version }
      });
      navigate('/approvals');
    } catch (e: any) {
      alert("Error: " + e.message);
    }
  };

  const rotateCompromisedIAM = async (principal: string) => {
    try {
      await api.proposeAction({
        action_type: "ROTATE_CREDENTIALS",
        target_resource: principal,
        parameters: {}
      });
      navigate('/approvals');
    } catch (e: any) {
      alert("Error: " + e.message);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Shield className="w-6 h-6 text-indigo-400" />
            Security Intelligence & AI Security Posture
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Vulnerability Blast Radius • IAM Anomaly Detection • Controlled Remediation
          </p>
        </div>

        <button
          onClick={loadSecurity}
          className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition self-start"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* CVE Vulnerabilities Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white font-mono flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            Active Dependency Vulnerabilities (CVE Catalog)
          </h2>
          <span className="text-xs font-mono text-slate-400">{findings.length} findings tracked</span>
        </div>

        <div className="space-y-3">
          {findings.map((f) => (
            <div key={f.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-3 mb-1.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono border ${
                    f.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40' : 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                  }`}>
                    {f.severity} (CVSS {f.cvss_score})
                  </span>
                  <span className="text-xs font-mono font-bold text-white">{f.cve_id}</span>
                  <span className="text-xs font-mono text-indigo-400">Target: {f.service_name}</span>
                  {f.is_exploitable && (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-rose-500 text-white font-bold">
                      EXPLOITABLE
                    </span>
                  )}
                </div>
                <div className="text-xs font-bold text-slate-200">{f.title}</div>
                <p className="text-xs text-slate-400 mt-1 font-sans">{f.description}</p>
                <div className="text-[11px] font-mono text-slate-500 mt-2">
                  Package: <span className="text-slate-300">{f.package_name}</span> • Affected: <span className="text-rose-400">{f.affected_version}</span> • Fixed: <span className="text-emerald-400">{f.fixed_version}</span>
                </div>
              </div>

              <div>
                {f.status === 'OPEN' ? (
                  <button
                    onClick={() => remediateVulnerability(f)}
                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/30 transition whitespace-nowrap"
                  >
                    Propose Hotfix Patch →
                  </button>
                ) : (
                  <span className="px-2.5 py-1 rounded text-xs font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    RESOLVED
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* IAM Activity & Anomalies Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white font-mono flex items-center gap-2">
            <Key className="w-4 h-4 text-amber-400" />
            IAM Audit Trail & Suspicious Privilege Escalation
          </h2>
          <span className="text-xs font-mono text-slate-400">{iamEvents.length} audit records</span>
        </div>

        <div className="space-y-3">
          {iamEvents.map((ev) => (
            <div
              key={ev.id}
              className={`p-4 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                ev.is_suspicious ? 'bg-rose-950/20 border-rose-500/40' : 'bg-slate-950 border-slate-800'
              }`}
            >
              <div>
                <div className="flex items-center gap-3 mb-1">
                  {ev.is_suspicious && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-rose-500 text-white animate-pulse">
                      SUSPICIOUS IAM ANOMALY
                    </span>
                  )}
                  <span className="text-xs font-mono font-bold text-white">{ev.event_name}</span>
                  <span className="text-xs font-mono text-slate-400">by {ev.service_account || ev.user_email}</span>
                </div>
                <div className="text-xs font-mono text-slate-400">
                  Source IP: <span className={ev.is_suspicious ? 'text-rose-400 font-bold' : 'text-slate-300'}>{ev.source_ip}</span>
                  {ev.is_suspicious && <span className="ml-2 text-rose-400 font-sans">(External untrusted IP outside VPC)</span>}
                </div>
                {ev.details_json && (
                  <div className="text-[11px] font-mono text-slate-500 mt-1">
                    Details: {ev.details_json}
                  </div>
                )}
              </div>

              <div>
                {ev.is_suspicious && (
                  <button
                    onClick={() => rotateCompromisedIAM(ev.service_account || ev.user_email || "principal")}
                    className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-rose-600/30 transition whitespace-nowrap"
                  >
                    Rotate Credentials & Revoke Sessions
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
