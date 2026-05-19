import api from '@/lib/axiosInstance';

export const fetchBranches  = (params) => api.get('/api/branches/', { params });
export const fetchBranch    = (id)     => api.get(`/api/branches/${id}/`);
export const createBranch   = (data)   => api.post('/api/branches/', data);
export const updateBranch   = (id, data) => api.patch(`/api/branches/${id}/`, data);
export const deleteBranch   = (id)     => api.delete(`/api/branches/${id}/`);
export const restoreBranch  = (id)     => api.post(`/api/branches/${id}/restore/`);
