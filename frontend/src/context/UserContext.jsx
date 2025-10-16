// src/context/UserContext.jsx
import {createContext,useContext,useState,useEffect,useMemo,useCallback,} from "react";

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

const isJwtValid = (token) => {
  try {
    const { exp } = JSON.parse(atob(token.split(".")[1]));
    return exp * 1000 > Date.now();
  } catch {
    return false;
  }
};

// ---------- constants ----------
const API_BASE = import.meta.env.VITE_API_BASE || "/api";

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

  // 👉 public: MAJ après login
  const refreshUser = useCallback(async () => {
    const access = localStorage.getItem("access");
    if (!access || !isJwtValid(access)) {
      setUser(null);
      return;
    }

    try {
      const r = await fetch(`${API_BASE}/token/whoami/`, {
        headers: { Authorization: `Bearer ${access}`, Accept: "application/json" },
      });

      if (r.ok) {
        const data = await r.json();
        const u = data?.user || {};
        setUser((prev) => normalizeUserFromApi(u, prev));
        return;
      }
    } catch {
      // ignore
    }

    // fallback : hydrate depuis JWT minimalement
    const claims = decodeJwt(access) || {};
    setUser((prev) => minimalUserFromClaims(claims, prev));
  }, []);

  //Synchronisation user <-> localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      localStorage.removeItem("user");
    }
  }, [user]);

  // 🔓 Déconnexion complète
  const logout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,                 
      setUser,              
      logout,
      isLoggedIn: !!user,
      refreshUser,         
    }),
    [user, refreshUser]
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};
