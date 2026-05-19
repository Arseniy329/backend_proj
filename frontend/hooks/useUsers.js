'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchUsers, createUser, updateUser, deleteUser } from '@/api/usersApi';

export function useUsers(initialParams = {}) {
  const [users, setUsers]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);
  const [params, setParams]   = useState(initialParams);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await fetchUsers(params);
      setUsers(data);
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Помилка завантаження користувачів.');
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => { load(); }, [load]);

  const addUser    = async (d)     => { const { data } = await createUser(d);     setUsers((p) => [data, ...p]); return data; };
  const editUser   = async (id, d) => { const { data } = await updateUser(id, d); setUsers((p) => p.map((u) => (u.id === id ? data : u))); return data; };
  const removeUser = async (id)    => { await deleteUser(id); setUsers((p) => p.filter((u) => u.id !== id)); };

  return { users, loading, error, reload: load, setParams, addUser, editUser, removeUser };
}
