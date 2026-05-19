'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchStudents, createStudent, updateStudent, deleteStudent, restoreStudent } from '@/api/studentsApi';

export function useStudents(initialParams = {}) {
  const [students, setStudents] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [params, setParams]     = useState(initialParams);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await fetchStudents(params);
      setStudents(data);
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Помилка завантаження студентів.');
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => { load(); }, [load]);

  const addStudent     = async (formData)     => { const { data } = await createStudent(formData);      setStudents((p) => [data, ...p]); return data; };
  const editStudent    = async (id, formData) => { const { data } = await updateStudent(id, formData);  setStudents((p) => p.map((s) => (s.id === id ? data : s))); return data; };
  const removeStudent  = async (id)           => { await deleteStudent(id); setStudents((p) => p.filter((s) => s.id !== id)); };
  const recoverStudent = async (id)           => { const { data } = await restoreStudent(id); setStudents((p) => p.map((s) => (s.id === id ? data : s))); return data; };

  return { students, loading, error, reload: load, setParams, addStudent, editStudent, removeStudent, recoverStudent };
}
