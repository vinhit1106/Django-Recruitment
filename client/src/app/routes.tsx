import { Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "../auth/ProtectedRoute";
import { AccessDenied, ApplicationDetailPage, Auth, CompaniesPage, CompanyDetail, DashboardPage, Home, JobDetail, JobsPage } from "../App";

export function AppRoutes() {
  return <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/jobs" element={<JobsPage />} />
    <Route path="/jobs/:id" element={<JobDetail />} />
    <Route path="/companies" element={<CompaniesPage />} />
    <Route path="/companies/:id" element={<CompanyDetail />} />
    <Route path="/login" element={<Auth />} />
    <Route path="/register" element={<Auth register />} />
    <Route path="/candidate" element={<ProtectedRoute roles={["candidate"]}><DashboardPage role="candidate" /></ProtectedRoute>} />
    <Route path="/candidate/applications/:id" element={<ProtectedRoute roles={["candidate"]}><ApplicationDetailPage role="candidate" /></ProtectedRoute>} />
    <Route path="/employer" element={<ProtectedRoute roles={["employer", "recruiter"]}><DashboardPage role="employer" /></ProtectedRoute>} />
    <Route path="/employer/applications/:id" element={<ProtectedRoute roles={["employer", "recruiter"]}><ApplicationDetailPage role="employer" /></ProtectedRoute>} />
    <Route path="/admin" element={<ProtectedRoute roles={["admin"]}><DashboardPage role="admin" /></ProtectedRoute>} />
    <Route path="/access-denied" element={<AccessDenied />} />
    <Route path="*" element={<Home />} />
  </Routes>;
}
