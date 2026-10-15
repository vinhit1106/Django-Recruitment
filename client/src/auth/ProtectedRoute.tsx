import { useEffect, type ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getAccessToken } from "../api/client";
import { useAuth } from "./AuthProvider";

export function ProtectedRoute({ children, roles }: { children: ReactNode; roles?: string[] }) {
  const { user, loading, error, refreshUser } = useAuth();
  const navigate = useNavigate();
  useEffect(() => {
    if (!loading && !user && !(getAccessToken() && error)) navigate("/login", { replace: true });
    if (!loading && user && roles && !roles.includes(String(user.role))) navigate("/access-denied", { replace: true });
  }, [loading, user, roles, navigate, error]);
  if (loading) return <main className="page"><div className="container"><div className="empty"><h3>Đang khôi phục phiên đăng nhập...</h3></div></div></main>;
  if (!user && getAccessToken() && error) return <main className="page"><div className="container"><div className="empty"><h3>Phiên đăng nhập không còn hợp lệ</h3><p>{error}</p><Link to="/login" className="button button-primary">Đăng nhập lại</Link></div></div></main>;
  if (!user) return <main className="page"><div className="container"><div className="empty"><h3>Đang chuyển tới đăng nhập...</h3></div></div></main>;
  if (roles && !roles.includes(String(user.role))) return <main className="page"><div className="container"><div className="empty"><h3>Không có quyền truy cập</h3><Link to="/access-denied" className="button button-primary">Xem chi tiết</Link></div></div></main>;
  return <>{children}</>;
}
