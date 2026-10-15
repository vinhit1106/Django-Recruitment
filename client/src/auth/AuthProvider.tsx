import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { clearTokens, getAccessToken, login, logout, me, normalizeRole, SESSION_EXPIRED_EVENT, type AuthUser } from "../api/client";

type AuthContextValue = { user: AuthUser | null; loading: boolean; error: string; signIn: (payload: { email: string; password: string }) => Promise<AuthUser>; signOut: () => Promise<void>; refreshUser: () => Promise<AuthUser | null> };
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(Boolean(getAccessToken()));
  const [error, setError] = useState("");
  const normalizeUser = useCallback((value: AuthUser | undefined): AuthUser => {
    if (!value || value.id === undefined || !value.email) throw new Error("Phản hồi xác thực thiếu thông tin user.");
    const role = normalizeRole(value.role);
    if (!role) throw new Error("Tài khoản có role không được hỗ trợ.");
    return { ...value, role };
  }, []);
  const refreshUser = useCallback(async () => {
    if (!getAccessToken()) { setUser(null); return null; }
    try {
      const next = await me();
      const normalized = normalizeUser(next);
      setUser(normalized);
      setError("");
      return normalized;
    } catch (err) {
      const status = (err as { status?: number }).status;
      const message = (err as Error).message;
      const transientNetworkError = !status && message.includes("Không thể kết nối Backend");
      setError(message);
      if (!transientNetworkError) {
        clearTokens();
        setUser(null);
      }
      return null;
    }
  }, [normalizeUser]);
  useEffect(() => { refreshUser().finally(() => setLoading(false)); }, [refreshUser]);
  useEffect(() => {
    const handleExpired = () => {
      clearTokens();
      setUser(null);
      setError("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
    };
    window.addEventListener(SESSION_EXPIRED_EVENT, handleExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, handleExpired);
  }, []);
  const signIn = useCallback(async (payload: { email: string; password: string }) => {
    const result = await login(payload);
    const next = normalizeUser(result.user ?? await me());
    setUser(next);
    setError("");
    return next;
  }, [normalizeUser]);
  const signOut = useCallback(async () => { try { await logout(); } finally { setUser(null); setError(""); } }, []);
  const value = useMemo(() => ({ user, loading, error, signIn, signOut, refreshUser }), [user, loading, error, signIn, signOut, refreshUser]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth() { const context = useContext(AuthContext); if (!context) throw new Error("useAuth phải được dùng trong AuthProvider"); return context; }
