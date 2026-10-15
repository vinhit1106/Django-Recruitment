import type { UserRole } from "../types";

export type AuthUser = {
  id: string | number;
  email: string;
  first_name?: string;
  last_name?: string;
  name?: string;
  role?: UserRole | string;
};
export type AuthTokens = { access: string; refresh: string };
export type AuthResponse = {
  access?: string;
  refresh?: string;
  access_token?: string;
  refresh_token?: string;
  user?: AuthUser;
};

export type RegisterPayload = {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  role: "CANDIDATE" | "EMPLOYER";
};

const ACCESS_KEY = "ptit_careerhub_access_token";
const REFRESH_KEY = "ptit_careerhub_refresh_token";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY);
}
export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}
export function setTokens(tokens: AuthTokens) {
  localStorage.setItem(ACCESS_KEY, tokens.access);
  localStorage.setItem(REFRESH_KEY, tokens.refresh);
}
export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function parseAuthResponse(response: AuthResponse): AuthTokens {
  const access = response.access ?? response.access_token;
  const refresh = response.refresh ?? response.refresh_token;
  if (!access || !refresh)
    throw new Error(
      "Phản hồi đăng nhập thiếu access hoặc refresh token theo contract.",
    );
  return { access, refresh };
}

export function authHeaders(): HeadersInit {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function normalizeRole(role: AuthUser["role"]): UserRole | undefined {
  if (!role) return undefined;
  const value = String(role).toUpperCase();
  if (value === "CANDIDATE") return "candidate";
  if (value === "EMPLOYER" || value === "RECRUITER") return "employer";
  if (value === "ADMIN") return "admin";
  return undefined;
}
