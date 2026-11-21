import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { getAuthToken } from './services/api';

// Pages
import { Login } from './pages/Login';
import { Overview } from './pages/Overview';
import { Services } from './pages/Services';
import { Incidents } from './pages/Incidents';
import { IncidentDetail } from './pages/IncidentDetail';
import { InvestigationWorkspace } from './pages/InvestigationWorkspace';
import { SecurityIntelligence } from './pages/SecurityIntelligence';
import { DeploymentRisk } from './pages/DeploymentRisk';
import { AgentActivity } from './pages/AgentActivity';
import { ApprovalQueue } from './pages/ApprovalQueue';
import { Reports } from './pages/Reports';
import { ModelEvaluation } from './pages/ModelEvaluation';
import { KnowledgeBase } from './pages/KnowledgeBase';
import { UserManagement } from './pages/UserManagement';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const token = getAuthToken();
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <Layout>{children}</Layout>;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={<ProtectedRoute><Overview /></ProtectedRoute>} />
        <Route path="/services" element={<ProtectedRoute><Services /></ProtectedRoute>} />
        <Route path="/incidents" element={<ProtectedRoute><Incidents /></ProtectedRoute>} />
        <Route path="/incidents/:id" element={<ProtectedRoute><IncidentDetail /></ProtectedRoute>} />
        <Route path="/investigation" element={<ProtectedRoute><InvestigationWorkspace /></ProtectedRoute>} />
        <Route path="/security" element={<ProtectedRoute><SecurityIntelligence /></ProtectedRoute>} />
        <Route path="/deployments" element={<ProtectedRoute><DeploymentRisk /></ProtectedRoute>} />
        <Route path="/agent-activity" element={<ProtectedRoute><AgentActivity /></ProtectedRoute>} />
        <Route path="/approvals" element={<ProtectedRoute><ApprovalQueue /></ProtectedRoute>} />
        <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />
        <Route path="/models" element={<ProtectedRoute><ModelEvaluation /></ProtectedRoute>} />
        <Route path="/knowledge" element={<ProtectedRoute><KnowledgeBase /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><UserManagement /></ProtectedRoute>} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
