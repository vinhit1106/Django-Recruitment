import {
  authHeaders,
  clearTokens,
  getAccessToken,
  getRefreshToken,
  parseAuthResponse,
  setTokens,
  type AuthResponse,
  type AuthTokens,
  type AuthUser,
  type RegisterPayload,
  normalizeRole,
} from "./auth";

// Vite chỉ expose các biến có tiền tố VITE_. Keep the legacy public name as a
// compatibility fallback, but use VITE_API_BASE_URL as the canonical setting.
const configuredBaseUrl = String(
  import.meta.env.VITE_API_BASE_URL ||
    import.meta.env.VITE_PUBLIC_API_BASE_URL ||
    "",
).trim();
const API_BASE_URL = configuredBaseUrl.replace(/\/+$/, "");
export const isApiConfigured = Boolean(API_BASE_URL);
export const apiBaseUrl = API_BASE_URL;
let refreshInFlight: Promise<string | null> | null = null;
export const SESSION_EXPIRED_EVENT = "ptit:session-expired";
export const SESSION_EXPIRED_NOTICE_KEY = "ptit_careerhub_session_expired";

function isAuthEndpoint(path: string): boolean {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return ["/auth/login/", "/auth/register/", "/auth/refresh/", "/auth/logout/"].includes(normalized);
}

function notifySessionExpired() {
  if (typeof window !== "undefined") {
    sessionStorage.setItem(SESSION_EXPIRED_NOTICE_KEY, "1");
    window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT));
  }
}

function sessionExpiredError(original: unknown): Error & { status?: number; code?: string; fields?: Record<string, string[]> } {
  const error = new Error("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.") as Error & { status?: number; code?: string; fields?: Record<string, string[]> };
  error.status = 401;
  error.code = "AUTH_SESSION_EXPIRED";
  error.fields = (original as { fields?: Record<string, string[]> })?.fields;
  return error;
}

function apiError(
  status: number,
  body: unknown,
): Error & { status?: number; fields?: Record<string, string[]> } {
  const value = body as {
    detail?: string;
    message?: string;
    error?: { message?: string; details?: Record<string, string[]> };
    [key: string]: unknown;
  };
  const error = new Error(
    value?.error?.message ?? value?.detail ?? value?.message ?? `Yêu cầu thất bại (${status})`,
  ) as Error & { status?: number; fields?: Record<string, string[]> };
  error.status = status;
  if (value?.error?.details) error.fields = value.error.details;
  if (body && typeof body === "object") {
    const fields = Object.fromEntries(
      Object.entries(value)
        .filter(([, item]) => Array.isArray(item))
        .map(([key, item]) => [key, item as string[]]),
    );
    if (Object.keys(fields).length) error.fields = { ...error.fields, ...fields };
  }
  return error;
}

async function rawRequest<T>(
  path: string,
  options: RequestInit = {},
  token = getAccessToken(),
): Promise<T> {
  if (!API_BASE_URL)
    throw new Error(
      "API chưa được cấu hình. Hãy tạo file .env từ .env.example.",
    );
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData) && !headers.has("Content-Type"))
    headers.set("Content-Type", "application/json");
  if (token && !headers.has("Authorization"))
    headers.set("Authorization", `Bearer ${token}`);
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${normalizedPath}`, {
      ...options,
      headers,
    });
  } catch (error) {
    // TypeError is what browsers normally expose for a refused connection or
    // a CORS/network failure. Keep the configured URL in the message so the
    // developer can immediately verify the Django process and port.
    if (error instanceof TypeError) {
      throw new Error(
        `Không thể kết nối Backend tại ${API_BASE_URL}. Hãy kiểm tra Django có đang chạy và CORS đã cho phép frontend chưa.`,
      );
    }
    throw error;
  }
  const body =
    response.status === 204
      ? undefined
      : await response.json().catch(() => undefined);
  if (!response.ok) throw apiError(response.status, body);
  return body as T;
}

async function rawBlobRequest(path: string, options: RequestInit = {}, token = getAccessToken()): Promise<Blob> {
  if (!API_BASE_URL) throw new Error("API chưa được cấu hình. Hãy tạo file .env từ .env.example.");
  const headers = new Headers(options.headers);
  if (token && !headers.has("Authorization")) headers.set("Authorization", `Bearer ${token}`);
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  let response: Response;
  try { response = await fetch(`${API_BASE_URL}${normalizedPath}`, { ...options, headers }); }
  catch { throw new Error(`Không thể kết nối Backend tại ${API_BASE_URL}.`); }
  if (!response.ok) {
    const body = await response.json().catch(() => undefined);
    throw apiError(response.status, body);
  }
  return response.blob();
}

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;
  if (!refreshInFlight) {
    refreshInFlight = rawRequest<AuthResponse>(
      "/auth/refresh/",
      { method: "POST", body: JSON.stringify({ refresh }) },
      null,
    )
      .then((response) => {
        const tokens = parseAuthResponse(response);
        localStorage.setItem("ptit_careerhub_access_token", tokens.access);
        localStorage.setItem("ptit_careerhub_refresh_token", tokens.refresh);
        return tokens.access;
      })
      .catch(() => {
        clearTokens();
        return null;
      })
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  try {
    return await rawRequest<T>(path, options);
  } catch (error) {
    if ((error as { status?: number }).status !== 401 || isAuthEndpoint(path))
      throw error;
    const token = await refreshAccessToken();
    if (!token) { notifySessionExpired(); throw sessionExpiredError(error); }
    try {
      return await rawRequest<T>(path, options, token);
    } catch (retryError) {
      if ((retryError as { status?: number }).status === 401) { clearTokens(); notifySessionExpired(); throw sessionExpiredError(retryError); }
      throw retryError;
    }
  }
}

export async function requestBlob(path: string, options: RequestInit = {}): Promise<Blob> {
  try { return await rawBlobRequest(path, options); }
  catch (error) {
    if ((error as { status?: number }).status !== 401 || isAuthEndpoint(path)) throw error;
    const token = await refreshAccessToken();
    if (!token) { notifySessionExpired(); throw sessionExpiredError(error); }
    try {
      return await rawBlobRequest(path, options, token);
    } catch (retryError) {
      if ((retryError as { status?: number }).status === 401) { clearTokens(); notifySessionExpired(); throw sessionExpiredError(retryError); }
      throw retryError;
    }
  }
}

export async function login(payload: { email: string; password: string }) {
  const response = await rawRequest<AuthResponse>(
    "/auth/login/",
    { method: "POST", body: JSON.stringify(payload) },
    null,
  );
  const tokens = parseAuthResponse(response);
  setTokens(tokens);
  return { tokens, user: response.user };
}
export async function register(payload: RegisterPayload) {
  const response = await rawRequest<AuthResponse>(
    "/auth/register/",
    { method: "POST", body: JSON.stringify(payload) },
    null,
  );
  const hasTokens = Boolean(
    (response.access ?? response.access_token) &&
      (response.refresh ?? response.refresh_token),
  );
  const tokens = hasTokens ? parseAuthResponse(response) : undefined;
  if (tokens) setTokens(tokens);
  return { tokens, user: response.user };
}
export async function me() {
  return request<AuthUser>("/auth/me/");
}
export async function logout() {
  const refresh = getRefreshToken();
  try {
    if (refresh)
      await rawRequest("/auth/logout/", {
        method: "POST",
        body: JSON.stringify({ refresh }),
      });
  } finally {
    clearTokens();
    if (typeof window !== "undefined") sessionStorage.removeItem(SESSION_EXPIRED_NOTICE_KEY);
  }
}
export { authHeaders, clearTokens, getAccessToken, getRefreshToken, normalizeRole };
export type { AuthTokens, AuthUser };
