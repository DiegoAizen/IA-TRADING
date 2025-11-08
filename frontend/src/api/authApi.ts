import api from './axiosConfig';

const API_URL = '/api/auth';

export interface LoginData {
  username: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  risk_level: string;
  theme: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export const authApi = {
  login: async (credentials: LoginData): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post(`${API_URL}/login`, formData);
    return response.data;
  },

  register: async (userData: any) => {
    const response = await api.post(`${API_URL}/register`, userData);
    return response.data;
  },

  getDemoInfo: async () => {
    const response = await api.get(`${API_URL}/demo-info`);
    return response.data;
  },
};