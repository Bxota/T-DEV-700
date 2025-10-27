// src/context/UserContext.jsx
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useMemo,
  useCallback,
} from "react";

import api from "../api/client"; // ✅ instance axios avec intercepteurs
import {
  getAccess,
  getRefresh,
  getAccessExpiry,
  getRefreshExpiry,
  isPast,
  msUntil,
  refreshAccess,
  initAuthBackgroundTasks,
  logout as hardLogout, // vide tokens + redirect
} from "../api/auth"; // ✅ note le .js

const UserContext = createContext(null);
export const useUser = () => {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within <UserProvider>");
  return ctx;
};

// ---------- helpers JWT ----------
const decodeJwt = (token) => {
  try {
    const b64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(b64);
    return JSON.parse(decodeURIComponent(escape(json)));
  } catch {
    return null;
  }
};

// ---------- normalization helpers ----------
const normalizeRole = (roleLike) => {
  if (!roleLike) return { id: null, name: "" };
  if (typeof roleLike === "string") return { id: null, name: roleLike };
  return { id: roleLike.id ?? null, name: roleLike.name ?? "" };
};

const normalizeTeam = (teamLike) => {
  if (!teamLike) return { id: null, name: "" };
  if (typeof teamLike === "string") return { id: null, name: teamLike };
  return { id: teamLike.id ?? null, name: teamLike.name ?? "" };
};

const normalizeUserFromApi = (u, prev = null) => ({
  id: u?.id ?? prev?.id ?? null,
  email: u?.email ?? prev?.email ?? null,
  username: u?.username ?? prev?.username ?? null,
  first_name: u?.first_name ?? prev?.first_name ?? "",
  last_name: u?.last_name ?? prev?.last_name ?? "",
  role: normalizeRole(u?.role),
  team: normalizeTeam(u?.team),
  avatarUrl: prev?.avatarUrl ?? "",
});

const minimalUserFromClaims = (claims, prev = null) => ({
  id: claims?.user_id ?? claims?.sub ?? prev?.id ?? null,
  email: claims?.email ?? prev?.email ?? null,
  username: claims?.username ?? prev?.username ?? null,
  first_name: prev?.first_name ?? "",
  last_name: prev?.last_name ?? "",
  role: normalizeRole(prev?.role),
  team: normalizeTeam(prev?.team),
  avatarUrl: prev?.avatarUrl ?? "",
});

// ---------- provider ----------
export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [booting, setBooting] = useState(true); 

  // Restaure/actualise la session et charge l’utilisateur
  const refreshUser = useCallback(async () => {
    // 1) a-t-on une session potentielle ? (refresh valide = source de vérité)
    const hasRefresh = !!getRefresh() && !isPast(getRefreshExpiry());
    if (!hasRefresh) {
      setUser(null);
      return;
    }

    // 2) access présent et valable pour >= 60s ? sinon → refresh
    const accessOk =
      !!getAccess() &&
      !isPast(getAccessExpiry()) &&
      msUntil(getAccessExpiry()) >= 60_000;

    if (!accessOk) {
      await refreshAccess(); // peut throw si refresh expiré
    }

    // 3) Charger le profil via whoami
    try {
      const { data } = await api.get("/token/whoami/");
      const u = data?.user ?? data;
      setUser((prev) => normalizeUserFromApi(u, prev));
    } catch {
      const claims = decodeJwt(getAccess()) || {};
      setUser((prev) => minimalUserFromClaims(claims, prev));
    }
  }, []);

  useEffect(() => {
    (async () => {
      try {
        await refreshUser();
        initAuthBackgroundTasks(); 
      } catch {
        hardLogout("/login");
        return;
      } finally {
        setBooting(false);
      }
    })();
  }, [refreshUser]);

  // Synchronisation user <-> localStorage (facultatif)
  useEffect(() => {
    if (user) localStorage.setItem("user", JSON.stringify(user));
    else localStorage.removeItem("user");
  }, [user]);

  // Déconnexion manuelle
  const logout = () => {
    localStorage.removeItem("user");
    hardLogout("/login");
  };

  const value = useMemo(
    () => ({
      user,
      setUser,
      booting,            
      isLoggedIn: !!user, 
      logout,
      refreshUser,
    }),
    [user, booting, refreshUser]
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};
