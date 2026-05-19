'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchGroups, createGroup, updateGroup, deleteGroup } from '@/api/groupsApi';

export function useGroups(initialParams = {}) {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);
  const [params, setParams]   = useState(initialParams);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await fetchGroups(params);
      setGroups(data);
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Помилка завантаження груп.');
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => { load(); }, [load]);

  const addGroup    = async (formData)     => { const { data } = await createGroup(formData);     setGroups((p) => [data, ...p]); return data; };
  const editGroup   = async (id, formData) => { const { data } = await updateGroup(id, formData); setGroups((p) => p.map((g) => (g.id === id ? data : g))); return data; };
  const removeGroup = async (id)           => { await deleteGroup(id); setGroups((p) => p.filter((g) => g.id !== id)); };

  return { groups, loading, error, reload: load, setParams, addGroup, editGroup, removeGroup };
}
