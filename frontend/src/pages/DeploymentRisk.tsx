import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Deployment } from '../types';
import { GitCommit, GitPullRequest, Calculator, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';

export const DeploymentRisk: React.FC = () => {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);

  // Risk Calculator Form state
  const [calcTier, setCalcTier] = useState('Tier-1');
  const [calcAdded, setCalcAdded] = useState(180);
  const [calcDeleted, setCalcDeleted] = useState(25);
  const [calcFiles, setCalcFiles] = useState(8);
  const [calcMigrations, setCalcMigrations] = useState(true);
  const [calcWeekend, setCalcWeekend] = useState(false);
  const [calcPrior, setCalcPrior] = useState(15);
  const [calcResult, setCalcResult] = useState<any | null>(null);

  const loadDeployments = async () => {
    setLoading(true);
    try {
      const data = await api.getDeployments();
      setDeployments(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDeployments();
    calculateRisk();
  }, []);

  const calculateRisk = async () => {
    try {
      const res = await api.predictDeploymentRisk({
        service_tier: calcTier,
        lines_added: calcAdded,
        lines_deleted: calcDeleted,
        files_changed: calcFiles,
        has_migrations: calcMigrations,
        author_prior_deployments: calcPrior,
        is_friday_or_weekend: calcWeekend
      });
      setCalcResult(res);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <GitCommit className="w-6 h-6 text-indigo-400" />
          Pre-Deployment Risk Intelligence
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-mono">
          Machine Learning regression probability estimation using strictly pre-deployment features
        </p>
      </div>

      {/* Interactive Risk Simulator */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2">
            <Calculator className="w-5 h-5 text-indigo-400" />
            <h2 className="text-sm font-bold text-white">Pre-Flight Release Risk Estimator</h2>
          </div>
          <span className="text-[11px] font-mono text-emerald-400">Zero Temporal Leakage Boundary</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1">Target Service Tier</label>
            <select
              value={calcTier}
              onChange={(e) => setCalcTier(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono focus:outline-none"
            >
              <option value="Tier-1">Tier-1 (High Criticality)</option>
              <option value="Tier-2">Tier-2 (Core Services)</option>
              <option value="Tier-3">Tier-3 (Internal)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1">Lines Added</label>
            <input
              type="number"
              value={calcAdded}
              onChange={(e) => setCalcAdded(Number(e.target.value))}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1">Files Changed</label>
            <input
              type="number"
              value={calcFiles}
              onChange={(e) => setCalcFiles(Number(e.target.value))}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1">Database Migrations</label>
            <select
              value={calcMigrations ? 'yes' : 'no'}
              onChange={(e) => setCalcMigrations(e.target.value === 'yes')}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono focus:outline-none"
            >
              <option value="yes">Yes (Schema/Data Migration)</option>
              <option value="no">No Migrations</option>
            </select>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center gap-4 text-xs font-mono text-slate-300">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={calcWeekend}
                onChange={(e) => setCalcWeekend(e.target.checked)}
                className="rounded border-slate-700 text-indigo-600 focus:ring-0 bg-slate-950"
              />
              <span>Friday / Weekend Deployment</span>
            </label>
          </div>

          <button
            onClick={calculateRisk}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/30 transition"
          >
            Compute ML Risk Score
          </button>
        </div>

        {/* Calculation Result */}
        {calcResult && (
          <div className="mt-4 p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <span className={`px-2.5 py-0.5 rounded text-xs font-bold font-mono border ${
                  calcResult.risk_level === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40' :
                  calcResult.risk_level === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border-amber-500/40' :
                  'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                }`}>
                  {calcResult.risk_level} RISK ({(calcResult.risk_score * 100).toFixed(1)}%)
                </span>
                <span className="text-xs font-mono text-slate-300">
                  Recommended Strategy: <strong className="text-indigo-400">{calcResult.recommended_strategy}</strong>
                </span>
              </div>
              <div className="text-[11px] text-slate-400 font-mono mt-2">
                Risk Drivers: {calcResult.top_risk_factors.join('; ')}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Historical Releases Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-xs font-bold text-white font-mono uppercase tracking-wider">Historical Releases</h2>
          <span className="text-xs font-mono text-slate-400">{deployments.length} releases</span>
        </div>

        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-mono uppercase tracking-wider">
            <tr>
              <th className="py-3 px-4">Service</th>
              <th className="py-3 px-4">Version</th>
              <th className="py-3 px-4">Commit SHA</th>
              <th className="py-3 px-4">Environment</th>
              <th className="py-3 px-4">Risk Score</th>
              <th className="py-3 px-4">Rollback Target</th>
              <th className="py-3 px-4 text-right">Deployed By</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {deployments.map((d) => (
              <tr key={d.id} className="hover:bg-slate-800/40 transition">
                <td className="py-3 px-4 font-bold text-white">{d.service_name}</td>
                <td className="py-3 px-4 text-indigo-400 font-bold">{d.version}</td>
                <td className="py-3 px-4 text-slate-400">{d.commit_sha.slice(0, 10)}</td>
                <td className="py-3 px-4 text-slate-300">{d.environment}</td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] ${
                    d.risk_score > 0.6 ? 'bg-rose-500/20 text-rose-400' :
                    d.risk_score > 0.3 ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {d.risk_score}
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-400">{d.rollback_target_version || 'None (Initial)'}</td>
                <td className="py-3 px-4 text-right text-slate-400">{d.deployed_by}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
