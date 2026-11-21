const API_BASE = '/api/v1';

export function getAuthToken(): string | null {
  return localStorage.getItem('ops_token');
}

export function setAuthToken(token: string, user: any) {
  localStorage.setItem('ops_token', token);
  localStorage.setItem('ops_user', JSON.stringify(user));
}

export function getCurrentUser() {
  const user = localStorage.getItem('ops_user');
  return user ? JSON.parse(user) : null;
}

export function clearAuth() {
  localStorage.removeItem('ops_token');
  localStorage.removeItem('ops_user');
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {})
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  if (response.status === 401) {
    // Session expired or unauthenticated
    if (!endpoint.includes('/auth/login')) {
      clearAuth();
      window.location.href = '/login';
    }
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorBody.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  login: (email: string, password: string = "NexaTech2026!Secure") =>
    request<any>('/auth/login/json', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    }),
  getMe: () => request<any>('/auth/me'),

  // Dashboard & Overview
  getDashboardOverview: () => request<any>('/dashboard/overview'),
  getHealth: () => request<any>('/health/health'),

  // Services
  getServices: (tier?: string, status?: string) => {
    const params = new URLSearchParams();
    if (tier) params.append('tier', tier);
    if (status) params.append('status', status);
    return request<any[]>(`/services/?${params.toString()}`);
  },
  getServiceDetails: (slug: string) => request<any>(`/services/${slug}`),

  // Incidents
  getIncidents: (statusFilter?: string, severityFilter?: string) => {
    const params = new URLSearchParams();
    if (statusFilter) params.append('status_filter', statusFilter);
    if (severityFilter) params.append('severity_filter', severityFilter);
    return request<any[]>(`/incidents/?${params.toString()}`);
  },
  getIncident: (id: number) => request<any>(`/incidents/${id}`),
  createIncident: (data: { title: string; service_id: number; severity: string; description?: string }) =>
    request<any>('/incidents/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Agent & Investigations
  getInvestigations: () => request<any[]>('/investigations/'),
  getInvestigation: (id: number) => request<any>(`/investigations/${id}`),
  runInvestigation: (incidentId: number) =>
    request<any>('/agent/investigate', {
      method: 'POST',
      body: JSON.stringify({ incident_id: incidentId })
    }),
  getAgentStatus: () => request<any>('/agent/status'),

  // Actions & Approvals
  getActions: (statusFilter?: string) => {
    const params = new URLSearchParams();
    if (statusFilter) params.append('status_filter', statusFilter);
    return request<any[]>(`/actions/?${params.toString()}`);
  },
  proposeAction: (data: { action_type: string; target_resource: string; parameters: any; incident_id?: number }) =>
    request<any>('/actions/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  approveAction: (actionId: number, approved: boolean, reason?: string) =>
    request<any>(`/actions/${actionId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ approved, rejection_reason: reason })
    }),
  executeAction: (actionId: number) =>
    request<any>(`/actions/${actionId}/execute`, {
      method: 'POST'
    }),

  // Observability & Telemetry
  getMetrics: (slug: string, limit: number = 30) =>
    request<any[]>(`/observability/metrics?service_slug=${slug}&limit=${limit}`),
  getLogs: (slug?: string, level?: string, search?: string) => {
    const params = new URLSearchParams();
    if (slug) params.append('service_slug', slug);
    if (level) params.append('level', level);
    if (search) params.append('search', search);
    return request<any[]>(`/observability/logs?${params.toString()}`);
  },

  // Deployments
  getDeployments: (slug?: string) => {
    const params = new URLSearchParams();
    if (slug) params.append('service_slug', slug);
    return request<any[]>(`/deployments/?${params.toString()}`);
  },
  getPullRequests: (slug?: string) => {
    const params = new URLSearchParams();
    if (slug) params.append('service_slug', slug);
    return request<any[]>(`/deployments/pull-requests?${params.toString()}`);
  },

  // Security Intelligence
  getSecurityFindings: (severity?: string, status?: string) => {
    const params = new URLSearchParams();
    if (severity) params.append('severity', severity);
    if (status) params.append('status', status);
    return request<any[]>(`/security/findings?${params.toString()}`);
  },
  getIAMEvents: (suspiciousOnly: boolean = false) =>
    request<any[]>(`/security/iam-events?suspicious_only=${suspiciousOnly}`),

  // ML Models
  getMLInfo: () => request<any>('/ml/info'),
  detectAnomaly: (data: any) =>
    request<any>('/ml/anomaly/detect', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  predictSeverity: (data: any) =>
    request<any>('/ml/severity/predict', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  predictDeploymentRisk: (data: any) =>
    request<any>('/ml/deployment-risk/predict', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Knowledge & RAG
  getDocuments: (category?: string) => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    return request<any[]>(`/knowledge/documents?${params.toString()}`);
  },
  searchKnowledge: (query: string, limit: number = 4) =>
    request<any>('/knowledge/search', {
      method: 'POST',
      body: JSON.stringify({ query, limit })
    }),

  // Evaluation
  getEvaluationRuns: () => request<any[]>('/evaluation/runs'),
  runEvaluationSuite: () =>
    request<any>('/evaluation/run-suite', {
      method: 'POST'
    })
};
