// src/auth.js
import axios from "axios";

export const BASE = import.meta.env.VITE_API_BASE || "/api";
export const ACCESS_KEY  = "access";
export const REFRESH_KEY = "refresh";

function decodeJwt(token) {
  try {
    const b64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(b64);
    return JSON.parse(decodeURIComponent(escape(json)));
  } catch {
    return null;
  }
}

export function getAccess()  { return localStorage.getItem(ACCESS_KEY); }
export function getRefresh() { return localStorage.getItem(REFRESH_KEY); }

export function setTokens({ access, refresh }) {
  if (access)  localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

// 🔓 Déconnexion fiable (nettoie et redirige)
export function logout(redirectTo = "/login") {
  clearTokens();
  // Si tu as un endpoint serveur de logout basé cookie, tu peux l’appeler ici en option
  // fetch(`${BASE}/logout/`, { method: "POST", credentials: "include" }).catch(()=>{});
  window.location.replace(redirectTo); // évite de revenir en arrière sur une page protégée
}

// 🔑 Login: récupère access/refresh et stocke
export async function login(email, password) {
  try {
    const res = await axios.post(`${BASE}/token/`, { email, password }, {
      headers: { "Content-Type": "application/json" },
    });
    const { access, refresh } = res.data;
    setTokens({ access, refresh });
    return { access, refresh, claims: decodeJwt(access) };
  } catch (err) {
    const msg = err?.response?.data?.detail || err?.message || "Login échoué";
    throw new Error(msg);
  }
}
