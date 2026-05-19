import api from '@/lib/axiosInstance';

export const fetchStudents  = (params)   => api.get('/api/students/', { params });
export const fetchStudent   = (id)       => api.get(`/api/students/${id}/`);
export const createStudent  = (data)     => api.post('/api/students/', data);
export const updateStudent  = (id, data) => api.patch(`/api/students/${id}/`, data);
export const deleteStudent  = (id)       => api.delete(`/api/students/${id}/`);
export const restoreStudent = (id)       => api.post(`/api/students/${id}/restore/`);
