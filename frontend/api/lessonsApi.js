import api from '@/lib/axiosInstance';

export const fetchLessons       = (params)   => api.get('/api/lessons/', { params });
export const fetchLesson        = (id)       => api.get(`/api/lessons/${id}/`);
export const createLesson       = (data)     => api.post('/api/lessons/', data);
export const updateLesson       = (id, data) => api.patch(`/api/lessons/${id}/`, data);
export const deleteLesson       = (id)       => api.delete(`/api/lessons/${id}/`);
export const markAttendance     = (id, data) => api.post(`/api/lessons/${id}/mark-attendance/`, data);
