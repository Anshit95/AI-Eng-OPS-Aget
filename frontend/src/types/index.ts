export type UserRole = 'Viewer' | 'Engineer' | 'Security Analyst' | 'Administrator';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  team_id?: number;
}

export interface Service {
  id: number;
  name: string;
  slug: string;
  description?: string;
  tier: 'Tier-1' | 'Tier-2' | 'Tier-3';
  status: 'HEALTHY' | 'DEGRADED' | 'CRITICAL';
  active_version: string;
  owner_team_name?: string;
  language: string;
  framework: string;
  repo_url?: string;
  created_at: string;
  updated_at: string;
}

export interface IncidentTimeline {
  id: number;
  timestamp: string;
  title: string;
  description?: string;
  entry_type: 'ALERT' | 'SYSTEM_EVENT' | 'INVESTIGATION_NOTE' | 'ACTION_EXECUTED';
}

export interface Incident {
  id: number;
  incident_number: string;
  title: string;
  description?: string;
  service_id: number;
  service_name?: string;
  service_slug?: string;
  severity: 'P0' | 'P1' | 'P2' | 'P3';
  status: 'TRIGGERED' | 'INVESTIGATING' | 'MITIGATED' | 'RESOLVED';
  triggered_at: string;
  resolved_at?: string;
  root_cause?: string;
  assigned_to_email?: string;
  timeline: IncidentTimeline[];
}

export interface Investigation {
  id: number;
  incident_id: number;
  incident_number?: string;
  service_name?: string;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  summary?: string;
  root_cause_hypotheses: Array<{
    rank: number;
    title: string;
    description: string;
    confidence: number;
    supporting_evidence?: string[];
    falsification_test?: string;
  }>;
  evidence_citations: Array<{
    source_type: string;
    reference: string;
    finding: string;
  }>;
  recommendations: Array<{
    action_type: string;
    target_resource: string;
    parameters: Record<string, any>;
    rationale: string;
    requires_approval: boolean;
    urgency: string;
  }>;
  confidence_score: number;
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    model: string;
  };
  created_at: string;
  updated_at: string;
}

export interface ActionRequest {
  id: number;
  investigation_id?: number;
  incident_id?: number;
  action_type: string;
  target_resource: string;
  status: 'PROPOSED' | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'EXECUTING' | 'VERIFIED' | 'FAILED';
  parameters: Record<string, any>;
  requested_by_email: string;
  approved_by_email?: string;
  execution_result?: any;
  verification_result?: any;
  created_at: string;
  updated_at: string;
}

export interface SecurityFinding {
  id: number;
  service_id: number;
  service_name?: string;
  cve_id?: string;
  title: string;
  description?: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  cvss_score: number;
  package_name?: string;
  affected_version?: string;
  fixed_version?: string;
  attack_vector: string;
  is_exploitable: boolean;
  status: 'OPEN' | 'RESOLVED' | 'IGNORED';
  created_at: string;
}

export interface IAMEvent {
  id: number;
  user_email?: string;
  service_account?: string;
  event_name: string;
  event_source: string;
  source_ip: string;
  is_suspicious: boolean;
  details_json?: string;
  timestamp: string;
}

export interface Deployment {
  id: number;
  service_id: number;
  service_name?: string;
  commit_sha: string;
  version: string;
  environment: string;
  status: string;
  deployed_by: string;
  risk_score: number;
  rollback_target_version?: string;
  created_at: string;
}

export interface DashboardOverview {
  health_score: number;
  services: {
    total: number;
    healthy: number;
    degraded: number;
    critical: number;
  };
  incidents: {
    total_active: number;
    p0: number;
    p1: number;
    p2: number;
    p3: number;
  };
  security: {
    open_vulnerabilities: number;
    critical_cves: number;
    high_cves: number;
    suspicious_iam_events: number;
  };
  deployments: {
    recent_count: number;
    avg_risk_score: number;
  };
  recent_activity: Array<{
    id: number;
    timestamp: string;
    title: string;
    description?: string;
    type: string;
    incident_id?: number;
  }>;
}
