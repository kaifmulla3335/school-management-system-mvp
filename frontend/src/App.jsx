import { useEffect, useState } from "react";
import api, { setAccessToken } from "./api";
import "./style.css";

function localDate() {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

const blank = {
  name: "", class_name: "", roll_number: "",
  date_of_birth: "", gender: "", guardian_name: "", guardian_phone: "", address: "",
  admission_date: localDate(), password: "",
};

function suggestedPassword(name) {
  const simpleName = name.toLowerCase().replace(/[^a-z0-9]/g, "");
  return `${simpleName.length >= 3 ? simpleName : "student"}@1234`;
}

function errorText(error) {
  const detail = error.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((item) => `${item.loc?.at(-1)}: ${item.msg}`).join("; ");
  if (error.code === "ECONNABORTED") return "The server took too long to respond.";
  if (!error.response) return "Cannot reach the backend at http://localhost:8000.";
  return "Request failed. Check the FastAPI logs.";
}

function Field({ label, name, value, onChange, type = "text", required = true, ...props }) {
  return <label className="field"><span>{label}</span><input name={name} value={value} type={type} onChange={onChange} required={required} {...props} /></label>;
}

function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [login, setLogin] = useState({ login_id: "", password: "" });
  const [form, setForm] = useState(blank);
  const [editingId, setEditingId] = useState(null);
  const [students, setStudents] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [adminView, setAdminView] = useState("dashboard");
  const [classFilter, setClassFilter] = useState("all");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [passwordEdited, setPasswordEdited] = useState(false);
  const [resetPassword, setResetPassword] = useState("");

  function logout(message = "") {
    setAccessToken(null);
    sessionStorage.removeItem("access_token");
    setUser(null);
    setDashboard(null);
    setStudents([]);
    setAdminView("dashboard");
    setClassFilter("all");
    setMobileMenuOpen(false);
    setNotice(message);
  }

  useEffect(() => {
    const token = sessionStorage.getItem("access_token");
    if (!token) { setChecking(false); return; }
    setAccessToken(token);
    api.get("/auth/me").then(({ data }) => setUser(data))
      .catch(() => logout("Session expired. Please log in again."))
      .finally(() => setChecking(false));
  }, []);

  useEffect(() => {
    if (!user) return;
    if (user.role === "admin") loadStudents();
    else api.get("/student/dashboard").then(({ data }) => setDashboard(data)).catch((err) => setError(errorText(err)));
  }, [user]);

  useEffect(() => {
    const id = api.interceptors.response.use((response) => response, (err) => {
      if (err.response?.status === 401 && user) logout("Session expired. Please log in again.");
      return Promise.reject(err);
    });
    return () => api.interceptors.response.eject(id);
  }, [user]);

  useEffect(() => {
    if (!mobileMenuOpen) return;
    const onKeyDown = (event) => { if (event.key === "Escape") setMobileMenuOpen(false); };
    const onResize = () => { if (window.innerWidth > 760) setMobileMenuOpen(false); };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("resize", onResize);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("resize", onResize);
    };
  }, [mobileMenuOpen]);

  async function run(task, success) {
    setBusy(true); setError(""); setNotice("");
    try { await task(); if (success) setNotice(typeof success === "function" ? success() : success); }
    catch (err) { setError(errorText(err)); }
    finally { setBusy(false); }
  }

  async function handleLogin(event) {
    event.preventDefault();
    await run(async () => {
      const body = new URLSearchParams();
      body.set("username", login.login_id.trim());
      body.set("password", login.password);
      const { data } = await api.post("/auth/login", body);
      setAccessToken(data.access_token);
      sessionStorage.setItem("access_token", data.access_token);
      try {
        const me = await api.get("/auth/me");
        setUser(me.data);
        setLogin({ login_id: "", password: "" });
      } catch (err) { logout(); throw err; }
    });
  }

  async function loadStudents() {
    try { const { data } = await api.get("/students"); setStudents(data); }
    catch (err) { setError(errorText(err)); }
  }

  function handleField(event) {
    const { name, value } = event.target;
    if (name === "password") setPasswordEdited(true);
    setForm((current) => ({
      ...current,
      [name]: value,
      ...(!editingId && name === "name" && !passwordEdited ? { password: suggestedPassword(value) } : {}),
    }));
  }

  async function saveStudent(event) {
    event.preventDefault();
    const createdPassword = form.password;
    let createdId = "";
    await run(async () => {
      const { data } = await api.post("/admin/student-accounts", { ...form, name: form.name.trim() });
      createdId = data.login_id;
      setForm(blank); setEditingId(null); await loadStudents();
      setShowPassword(false); setPasswordEdited(false);
      setClassFilter("all");
      setAdminView("dashboard");
    }, () => `Student added. Login ID: ${createdId}. Initial password: ${createdPassword}. Share it with the student manually.`);
  }

  function editStudent(student) {
    setEditingId(student.id);
    setForm({ ...blank, ...student });
    setResetPassword(suggestedPassword(student.name));
    setShowPassword(false);
    setError(""); setNotice("");
    setAdminView("add");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function deleteStudent(student) {
    if (!window.confirm(`Delete ${student.name} and their login account?`)) return;
    await run(async () => { await api.delete(`/students/${student.id}`); await loadStudents(); }, "Student deleted.");
  }

  async function resetStudentPassword() {
    if (!editingId || resetPassword.length < 8) { setError("Enter a new password of at least 8 characters."); return; }
    await run(async () => {
      await api.put(`/admin/students/${editingId}/password`, { password: resetPassword });
    }, `Password reset. New password: ${resetPassword}. Share it with the student manually.`);
  }

  if (checking) return <main className="login-shell"><div className="login-card">Checking session...</div></main>;

  if (!user) return <main className="login-shell"><div className="login-card">
    <div className="login-badge">SCHOOL PORTAL</div><h1>Welcome back</h1><p>Sign in with your school login ID.</p>
    <form className="login-form" onSubmit={handleLogin}>
      <Field label="Login ID" name="login_id" value={login.login_id} onChange={(e) => setLogin({ ...login, login_id: e.target.value })} autoComplete="username" />
      <Field label="Password" name="password" value={login.password} onChange={(e) => setLogin({ ...login, password: e.target.value })} type="password" autoComplete="current-password" />
      <button disabled={busy}>{busy ? "Signing in..." : "Sign in"}</button>
    </form>{error && <p className="error" role="alert">{error}</p>}{notice && <p className="success">{notice}</p>}
  </div></main>;

  const isAdmin = user.role === "admin";
  const visibleStudents = classFilter === "all" ? students : students.filter((student) => (student.class_name || student.course) === classFilter);
  const classCounts = Array.from({ length: 10 }, (_, index) => ({
    className: String(index + 1),
    count: students.filter((student) => (student.class_name || student.course) === String(index + 1)).length,
  }));
  const admissionYear = form.admission_date?.slice(0, 4) || String(new Date().getFullYear());
  const usedNumbers = students.map((student) => student.admission_number).filter((id) => new RegExp(`^${admissionYear}-\\d{3,}$`).test(id || "")).map((id) => Number(id.slice(5)));
  const exampleId = `${admissionYear}-${String(Math.max(0, ...usedNumbers) + 1).padStart(3, "0")}`;
  const nameKey = form.name.normalize("NFKD").replace(/[^a-zA-Z0-9]/g, "").toLowerCase() || "student";
  const birthYear = form.date_of_birth?.slice(0, 4) || "YYYY";
  const baseLogin = `${nameKey}${birthYear}`;
  const existingLogins = new Set(students.map((student) => student.login_id));
  let exampleLogin = baseLogin;
  for (let suffix = 2; existingLogins.has(exampleLogin); suffix += 1) exampleLogin = `${baseLogin}${suffix}`;
  return <div className="app-shell">
    {mobileMenuOpen && <button type="button" className="menu-backdrop" aria-label="Close menu" onClick={() => setMobileMenuOpen(false)} />}
    <aside id="school-sidebar" className={`sidebar ${mobileMenuOpen ? "sidebar-open" : ""}`} aria-label="Main navigation">
      <div className="brand"><span className="brand-icon">S</span><div><strong>School Portal</strong><small>Management system</small></div><button className="menu-close" type="button" aria-label="Close menu" onClick={() => setMobileMenuOpen(false)}>×</button></div>
      <div className="sidebar-label">MAIN MENU</div>
      {isAdmin ? <>
        <button className={`nav-item ${adminView === "dashboard" ? "active" : ""}`} aria-current={adminView === "dashboard" ? "page" : undefined} type="button" onClick={() => { setAdminView("dashboard"); setMobileMenuOpen(false); }}><span>▦</span> Dashboard</button>
        <button className={`nav-item ${adminView === "add" ? "active" : ""}`} aria-current={adminView === "add" ? "page" : undefined} type="button" onClick={() => { setEditingId(null); setForm(blank); setShowPassword(false); setPasswordEdited(false); setAdminView("add"); setMobileMenuOpen(false); }}><span>＋</span> Add Student</button>
      </> : <button className="nav-item active" type="button"><span>▦</span> My Dashboard</button>}
      <div className="sidebar-bottom"><div className="sidebar-user"><span className="avatar">{(user.username || user.email || "U")[0].toUpperCase()}</span><div><strong>{user.username || user.email}</strong><small>{isAdmin ? "Administrator" : "Student"}</small></div></div><button className="logout" onClick={() => logout()}>Log out</button></div>
    </aside>

    <main className="workspace">
      <div className="mobile-topbar"><button type="button" className="menu-toggle" aria-label="Open menu" aria-controls="school-sidebar" aria-expanded={mobileMenuOpen} onClick={() => setMobileMenuOpen(true)}><span></span><span></span><span></span></button><strong>School Portal</strong></div>
      <header className="page-header"><div><p className="eyebrow">{isAdmin ? "ADMINISTRATION" : "STUDENT PORTAL"}</p><h1>{isAdmin ? adminView === "dashboard" ? "School Dashboard" : editingId ? "Student Details" : "Add Student" : "My Dashboard"}</h1><p>{isAdmin ? adminView === "dashboard" ? "Students organized by class, from 1 to 10." : editingId ? "Student details are read-only. You can reset the password below." : "Create a student record and login in one step." : "Your school details, all in one place."}</p></div><span className="role-pill">{isAdmin ? "Admin" : "Student"}</span></header>
      {error && <p className="error" role="alert">{error}</p>}{notice && <p className="success" role="status">{notice}</p>}

      {isAdmin ? <>
        {adminView === "add" && (
        <section className="content-card"><div className="section-heading"><div><h2>Student information</h2><p>{editingId ? "Record created by the school" : "For classes 1 to 10. Fields marked * are required."}</p></div></div>
          {editingId ? <>
            <div className="profile-grid">{[
              ["Full name", form.name], ["Admission number", form.admission_number], ["Login ID", form.login_id],
              ["Class", form.class_name], ["Roll number", form.roll_number],
              ["Date of birth", form.date_of_birth], ["Gender", form.gender],
              ["Guardian", form.guardian_name], ["Guardian phone", form.guardian_phone],
              ["Address", form.address], ["Admission date", form.admission_date],
            ].map(([label, value]) => <div className="profile-item" key={label}><span>{label}</span><strong>{value || "—"}</strong></div>)}</div>
            <div className="reset-panel"><h3>Student forgot the password?</h3><p>The existing password cannot be viewed. Set a new one and tell the student.</p><div className="reset-row"><input aria-label="New student password" value={resetPassword} onChange={(event) => setResetPassword(event.target.value)} type={showPassword ? "text" : "password"} minLength={8} /><button className="secondary" type="button" onClick={() => setShowPassword((current) => !current)}>{showPassword ? "Hide" : "Show"}</button><button type="button" disabled={busy} onClick={resetStudentPassword}>Reset password</button></div></div>
            <button className="secondary" type="button" onClick={() => { setEditingId(null); setAdminView("dashboard"); }}>Back to dashboard</button>
          </> :
          <form className="student-form" onSubmit={saveStudent}>
            <h3>Basic details</h3><div className="form-grid">
              <Field label="Full name *" name="name" value={form.name} onChange={handleField} maxLength={100} />
              <label className="field"><span>Class *</span><select name="class_name" value={form.class_name} onChange={handleField} required><option value="">Select class</option>{Array.from({ length: 10 }, (_, i) => <option key={i + 1} value={String(i + 1)}>Class {i + 1}</option>)}</select></label>
              <Field label="Roll number *" name="roll_number" value={form.roll_number} onChange={handleField} maxLength={30} />
              <Field label="Date of birth *" name="date_of_birth" value={form.date_of_birth} onChange={handleField} type="date" />
              <label className="field"><span>Gender *</span><select name="gender" value={form.gender} onChange={handleField} required><option value="">Select gender</option><option>Male</option><option>Female</option><option>Other</option></select></label>
            </div>
            <h3>Parent or guardian</h3><div className="form-grid">
              <Field label="Guardian name *" name="guardian_name" value={form.guardian_name} onChange={handleField} maxLength={100} />
              <Field label="Guardian phone *" name="guardian_phone" value={form.guardian_phone} onChange={handleField} type="tel" maxLength={20} />
              <label className="field wide"><span>Address *</span><textarea name="address" value={form.address} onChange={handleField} maxLength={500} rows={3} required /></label>
            </div>
            <h3>Admission and login</h3><div className="form-grid">
              <Field label="Admission date *" name="admission_date" value={form.admission_date} onChange={handleField} type="date" />
              <div className="field"><span>Admission number</span><strong className="id-preview">Example: {exampleId}</strong><small>Assigned automatically from the admission year.</small></div>
              <div className="field"><span>Student login ID</span><strong className="id-preview">Example: {exampleLogin}</strong><small>Based on the student's name and birth year; assigned when saved.</small></div>
              <div className="password-control"><Field label="Initial password *" name="password" value={form.password} onChange={handleField} type={showPassword ? "text" : "password"} minLength={8} maxLength={128} autoComplete="new-password" /><button type="button" onClick={() => setShowPassword((current) => !current)}>{showPassword ? "Hide" : "Show"}</button></div>
            </div>
            <p className="form-note">A simple password is suggested from the student's name. You can change it before saving. Share it personally; only its hash is stored.</p>
            <div className="form-actions"><button disabled={busy}>{busy ? "Saving..." : "Add student"}</button></div>
          </form>
          }
        </section>
        )}

        {adminView === "dashboard" && <>
        <section className="dashboard-overview">
          <div className="overview-card"><span>Total students</span><strong>{students.length}</strong><small>Classes 1 to 10</small></div>
          <div className="overview-card"><span>Classes with students</span><strong>{classCounts.filter((item) => item.count > 0).length}</strong><small>Currently enrolled</small></div>
        </section>
        <section className="content-card"><div className="section-heading"><div><h2>Students by class</h2><p>Select a class to see its students below.</p></div></div>
          <div className="class-grid">{classCounts.map((item) => <button type="button" key={item.className} className={`class-card ${classFilter === item.className ? "selected" : ""}`} onClick={() => setClassFilter(item.className)}><span>Class {item.className}</span><strong>{item.count}</strong><small>{item.count === 1 ? "student" : "students"}</small></button>)}</div>
        </section>
        <section className="content-card roster"><div className="section-heading roster-heading"><div><h2>{classFilter === "all" ? "All students" : `Class ${classFilter} students`}</h2><p>{visibleStudents.length} student{visibleStudents.length === 1 ? "" : "s"} shown</p></div><button className="filter-reset" type="button" onClick={() => setClassFilter("all")}>Show all classes</button></div>
          <div className="table-wrap"><table><thead><tr><th>Student</th><th>Admission no.</th><th>Class</th><th>Roll</th><th>Login ID</th><th>Actions</th></tr></thead><tbody>
            {visibleStudents.map((student) => <tr key={student.id}><td><strong>{student.name}</strong></td><td>{student.admission_number || "—"}</td><td>{student.class_name || student.course}</td><td>{student.roll_number || "—"}</td><td>{student.login_id || "—"}</td><td><button className="table-action" onClick={() => editStudent(student)}>View / Password</button><button className="table-action delete" onClick={() => deleteStudent(student)}>Delete</button></td></tr>)}
          </tbody></table>{visibleStudents.length === 0 && <p className="empty">{students.length === 0 ? "No students yet. Choose Add Student from the sidebar." : "No students in this class yet."}</p>}</div>
        </section>
        </>}
      </> : dashboard && <>
        <section className="content-card profile-card"><div className="section-heading"><div><h2>My profile</h2><p>Details provided by your school administrator</p></div></div>
          <div className="profile-grid">{[
            ["Full name", dashboard.profile.name], ["Admission number", dashboard.profile.admission_number],
            ["Class", dashboard.profile.class_name],
            ["Roll number", dashboard.profile.roll_number], ["Date of birth", dashboard.profile.date_of_birth],
            ["Gender", dashboard.profile.gender], ["Guardian", dashboard.profile.guardian_name],
            ["Guardian phone", dashboard.profile.guardian_phone],
            ["Admission date", dashboard.profile.admission_date], ["Address", dashboard.profile.address],
          ].map(([label, value]) => <div className="profile-item" key={label}><span>{label}</span><strong>{value || "—"}</strong></div>)}</div>
        </section><div className="future-note">Attendance, marks, fees and homework will appear here as the school adds those sections.</div>
      </>}
    </main>
  </div>;
}

export default App;
