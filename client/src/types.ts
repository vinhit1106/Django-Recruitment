export type Job = {
  id: string | number;
  title: string;
  company: string;
  companyId?: number;
  location: string;
  employmentType: string;
  experience: string;
  salary?: string;
  description: string;
  requirements?: string;
  benefits?: string;
  category?: string;
  tags: string[];
  postedAt: string;
  featured?: boolean;
};
export type UserRole = 'candidate' | 'employer' | 'recruiter' | 'admin';
