import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = (import.meta.env.VITE_API_URL || "https://api.qorgo.services/api/v1").replace(/\/$/, "");
const TOKEN_KEY = "qorgo.operator.access";

function Icon({ name, size = 18 }) {
  const paths = {
    shield: <><path d="M12 3 20 6v5c0 5-3.4 8.2-8 10-4.6-1.8-8-5-8-10V6l8-3Z"/><path d="m8.5 12 2.2 2.2 4.8-5"/></>,
    bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/></>,
    search: <><circle cx="10.8" cy="10.8" r="6.3"/><path d="m16 16 4.5 4.5"/></>,
    refresh: <><path d="M20 7v5h-5M4 17v-5h5"/><path d="M5.7 9A7 7 0 0 1 18 6l2 2M4 16l2 2a7 7 0 0 0 12.3-3"/></>,
    pin: <><path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2"/></>,
    phone: <path d="M7 3H5a2 2 0 0 0-2 2c0 8.8 7.2 16 16 16a2 2 0 0 0 2-2v-2l-5-2-2 2a14 14 0 0 1-6-6l2-2-2-5Z"/>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    logout: <><path d="M10 17l5-5-5-5M15 12H3"/><path d="M12 3h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
    close: <path d="m6 6 12 12M18 6 6 18"/>,
    arrow: <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
    battery: <><rect x="3" y="7" width="17" height="10" rx="2"/><path d="M23 10v4"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

async function request(path, { token, method = "GET", body } = {}) {
  let response;
  try {
    response = await fetch(`${API}/${path}`, {
    method,
    headers: { ...(body ? { "Content-Type": "application/json" } : {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    ...(body ? { body: JSON.stringify(body) } : {}),
    });
  } catch {
    throw new Error("Не удалось связаться с сервером QORGO. Проверьте подключение и повторите.");
  }
  const data = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const message = data?.detail || data?.error || data?.phone_number?.[0] || data?.password?.[0];
    if (response.status === 401) throw new Error("Сессия закончилась. Войдите снова.");
    if (response.status === 403) throw new Error("У этой учётной записи нет доступа оператора.");
    throw new Error(message || "Не удалось выполнить запрос. Попробуйте ещё раз.");
  }
  return data;
}

function formatAge(value) {
  const mins = Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 60000));
  if (mins < 1) return "Только что";
  if (mins < 60) return `${mins} мин назад`;
  const hours = Math.floor(mins / 60);
  return `${hours} ч ${mins % 60} мин назад`;
}

function initials(name = "") {
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase() || "Q";
}

function Login({ onLogin }) {
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit(event) {
    event.preventDefault();
    setError(""); setBusy(true);
    try { await onLogin(phone, password); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return <main className="login-page">
    <section className="login-art">
      <div className="brand brand-light"><span className="brand-mark"><Icon name="shield" size={23}/></span><span>QORGO</span><small>OPERATOR</small></div>
      <div className="art-copy"><span className="eyebrow"><i/> ЦЕНТР КООРДИНАЦИИ</span><h1>Помощь начинается<br/>с точного действия.</h1><p>Рабочее пространство операторов QORGO для быстрой и внимательной обработки сигналов SOS.</p></div>
      <div className="art-foot"><span>QORGO RESPONSE SYSTEM</span><span>24 / 7</span></div>
      <div className="art-grid" aria-hidden="true"/>
    </section>
    <section className="login-side"><div className="login-box">
      <div className="mobile-brand brand"><span className="brand-mark"><Icon name="shield" size={22}/></span><span>QORGO</span><small>OPERATOR</small></div>
      <span className="eyebrow muted-eyebrow">РАБОЧИЙ ПОРТАЛ</span><h2>Вход оператора</h2><p className="login-lead">Введите данные, выданные администратором.</p>
      <form onSubmit={submit}>
        <label htmlFor="phone">Рабочий номер</label><div className="input-wrap"><Icon name="phone"/><input id="phone" type="tel" autoComplete="username" placeholder="+996 700 000 000" value={phone} onChange={(e) => setPhone(e.target.value)} required/></div>
        <label htmlFor="password">Пароль</label><input id="password" type="password" autoComplete="current-password" placeholder="Введите пароль" value={password} onChange={(e) => setPassword(e.target.value)} required/>
        {error && <div className="form-error" role="alert">{error}</div>}
        <button className="primary-btn login-btn" disabled={busy}>{busy ? <><span className="spinner"/>Проверяем доступ…</> : <>Войти в диспетчерскую <Icon name="arrow"/></>}</button>
      </form>
      <div className="login-note"><Icon name="shield" size={16}/><span>Доступ защищён. Вход разрешён только сотрудникам QORGO.</span></div>
      <div className="login-copy">© {new Date().getFullYear()} QORGO · Безопасность и поддержка</div>
    </div></section>
  </main>;
}

function IncidentCard({ incident, active, onClick }) {
  const user = incident.user || {};
  const name = [user.first_name, user.last_name].filter(Boolean).join(" ") || "Пользователь QORGO";
  const assigned = incident.assigned_operator_name;
  return <button className={`incident-card ${active ? "selected" : ""}`} onClick={onClick}>
    <span className="incident-card-top"><span className="alert-label"><i/> SOS · {formatAge(incident.started_at)}</span><span className={`status-chip ${assigned ? "assigned" : "waiting"}`}>{assigned ? "В работе" : "Ожидает"}</span></span>
    <span className="incident-person"><span className="avatar">{initials(name)}</span><span className="person-copy"><strong>{name}</strong><small>{user.phone_number || "Номер не указан"}</small></span></span>
    <span className="incident-address"><Icon name="pin" size={16}/><span>{incident.address || `${Number(incident.latitude).toFixed(5)}, ${Number(incident.longitude).toFixed(5)}`}</span></span>
    <span className="incident-card-bottom"><span><Icon name="battery" size={15}/> {Math.round(incident.battery_level || 0)}%</span><span className="card-open">Открыть <Icon name="arrow" size={15}/></span></span>
  </button>;
}

function DetailPanel({ incident, busy, onTake, onClose }) {
  const [showClose, setShowClose] = useState(false);
  const [note, setNote] = useState("");
  const user = incident?.user || {};
  const name = [user.first_name, user.last_name].filter(Boolean).join(" ") || "Пользователь QORGO";
  useEffect(() => { setShowClose(false); setNote(""); }, [incident?.id]);
  if (!incident) return <aside className="detail-panel detail-empty"><span className="detail-empty-icon"><Icon name="bell" size={24}/></span><strong>Выберите сигнал</strong><p>Подробности инцидента появятся здесь.</p></aside>;
  const latitude = Number(incident.latitude);
  const longitude = Number(incident.longitude);
  const mapEmbed = `https://www.openstreetmap.org/export/embed.html?bbox=${longitude - 0.008}%2C${latitude - 0.005}%2C${longitude + 0.008}%2C${latitude + 0.005}&layer=mapnik&marker=${latitude}%2C${longitude}`;
  const mapUrl = `https://www.openstreetmap.org/?mlat=${incident.latitude}&mlon=${incident.longitude}#map=16/${incident.latitude}/${incident.longitude}`;
  return <aside className="detail-panel">
    <div className="detail-heading"><div><span className="eyebrow muted-eyebrow">КАРТОЧКА ИНЦИДЕНТА</span><h2>Сигнал SOS</h2></div><span className="live-tag"><i/> LIVE</span></div>
    <div className="detail-map"><iframe title={`Карта места сигнала SOS: ${name}`} src={mapEmbed} loading="lazy"/><a href={mapUrl} target="_blank" rel="noreferrer">Открыть карту <Icon name="arrow" size={14}/></a></div>
    <div className="detail-person"><span className="avatar avatar-large">{initials(name)}</span><div><strong>{name}</strong><span>{user.phone_number || "Телефон не указан"}</span></div></div>
    {user.phone_number ? <a className="phone-action" href={`tel:${user.phone_number}`}><Icon name="phone" size={16}/> Позвонить пользователю</a> : <span className="phone-action disabled"><Icon name="phone" size={16}/> Телефон не указан</span>}
    <div className="detail-stats"><div><span>ПОЛУЧЕН</span><strong><Icon name="clock" size={15}/>{formatAge(incident.started_at)}</strong></div><div><span>ЗАРЯД УСТРОЙСТВА</span><strong><Icon name="battery" size={15}/>{Math.round(incident.battery_level || 0)}%</strong></div></div>
    {incident.assigned_operator_name && <div className="assigned-note"><span className="assigned-dot"/> Принял: {incident.assigned_operator_name}</div>}
    {showClose ? <div className="close-form"><label htmlFor="note">Комментарий к завершению</label><textarea id="note" maxLength={1000} placeholder="Кратко опишите результат помощи" value={note} onChange={(e) => setNote(e.target.value)}/><div className="close-actions"><button className="quiet-btn" onClick={() => setShowClose(false)}>Назад</button><button className="primary-btn" disabled={busy} onClick={() => onClose("resolved", note)}>Помощь оказана <Icon name="check"/></button></div><button className="false-alarm" disabled={busy} onClick={() => onClose("false_alarm", note)}>Отметить как ложный вызов</button></div> : <div className="detail-actions">{incident.assigned_operator_name ? <button className="primary-btn" disabled={busy} onClick={() => setShowClose(true)}>Завершить инцидент <Icon name="check"/></button> : <button className="primary-btn" disabled={busy} onClick={onTake}>Принять в работу <Icon name="arrow"/></button>}</div>}
    <p className="privacy-hint"><Icon name="shield" size={14}/> Данные доступны только авторизованным операторам.</p>
  </aside>;
}

function Dashboard({ token, onLogout }) {
  const [incidents, setIncidents] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [updatedAt, setUpdatedAt] = useState(null);
  const load = useCallback(async (quiet = false) => {
    if (!quiet) setBusy(true);
    try {
      const data = await request("operator/incidents/", { token });
      const rows = data?.results || data || [];
      setIncidents(rows); setSelectedId((current) => rows.some((row) => row.id === current) ? current : rows[0]?.id || null);
      setUpdatedAt(new Date()); setError("");
    } catch (err) { setError(err.message); if (/сессия закончилась/i.test(err.message)) onLogout(); }
    finally { if (!quiet) setBusy(false); }
  }, [token, onLogout]);
  useEffect(() => { load(); const timer = window.setInterval(() => load(true), 10000); return () => window.clearInterval(timer); }, [load]);
  const filtered = useMemo(() => incidents.filter((incident) => {
    const user = incident.user || {};
    const text = [user.first_name, user.last_name, user.phone_number, incident.address].join(" ").toLowerCase();
    return text.includes(query.trim().toLowerCase());
  }), [incidents, query]);
  const selected = incidents.find((item) => item.id === selectedId) || null;
  async function act(path, body) {
    if (!selected) return;
    setBusy(true); setError("");
    try { await request(`operator/incidents/${selected.id}/${path}/`, { token, method: "POST", body }); await load(true); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  const name = selected ? [selected.user?.first_name, selected.user?.last_name].filter(Boolean).join(" ") || "Пользователь QORGO" : "";
  return <div className="app-shell">
    <aside className="sidebar"><a className="brand brand-light" href="#home"><span className="brand-mark"><Icon name="shield" size={22}/></span><span>QORGO</span><small>OPERATOR</small></a>
      <div className="side-section-label">РАБОЧЕЕ ПРОСТРАНСТВО</div><button className="side-link active"><Icon name="bell"/>Активные сигналы<span className="side-count">{incidents.length}</span></button>
      <div className="sidebar-bottom"><div className="shift-card"><span className="shift-icon"><Icon name="shield" size={17}/></span><div><strong>Смена активна</strong><small>Подключение защищено</small></div><i/></div><div className="operator-profile"><span className="profile-avatar">О</span><div><strong>Оператор QORGO</strong><small>Рабочая учётная запись</small></div><button className="logout-btn" onClick={onLogout} title="Выйти"><Icon name="logout"/></button></div></div>
    </aside>
    <main className="workspace">
      <header className="topbar"><div className="breadcrumb">Диспетчерская <span>/</span> <strong>Активные SOS</strong></div><div className="topbar-right"><span className="api-status"><i/> Система онлайн</span><span className="top-divider"/><span className="top-time"><Icon name="clock" size={16}/>{updatedAt ? `Обновлено ${updatedAt.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })}` : "Подключение…"}</span><button className={`icon-btn ${busy ? "spinning" : ""}`} onClick={() => load()} disabled={busy} aria-label="Обновить очередь"><Icon name="refresh"/></button><button className="mobile-logout" onClick={onLogout} aria-label="Выйти"><Icon name="logout"/></button></div></header>
      <div className="workspace-inner"><section className="page-heading"><div><span className="eyebrow muted-eyebrow">ЦЕНТР КООРДИНАЦИИ QORGO</span><h1>Активные сигналы</h1><p>Следите за очередью и координируйте помощь.</p></div><div className="total-card"><span className="total-icon"><Icon name="bell"/></span><div><strong>{incidents.length}</strong><span>активных SOS</span></div></div></section>
        {error && <div className="banner-error" role="alert"><span>{error}</span><button onClick={() => setError("")} aria-label="Закрыть"><Icon name="close" size={16}/></button></div>}
        <section className="queue-toolbar"><div className="queue-tabs"><span className="tab-active">Все сигналы <b>{incidents.length}</b></span><span className="queue-live"><i/> Автообновление · 10 сек</span></div><label className="search-box"><Icon name="search"/><input aria-label="Поиск по очереди" placeholder="Поиск по имени, номеру или адресу" value={query} onChange={(e) => setQuery(e.target.value)}/><kbd>⌘ K</kbd></label></section>
        <section className="queue-layout"><div className="queue-list"><div className="list-heading"><strong>Очередь <span>{filtered.length}</span></strong><span>Сначала новые</span></div>
          {filtered.length ? filtered.map((incident) => <IncidentCard key={incident.id} incident={incident} active={incident.id === selectedId} onClick={() => setSelectedId(incident.id)}/>) : <div className="empty-state"><span className="empty-icon"><Icon name="check" size={24}/></span><strong>{query ? "Ничего не найдено" : "Очередь спокойна"}</strong><p>{query ? "Измените запрос и попробуйте снова." : "Новых сигналов SOS сейчас нет. Мы обновляем очередь автоматически."}</p>{!query && <button className="quiet-btn" onClick={() => load()}><Icon name="refresh" size={16}/> Обновить очередь</button>}</div>}
        </div><DetailPanel incident={selected} busy={busy} onTake={() => act("take")} onClose={(status, note) => act("close", { status, note })}/></section>
        <footer className="workspace-footer"><span>QORGO RESPONSE SYSTEM</span><span><Icon name="shield" size={13}/> Защищённый канал связи</span></footer>
      </div>
    </main>
  </div>;
}

function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem(TOKEN_KEY));
  const logout = useCallback(() => { sessionStorage.removeItem(TOKEN_KEY); setToken(null); }, []);
  async function login(phone, password) {
    const data = await request("auth/login/", { method: "POST", body: { phone_number: phone.trim(), password } });
    if (!data?.access) throw new Error("Сервер не выдал токен доступа.");
    sessionStorage.setItem(TOKEN_KEY, data.access); setToken(data.access);
  }
  return token ? <Dashboard token={token} onLogout={logout}/> : <Login onLogin={login}/>;
}

createRoot(document.getElementById("root")).render(<React.StrictMode><App/></React.StrictMode>);
