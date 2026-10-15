import { request } from "./client";
import type { Job } from "../types";

export type JobsPage = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Job[];
};
export type JobFilters = {
  search?: string;
  location?: string;
  category?: string;
  employment_type?: string;
  salary_min?: string;
  salary_max?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
};

function mapJob(input: Record<string, unknown>): Job {
  const company = input.company as Record<string, unknown> | undefined;
  return {
    id: String(input.id ?? input.pk ?? ""),
    title: String(input.title ?? ""),
    company: String(
      input.company_name ?? company?.name ?? input.company ?? "Doanh nghiệp",
    ),
    companyId: typeof company?.id === "number" ? company.id : undefined,
    location: String(input.location ?? ""),
    employmentType: String(input.employment_type ?? input.employmentType ?? ""),
    experience: String(input.experience_level ?? input.experience ?? ""),
    salary: input.salary ? String(input.salary) : undefined,
    description: String(input.description ?? ""),
    requirements: String(input.requirements ?? ""),
    benefits: String(input.benefits ?? ""),
    category: String(((input.category as Record<string, unknown> | undefined)?.name ?? input.category_name ?? "")),
    tags: Array.isArray(input.tags) ? input.tags.map(String) : [],
    postedAt: String(input.posted_at ?? input.created_at ?? ""),
    featured: Boolean(input.featured),
  };
}

export async function getJobs(filters: JobFilters = {}): Promise<JobsPage> {
  const query = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") query.set(key, String(value));
  });
  const data = await request<
    | {
        count?: number;
        next?: string | null;
        previous?: string | null;
        results?: Record<string, unknown>[];
      }
    | Record<string, unknown>[]
  >(`/jobs/?${query}`);
  if (Array.isArray(data))
    return {
      count: data.length,
      next: null,
      previous: null,
      results: data.map(mapJob),
    };
  if (!Array.isArray(data.results))
    throw new Error(
      "API jobs trả về cấu trúc không hợp lệ: thiếu trường results.",
    );
  return {
    count: Number(data.count ?? data.results.length),
    next: data.next ?? null,
    previous: data.previous ?? null,
    results: data.results.map(mapJob),
  };
}
export async function getJob(id: string | number): Promise<Job> {
  return mapJob(await request<Record<string, unknown>>(`/jobs/${id}/`));
}
