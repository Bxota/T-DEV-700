import axios from "axios";
const BASE = import.meta.env.VITE_API_BASE || "/api";

const api = axios.create({ baseURL: BASE });

api.interceptors.request.use((config) => {
  const access = localStorage.getItem("access");
  if (access) config.headers.Authorization = `Bearer ${access}`;
  return config;
});

export default api;
