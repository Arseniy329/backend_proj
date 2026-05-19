'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchLessons, createLesson, updateLesson, deleteLesson } from '@/api/lessonsApi';

export function useLessons(initialParams = {}) {
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);
  const [params, setParams]   = useState(initialParams);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await fetchLessons(params);
      setLessons(data);
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Помилка завантаження занять.');
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => { load(); }, [load]);

  const addLesson    = async (d)     => { const { data } = await createLesson(d);     setLessons((p) => [data, ...p]); return data; };
  const editLesson   = async (id, d) => { const { data } = await updateLesson(id, d); setLessons((p) => p.map((l) => (l.id === id ? data : l))); return data; };
  const removeLesson = async (id)    => { await deleteLesson(id); setLessons((p) => p.filter((l) => l.id !== id)); };

  return { lessons, loading, error, reload: load, setParams, addLesson, editLesson, removeLesson };
}
