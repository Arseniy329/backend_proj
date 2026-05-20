import api from '@/lib/axiosInstance';

export const fetchSubscriptionPlans  = (params)   => api.get('/api/subscription-plans/', { params });
export const fetchSubscriptionPlan   = (id)       => api.get(`/api/subscription-plans/${id}/`);
export const createSubscriptionPlan  = (data)     => api.post('/api/subscription-plans/', data);
export const updateSubscriptionPlan  = (id, data) => api.patch(`/api/subscription-plans/${id}/`, data);
export const deleteSubscriptionPlan  = (id)       => api.delete(`/api/subscription-plans/${id}/`);
