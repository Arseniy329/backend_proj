'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import api from '@/lib/axiosInstance';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem('user');
    if (stored) {
      try { setUser(JSON.parse(stored)); } catch { localStorage.removeItem('user'); }
    }
    setLoading(false);
  }, []);

  async function login(phone, password) {
    const { data } = await api.post('/api/auth/login/', { phone, password });
    localStorage.setItem('access',  data.access);
    localStorage.setItem('refresh', data.refresh);
    localStorage.setItem('user',    JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  }

  async function logout() {
    const refresh = localStorage.getItem('refresh');
    try { if (refresh) await api.post('/api/auth/logout/', { refresh }); } catch { /* ignore */ }
    finally {
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      localStorage.removeItem('user');
      setUser(null);
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
