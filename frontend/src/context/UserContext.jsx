import { createContext, useContext, useState, useEffect, useMemo } from "react";

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

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // Mets à true pour forcer un faux utilisateur (dev seulement)
  const DEBUG_FORCE_LOGIN = false;

  useEffect(() => {
    const boot = async () => {
      if (DEBUG_FORCE_LOGIN) {
        setUser({
          id: "123",
          email: "test@exemple.com",
          name: "Jean Mupont",
          avatarUrl: "",
        });
        return;
      }

      const storedUser = localStorage.getItem("user");
      const access = localStorage.getItem("access");
      const refresh = localStorage.getItem("refresh");

      // 1) access token OK → on restaure
      if (access && isJwtValid(access)) {
        if (storedUser) {
          setUser(JSON.parse(storedUser));
          return;
        }
        // pas d'user stocké ? on le reconstruit depuis le JWT
        const claims = decodeJwt(access) || {};
        setUser({
          id: claims.user_id ?? claims.sub ?? null,
          email: claims.email ?? null,
          username: claims.username ?? null,
        });
        return;
      }

      // 2) access expiré mais refresh présent → tente un refresh
      if (refresh) {
        try {
          const res = await fetch(
            (import.meta.env.VITE_API_BASE || "/api") + "/token/refresh/",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ refresh }),
            }
          );
          if (res.ok) {
            const data = await res.json();
            if (data?.access) {
              localStorage.setItem("access", data.access);
              const claims = decodeJwt(data.access) || {};
              // restaure user depuis storage ou claims
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

      // 3) rien de valide → on nettoie et on reste déconnecté
      localStorage.removeItem("user");
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      setUser(null);
    };

    boot();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [DEBUG_FORCE_LOGIN]);

  // Sync user <-> localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      localStorage.removeItem("user");
      // (ne supprime pas forcément les tokens ici, laisse logout le faire)
    }
  }, [user]);

  const logout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setUser(null);
  };

  const value = useMemo(
    () => ({ user, setUser, logout, isLoggedIn: !!user }),
    [user]
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};
