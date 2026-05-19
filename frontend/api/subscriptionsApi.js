import api from '@/lib/axiosInstance';

export const fetchSubscriptionPlans  = (params)   => api.get('/api/subscriptions/', { params });
export const fetchSubscriptionPlan   = (id)       => api.get(`/api/subscriptions/${id}/`);
export const createSubscriptionPlan  = (data)     => api.post('/api/subscriptions/', data);
export const updateSubscriptionPlan  = (id, data) => api.patch(`/api/subscriptions/${id}/`, data);
export const deleteSubscriptionPlan  = (id)       => api.delete(`/api/subscriptions/${id}/`);
