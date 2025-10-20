import React, { useEffect, useMemo, useState } from 'react';
import './Dashboard.css';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import { BASE as ENV_BASE, getAuthHeaders, getAccess, logout } from '../../api/auth';

const API_BASE = (ENV_BASE || '/api').replace(/\/$/, '');
const u = (p) => `${API_BASE}${p}`;

function parseJwtUserId(token) {
  try {
    const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const json = atob(payload);
    const data = JSON.parse(decodeURIComponent(escape(json)));
    return data.user_id ?? data.sub ?? null;
  } catch { return null; }
}
function fmtHHmm(iso) { return iso ? new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'; }
const toDate = (iso) => (iso ? new Date(iso) : null);
const colorForCheckIn  = (plannedIso, realIso) => (!realIso ? '#111' : (toDate(realIso) <= toDate(plannedIso) ? 'green' : 'red'));
const colorForCheckOut = (plannedIso, realIso) => (!realIso ? '#111' : (toDate(realIso) >= toDate(plannedIso) ? 'green' : 'red'));
function isToday(iso) {
  if (!iso) return false;
  const d = new Date(iso), t = new Date();
  return d.getFullYear()===t.getFullYear() && d.getMonth()===t.getMonth() && d.getDate()===t.getDate();
}
function isoForToday(hhmm) {
  const [h,m] = hhmm.split(':').map(Number);
  const d = new Date(); d.setHours(h, m, 0, 0);
  return d.toISOString();
}
function todayRangeUTC() {
  const now = new Date();
  const y = now.getUTCFullYear(), m = now.getUTCMonth(), d = now.getUTCDate();
  return {
    from: new Date(Date.UTC(y, m, d, 0, 0, 0)).toISOString(),
    to:   new Date(Date.UTC(y, m, d, 23, 59, 59)).toISOString(),
  };
}
function normalizeShiftsResponse(data) {
  let arr = [];
  if (!data) return arr;
  if (Array.isArray(data)) arr = data;
  else if (Array.isArray(data.shifts)) arr = data.shifts;
  else if (typeof data === 'object') arr = Object.values(data);
  return arr.filter(s => s && s.id).sort((a,b)=> new Date(a.start_time)-new Date(b.start_time));
}

const Dashboard = () => {
  const access = useMemo(() => getAccess(), []);
  const userId = useMemo(() => parseJwtUserId(access), [access]);
  if (!access || !userId) { logout(); return null; }

  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');
  const [shifts, setShifts]   = useState([]);

  const totalSlots  = Math.max(1, shifts.length * 2);
  const filledSlots = shifts.reduce((acc, s) => acc + (s.real_start_time ? 1 : 0) + (s.real_end_time ? 1 : 0), 0);
  const percentage  = Math.round((filledSlots / totalSlots) * 100);
  const headers     = () => getAuthHeaders();

  useEffect(() => { fetchUserShifts(); }, []);

  async function fetchUserShifts() {
    setError(''); setLoading(true);
    try {
      const { from, to } = todayRangeUTC();
      const url = `${API_BASE}/users/${userId}/shifts/list?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`;
      const res = await fetch(url, { method: 'GET', headers: headers() });
      const ct  = res.headers.get('content-type') || '';
      const data = ct.includes('application/json') ? await res.json() : { error: await res.text() };
      if (!res.ok) throw new Error(data?.detail || data?.error || `Erreur ${res.status}`);
      setShifts(normalizeShiftsResponse(data?.results ?? data));
    } catch (e) { setError(e.message || 'Erreur réseau'); }
    finally { setLoading(false); }
  }

  async function createShift0812() {
    setError(''); setLoading(true);
    try {
      const body = { start_time: isoForToday('19:00'), end_time: isoForToday('20:00') };
      const res  = await fetch(u(`/users/${userId}/shifts`), { method: 'POST', headers: headers(), body: JSON.stringify(body) });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.detail || data?.error || `Erreur ${res.status}`);
      await fetchUserShifts();
    } catch (e) { setError(e.message || 'Erreur réseau'); }
    finally { setLoading(false); }
  }

  async function rowCheckIn(s) {
    setError(''); setLoading(true);
    try {
      const res  = await fetch(u(`/users/${userId}/shifts/${s.id}/check-in/`), {
        method:'POST', headers: headers(), body: JSON.stringify({ start_time: new Date().toISOString() })
      });
      const data = await res.json().catch(()=> ({}));
      if (!res.ok) throw new Error(data?.detail || data?.error || `Erreur ${res.status}`);
      const updated = data?.shift || {};
      setShifts(lst => lst.map(x => x.id === s.id ? { ...x, ...updated } : x));
    } catch (e) { setError(e.message || 'Erreur réseau'); }
    finally { setLoading(false); }
  }

  async function rowCheckOut(s) {
    setError(''); setLoading(true);
    try {
      const res  = await fetch(u(`/users/${userId}/shifts/${s.id}/check-out/`), {
        method:'POST', headers: headers(), body: JSON.stringify({ end_time: new Date().toISOString() })
      });
      const data = await res.json().catch(()=> ({}));
      if (!res.ok) throw new Error(data?.detail || data?.error || `Erreur ${res.status}`);
      const updated = data?.shift || {};
      setShifts(lst => lst.map(x => x.id === s.id ? { ...x, ...updated } : x));
    } catch (e) { setError(e.message || 'Erreur réseau'); }
    finally { setLoading(false); }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Tableau de bord</h1>
        <p className="page-description">Vue d’ensemble de votre journée et de vos pointages</p>
        {error && <p className="error-banner">⚠️ {error}</p>}
      </div>

      <div className="dashboard-content">
        {/* Colonne principale : Shifts */}
        <section className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Mes shifts</h2>
            <div className="card-actions">
              <button className="pointage-button" onClick={fetchUserShifts} disabled={loading}>Rafraîchir</button>
              <button className="pointage-button" onClick={createShift0812} disabled={loading}>Créer shift 16–17</button>
            </div>
          </div>

          {loading && <p className="muted-text">Chargement…</p>}

          <div className="shifts-scroll">
            {shifts.length === 0 ? (
              <p className="muted-text">Aucun shift.</p>
            ) : (
              shifts.map((s) => {
                const completedToday = isToday(s.start_time) && s.real_start_time && s.real_end_time;
                return (
                  <div key={s.id} className={`bloc shift-block ${completedToday ? 'completed' : ''}`}>
                    <div className="bloc-title"><h3>Shift {s.id}</h3></div>
                    <div className="shift-actions">
                      <div className="shift-action">
                        <button
                          className="pointage-button"
                          onClick={() => rowCheckIn(s)}
                          disabled={!!s.real_start_time || completedToday || loading}
                          title={`Check-in prévu ${fmtHHmm(s.start_time)}`}
                        >
                          {`Check-in ${fmtHHmm(s.start_time)}`}
                        </button>
                        <span className="pointage-time" style={{ color: colorForCheckIn(s.start_time, s.real_start_time) }}>
                          {s.real_start_time ? `Réel ${fmtHHmm(s.real_start_time)}` : `Prévu ${fmtHHmm(s.start_time)}`}
                        </span>
                      </div>

                      <div className="shift-action">
                        <button
                          className="pointage-button"
                          onClick={() => rowCheckOut(s)}
                          disabled={!s.real_start_time || !!s.real_end_time || completedToday || loading}
                          title={`Check-out prévu ${fmtHHmm(s.end_time)}`}
                        >
                          {`Check-out ${fmtHHmm(s.end_time)}`}
                        </button>
                        <span className="pointage-time" style={{ color: colorForCheckOut(s.end_time, s.real_end_time) }}>
                          {s.real_end_time ? `Réel ${fmtHHmm(s.real_end_time)}` : `Prévu ${fmtHHmm(s.end_time)}`}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </section>

        {/* Colonne droite : Stats */}
        <aside className="dashboard-card small">
          <h2 className="card-title">Statistiques</h2>
          <div className="progress-wrap">
            <CircularProgressbar
              value={percentage}
              text={`${percentage}%`}
              styles={buildStyles({
                textSize: '18px',
                pathColor: '#007bff',
                textColor: '#333',
                trailColor: '#eee',
              })}
            />
            <p className="muted-text" style={{ marginTop: 10 }}>Présence (tous les shifts)</p>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default Dashboard;
