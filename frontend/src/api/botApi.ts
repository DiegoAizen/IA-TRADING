import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const API_URL = 'http://localhost:8000/api/bot';

// Crear instancia de axios con interceptor
const api = axios.create({
    baseURL: 'http://localhost:8000',
});

// Interceptor para agregar token automáticamente
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 || error.response?.status === 403) {
            // Token expirado o inválido - hacer logout
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_data');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export interface BotStatus {
    status: 'active' | 'stopped' | 'starting' | 'stopping';
    auto_trading: boolean;
    trading_strategy: string;
    max_open_trades: number;
    current_trades: number;
    last_signal: string;
    max_drawdown: number; // ⬅️ AGREGAR ESTE CAMPO
    performance_today: {
        trades: number;
        win_rate: number;
        profit: number;
    };
}

export const botApi = {
    getStatus: async (): Promise<BotStatus> => {
        const response = await api.get(`${API_URL}/status`);
        return response.data;
    },

    start: async (): Promise<any> => {
        const response = await api.post(`${API_URL}/start`);
        return response.data;
    },

    stop: async (): Promise<any> => {
        const response = await api.post(`${API_URL}/stop`);
        return response.data;
    },

    updateSettings: async (settings: any): Promise<any> => {
        const response = await api.put(`${API_URL}/settings`, settings);
        return response.data;
    }
};