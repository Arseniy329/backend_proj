import api from '@/lib/axiosInstance';

export const fetchUsers   = (params)   => api.get('/api/users/', { params });
export const fetchUser    = (id)       => api.get(`/api/users/${id}/`);
export const createUser   = (data)     => api.post('/api/users/', data);
export const updateUser   = (id, data) => api.patch(`/api/users/${id}/`, data);
export const deleteUser   = (id)       => api.delete(`/api/users/${id}/`);
