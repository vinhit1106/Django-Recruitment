import { useEffect } from "react";

export function Toast({ message, tone = "success", onClose }: { message: string; tone?: "success" | "error"; onClose: () => void }) {
  useEffect(() => { const timer = window.setTimeout(onClose, 4500); return () => window.clearTimeout(timer); }, [onClose]);
  return <div className={`toast toast-${tone}`} role={tone === "error" ? "alert" : "status"}><span>{message}</span><button type="button" aria-label="Đóng thông báo" onClick={onClose}>×</button></div>;
}

export function FieldErrors({ fields }: { fields?: Record<string, string[]> }) {
  if (!fields || !Object.keys(fields).length) return null;
  const labels: Record<string, string> = { email: "Email", password: "Mật khẩu", role: "Vai trò", first_name: "Tên", last_name: "Họ" };
  return <div className="field-errors" role="alert">{Object.entries(fields).map(([field, messages]) => <div key={field}><strong>{labels[field] ?? field}:</strong> {messages.join(" ")}</div>)}</div>;
}

export function formatApiError(error: unknown): string {
  const value = error as { message?: string; fields?: Record<string, string[]> };
  const fieldText = value.fields ? Object.values(value.fields).flat().join(" ") : "";
  return fieldText || value.message || "Đã xảy ra lỗi. Vui lòng thử lại.";
}
