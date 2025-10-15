// src/auth.js
import axios from "axios";

export const BASE = (import.meta.env.VITE_API_BASE || "/api").replace(/\/$/, "");
export const ACCESS_KEY  = "access";
export const REFRESH_KEY = "refresh";
export const ACCESS_EXP  = "access_expires_at";   // ISO string
export const REFRESH_EXP = "refresh_expires_at";  // ISO string

// ---------- getters / setters tokens ----------
export function getAccess()  { return localStorage.getItem(ACCESS_KEY); }
export function getRefresh() { return localStorage.getItem(REFRESH_KEY); }
export function getAccessExpiry()  { return localStorage.getItem(ACCESS_EXP); }
export function getRefreshExpiry() { return localStorage.getItem(REFRESH_EXP); }

export function setTokens({ access, refresh, access_expires_at, refresh_expires_at }) {
  if (access) localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  if (access_expires_at)  localStorage.setItem(ACCESS_EXP, access_expires_at);
  if (refresh_expires_at) localStorage.setItem(REFRESH_EXP, refresh_expires_at);
  scheduleAccessRefresh(); // replanifie dès qu’on met à jour
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(ACCESS_EXP);
  localStorage.removeItem(REFRESH_EXP);
  cancelAccessRefresh();
}

export function logout(redirectTo = "/login") {
  clearTokens();
  window.location.replace(redirectTo);
}

export function getAuthHeaders() {
  const access = getAccess();
  return { Authorization: access ? `Bearer ${access}` : undefined, "Content-Type": "application/json" };
}

// ---------- utils expirations ----------
export function msUntil(iso) {
  if (!iso) return -Infinity;
  const t = Date.parse(iso);    // ISO → ms (UTC ok)
  if (Number.isNaN(t)) return -Infinity;
  return t - Date.now();
}
export function isPast(iso, skewSeconds = 0) {
  return msUntil(iso) <= -(skewSeconds * 1000);
}

// ---------- login : /token/ ----------
export async function login(email, password) {
  const res = await axios.post(`${BASE}/token/`, { email, password }, {
    headers: { "Content-Type": "application/json" },
  });
  const { access, refresh, access_token_expires_at, refresh_token_expires_at } = res.data || {};
  setTokens({
    access,
    refresh,
    access_expires_at:  access_token_expires_at,
    refresh_expires_at: refresh_token_expires_at,
  });
  return res.data;
}

// ---------- refresh : /token/refresh/ ----------
let refreshingPromise = null;

export async function refreshAccess() {
  if (refreshingPromise) return refreshingPromise;

  const refresh = getRefresh();
  const refreshExp = getRefreshExpiry();
  if (!refresh || isPast(refreshExp)) {
    logout();
    return null;
  }

  refreshingPromise = axios
    .post(`${BASE}/token/refresh/`, { refresh }, { headers: { "Content-Type": "application/json" } })
    .then((res) => {
      const { access, access_token_expires_at } = res.data || {};
      if (!access) throw new Error("Refresh: access manquant");
      // on conserve le refresh + sa date (souvent pas renvoyés au refresh)
      setTokens({
        access,
        access_expires_at: access_token_expires_at,
        refresh: getRefresh(),
        refresh_expires_at: getRefreshExpiry(),
      });
      return access;
    })
    .catch((err) => {
      clearTokens();
      throw err;
    })
    .finally(() => { refreshingPromise = null; });

  return refreshingPromise;
}

// ---------- planificateur proactif (1 min avant) ----------
let refreshTimer = null;

function cancelAccessRefresh() {
  if (refreshTimer) {
    clearTimeout(refreshTimer);
    refreshTimer = null;
  }
}

export function scheduleAccessRefresh() {
  cancelAccessRefresh();

  const accessExp = getAccessExpiry();
  if (!accessExp) return;

  const remaining = msUntil(accessExp); // ms restants
  if (remaining <= 0) {
    // déjà expiré -> refresh immédiat
    refreshAccess().catch(() => logout());
    return;
  }

  // > 1 min => on anticipe de 60s. <= 1 min => on attend l'expiration exacte.
  const delay = remaining > 60_000 ? (remaining - 60_000) : remaining;

  // petit plancher pour éviter un setTimeout(0) spammy
  const safeDelay = Math.max(250, delay);

  refreshTimer = setTimeout(() => {
    refreshAccess().catch(() => logout());
  }, safeDelay);
}

// A appeler une seule fois au boot (main.jsx / App.jsx)
export function initAuthBackgroundTasks() {
  scheduleAccessRefresh();

  // si on revient visible et que l’access est proche d’expirer/expiré -> refresh
  window.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      const accessExp = getAccessExpiry();
      if (!accessExp) return;
      // si < 60s restant (ou passé) → refresh
      if (msUntil(accessExp) < 60_000) {
        refreshAccess().catch(() => logout());
      }
    }
  });

  // multi-onglets : synchroniser les timers
  window.addEventListener("storage", (e) => {
    if ([ACCESS_KEY, REFRESH_KEY, ACCESS_EXP, REFRESH_EXP].includes(e.key)) {
      scheduleAccessRefresh();
    }
  });
}
