// frontend/src/api/dashboardApi.ts
import api from './axiosConfig';

const API_URL = '/api/dashboard';

export const dashboardApi = {
  getStats: async (): Promise<any> => {
    const response = await api.get(`${API_URL}/stats`);
    return response.data;
  },

  getMarketOverview: async (): Promise<any> => {
    const response = await api.get(`${API_URL}/market-overview`);
    return response.data;
  },

  getRecentActivity: async (): Promise<any> => {
    const response = await api.get(`${API_URL}/recent-activity`);
    return response.data;
  }
};