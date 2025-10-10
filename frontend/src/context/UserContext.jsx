import {
  createContext,
  useContext,
  useState,
  useEffect,
  useMemo,
  useCallback,
} from "react";

const UserContext = createContext(null);
export const useUser = () => {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within <UserProvider>");
  return ctx;
};

// util pour décoder un JWT
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

const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const DEBUG_FORCE_LOGIN = false;

  // 👉 exposé publiquement pour forcer la MAJ après login
  const refreshUser = useCallback(async () => {
    const access = localStorage.getItem("access");
    if (!access || !isJwtValid(access)) {
      setUser(null);
      return;
    }
    try {
      const r = await fetch(`${API_BASE}/token/whoami/`, {
        headers: { Authorization: `Bearer ${access}` },
      });
      if (r.ok) {
        const data = await r.json();
        const u = data?.user || {};
        setUser((prev) => ({
          ...prev,
          id: u.id ?? prev?.id ?? null,
          email: u.email ?? prev?.email ?? null,
          username: prev?.username ?? null,
          first_name: u.first_name ?? "",
          last_name: u.last_name ?? "",
          role: u.role ?? prev?.role ?? null,
          team: u.team ?? prev?.team ?? null,
          avatarUrl: prev?.avatarUrl ?? "",
        }));
        return;
      }
    } catch {
      // ignore
    }
    // fallback : au moins hydrater depuis le JWT
    const claims = decodeJwt(access) || {};
    setUser((prev) => ({
      ...prev,
      id: claims.user_id ?? claims.sub ?? prev?.id ?? null,
      email: claims.email ?? prev?.email ?? null,
      username: claims.username ?? prev?.username ?? null,
    }));
  }, []);

  useEffect(() => {
    const boot = async () => {
      if (DEBUG_FORCE_LOGIN) {
        setUser({
          id: "123",
          email: "test@exemple.com",
          username: "jean",
          first_name: "Jean",
          last_name: "Dupont",
          role: "manager",
          team: "Equipe A",
          avatarUrl: "",
        });
        return;
      }

      const storedUser = localStorage.getItem("user");
      const access = localStorage.getItem("access");
      const refresh = localStorage.getItem("refresh");

      // 1) access token OK → tente whoami (ou hydrate depuis storage/JWT)
      if (access && isJwtValid(access)) {
        try {
          const r = await fetch(`${API_BASE}/token/whoami/`, {
            headers: { Authorization: `Bearer ${access}` },
          });
          if (r.ok) {
            const data = await r.json();
            const u = data?.user || {};
            setUser({
              ...(storedUser ? JSON.parse(storedUser) : {}),
              id: u.id ?? null,
              email: u.email ?? null,
              username: u.username ?? null,
              first_name: u.first_name ?? "",
              last_name: u.last_name ?? "",
              role: u.role ?? null,
              team: u.team ?? null,
              avatarUrl: "",
            });
            return;
          }
        } catch {
          // ignore
        }

        const claims = decodeJwt(access) || {};
        setUser(
          (storedUser && JSON.parse(storedUser)) || {
            id: claims.user_id ?? claims.sub ?? null,
            email: claims.email ?? null,
            username: claims.username ?? null,
          }
        );
        return;
      }

      // 2) access expiré mais refresh présent → tente un refresh
      if (refresh) {
        try {
          const res = await fetch(`${API_BASE}/token/refresh/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh }),
          });
          if (res.ok) {
            const data = await res.json();
            if (data?.access) {
              localStorage.setItem("access", data.access);
              const claims = decodeJwt(data.access) || {};
              const u =
                (storedUser && JSON.parse(storedUser)) || {
                  id: claims.user_id ?? claims.sub ?? null,
                  email: claims.email ?? null,
                  username: claims.username ?? null,
                };
              setUser(u);
              return;
            }
          }
        } catch {
          // ignore
        }
      }

      // 3) rien de valide → on nettoie
      localStorage.removeItem("user");
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      setUser(null);
    };

    boot();
  }, [DEBUG_FORCE_LOGIN]);

  // Sync user <-> localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      localStorage.removeItem("user");
    }
  }, [user]);

  const logout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setUser(null);
  };

  const value = useMemo(
    () => ({ user, setUser, logout, isLoggedIn: !!user, refreshUser }),
    [user, refreshUser]
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};
