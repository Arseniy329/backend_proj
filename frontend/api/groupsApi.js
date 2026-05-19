import api from '@/lib/axiosInstance';

export const fetchGroups  = (params)   => api.get('/api/groups/', { params });
export const fetchGroup   = (id)       => api.get(`/api/groups/${id}/`);
export const createGroup  = (data)     => api.post('/api/groups/', data);
export const updateGroup  = (id, data) => api.patch(`/api/groups/${id}/`, data);
export const deleteGroup  = (id)       => api.delete(`/api/groups/${id}/`);
