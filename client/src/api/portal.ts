import { request, requestBlob } from "./client";

export type Dashboard = Record<string, unknown> & {
  application_count?: number;
  job_count?: number;
  company_id?: number;
  pending_job_count?: number;
  recent_applications?: Array<Record<string, unknown>>;
};
export type Profile = { id: number; full_name: string; phone: string; location: string; summary: string; updated_at?: string };
export type CV = { id: number; original_filename: string; file_size: number; content_type?: string; status: string; created_at?: string };
export type Application = { id: number; job: Record<string, unknown>; cv: Record<string, unknown>; cover_letter: string; status: string; applied_at: string; updated_at?: string };
export type Company = { id: number; name: string; website?: string; address?: string; description?: string };
export type EmployerJob = Record<string, unknown> & { id: number; title: string; status: string; rejection_reason?: string };
export type Skill = { id: number; name: string; is_active: boolean };
export type Category = { id: number; name: string; slug: string; description?: string };
export type AdminSkill = Skill;
export type CandidateSkill = { id: number; skill: Skill; created_at?: string };
export type Experience = { id: number; company_name: string; job_title: string; description: string; start_date: string; end_date?: string | null; is_current: boolean };

export const portalApi = {
  candidateDashboard: () => request<Dashboard>("/dashboard/candidate/"),
  employerDashboard: () => request<Dashboard>("/employer/dashboard/"),
  adminDashboard: () => request<Dashboard>("/admin/dashboard/"),
  profile: () => request<Profile>("/candidate/profile/"),
  updateProfile: (data: Partial<Profile>) => request<Profile>("/candidate/profile/", { method: "PATCH", body: JSON.stringify(data) }),
  skills: () => request<{ count?: number; results?: CandidateSkill[] } | CandidateSkill[]>("/candidate/skills/"),
  skillCatalog: () => request<{ count?: number; results?: Skill[] } | Skill[]>("/candidate/skills/catalog/"),
  addSkill: (skill_id: number) => request<CandidateSkill>("/candidate/skills/", { method: "POST", body: JSON.stringify({ skill_id }) }),
  removeSkill: (id: number) => request<void>(`/candidate/skills/${id}/`, { method: "DELETE" }),
  experiences: () => request<{ count?: number; results?: Experience[] } | Experience[]>("/candidate/experiences/"),
  createExperience: (data: Omit<Experience, "id">) => request<Experience>("/candidate/experiences/", { method: "POST", body: JSON.stringify(data) }),
  updateExperience: (id: number, data: Partial<Experience>) => request<Experience>(`/candidate/experiences/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  removeExperience: (id: number) => request<void>(`/candidate/experiences/${id}/`, { method: "DELETE" }),
  cvs: () => request<{ count?: number; results?: CV[] } | CV[]>("/candidate/cvs/"),
  uploadCv: (file: File) => { const body = new FormData(); body.append("file", file); return request<CV>("/candidate/cvs/", { method: "POST", body }); },
  removeCv: (id: number) => request<void>(`/candidate/cvs/${id}/`, { method: "DELETE" }),
  downloadCv: (id: number) => requestBlob(`/candidate/cvs/${id}/download/`),
  applications: () => request<{ count?: number; results?: Application[] } | Application[]>("/candidate/applications/"),
  application: (id: number) => request<Application>(`/candidate/applications/${id}/`),
  apply: (data: { job_id: number; cv_id: number; cover_letter?: string }) => request<Application>("/candidate/applications/", { method: "POST", body: JSON.stringify(data) }),
  withdraw: (id: number) => request<Application>(`/candidate/applications/${id}/withdraw/`, { method: "POST" }),
  company: () => request<Company>("/employer/company/"),
  publicCompanies: () => request<{ count?: number; results?: Company[] } | Company[]>("/companies/"),
  publicCompany: (id: number) => request<Company>(`/companies/${id}/`),
  categories: () => request<{ count?: number; results?: Category[] } | Category[]>("/categories/"),
  createCompany: (data: Partial<Company>) => request<Company>("/employer/company/", { method: "POST", body: JSON.stringify(data) }),
  updateCompany: (data: Partial<Company>) => request<Company>("/employer/company/", { method: "PATCH", body: JSON.stringify(data) }),
  employerJobs: () => request<{ count?: number; results?: EmployerJob[] } | EmployerJob[]>("/employer/jobs/"),
  createJob: (data: Record<string, unknown>) => request<EmployerJob>("/employer/jobs/", { method: "POST", body: JSON.stringify(data) }),
  updateJob: (id: number, data: Record<string, unknown>) => request<EmployerJob>(`/employer/jobs/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  submitJob: (id: number) => request<EmployerJob>(`/employer/jobs/${id}/submit/`, { method: "POST" }),
  closeJob: (id: number) => request<EmployerJob>(`/employer/jobs/${id}/close/`, { method: "POST" }),
  employerApplications: () => request<{ count?: number; results?: Application[] } | Application[]>("/employer/applications/"),
  employerApplication: (id: number) => request<Application>(`/employer/applications/${id}/`),
  transitionApplication: (id: number, data: { status: string; note?: string }) => request<Application>(`/employer/applications/${id}/transition/`, { method: "POST", body: JSON.stringify(data) }),
  employerDownloadCv: (id: number) => requestBlob(`/employer/applications/${id}/cv/download/`),
  adminPendingJobs: () => request<{ count?: number; results?: EmployerJob[] } | EmployerJob[]>("/admin/jobs/pending/"),
  adminPendingJob: (id: number) => request<Record<string, unknown>>(`/admin/jobs/pending/${id}/`),
  approveJob: (id: number) => request<EmployerJob>(`/admin/jobs/${id}/approve/`, { method: "POST" }),
  rejectJob: (id: number, reason: string) => request<EmployerJob>(`/admin/jobs/${id}/reject/`, { method: "POST", body: JSON.stringify({ reason }) }),
  adminUsers: () => request<{ count?: number; results?: Array<Record<string, unknown>> } | Array<Record<string, unknown>>>("/admin/users/"),
  adminCategories: () => request<{ count?: number; results?: Array<Record<string, unknown>> } | Array<Record<string, unknown>>>("/admin/categories/"),
  createCategory: (data: Record<string, unknown>) => request<Record<string, unknown>>("/admin/categories/", { method: "POST", body: JSON.stringify(data) }),
  deleteCategory: (id: number) => request<void>(`/admin/categories/${id}/`, { method: "DELETE" }),
  adminSkills: (search?: string) => request<{ count?: number; results?: AdminSkill[] } | AdminSkill[]>(`/admin/skills/${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  createSkill: (data: { name: string; is_active?: boolean }) => request<AdminSkill>("/admin/skills/", { method: "POST", body: JSON.stringify(data) }),
  updateSkill: (id: number, data: Partial<AdminSkill>) => request<AdminSkill>(`/admin/skills/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteSkill: (id: number) => request<void>(`/admin/skills/${id}/`, { method: "DELETE" }),
};

export function listResults<T>(value: T[] | { results?: T[] }): T[] {
  return Array.isArray(value) ? value : value.results ?? [];
}
