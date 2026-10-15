import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent } from "react";
import {
  BrowserRouter,
  Link,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import {
  ArrowRight,
  BriefcaseBusiness,
  Building2,
  CheckCircle2,
  ChevronDown,
  Clock3,
  MapPin,
  Menu,
  Search,
  Sparkles,
  Users,
  X,
} from "lucide-react";
import type { Job } from "./types";
import { isApiConfigured, register as registerUser, SESSION_EXPIRED_NOTICE_KEY } from "./api/client";
import { getJob, getJobs } from "./api/jobs";
import { useAuth } from "./auth/AuthProvider";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { listResults, portalApi, type CandidateSkill, type Category, type Company, type Dashboard, type Experience, type Profile, type CV, type Skill } from "./api/portal";
import { FieldErrors, formatApiError, Toast } from "./components/feedback/Toast";
import { AppRoutes } from "./app/routes";
import "./styles/global.css";

function Header() {
  const [open, setOpen] = useState(false);
  const { user } = useAuth();
  const portalPath = user?.role === "candidate" ? "/candidate" : user?.role === "admin" ? "/admin" : "/employer";
  return (
    <header className="header">
      <div className="container nav">
        <Link to="/" className="brand">
          <span className="brand-mark">P</span>
          <span>
            PTIT <b>CareerHub</b>
          </span>
        </Link>
        <button
          className="menu-button"
          aria-label="Mở menu"
          onClick={() => setOpen(!open)}
        >
          {open ? <X /> : <Menu />}
        </button>
        <nav className={open ? "nav-links open" : "nav-links"}>
          <Link to="/jobs" onClick={() => setOpen(false)}>
            Tìm việc
          </Link>
          <Link to="/companies" onClick={() => setOpen(false)}>Công ty</Link>
          <a href="#about">Về chúng tôi</a>
          <span className="nav-divider" />
          {user ? <Link to={portalPath} className="login-link">Bảng điều khiển</Link> : <><Link to="/login" className="login-link">Đăng nhập</Link><Link to="/register" className="button button-primary small">Đăng ký miễn phí</Link></>}
        </nav>
      </div>
    </header>
  );
}
function Footer() {
  return (
    <footer>
      <div className="container footer-grid">
        <div>
          <div className="brand footer-brand">
            <span className="brand-mark">P</span>
            <span>
              PTIT <b>CareerHub</b>
            </span>
          </div>
          <p>
            Nền tảng kết nối tài năng trẻ PTIT với những cơ hội nghề nghiệp tốt
            nhất.
          </p>
        </div>
        <div>
          <h4>Dành cho ứng viên</h4>
          <Link to="/jobs">Tìm việc làm</Link>
          <Link to="/register">Tạo hồ sơ</Link>
          <a href="#tips">Cẩm nang nghề nghiệp</a>
        </div>
        <div>
          <h4>Dành cho nhà tuyển dụng</h4>
          <a href="#post">Đăng tin tuyển dụng</a>
          <a href="#talent">Tìm kiếm ứng viên</a>
          <a href="#pricing">Bảng giá dịch vụ</a>
        </div>
        <div>
          <h4>Liên hệ</h4>
          <p>support@ptitcareerhub.vn</p>
          <p>Hà Nội, Việt Nam</p>
        </div>
      </div>
      <div className="container copyright">
        © 2025 PTIT CareerHub · Được xây dựng bởi sinh viên PTIT
      </div>
    </footer>
  );
}
function SearchBar({ initial = "" }: { initial?: string }) {
  const [q, setQ] = useState(initial);
  const [location, setLocation] = useState("");
  const navigate = useNavigate();
  return (
    <form
      className="search-bar"
      onSubmit={(e) => {
        e.preventDefault();
        const params = new URLSearchParams(); if (q) params.set("q", q); if (location) params.set("location", location); navigate(`/jobs?${params}`);
      }}
    >
      <Search size={20} />
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Chức danh, kỹ năng hoặc từ khóa..."
        aria-label="Tìm kiếm việc làm"
      />
      <span className="search-divider" />
      <MapPin size={19} />
      <input
        className="location-input"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        placeholder="Địa điểm"
        aria-label="Địa điểm"
      />
      <button className="button button-primary" type="submit">
        Tìm việc
      </button>
    </form>
  );
}
function JobCard({ job }: { job: Job }) {
  return (
    <Link to={`/jobs/${job.id}`} className="job-card">
      <div className="job-logo">{job.company.slice(0, 1)}</div>
      <div className="job-card-body">
        <div className="job-title-row">
          <h3>{job.title}</h3>
          {job.featured && <span className="badge featured">Nổi bật</span>}
        </div>
        <p className="company">{job.company}</p>
        <div className="meta">
          <span>
            <MapPin size={15} />
            {job.location}
          </span>
          <span>
            <BriefcaseBusiness size={15} />
            {job.employmentType}
          </span>
        </div>
        <div className="tags">
          {job.tags.map((t) => (
            <span key={t}>{t}</span>
          ))}
        </div>
      </div>
      <div className="job-time">{job.postedAt}</div>
    </Link>
  );
}
export function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]> | undefined>();
  useEffect(() => { if (isApiConfigured) portalApi.publicCompanies().then((data) => setCompanies(listResults(data))).catch((err: Error) => setError(err.message)); }, []);
  return <><Header /><main className="page"><div className="container"><div className="page-intro"><div><div className="eyebrow muted">Khám phá nhà tuyển dụng</div><h1>Công ty đang tuyển dụng</h1><p>{companies.length} doanh nghiệp công khai trên CareerHub</p></div></div>{!isApiConfigured && <div className="error-notice">API chưa được cấu hình. Không thể tải dữ liệu công ty.</div>}{error && <div className="error-notice">{error}</div>}<div className="jobs-grid">{companies.map((company) => <Link className="job-card" to={`/companies/${company.id}`} key={company.id}><div className="job-logo">{company.name.slice(0, 1)}</div><div className="job-card-body"><h3>{company.name}</h3><p className="company">{company.address || "Việt Nam"}</p><p>{company.description || "Doanh nghiệp chưa cập nhật phần giới thiệu."}</p></div></Link>)}</div>{isApiConfigured && !companies.length && !error && <div className="empty"><Building2 size={32} /><h3>Chưa có công ty công khai</h3></div>}</div></main><Footer /></>;
}
export function CompanyDetail() {
  const { id } = useParams(); const [company, setCompany] = useState<Company | null>(null); const [jobs, setJobs] = useState<Job[]>([]); const [error, setError] = useState("");
  useEffect(() => { if (!id) return; portalApi.publicCompany(Number(id)).then(setCompany).catch((err: Error) => setError(err.message)); if (isApiConfigured) getJobs({ page_size: 100 }).then((page) => setJobs(page.results.filter((job) => job.companyId === Number(id)))).catch((err: Error) => setError(err.message)); }, [id]);
  return <><Header /><main className="page"><div className="container"><Link to="/companies" className="back-link">← Danh sách công ty</Link>{error && <div className="error-notice">{error}</div>}{!company && !error ? <div className="empty"><h3>Đang tải thông tin công ty...</h3></div> : company ? <><article className="portal-card"><div className="detail-head"><div className="job-logo large">{company.name.slice(0, 1)}</div><div><h1>{company.name}</h1><p className="company">{company.address || "Việt Nam"}</p>{company.website && <a href={company.website} target="_blank" rel="noreferrer">Website công ty</a>}</div></div><div className="content-block"><h2>Giới thiệu</h2><p>{company.description || "Doanh nghiệp chưa cập nhật phần giới thiệu."}</p></div></article><section className="section"><div className="section-heading"><h2>Việc làm đang tuyển ({jobs.length})</h2></div><div className="jobs-grid">{jobs.map((job) => <JobCard job={job} key={job.id} />)}</div>{!jobs.length && <div className="empty compact"><p>Hiện chưa có việc làm công khai.</p></div>}</section></> : null}</div></main><Footer /></>;
}
export function Home() {
  const [featured, setFeatured] = useState<Job[]>([]);
  const [apiError, setApiError] = useState("");
  const [jobCount, setJobCount] = useState<number | null>(null);
  const [companyCount, setCompanyCount] = useState<number | null>(null);
  useEffect(() => {
    if (!isApiConfigured) { setApiError("API chưa được cấu hình."); return; }
    Promise.all([getJobs({ page_size: 4, ordering: "-created_at" }), portalApi.publicCompanies()])
      .then(([page, companies]) => { setFeatured(page.results.slice(0, 4)); setJobCount(page.count); setCompanyCount(Array.isArray(companies) ? companies.length : Number(companies.count ?? companies.results?.length ?? 0)); })
      .catch((error: Error) => setApiError(error.message));
  }, []);
  return (
    <>
      <Header />
      <main>
        <section className="hero">
          <div className="container hero-content">
            <div className="eyebrow">
              <Sparkles size={16} /> Cơ hội mới đang chờ bạn
            </div>
            <h1>
              Tìm công việc
              <br />
              <span>đúng với bạn.</span>
            </h1>
            <p className="hero-subtitle">
              Khám phá hàng nghìn cơ hội việc làm chất lượng từ các doanh nghiệp
              hàng đầu. Bắt đầu hành trình sự nghiệp của bạn ngay hôm nay.
            </p>
            <SearchBar />
            <div className="hero-stats">
              <div>
                <strong>{jobCount === null ? "—" : jobCount.toLocaleString("vi-VN")}</strong>
                <span>Việc làm đang tuyển</span>
              </div>
              <div>
                <strong>{companyCount === null ? "—" : companyCount.toLocaleString("vi-VN")}</strong>
                <span>Doanh nghiệp uy tín</span>
              </div>
              <div>
                <strong>API</strong>
                <span>Dữ liệu cập nhật trực tiếp</span>
              </div>
            </div>
          </div>
          <div className="hero-glow" />
        </section>
        <section className="section" id="jobs">
          <div className="container">
            <div className="section-heading">
              <div>
                <div className="eyebrow muted">Cơ hội dành cho bạn</div>
                <h2>Việc làm nổi bật</h2>
              </div>
              <Link className="text-link" to="/jobs">
                Xem tất cả việc làm <ArrowRight size={17} />
              </Link>
            </div>
            {apiError && <div className="error-notice">Không thể tải việc làm từ Backend: {apiError}</div>}
            <div className="jobs-grid">
              {featured.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          </div>
        </section>
        <section className="trust-section" id="companies">
          <div className="container trust">
            <div>
              <div className="eyebrow muted">Được tin dùng bởi</div>
              <h2>Những nơi tài năng PTIT đang tỏa sáng</h2>
            </div>
            <Link className="text-link" to="/companies">Xem danh sách doanh nghiệp <ArrowRight size={17} /></Link>
          </div>
        </section>
        <section className="cta-section" id="about">
          <div className="container cta">
            <div>
              <div className="eyebrow">Dành cho nhà tuyển dụng</div>
              <h2>
                Tìm đúng người.
                <br />
                Xây đúng đội ngũ.
              </h2>
              <p>
                Tiếp cận cộng đồng tài năng trẻ PTIT năng động và sẵn sàng tạo
                ra khác biệt.
              </p>
              <Link to="/register?role=EMPLOYER" className="button button-light">
                Đăng tin tuyển dụng <ArrowRight size={17} />
              </Link>
            </div>
            <div className="cta-art">
              <div className="art-card">
                <Users size={25} />
                <strong>API</strong>
                <span>Dữ liệu cập nhật trực tiếp</span>
              </div>
              <div className="art-card offset">
                <CheckCircle2 size={22} />
                <strong>98%</strong>
                <span>hài lòng doanh nghiệp</span>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
export function JobsPage() {
  const [params, setParams] = useSearchParams();
  const q = params.get("q") ?? "";
  const location = params.get("location") ?? "";
  const [search, setSearch] = useState(q);
  const [type, setType] = useState("Tất cả");
  const [apiJobs, setApiJobs] = useState<Job[] | null>(null);
  const [pageInfo, setPageInfo] = useState({ count: 0, page: Number(params.get("page") ?? 1), pageSize: 10 });
  const [apiError, setApiError] = useState("");
  const [categories, setCategories] = useState<Category[]>([]);
  const category = params.get("category") ?? "";
  useEffect(() => { if (isApiConfigured) portalApi.categories().then((data) => setCategories(listResults(data))).catch((error: Error) => setApiError(error.message)); }, []);
  useEffect(() => {
    if (!isApiConfigured) return;
    const page = Number(params.get("page") ?? 1);
    getJobs({ search: q || undefined, location: location || undefined, category: category || undefined, employment_type: type === "Tất cả" ? undefined : type, page, page_size: 10 })
      .then((result) => { setApiJobs(result.results); setPageInfo({ count: result.count, page, pageSize: 10 }); })
      .catch((error: Error) => setApiError(error.message));
  }, [q, location, category, type, params]);
  const filtered = useMemo(
    () =>
      (apiJobs ?? []).filter(
        (j) =>
          (!q ||
            `${j.title} ${j.company} ${j.tags.join(" ")}`
              .toLowerCase()
              .includes(q.toLowerCase())) &&
          (type === "Tất cả" || j.employmentType === type || (type === "FULL_TIME" && j.employmentType === "FULL_TIME")),
      ),
    [q, type, apiJobs],
  );
  return (
    <>
      <Header />
      <main className="page">
        <div className="container">
          <div className="page-intro">
            <div>
              <div className="eyebrow muted">Khám phá cơ hội</div>
              <h1>Việc làm phù hợp với bạn</h1>
              <p>{filtered.length} vị trí đang tuyển dụng</p>
            </div>
          </div>
          {apiError && <div className="error-notice">Không thể tải danh sách từ Backend: {apiError}</div>}
          <form
            className="listing-search"
            onSubmit={(e) => {
              e.preventDefault();
              const next = new URLSearchParams(); if (search) next.set("q", search); if (location) next.set("location", location); setParams(next);
            }}
          >
            <Search size={19} />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Tìm theo chức danh, công ty hoặc kỹ năng"
            />
            <button className="button button-primary">Tìm kiếm</button>
          </form>
          <div className="listing-layout">
            <aside className="filters">
              <h3>Bộ lọc tìm kiếm</h3>
              <label>
                Loại hình công việc
                <select value={type} onChange={(e) => setType(e.target.value)}>
                  <option value="Tất cả">Tất cả</option>
                  <option value="FULL_TIME">Toàn thời gian</option>
                  <option value="PART_TIME">Bán thời gian</option>
                  <option value="CONTRACT">Hợp đồng</option>
                  <option value="INTERNSHIP">Thực tập</option>
                </select>
              </label>
              <label>
                Lĩnh vực
                <select value={category || "Tất cả lĩnh vực"} onChange={(e) => { const next = new URLSearchParams(params); if (e.target.value === "Tất cả lĩnh vực") next.delete("category"); else next.set("category", e.target.value); next.delete("page"); setParams(next); }}>
                  <option value="Tất cả lĩnh vực">Tất cả lĩnh vực</option>
                  {categories.map((item) => <option value={item.slug} key={item.id}>{item.name}</option>)}
                </select>
              </label>
              <label>
                Khu vực
                <select value={location || "Tất cả địa điểm"} onChange={(e) => { const next = new URLSearchParams(params); if (e.target.value === "Tất cả địa điểm") next.delete("location"); else next.set("location", e.target.value); next.delete("page"); setParams(next); }}>
                  <option>Tất cả địa điểm</option>
                  <option>Hà Nội</option>
                  <option>TP. Hồ Chí Minh</option>
                  <option>Đà Nẵng</option>
                </select>
              </label>
              <button
                className="clear-filter"
                onClick={() => {
                  setType("Tất cả");
                  setSearch("");
                  setParams({});
                }}
              >
                Xóa bộ lọc
              </button>
            </aside>
            <div className="results">
              <div className="results-header">
                <span>
                  Sắp xếp: <b>Mới nhất</b> <ChevronDown size={15} />
                </span>
              </div>
              {filtered.length ? (
                filtered.map((job) => <JobCard key={job.id} job={job} />)
              ) : (
                <div className="empty">
                  <Search size={32} />
                  <h3>Không tìm thấy việc làm</h3>
                  <p>Hãy thử từ khóa hoặc bộ lọc khác.</p>
                </div>
              )}
              {isApiConfigured && pageInfo.count > pageInfo.pageSize && <div className="pagination"><button className="button button-outline small" disabled={pageInfo.page <= 1} onClick={() => { const next = new URLSearchParams(params); next.set("page", String(pageInfo.page - 1)); setParams(next); }}>Trước</button><span>Trang {pageInfo.page} / {Math.ceil(pageInfo.count / pageInfo.pageSize)}</span><button className="button button-outline small" disabled={pageInfo.page >= Math.ceil(pageInfo.count / pageInfo.pageSize)} onClick={() => { const next = new URLSearchParams(params); next.set("page", String(pageInfo.page + 1)); setParams(next); }}>Sau</button></div>}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
export function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState<Job | null>(null);
  const [apiError, setApiError] = useState("");
  useEffect(() => {
    if (!id) return;
    if (!isApiConfigured) { setApiError("API chưa được cấu hình."); return; }
    getJob(id).then(setJob).catch((error: Error) => setApiError(error.message));
  }, [id]);
  const [applied, setApplied] = useState(false);
  const { user } = useAuth();
  const navigate = useNavigate();
  const [cvs, setCvs] = useState<CV[]>([]);
  const [selectedCv, setSelectedCv] = useState("");
  const [coverLetter, setCoverLetter] = useState("");
  const [applyError, setApplyError] = useState("");
  const [applyLoading, setApplyLoading] = useState(false);
  const [showApplyForm, setShowApplyForm] = useState(false);
  const openApply = async () => {
    setApplyError("");
    if (!user) { navigate("/login", { state: { from: `/jobs/${id}` } }); return; }
    if (user.role !== "candidate") { setApplyError("Chỉ tài khoản Candidate mới có thể ứng tuyển."); return; }
    try { setCvs(listResults(await portalApi.cvs())); setShowApplyForm(true); } catch (err) { setApplyError((err as Error).message); }
  };
  const submitApplication = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedCv || !id) { setApplyError("Hãy chọn CV trước khi gửi hồ sơ."); return; }
    setApplyLoading(true); setApplyError("");
    try { await portalApi.apply({ job_id: Number(id), cv_id: Number(selectedCv), cover_letter: coverLetter }); setApplied(true); setShowApplyForm(false); }
    catch (err) { setApplyError((err as Error).message); }
    finally { setApplyLoading(false); }
  };
  if (!job && !apiError) {
    return <><Header /><main className="page"><div className="container"><div className="empty"><h3>Đang tải việc làm...</h3></div></div></main><Footer /></>;
  }
  return (
    <>
      <Header />
      <main className="page detail-page">
        <div className="container">
          <Link to="/jobs" className="back-link">
            ← Quay lại danh sách việc làm
          </Link>
          {apiError && <div className="error-notice">Không thể tải chi tiết việc làm từ Backend: {apiError}</div>}
          <div className="detail-grid">
            <article className="detail-main">
              <div className="detail-head">
                <div className="job-logo large">{job?.company.slice(0, 1)}</div>
                <div>
                  <h1>{job?.title}</h1>
                  <p className="company">
                    {job?.companyId ? <Link to={`/companies/${job.companyId}`}>{job?.company}</Link> : job?.company} · <span>{job?.location}</span>
                  </p>
                  <div className="meta">
                    <span>
                      <BriefcaseBusiness size={15} />
                      {job?.employmentType}
                    </span>
                    <span>
                      <Clock3 size={15} />
                      {job?.experience}
                    </span>
                  </div>
                </div>
              </div>
              <div className="content-block">
                <h2>Mô tả công việc</h2>
                <p className="preserved-text">{job?.description}</p>
                {job?.requirements && <><h2>Yêu cầu</h2><p className="preserved-text">{job.requirements}</p></>}
                {job?.benefits && <><h2>Quyền lợi</h2><p className="preserved-text">{job.benefits}</p></>}
              </div>
            </article>
            <aside className="apply-card">
              <h3>Sẵn sàng ứng tuyển?</h3>
              <p>Hãy để nhà tuyển dụng biết bạn quan tâm đến vị trí này.</p>
              {applied ? (
                <div className="success-message">
                  <CheckCircle2 size={21} /> Hồ sơ đã được gửi thành công.
                </div>
              ) : showApplyForm ? (
                <form className="apply-form" onSubmit={submitApplication}>
                  <label>Chọn CV<select value={selectedCv} onChange={(event) => setSelectedCv(event.target.value)} required><option value="">Chọn CV đã tải lên</option>{cvs.map((cv) => <option key={cv.id} value={cv.id}>{cv.original_filename}</option>)}</select></label>
                  {!cvs.length && <p className="form-hint">Bạn chưa có CV. Hãy tải CV trong bảng điều khiển Candidate.</p>}
                  <label>Thư giới thiệu<textarea value={coverLetter} onChange={(event) => setCoverLetter(event.target.value)} rows={4} placeholder="Giới thiệu ngắn về bạn (không bắt buộc)" /></label>
                  {applyError && <div className="error-notice">{applyError}</div>}
                  <button disabled={applyLoading || !cvs.length} className="button button-primary full">{applyLoading ? "Đang gửi..." : "Gửi hồ sơ"}</button>
                  <button type="button" className="button button-outline full" onClick={() => setShowApplyForm(false)}>Hủy</button>
                </form>
              ) : (
                <button
                  className="button button-primary full"
                  onClick={openApply}
                >
                  Ứng tuyển ngay <ArrowRight size={17} />
                </button>
              )}
              {applyError && !showApplyForm && <div className="error-notice">{applyError}</div>}
              <button className="button button-outline full">
                Lưu việc làm
              </button>
              <div className="job-facts">
                <div>
                  <span>Mức lương</span>
                    <b>{job?.salary ?? "Thỏa thuận"}</b>
                </div>
                <div>
                  <span>Đăng tuyển</span>
                    <b>{job?.postedAt}</b>
                </div>
                <div>
                  <span>Địa điểm</span>
                    <b>{job?.location}</b>
                </div>
              </div>
            </aside>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
export function Auth({ register = false }: { register?: boolean }) {
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]> | undefined>();
  const [toast, setToast] = useState<{ message: string; tone: "success" | "error" } | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signIn, refreshUser, error: authError } = useAuth();
  const [params] = useSearchParams();
  const [registrationRole, setRegistrationRole] = useState<"CANDIDATE" | "EMPLOYER">(params.get("role") === "EMPLOYER" ? "EMPLOYER" : "CANDIDATE");
  const employerRegistration = register && registrationRole === "EMPLOYER";
  const visibleError = error || authError || (typeof sessionStorage !== "undefined" && sessionStorage.getItem(SESSION_EXPIRED_NOTICE_KEY) ? "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại." : "");
  return (
    <>
      <Header />
      <main className="auth-page">
        <div className="auth-card">
          <div className="auth-mark">P</div>
          <h1>{register ? (employerRegistration ? "Đăng ký nhà tuyển dụng" : "Tạo tài khoản mới") : "Chào mừng trở lại"}</h1>
          <p>
            {register
              ? employerRegistration ? "Tạo tài khoản doanh nghiệp để đăng tin và tuyển dụng." : "Bắt đầu hành trình sự nghiệp cùng PTIT CareerHub."
              : "Đăng nhập để tiếp tục khám phá cơ hội của bạn."}
          </p>
          <form onSubmit={async (e) => {
            e.preventDefault(); setError(""); setFieldErrors(undefined); setLoading(true);
            try {
              const data = new FormData(e.currentTarget);
              if (register) {
                const result = await registerUser({
                  email: String(data.get("email") ?? ""),
                  password: String(data.get("password") ?? ""),
                  first_name: String(data.get("first_name") ?? ""),
                  last_name: String(data.get("last_name") ?? ""),
                  role: employerRegistration ? "EMPLOYER" : "CANDIDATE",
                });
                if (result.tokens) {
                  const user = await refreshUser();
                  if (!user) throw new Error("Không thể khôi phục phiên sau khi đăng ký.");
                  sessionStorage.removeItem(SESSION_EXPIRED_NOTICE_KEY);
                  navigate(user.role === "candidate" ? "/candidate" : user.role === "admin" ? "/admin" : "/employer");
                }
                else setError("Đăng ký thành công. Hãy đăng nhập để tiếp tục.");
              } else {
                const user = await signIn({ email: String(data.get("email")), password: String(data.get("password")) });
                sessionStorage.removeItem(SESSION_EXPIRED_NOTICE_KEY);
                navigate(user.role === "candidate" ? "/candidate" : user.role === "admin" ? "/admin" : "/employer");
              }
            } catch (err) { const message = formatApiError(err); setError(message); setToast({ message, tone: "error" }); setFieldErrors((err as { fields?: Record<string, string[]> }).fields); }
            finally { setLoading(false); }
          }}>
            {register && (
              <>
                <label>
                  Bạn tham gia với vai trò
                  <select value={registrationRole} onChange={(event) => setRegistrationRole(event.target.value as "CANDIDATE" | "EMPLOYER")}>
                    <option value="CANDIDATE">Ứng viên tìm việc</option>
                    <option value="EMPLOYER">Nhà tuyển dụng</option>
                  </select>
                  <span className="field-hint">Bạn có thể tạo hồ sơ ứng viên hoặc tài khoản doanh nghiệp để đăng tuyển.</span>
                </label>
                <label>
                  Tên
                  <input name="first_name" required placeholder="An" />
                </label>
                <label>
                  Họ
                  <input name="last_name" required placeholder="Nguyễn" />
                </label>
              </>
            )}
            <label>
              Email
              <input name="email" type="email" required placeholder="you@example.com" />
            </label>
            <label>
              Mật khẩu
              <input name="password" type="password" required placeholder="••••••••" />
            </label>
            {visibleError && <div className="error-notice">{visibleError}</div>}
            <FieldErrors fields={fieldErrors} />
            {!isApiConfigured && <div className="error-notice">API chưa được cấu hình. Hãy kiểm tra `VITE_API_BASE_URL`.</div>}
            <button disabled={loading || !isApiConfigured} className="button button-primary full">
              {loading ? "Đang xử lý..." : register ? (employerRegistration ? "Tạo tài khoản nhà tuyển dụng" : "Tạo tài khoản") : "Đăng nhập"}
            </button>
          </form>
          <p className="auth-switch">
            {register ? "Đã có tài khoản?" : "Chưa có tài khoản?"}{" "}
            <Link to={register ? "/login" : "/register"}>
              {register ? "Đăng nhập" : "Đăng ký miễn phí"}
            </Link>
          </p>
        </div>
      </main>
      {toast && <Toast message={toast.message} tone={toast.tone} onClose={() => setToast(null)} />}
      <Footer />
    </>
  );
}

function Metric({ label, value }: { label: string; value: unknown }) { return <div className="metric-card"><span>{label}</span><strong>{String(value ?? 0)}</strong></div>; }

const applicationStatusLabels: Record<string, string> = { SUBMITTED: "Đã nộp", REVIEWING: "Đang xem xét", SHORTLISTED: "Vào vòng chọn", REJECTED: "Từ chối", HIRED: "Đã tuyển", WITHDRAWN: "Đã rút" };
const jobStatusLabels: Record<string, string> = { DRAFT: "Bản nháp", PENDING: "Chờ duyệt", PUBLISHED: "Đang tuyển", REJECTED: "Cần chỉnh sửa", CLOSED: "Đã đóng" };
function statusLabel(status: unknown, labels = applicationStatusLabels) { return labels[String(status)] ?? String(status ?? "-"); }
function displayDate(value: unknown) { if (!value) return "-"; const date = new Date(String(value)); return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString("vi-VN", { dateStyle: "medium", timeStyle: "short" }); }

function CandidateWorkspace({ setMessage, setError }: { setMessage: (value: string) => void; setError: (value: string) => void }) {
  const [skills, setSkills] = useState<CandidateSkill[]>([]);
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [cvs, setCvs] = useState<CV[]>([]);
  const [skillId, setSkillId] = useState("");
  const [skillCatalog, setSkillCatalog] = useState<Skill[]>([]);
  const [experienceLoading, setExperienceLoading] = useState(false);
  const [cvLoading, setCvLoading] = useState(false);
  const reload = async () => {
    try {
      const [skillData, experienceData, cvData, catalogData] = await Promise.all([portalApi.skills(), portalApi.experiences(), portalApi.cvs(), portalApi.skillCatalog()]);
      setSkills(listResults(skillData)); setExperiences(listResults(experienceData)); setCvs(listResults(cvData));
      setSkillCatalog(listResults(catalogData));
    } catch (err) { setError((err as Error).message); }
  };
  useEffect(() => { reload(); }, []);
  const addExperience = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setExperienceLoading(true);
    const values = Object.fromEntries(new FormData(event.currentTarget).entries());
    try { await portalApi.createExperience({ company_name: String(values.company_name), job_title: String(values.job_title), description: String(values.description ?? ""), start_date: String(values.start_date), end_date: values.end_date ? String(values.end_date) : null, is_current: values.is_current === "on" }); setMessage("Đã thêm kinh nghiệm."); event.currentTarget.reset(); await reload(); }
    catch (err) { setError((err as Error).message); } finally { setExperienceLoading(false); }
  };
  const uploadCv = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]; if (!file) return;
    if (file.type !== "application/pdf" || file.size > 5 * 1024 * 1024) { setError("CV phải là PDF và không vượt quá 5 MB."); return; }
    setCvLoading(true); try { await portalApi.uploadCv(file); setMessage("Đã tải CV lên."); await reload(); } catch (err) { setError((err as Error).message); } finally { setCvLoading(false); event.target.value = ""; }
  };
  return <div className="workspace-grid">
    <section className="portal-card"><div className="section-heading"><div><div className="eyebrow muted">Hồ sơ năng lực</div><h2>Kỹ năng</h2></div></div><form className="inline-form" onSubmit={async (event) => { event.preventDefault(); if (!skillId) return; try { await portalApi.addSkill(Number(skillId)); setSkillId(""); setMessage("Đã thêm kỹ năng."); await reload(); } catch (err) { setError((err as Error).message); } }}><select value={skillId} onChange={(event) => setSkillId(event.target.value)} aria-label="Chọn kỹ năng"><option value="">Chọn kỹ năng</option>{skillCatalog.filter((skill) => !skills.some((item) => item.skill.id === skill.id)).map((skill) => <option value={skill.id} key={skill.id}>{skill.name}</option>)}</select><button disabled={!skillId} className="button button-primary">Thêm</button></form>{skills.length ? <div className="chip-list">{skills.map((item) => <span className="chip" key={item.id}>{item.skill.name}<button type="button" aria-label={`Xóa ${item.skill.name}`} onClick={() => portalApi.removeSkill(item.id).then(reload).catch((err: Error) => setError(err.message))}>×</button></span>)}</div> : <div className="empty compact"><p>Chưa có kỹ năng.</p></div>}</section>
    <section className="portal-card"><div className="section-heading"><div><div className="eyebrow muted">Kinh nghiệm</div><h2>Lịch sử làm việc</h2></div></div><form className="experience-form" onSubmit={addExperience}><div className="form-grid"><label>Công ty<input name="company_name" required /></label><label>Vị trí<input name="job_title" required /></label><label>Bắt đầu<input name="start_date" type="date" required /></label><label>Kết thúc<input name="end_date" type="date" /></label><label className="wide">Mô tả<textarea name="description" rows={2} /></label><label className="checkbox-label wide"><input name="is_current" type="checkbox" /> Đây là công việc hiện tại</label></div><button disabled={experienceLoading} className="button button-primary">{experienceLoading ? "Đang lưu..." : "Thêm kinh nghiệm"}</button></form>{experiences.map((item) => <div className="portal-row" key={item.id}><div><strong>{item.job_title}</strong><span>{item.company_name} · {item.start_date} - {item.is_current ? "Hiện tại" : item.end_date}</span></div><button className="button button-outline small" onClick={() => portalApi.removeExperience(item.id).then(() => { setMessage("Đã xóa kinh nghiệm."); return reload(); }).catch((err: Error) => setError(err.message))}>Xóa</button></div>)}</section>
    <section className="portal-card"><div className="section-heading"><div><div className="eyebrow muted">Tài liệu</div><h2>CV của tôi</h2></div><label className="button button-primary small">{cvLoading ? "Đang tải..." : "Tải CV PDF"}<input type="file" accept="application/pdf,.pdf" onChange={uploadCv} hidden disabled={cvLoading} /></label></div>{cvs.length ? cvs.map((cv) => <div className="portal-row" key={cv.id}><div><strong>{cv.original_filename}</strong><span>{Math.ceil(cv.file_size / 1024)} KB · {cv.status}</span></div><div className="row-actions"><button className="button button-outline small" onClick={async () => { try { const blob = await portalApi.downloadCv(cv.id); const url = URL.createObjectURL(blob); const anchor = document.createElement("a"); anchor.href = url; anchor.download = cv.original_filename; anchor.click(); URL.revokeObjectURL(url); } catch (err) { setError((err as Error).message); } }}>Tải xuống</button><button className="button button-outline small" onClick={() => portalApi.removeCv(cv.id).then(() => { setMessage("Đã xóa CV."); return reload(); }).catch((err: Error) => setError(err.message))}>Xóa</button></div></div>) : <div className="empty compact"><p>Chưa có CV. Tải lên PDF để ứng tuyển.</p></div>}</section>
  </div>;
}

function EmployerWorkspace({ setMessage, setError }: { setMessage: (value: string) => void; setError: (value: string) => void }) {
  const [company, setCompany] = useState<{ id: number; name: string; website?: string; address?: string; description?: string } | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [jobs, setJobs] = useState<Array<Record<string, unknown>>>([]);
  const [applications, setApplications] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(false);
  const [editingJob, setEditingJob] = useState<Record<string, unknown> | null>(null);
  const reload = async () => {
    try { const [companyData, jobData, appData, categoryData] = await Promise.all([portalApi.company().catch(() => null), portalApi.employerJobs(), portalApi.employerApplications(), portalApi.categories()]); setCompany(companyData); setJobs(listResults(jobData)); setApplications(listResults(appData)); setCategories(listResults(categoryData)); }
    catch (err) { setError((err as Error).message); }
  };
  useEffect(() => { reload(); }, []);
  const saveCompany = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); setLoading(true); const values = Object.fromEntries(new FormData(event.currentTarget).entries()) as Partial<Company>; try { const next = company ? await portalApi.updateCompany(values) : await portalApi.createCompany(values); setCompany(next); setMessage("Đã lưu thông tin công ty."); } catch (err) { setError((err as Error).message); } finally { setLoading(false); } };
  const jobPayloadFromForm = (form: HTMLFormElement) => {
    const values = Object.fromEntries(new FormData(form).entries());
    const text = (name: string) => String(values[name] ?? "");
    const optionalNumber = (name: string) => text(name).trim() ? Number(text(name)) : null;
    return {
      title: text("title"),
      category_id: Number(text("category_id")),
      location: text("location"),
      employment_type: text("employment_type"),
      deadline: text("deadline"),
      salary_min: optionalNumber("salary_min"),
      salary_max: optionalNumber("salary_max"),
      // Do not trim these fields: line breaks and intentional spacing are part
      // of the job description entered by the employer.
      description: text("description"),
      requirements: text("requirements"),
      benefits: text("benefits"),
    };
  };
  const createJob = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); setLoading(true); try { await portalApi.createJob(jobPayloadFromForm(event.currentTarget)); setMessage("Đã tạo tin tuyển dụng nháp."); event.currentTarget.reset(); await reload(); } catch (err) { setError((err as Error).message); } finally { setLoading(false); } };
  const editJob = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); if (!editingJob) return; setLoading(true); try { await portalApi.updateJob(Number(editingJob.id), jobPayloadFromForm(event.currentTarget)); setEditingJob(null); setMessage("Đã cập nhật tin tuyển dụng."); await reload(); } catch (err) { setError((err as Error).message); } finally { setLoading(false); } };
  const categoryOptions = categories.length ? categories : [];
  const categorySelect = (defaultValue?: string) => <select name="category_id" required defaultValue={defaultValue ?? ""} aria-label="Chọn lĩnh vực tuyển dụng"><option value="" disabled>Chọn lĩnh vực tuyển dụng</option>{categoryOptions.map((category) => <option value={category.id} key={category.id}>{category.name}</option>)}</select>;
  return <div className="workspace-grid"><section className="portal-card"><div className="section-heading"><div><div className="eyebrow muted">Doanh nghiệp</div><h2>{company ? "Thông tin công ty" : "Tạo công ty"}</h2></div></div><form className="experience-form" onSubmit={saveCompany}><div className="form-grid"><label>Tên công ty<input name="name" required defaultValue={company?.name ?? ""} /></label><label>Website<input name="website" type="url" defaultValue={company?.website ?? ""} /></label><label>Địa chỉ<input name="address" defaultValue={company?.address ?? ""} /></label><label className="wide">Mô tả<textarea name="description" rows={3} defaultValue={company?.description ?? ""} /></label></div><button disabled={loading} className="button button-primary">{loading ? "Đang lưu..." : company ? "Cập nhật công ty" : "Tạo công ty"}</button></form></section>{editingJob && <section className="portal-card"><div className="section-heading"><h2>Sửa tin tuyển dụng</h2><button type="button" className="button button-outline small" onClick={() => setEditingJob(null)}>Hủy</button></div><form className="experience-form" onSubmit={editJob}><div className="form-grid"><label>Tiêu đề<input name="title" required defaultValue={String(editingJob.title ?? "")} /></label><label>Lĩnh vực tuyển dụng{categorySelect(String((editingJob.category as Record<string, unknown> | undefined)?.id ?? ""))}</label><label>Địa điểm<input name="location" required defaultValue={String(editingJob.location ?? "")} /></label><label>Loại hình<select name="employment_type" defaultValue={String(editingJob.employment_type ?? "FULL_TIME")}><option value="FULL_TIME">Toàn thời gian</option><option value="PART_TIME">Bán thời gian</option><option value="CONTRACT">Hợp đồng</option><option value="INTERNSHIP">Thực tập</option></select></label><label>Hạn nộp<input name="deadline" type="date" required defaultValue={String(editingJob.deadline ?? "")} /></label><label>Lương tối thiểu<input name="salary_min" type="number" min="0" defaultValue={String(editingJob.salary_min ?? "")} /></label><label>Lương tối đa<input name="salary_max" type="number" min="0" defaultValue={String(editingJob.salary_max ?? "")} /></label><label className="wide">Mô tả<textarea name="description" rows={3} required defaultValue={String(editingJob.description ?? "")} /></label><label className="wide">Yêu cầu<textarea name="requirements" rows={3} defaultValue={String(editingJob.requirements ?? "")} /></label><label className="wide">Quyền lợi<textarea name="benefits" rows={3} defaultValue={String(editingJob.benefits ?? "")} /></label></div><button disabled={loading || !categories.length} className="button button-primary">Lưu tin</button>{!categories.length && <p className="form-hint">Chưa có lĩnh vực tuyển dụng đang hoạt động.</p>}</form></section>}<section className="portal-card"><div className="section-heading"><div><div className="eyebrow muted">Tin tuyển dụng</div><h2>Tạo tin nháp</h2></div></div><form onSubmit={createJob} className="experience-form"><div className="form-grid"><label>Tiêu đề<input name="title" required /></label><label>Lĩnh vực tuyển dụng{categorySelect()}</label><label>Địa điểm<input name="location" required /></label><label>Loại hình<select name="employment_type" defaultValue="FULL_TIME"><option value="FULL_TIME">Toàn thời gian</option><option value="PART_TIME">Bán thời gian</option><option value="CONTRACT">Hợp đồng</option><option value="INTERNSHIP">Thực tập</option></select></label><label>Hạn nộp<input name="deadline" type="date" required /></label><label>Lương tối thiểu<input name="salary_min" type="number" min="0" /></label><label>Lương tối đa<input name="salary_max" type="number" min="0" /></label><label className="wide">Mô tả<textarea name="description" rows={3} required /></label><label className="wide">Yêu cầu<textarea name="requirements" rows={2} /></label><label className="wide">Quyền lợi<textarea name="benefits" rows={2} /></label></div><button disabled={loading || !company || !categories.length} className="button button-primary">Tạo tin nháp</button>{!company && <p className="form-hint">Hãy tạo công ty trước khi đăng tin.</p>}{company && !categories.length && <p className="form-hint">Chưa có lĩnh vực tuyển dụng đang hoạt động.</p>}</form></section><section className="portal-card"><div className="section-heading"><div><div className="eyebrow muted">Quản lý tin tuyển dụng</div><h2>Danh sách tin của bạn</h2></div></div>{jobs.length ? <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Vị trí</th><th>Lĩnh vực</th><th>Trạng thái</th><th>Hạn nộp</th><th>Thao tác</th></tr></thead><tbody>{jobs.map((job) => <tr key={String(job.id)}><td><strong>{String(job.title)}</strong></td><td>{String((job.category as Record<string, unknown> | undefined)?.name ?? "-")}</td><td><span className={`status-badge status-${String(job.status).toLowerCase()}`}>{statusLabel(job.status, jobStatusLabels)}</span></td><td>{String(job.deadline ?? "-")}</td><td><div className="row-actions"><button disabled={!['DRAFT','REJECTED'].includes(String(job.status))} className="button button-outline small" onClick={() => setEditingJob(job)}>Sửa</button><button disabled={!['DRAFT','REJECTED','PUBLISHED'].includes(String(job.status))} className="button button-outline small" onClick={() => portalApi.closeJob(Number(job.id)).then(() => { setMessage("Đã đóng tin tuyển dụng."); return reload(); }).catch((err: Error) => setError(err.message))}>Đóng</button><button disabled={!['DRAFT','REJECTED'].includes(String(job.status))} className="button button-primary small" onClick={() => portalApi.submitJob(Number(job.id)).then(() => { setMessage("Đã gửi tin chờ duyệt."); return reload(); }).catch((err: Error) => setError(err.message))}>Gửi duyệt</button></div></td></tr>)}</tbody></table></div> : <div className="empty compact"><p>Chưa có tin tuyển dụng.</p></div>}</section><section className="portal-card"><div className="section-heading"><div><div className="eyebrow muted">Quản lý hồ sơ ứng tuyển</div><h2>Ứng viên theo từng tin</h2></div></div>{applications.length ? <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Ứng viên</th><th>Vị trí</th><th>Đã nộp lúc</th><th>Trạng thái</th><th></th></tr></thead><tbody>{applications.map((item) => { const candidate = item.candidate as Record<string, unknown> | undefined; const job = item.job as Record<string, unknown> | undefined; return <tr key={String(item.id)}><td><strong>{String(candidate?.full_name ?? "Ứng viên")}</strong><small>{String(candidate?.email ?? "")}</small></td><td>{String(job?.title ?? "-")}</td><td>{displayDate(item.applied_at)}</td><td><span className={`status-badge status-${String(item.status).toLowerCase()}`}>{statusLabel(item.status)}</span></td><td><Link className="button button-outline small" to={`/employer/applications/${item.id}`}>Xem chi tiết</Link></td></tr>; })}</tbody></table></div> : <div className="empty compact"><p>Chưa có hồ sơ ứng tuyển.</p></div>}</section></div>;
}

function AdminWorkspace({ setMessage, setError }: { setMessage: (value: string) => void; setError: (value: string) => void }) {
  const [jobs, setJobs] = useState<Array<Record<string, unknown>>>([]);
  const [users, setUsers] = useState<Array<Record<string, unknown>>>([]);
  const [categories, setCategories] = useState<Array<Record<string, unknown>>>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [rejectingId, setRejectingId] = useState<number | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [selectedJob, setSelectedJob] = useState<Record<string, unknown> | null>(null);
  const reload = () => portalApi.adminPendingJobs().then((data) => setJobs(listResults(data))).catch((err: Error) => setError(err.message));
  useEffect(() => { reload(); Promise.all([portalApi.adminUsers(), portalApi.adminCategories(), portalApi.adminSkills()]).then(([userData, categoryData, skillData]) => { setUsers(listResults(userData)); setCategories(listResults(categoryData)); setSkills(listResults(skillData)); }).catch((err: Error) => setError(err.message)); }, []);
  const reject = async () => { if (rejectingId === null || !rejectReason.trim()) return; try { await portalApi.rejectJob(rejectingId, rejectReason.trim()); setMessage("Đã từ chối tin."); setRejectingId(null); setRejectReason(""); setSelectedJob(null); await reload(); } catch (err) { setError((err as Error).message); } };
  return <div className="workspace-grid"><section className="portal-card admin-moderation-card"><div className="section-heading"><div><div className="eyebrow muted">Moderation</div><h2>Đơn đăng tuyển chờ duyệt</h2></div><span className="badge">{jobs.length} hồ sơ</span></div>{jobs.length ? <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Vị trí</th><th>Doanh nghiệp</th><th>Địa điểm</th><th>Hạn nộp</th><th>Thao tác</th></tr></thead><tbody>{jobs.map((job) => <tr key={String(job.id)}><td><strong>{String(job.title)}</strong><small>{String(job.category_name ?? "")}</small></td><td>{String(job.company_name ?? "-")}</td><td>{String(job.location ?? "-")}</td><td>{String(job.deadline ?? "-")}</td><td><div className="row-actions"><button className="button button-outline small" onClick={() => portalApi.adminPendingJob(Number(job.id)).then(setSelectedJob).catch((err: Error) => setError(err.message))}>Xem chi tiết</button><button className="button button-primary small" onClick={() => portalApi.approveJob(Number(job.id)).then(() => { setMessage("Đã duyệt tin."); setSelectedJob(null); return reload(); }).catch((err: Error) => setError(err.message))}>Duyệt</button><button className="button button-outline small" onClick={() => { setRejectingId(Number(job.id)); setRejectReason(""); }}>Từ chối</button></div>{rejectingId === Number(job.id) && <div className="inline-form"><input aria-label="Lý do từ chối" value={rejectReason} onChange={(event) => setRejectReason(event.target.value)} placeholder="Nhập lý do từ chối" /><button className="button button-primary small" onClick={reject}>Gửi</button><button className="button button-outline small" onClick={() => setRejectingId(null)}>Hủy</button></div>}</td></tr>)}</tbody></table></div> : <div className="empty compact"><p>Không có đơn đăng tuyển chờ duyệt.</p></div>}{selectedJob && <div className="admin-detail-panel"><div className="section-heading"><div><div className="eyebrow muted">Chi tiết đơn đăng tuyển</div><h2>{String(selectedJob.title)}</h2></div><button className="button button-outline small" onClick={() => setSelectedJob(null)}>Đóng</button></div><div className="detail-grid-cards"><div className="info-list"><div><span>Doanh nghiệp</span><strong>{String((selectedJob.company as Record<string, unknown> | undefined)?.name ?? selectedJob.company_name ?? "-")}</strong></div><div><span>Người đăng</span><strong>{String((selectedJob.employer as Record<string, unknown> | undefined)?.full_name ?? "-")}</strong><small>{String((selectedJob.employer as Record<string, unknown> | undefined)?.email ?? "")}</small></div><div><span>Lĩnh vực</span><strong>{String(selectedJob.category_name ?? "-")}</strong></div><div><span>Địa điểm</span><strong>{String(selectedJob.location ?? "-")}</strong></div><div><span>Hạn nộp</span><strong>{String(selectedJob.deadline ?? "-")}</strong></div></div><div className="content-block"><h3>Mô tả</h3><p className="preserved-text">{String(selectedJob.description ?? "-")}</p><h3>Yêu cầu</h3><p className="preserved-text">{String(selectedJob.requirements ?? "-")}</p><h3>Quyền lợi</h3><p className="preserved-text">{String(selectedJob.benefits ?? "-")}</p></div></div><div className="row-actions"><button className="button button-primary" onClick={() => portalApi.approveJob(Number(selectedJob.id)).then(() => { setMessage("Đã duyệt tin."); setSelectedJob(null); return reload(); }).catch((err: Error) => setError(err.message))}>Duyệt đơn này</button><button className="button button-outline" onClick={() => { setRejectingId(Number(selectedJob.id)); setRejectReason(""); }}>Từ chối đơn này</button></div></div>}</section><section className="portal-card"><div className="section-heading"><h2>Người dùng ({users.length})</h2></div>{users.slice(0, 10).map((item) => <div className="portal-row" key={String(item.id)}><div><strong>{String(item.email)}</strong><span>{String(item.role)} · {item.is_active ? "Đang hoạt động" : "Đã khóa"}</span></div></div>)}</section><section className="portal-card"><div className="section-heading"><h2>Danh mục ({categories.length})</h2></div>{categories.map((item) => <div className="portal-row" key={String(item.id)}><div><strong>{String(item.name)}</strong><span>{String(item.slug)}</span></div></div>)}</section><section className="portal-card"><div className="section-heading"><h2>Kỹ năng ({skills.length})</h2></div>{skills.slice(0, 20).map((skill) => <div className="portal-row" key={skill.id}><div><strong>{skill.name}</strong><span>{skill.is_active ? "Đang hoạt động" : "Đã tắt"}</span></div></div>)}</section></div>;
}
export function ApplicationDetailPage({ role }: { role: "candidate" | "employer" }) {
  const { id } = useParams();
  const [application, setApplication] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { if (!id) return; const load = role === "candidate" ? portalApi.application(Number(id)) : portalApi.employerApplication(Number(id)); load.then((data) => setApplication(data as Record<string, unknown>)).catch((err: Error) => setError(err.message)); }, [id, role]);
  const job = application?.job as Record<string, unknown> | undefined;
  const candidate = application?.candidate as Record<string, unknown> | undefined;
  const cv = application?.cv as Record<string, unknown> | undefined;
  const history = Array.isArray(application?.status_history) ? application.status_history as Array<Record<string, unknown>> : [];
  return <><Header /><main className="page"><div className="container"><Link to={`/${role}`} className="back-link">← Quay lại bảng điều khiển</Link>{error && <div className="error-notice">{error}</div>}{!application && !error ? <div className="empty"><h3>Đang tải hồ sơ...</h3></div> : application ? <article className="application-detail"><div className="application-detail-header"><div><div className="eyebrow muted">Hồ sơ ứng tuyển #{String(application.id)}</div><h1>{String(job?.title ?? `Hồ sơ #${application.id}`)}</h1><p className="company">{String((job?.company as Record<string, unknown> | undefined)?.name ?? job?.company_name ?? "Doanh nghiệp")}</p></div><span className={`status-badge status-${String(application.status).toLowerCase()}`}>{statusLabel(application.status)}</span></div><div className="detail-grid-cards"><section className="portal-card"><h2>Thông tin ứng viên</h2>{candidate ? <div className="info-list"><div><span>Họ tên</span><strong>{String(candidate.full_name ?? "Chưa cập nhật")}</strong></div><div><span>Email</span><strong>{String(candidate.email ?? "-")}</strong></div><div><span>Số điện thoại</span><strong>{String(candidate.phone ?? "-")}</strong></div><div><span>Khu vực</span><strong>{String(candidate.location ?? "-")}</strong></div><div className="info-wide"><span>Tóm tắt</span><p>{String(candidate.summary ?? "Chưa có tóm tắt.")}</p></div></div> : <p>Đây là hồ sơ của bạn.</p>}</section><section className="portal-card"><h2>Thông tin nộp hồ sơ</h2><div className="info-list"><div><span>Thời gian nộp</span><strong>{displayDate(application.applied_at)}</strong></div><div><span>Cập nhật gần nhất</span><strong>{displayDate(application.updated_at)}</strong></div><div><span>CV sử dụng</span><strong>{String(cv?.original_filename ?? "-")}</strong></div></div>{cv && role === "employer" && <button className="button button-outline small" onClick={async () => { try { const blob = await portalApi.employerDownloadCv(Number(application.id)); const url = URL.createObjectURL(blob); const anchor = document.createElement("a"); anchor.href = url; anchor.download = String(cv.original_filename ?? "cv.pdf"); anchor.click(); URL.revokeObjectURL(url); } catch (err) { setError((err as Error).message); } }}>Tải CV ứng viên</button>}</section></div><section className="portal-card"><h2>Thư giới thiệu</h2><p className="preserved-text">{String(application.cover_letter || "Không có thư giới thiệu.")}</p></section><section className="portal-card"><h2>Lịch sử xử lý</h2>{history.length ? <div className="timeline">{history.map((row) => <div className="timeline-item" key={String(row.id)}><span className="timeline-dot" /><div><strong>{statusLabel(row.new_status)}</strong><span>{row.previous_status ? `Từ ${statusLabel(row.previous_status)}` : "Hồ sơ được tạo"} · {displayDate(row.created_at)}</span>{Boolean(row.note) && <p>{String(row.note)}</p>}</div></div>)}</div> : <p>Chưa có lịch sử xử lý.</p>}</section></article> : null}</div></main><Footer /></>;
}

export function DashboardPage({ role }: { role: "candidate" | "employer" | "admin" }) {
  const { user, signOut } = useAuth();
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [applications, setApplications] = useState<Array<Record<string, unknown>>>([]);
  const [message, setMessage] = useState("");
  useEffect(() => {
    const load = role === "candidate" ? portalApi.candidateDashboard : role === "employer" ? portalApi.employerDashboard : portalApi.adminDashboard;
    load().then(setData).catch((err: Error) => setError(err.message));
    if (role === "candidate") {
      portalApi.profile().then(setProfile).catch(() => undefined);
      portalApi.applications().then((items) => setApplications(listResults(items) as Array<Record<string, unknown>>)).catch(() => undefined);
    }
    if (role === "employer") portalApi.employerApplications().then((items) => setApplications(listResults(items) as Array<Record<string, unknown>>)).catch(() => undefined);
  }, [role]);
  const updateProfile = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.currentTarget).entries());
    try { const next = await portalApi.updateProfile(values as Partial<Profile>); setProfile(next); setMessage("Đã cập nhật hồ sơ."); } catch (err) { setError((err as Error).message); }
  };
  return <><Header /><main className="page portal-page"><div className="container">
    <div className="portal-header"><div><div className="eyebrow muted">PTIT CareerHub</div><h1>Xin chào, {user?.first_name || user?.email}</h1><p>Không gian làm việc được đồng bộ trực tiếp với dữ liệu tuyển dụng.</p></div><button className="button button-outline" onClick={() => signOut().then(() => window.location.assign("/"))}>Đăng xuất</button></div>
    {error && <div className="error-notice">{error}</div>}{message && <div className="success-message">{message}</div>}
    <div className="metrics"><Metric label={role === "candidate" ? "Đơn ứng tuyển" : role === "employer" ? "Đơn nhận được" : "Tổng người dùng"} value={role === "admin" ? data?.user_count : data?.application_count} /><Metric label={role === "employer" ? "Tin tuyển dụng" : role === "admin" ? "Việc làm" : "Đã shortlist"} value={role === "employer" ? data?.job_count : role === "admin" ? data?.job_count : (data?.applications_by_status as Record<string, unknown> | undefined)?.SHORTLISTED} /><Metric label={role === "admin" ? "Chờ duyệt" : "Hoạt động gần đây"} value={role === "admin" ? data?.pending_job_count : data?.recent_applications?.length} /></div>
    {role === "candidate" && profile && <><form className="portal-card profile-form" onSubmit={updateProfile}><div className="section-heading"><div><div className="eyebrow muted">Hồ sơ cá nhân</div><h2>Thông tin của bạn</h2></div></div><div className="form-grid"><label>Họ và tên<input name="full_name" defaultValue={profile.full_name} /></label><label>Số điện thoại<input name="phone" defaultValue={profile.phone} /></label><label>Khu vực<input name="location" defaultValue={profile.location} /></label><label className="wide">Tóm tắt<textarea name="summary" defaultValue={profile.summary} rows={4} /></label></div><button className="button button-primary">Lưu thay đổi</button></form><CandidateWorkspace setMessage={setMessage} setError={setError} /></>}
    {role === "employer" && <EmployerWorkspace setMessage={setMessage} setError={setError} />}
    {role === "admin" && <AdminWorkspace setMessage={setMessage} setError={setError} />}
    {role !== "employer" && <section className="portal-card"><div className="section-heading"><div><div className="eyebrow muted">Theo dõi hồ sơ</div><h2>Đơn ứng tuyển gần đây</h2></div></div>{applications.length ? <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Vị trí</th><th>Trạng thái</th><th>Thời gian</th><th></th></tr></thead><tbody>{applications.map((item) => <tr key={String(item.id)}><td><Link to={`/candidate/applications/${item.id}`}><strong>{String((item.job as Record<string, unknown> | undefined)?.title ?? item.job_title ?? `Hồ sơ #${item.id}`)}</strong></Link><small>{String((item.job as Record<string, unknown> | undefined)?.company_name ?? "")}</small></td><td><span className={`status-badge status-${String(item.status).toLowerCase()}`}>{statusLabel(item.status)}</span></td><td>{displayDate(item.applied_at)}</td><td>{role === "candidate" && ["SUBMITTED", "REVIEWING", "SHORTLISTED"].includes(String(item.status)) && <button className="button button-outline small" onClick={() => portalApi.withdraw(Number(item.id)).then(() => { setMessage("Đã rút hồ sơ."); return portalApi.applications(); }).then((next) => setApplications(listResults(next) as Array<Record<string, unknown>>)).catch((err: Error) => setError(err.message))}>Rút hồ sơ</button>}</td></tr>)}</tbody></table></div> : <div className="empty compact"><h3>Chưa có đơn ứng tuyển</h3><p>Thông tin sẽ xuất hiện sau khi bạn nộp hồ sơ.</p></div>}</section>}
  </div></main><Footer /></>;
}
export function AccessDenied() { return <><Header /><main className="page"><div className="container"><div className="empty"><h1>Không có quyền truy cập</h1><p>Vai trò hiện tại không được phép mở trang này.</p><Link to="/" className="button button-primary">Về trang chủ</Link></div></div></main><Footer /></>; }
function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
export default App;
