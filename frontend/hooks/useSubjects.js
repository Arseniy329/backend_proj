'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchSubjects, createSubject, updateSubject, deleteSubject } from '@/api/subjectsApi';

export function useSubjects(initialParams = {}) {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [params, setParams]     = useState(initialParams);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await fetchSubjects(params);
      setSubjects(data);
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Помилка завантаження предметів.');
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => { load(); }, [load]);

  const addSubject    = async (d)     => { const { data } = await createSubject(d);     setSubjects((p) => [data, ...p]); return data; };
  const editSubject   = async (id, d) => { const { data } = await updateSubject(id, d); setSubjects((p) => p.map((s) => (s.id === id ? data : s))); return data; };
  const removeSubject = async (id)    => { await deleteSubject(id); setSubjects((p) => p.filter((s) => s.id !== id)); };

  return { subjects, loading, error, reload: load, setParams, addSubject, editSubject, removeSubject };
}
