import api from '@/lib/axiosInstance';

export const fetchSubjects  = (params)   => api.get('/api/subjects/', { params });
export const fetchSubject   = (id)       => api.get(`/api/subjects/${id}/`);
export const createSubject  = (data)     => api.post('/api/subjects/', data);
export const updateSubject  = (id, data) => api.patch(`/api/subjects/${id}/`, data);
export const deleteSubject  = (id)       => api.delete(`/api/subjects/${id}/`);
