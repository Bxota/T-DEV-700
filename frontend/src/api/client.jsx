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

// Pré-refresh si < 60s avant expiration
api.interceptors.request.use(async (config) => {
  const access = getAccess();
  if (!config.headers) config.headers = {};
  if (access) config.headers.Authorization = `Bearer ${access}`;
  return config;
});

// Retry 401 avec refresh unique + mise en file
let isRefreshing = false;
let requestQueue = [];
function queueRequest(cb) {
  return new Promise((resolve, reject) => requestQueue.push({ resolve, reject, cb }));
}
function flushQueue(error, token) {
  requestQueue.forEach(p => (error ? p.reject(error) : p.resolve(p.cb(token))));
  requestQueue = [];
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (!error.response || error.response.status !== 401 || original._retry) {
      return Promise.reject(error);
    }
    original._retry = true;

    if (isRefreshing) {
      try {
        return await queueRequest((token) => {
          original.headers.Authorization = `Bearer ${token}`;
          return api(original);
        });
      } catch (err) { return Promise.reject(err); }
    }

    isRefreshing = true;
    try {
      const newAccess = await refreshAccess(); // peut throw
      if (!newAccess) throw new Error("No access after refresh");
      original.headers.Authorization = `Bearer ${newAccess}`;
      const resp = await api(original);
      flushQueue(null, newAccess);
      return resp;
    } catch (err) {
      flushQueue(err, null);
      logout();
      return Promise.reject(err);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;
