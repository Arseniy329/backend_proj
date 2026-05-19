'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchBranches, createBranch, updateBranch, deleteBranch, restoreBranch } from '@/api/branchesApi';

/**
 * Manages branch list state: loading, error, CRUD operations, and search.
 */
export function useBranches(initialParams = {}) {
  const [branches, setBranches] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [params, setParams]     = useState(initialParams);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await fetchBranches(params);
      setBranches(data);
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Помилка завантаження філій.');
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => { load(); }, [load]);

  const addBranch = async (formData) => {
    const { data } = await createBranch(formData);
    setBranches((prev) => [data, ...prev]);
    return data;
  };

  const editBranch = async (id, formData) => {
    const { data } = await updateBranch(id, formData);
    setBranches((prev) => prev.map((b) => (b.id === id ? data : b)));
    return data;
  };

  const removeBranch = async (id) => {
    await deleteBranch(id);
    setBranches((prev) => prev.filter((b) => b.id !== id));
  };

  const recoverBranch = async (id) => {
    const { data } = await restoreBranch(id);
    setBranches((prev) => prev.map((b) => (b.id === id ? data : b)));
    return data;
  };

  return {
    branches, loading, error,
    reload: load,
    setParams,
    addBranch, editBranch, removeBranch, recoverBranch,
  };
}
