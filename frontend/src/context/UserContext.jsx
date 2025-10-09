import { createContext, useContext, useState, useEffect, useMemo } from 'react';

const UserContext = createContext(null);

export const useUser = () => {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error('useUser must be used within <UserProvider>');
  return ctx;
};

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const DEBUG_FORCE_LOGIN = true;

  useEffect(() => {
    if (DEBUG_FORCE_LOGIN) {
      const fakeUser = {
        id: '123',
        email: 'test@exemple.com',
        name: 'Jean Mupont',
        avatarUrl: '',
      };
      setUser(fakeUser);
      return;
    }

    const storedUser = localStorage.getItem('user');
    if (storedUser) setUser(JSON.parse(storedUser));
  }, []);

  useEffect(() => {
    if (user) localStorage.setItem('user', JSON.stringify(user));
    else localStorage.removeItem('user');
  }, [user]);

  const logout = () => setUser(null);

  const value = useMemo(
    () => ({ user, setUser, logout, isLoggedIn: !!user }),
    [user]
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};
