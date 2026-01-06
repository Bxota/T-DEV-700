import React, { useEffect, useMemo, useState } from 'react';
import './Dashboard.css';
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
function fmtHourFR(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  const h = d.getHours();
  const m = d.getMinutes();
  return m === 0 ? `${h}h` : `${h}h${String(m).padStart(2, '0')}`;
}
function labelPlageHoraire(shift) {
  return `Plage horaire ${fmtHourFR(shift.start_time)}–${fmtHourFR(shift.end_time)}`;
}

/* ===== Fenêtres d'action ===== */
const ms = (min) => min * 60 * 1000;
const humanDelay = (msLeft) => {
  if (msLeft <= 0) return 'maintenant';
  const m = Math.round(msLeft / 60000);
  if (m < 60) return `${m} min`;
  const h = Math.floor(m / 60), r = m % 60;
  return r ? `${h}h${String(r).padStart(2, '0')}` : `${h}h`;
};
const canCheckInNow = (s, earlyMinutes = 15) => {
  const now = Date.now();
  const planned = new Date(s.start_time).getTime();
  return now >= (planned - ms(earlyMinutes));
};
const canCheckOutNow = (s) => !!s.real_start_time && !s.real_end_time;

const Dashboard = () => {
  const access = useMemo(() => getAccess(), []);
  const userId = useMemo(() => parseJwtUserId(access), [access]);
  if (!access || !userId) { logout(); return null; }

  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');
  const [shifts, setShifts]   = useState([]);

  // --- Stats 3 couleurs (OK/KO/Non pointé)
  const stats = useMemo(() => {
    let green = 0, red = 0, gray = 0;
    for (const s of shifts) {
      if (s.real_start_time) (toDate(s.real_start_time) <= toDate(s.start_time) ? green++ : red++);
      else gray++;
      if (s.real_end_time)   (toDate(s.real_end_time)   >= toDate(s.end_time)   ? green++ : red++);
      else gray++;
    }
    const total = Math.max(1, shifts.length * 2);
    const pct = {
      green: (green / total) * 100,
      red:   (red   / total) * 100,
      gray:  (gray  / total) * 100,
    };
    return { green, red, gray, total, pct };
  }, [shifts]);

  useEffect(() => { fetchUserShifts(); }, []);

  async function fetchUserShifts() {
    setError(''); setLoading(true);
    try {
      const { from, to } = todayRangeUTC();
      const url = `${API_BASE}/users/${userId}/shifts/list?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`;
      const res = await fetch(url, { method: 'GET', headers: getAuthHeaders() });
      const ct  = res.headers.get('content-type') || '';
      const data = ct.includes('application/json') ? await res.json() : { error: await res.text() };
      if (!res.ok) throw new Error(data?.detail || data?.error || `Erreur ${res.status}`);
      setShifts(normalizeShiftsResponse(data?.results ?? data));
    } catch (e) {
      setError(e.message || 'Erreur réseau');
    } finally { setLoading(false); }
  }

  async function createShift0812() {
    setError(''); setLoading(true);
    try {
      const body = { start_time: isoForToday('20:25'), end_time: isoForToday('22:00') };
      const res  = await fetch(u(`/users/${userId}/shifts`), { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(body) });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.detail || data?.error || `Erreur ${res.status}`);
      await fetchUserShifts();
    } catch (e) {
      setError(e.message || 'Erreur réseau');
    } finally { setLoading(false); }
  }

  async function rowCheckIn(s) {
    if (!canCheckInNow(s, 15)) {
      setError(`⏰ Trop tôt pour le check-in. Autorisé à partir de ${fmtHHmm(s.start_time)} (fenêtre -15 min).`);
      return;
    }
    setError(''); setLoading(true);
    try {
      const res  = await fetch(u(`/users/${userId}/shifts/${s.id}/check-in/`), {
        method:'POST', headers: getAuthHeaders(), body: JSON.stringify({ start_time: new Date().toISOString() })
      });
      const data = await res.json().catch(()=> ({}));
      if (!res.ok) throw new Error(data?.detail || data?.error || `Erreur ${res.status}`);
      const updated = data?.shift || {};
      setShifts(lst => lst.map(x => x.id === s.id ? { ...x, ...updated } : x));
    } catch (e) { setError(e.message || 'Erreur réseau'); }
    finally { setLoading(false); }
  }

  async function rowCheckOut(s) {
    if (!canCheckOutNow(s)) {
      setError('⏳ Check-out indisponible : fais d’abord un check-in ou ce shift est déjà terminé.');
      return;
    }
    setError(''); setLoading(true);
    try {
      const res  = await fetch(u(`/users/${userId}/shifts/${s.id}/check-out/`), {
        method:'POST', headers: getAuthHeaders(), body: JSON.stringify({ end_time: new Date().toISOString() })
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
            </div>
          </div>

          {loading && <p className="muted-text">Chargement…</p>}

          <div className="shifts-scroll">
            {shifts.length === 0 ? (
              <p className="muted-text">Aucun shift.</p>
            ) : (
              shifts.map((s) => {
                const completedToday = isToday(s.start_time) && s.real_start_time && s.real_end_time;

                const nowTs = Date.now();
                const startTs = new Date(s.start_time).getTime();
                const openIn  = Math.max(0, (startTs - ms(15)) - nowTs);

                const canIn  = canCheckInNow(s, 15);
                const canOut = canCheckOutNow(s);

                return (
                  <div key={s.id} className={`bloc shift-block ${completedToday ? 'completed' : ''}`}>
                    <div className="bloc-title shift-header">
                      <h3 className="shift-title">{labelPlageHoraire(s)}</h3>

                      {!s.real_start_time && !canIn && (
                        <div className="availability-hint">
                          Disponible dans <strong>{humanDelay(openIn)}</strong>
                        </div>
                      )}
                    </div>

                    <div className="shift-actions">
                      <div className="shift-action">
                        <button
                          className="pointage-button"
                          onClick={() => rowCheckIn(s)}
                          disabled={!canIn || !!s.real_start_time || completedToday || loading}
                          title={`Check-in prévu ${fmtHHmm(s.start_time)} (autorisé -15 min)`}
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
                          disabled={!canOut || completedToday || loading}
                          title={`Check-out libre après check-in`}
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

        {/* Colonne droite : Statistiques */}
        <aside className="dashboard-card small">
          <h2 className="card-title">Statistiques</h2>

          {/* Donut 3 couleurs */}
          {(() => {
            const size = 180;
            const stroke = 14;
            const r = (size - stroke) / 2;
            const C = 2 * Math.PI * r;

            const lenGreen = (stats.pct.green / 100) * C;
            const lenRed   = (stats.pct.red   / 100) * C;
            const lenGray  = Math.max(0, C - lenGreen - lenRed);

            const offGreen = 0;
            const offRed   = lenGreen;
            const offGray  = lenGreen + lenRed;

            return (
              <div style={{ position: 'relative', width: size, height: size, margin: '20px auto 0' }}>
                <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
                  <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="transparent" strokeWidth={stroke} />
                  <circle cx={size/2} cy={size/2} r={r} fill="none"
                          stroke="#28a745" strokeWidth={stroke}
                          strokeDasharray={`${lenGreen} ${C - lenGreen}`} strokeDashoffset={offGreen}/>
                  <circle cx={size/2} cy={size/2} r={r} fill="none"
                          stroke="#e74c3c" strokeWidth={stroke}
                          strokeDasharray={`${lenRed} ${C - lenRed}`} strokeDashoffset={offRed}/>
                  <circle cx={size/2} cy={size/2} r={r} fill="none"
                          stroke="#e0e0e0" strokeWidth={stroke}
                          strokeDasharray={`${lenGray} ${C - lenGray}`} strokeDashoffset={offGray}/>
                </svg>

                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                  <div style={{ fontSize: 28, fontWeight: 700 }}>{Math.round(stats.pct.green)}%</div>
                  <div className="muted-text" style={{ marginTop: 4 }}>Présence OK</div>
                </div>
              </div>
            );
          })()}

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 12, flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 10, height: 10, background: '#28a745', borderRadius: 2 }}></span>
              <span>OK {stats.green}/{stats.total}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 10, height: 10, background: '#e74c3c', borderRadius: 2 }}></span>
              <span>En anomalie {stats.red}/{stats.total}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 10, height: 10, background: '#e0e0e0', borderRadius: 2 }}></span>
              <span>Non pointé {stats.gray}/{stats.total}</span>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default Dashboard;
