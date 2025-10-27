// src/api/api.js
import axios from "axios";
import {
  BASE,
  getAccess,
  getAccessExpiry,
  msUntil,
  refreshAccess,
  logout,
} from "../api/auth";

const api = axios.create({ baseURL: (BASE || "/api").replace(/\/$/, "") });

// Promesse de refresh partagée (évite les refresh parallèles)
let refreshPromise = null;

function ensureRefresh() {
  if (!refreshPromise) {
    refreshPromise = refreshAccess()
      .catch((err) => {
        // échec du refresh → logout global
        logout();
        throw err;
      })
      .finally(() => {
        // réinitialiser pour les prochains cycles
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

// ---- Interceptor requête : Authorization + pré-refresh si < 60s ----
api.interceptors.request.use(async (config) => {
  // Si l'access expire bientôt, on rafraîchit *une seule fois*
  const exp = getAccessExpiry();
  if (exp && msUntil(exp) < 60_000) {
    await ensureRefresh();
  }

  // Toujours poser le token le plus récent
  const access = getAccess();
  config.headers = config.headers || {};
  if (access) config.headers.Authorization = `Bearer ${access}`;
  return config;
});

// ---- Interceptor réponse : retry unique sur 401 avec refresh partagé ----
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (!error.response || error.response.status !== 401 || original?._retry) {
      return Promise.reject(error);
    }

    original._retry = true;

    // Lancer (ou rejoindre) le refresh unique
    const newAccess = await ensureRefresh();

    // Rejouer la requête d’origine avec le nouveau token
    original.headers = original.headers || {};
    if (newAccess) original.headers.Authorization = `Bearer ${newAccess}`;
    return api(original);
  }
);

export default api;
