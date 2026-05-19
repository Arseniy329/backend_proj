import api from '@/lib/axiosInstance';

export const fetchAttendances  = (params)   => api.get('/api/attendances/', { params });
export const fetchAttendance   = (id)       => api.get(`/api/attendances/${id}/`);
export const createAttendance  = (data)     => api.post('/api/attendances/', data);
export const updateAttendance  = (id, data) => api.patch(`/api/attendances/${id}/`, data);
export const deleteAttendance  = (id)       => api.delete(`/api/attendances/${id}/`);
