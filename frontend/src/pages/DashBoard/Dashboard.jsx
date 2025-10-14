import React, { useEffect, useMemo, useState } from 'react';
import './Dashboard.css';

import {
  BASE as ENV_BASE,
  getAuthHeaders,
  getAccess,
  logout,
} from '../../api/auth'; // adapte le chemin si besoin

// Base API (.env Vite: VITE_API_BASE=/api ou http://localhost:8080/api)
const API_BASE = (ENV_BASE || '/api').replace(/\/$/, '');

// ---- Helpers généraux ----
function parseJwtUserId(token) {
  try {
    const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const json = atob(payload);
    const data = JSON.parse(decodeURIComponent(escape(json)));
    return data.user_id ?? data.sub ?? null;
  } catch {
    return null;
  }
}
function fmtHHmm(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
function toDate(iso) { return iso ? new Date(iso) : null; }
function colorForCheckIn(plannedIso, realIso) {
  if (!realIso) return '#111';
  const p = toDate(plannedIso), r = toDate(realIso);
  return r <= p ? 'green' : 'red'; // à l’heure ou en avance -> vert
}
function colorForCheckOut(plannedIso, realIso) {
  if (!realIso) return '#111';
  const p = toDate(plannedIso), r = toDate(realIso);
  return r >= p ? 'green' : 'red'; // pas avant l’heure -> vert
}
function isToday(iso) {
  if (!iso) return false;
  const d = new Date(iso);
  const t = new Date();
  return d.getFullYear() === t.getFullYear()
    && d.getMonth() === t.getMonth()
    && d.getDate() === t.getDate();
}
// pour le bouton “Créer shift 08–12”
function isoForToday(hhmm) {
  const [h, m] = hhmm.split(':').map(Number);
  const d = new Date();
  d.setHours(h, m, 0, 0);
  return d.toISOString();
}

const Dashboard = () => {
  // ---- Auth / user_id
  const access = useMemo(() => getAccess(), []);
  const userId = useMemo(() => parseJwtUserId(access), [access]);
  if (!access || !userId) { logout(); return null; }

  // ---- State
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');
  const [shifts, setShifts]   = useState([]);

  const headers = () => getAuthHeaders();

  // ---- Charger automatiquement les shifts au montage
  useEffect(() => { fetchUserShifts(); }, []);

  async function fetchUserShifts() {
    setError(''); setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/users/${userId}/shifts/`, {
        method: 'GET', headers: headers(),
      });
      const ct = res.headers.get('content-type') || '';
      const data = ct.includes('application/json') ? await res.json() : { error: await res.text() };
      if (!res.ok) throw new Error(data?.detail || data?.error || `Erreur ${res.status}`);
      setShifts(Array.isArray(data?.shifts) ? data.shifts : []);
    } catch (e) {
      setError(e.message || 'Erreur réseau');
    } finally { setLoading(false); }
  }

  // ---- Créer un shift de test 08–12 (aujourd’hui)
  async function createShift0812() {
    setError(''); setLoading(true);
    try {
      const body = { start_time: isoForToday('08:00'), end_time: isoForToday('12:00') };
      const res  = await fetch(`${API_BASE}/users/${userId}/shifts/`, {
        method: 'POST', headers: headers(), body: JSON.stringify(body),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.detail || data?.error || `Erreur ${res.status}`);
      await fetchUserShifts(); // recharge la liste
    } catch (e) {
      setError(e.message || 'Erreur réseau');
    } finally { setLoading(false); }
  }

  // ---- Actions API par shift
  async function rowCheckIn(s) {
    setError(''); setLoading(true);
    try {
      const body = { start_time: new Date().toISOString() };
      const res  = await fetch(`${API_BASE}/users/${userId}/shifts/${s.id}/check-in/`, {
        method: 'POST', headers: headers(), body: JSON.stringify(body),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.detail || data?.error || `Erreur ${res.status}`);
      const updated = data?.shift || {};
      setShifts(lst => lst.map(x => (x.id === s.id ? { ...x, ...updated } : x)));
    } catch (e) {
      setError(e.message || 'Erreur réseau');
    } finally { setLoading(false); }
  }

  async function rowCheckOut(s) {
    setError(''); setLoading(true);
    try {
      const body = { end_time: new Date().toISOString() };
      const res  = await fetch(`${API_BASE}/users/${userId}/shifts/${s.id}/check-out/`, {
        method: 'POST', headers: headers(), body: JSON.stringify(body),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.detail || data?.error || `Erreur ${res.status}`);
      const updated = data?.shift || {};
      setShifts(lst => lst.map(x => (x.id === s.id ? { ...x, ...updated } : x)));
    } catch (e) {
      setError(e.message || 'Erreur réseau');
    } finally { setLoading(false); }
  }

  return (
    <div className="dashboard-root" style={{ marginLeft: '250px', padding: '20px' }}>
      <h1>Dashboard</h1>
      {error && <p className="error-text">{error}</p>}
      {loading && <p className="muted-text">Chargement…</p>}

      <div className="section">
        <h2 className="section-title">Mes shifts</h2>

        {/* Barre d’actions */}
        <div style={{ display:'flex', gap:12, justifyContent:'center', marginBottom:16, flexWrap:'wrap' }}>
          <button className="pointage-button" onClick={fetchUserShifts} disabled={loading}>
            Rafraîchir
          </button>
          <button className="pointage-button" onClick={createShift0812} disabled={loading}>
            Créer shift 08–12
          </button>
        </div>

        {/* Affichage par shift : deux gros boutons alignés + couleurs + grisé si terminé */}
        {shifts.length === 0 && <p className="muted-text">Aucun shift.</p>}

        {shifts.map((s) => {
          const completedToday = isToday(s.start_time) && s.real_start_time && s.real_end_time;
          return (
            <div
              key={s.id}
              className={`bloc shift-block ${completedToday ? 'completed' : ''}`}
              style={{ marginBottom: 28 }}
            >
              <div className="bloc-title"><h3>Shift #{s.id}</h3></div>
              <div className="bloc-title"><h3>Matin</h3></div>

              <div className="shift-actions">
                {/* Check-in */}
                <div className="shift-action">
                  <button
                    className="pointage-button"
                    onClick={() => rowCheckIn(s)}
                    disabled={!!s.real_start_time || completedToday || loading}
                  >
                    Check-in<br/>API
                  </button>
                  <span
                    className="pointage-time"
                    style={{ color: colorForCheckIn(s.start_time, s.real_start_time) }}
                  >
                    {s.real_start_time
                      ? `Réel ${fmtHHmm(s.real_start_time)}`
                      : `Prévu ${fmtHHmm(s.start_time)}`}
                  </span>
                </div>

                {/* Check-out */}
                <div className="shift-action">
                  <button
                    className="pointage-button"
                    onClick={() => rowCheckOut(s)}
                    disabled={!s.real_start_time || !!s.real_end_time || completedToday || loading}
                  >
                    Check-out<br/>API
                  </button>
                  <span
                    className="pointage-time"
                    style={{ color: colorForCheckOut(s.end_time, s.real_end_time) }}
                  >
                    {s.real_end_time
                      ? `Réel ${fmtHHmm(s.real_end_time)}`
                      : `Prévu ${fmtHHmm(s.end_time)}`}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Dashboard;
