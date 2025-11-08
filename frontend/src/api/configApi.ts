// frontend/src/api/configApi.ts - VERSIÓN CORREGIDA
import api from './axiosConfig';

const API_URL = '/api/config';

export interface UserConfig {
  selected_assets: string[];
  notifications_enabled: boolean;
  trading_hours: string;
  risk_level: string;
  confidence_threshold: number;
  default_lot_size: number;
  theme: string;
}

export interface BotConfig {
  id?: number;
  user_id: number;
  bot_name: string;
  is_active: boolean;
  auto_trading: boolean;
  max_drawdown: number;
  daily_loss_limit: number;
  max_open_trades: number;
  trading_strategy: string;
  default_lot_size: number;
  max_lot_size: number;
  min_lot_size: number;
  allowed_symbols: string;
  trading_hours_start: string;
  trading_hours_end: string;
  trading_days: string;
  use_trailing_stop: boolean;
  trailing_stop_distance: number;
  default_stop_loss: number;
  default_take_profit: number;
  email_notifications: boolean;
  sound_notifications: boolean;
}

export interface FullConfig {
  user_settings: UserConfig;
  bot_settings: BotConfig;
}

export const configApi = {
  // CONFIGURACIÓN GENERAL
  getConfig: async (): Promise<FullConfig> => {
    const response = await api.get(API_URL);
    return response.data;
  },

  updateUserConfig: async (config: Partial<UserConfig>): Promise<any> => {
    const response = await api.put(`${API_URL}/user`, config);
    return response.data;
  },

  updateBotConfig: async (config: Partial<BotConfig>): Promise<any> => {
    const response = await api.put(`${API_URL}/bot`, config);
    return response.data;
  },

  getAvailableAssets: async (): Promise<any> => {
    const response = await api.get(`${API_URL}/available-assets`);
    return response.data;
  },

  getRiskProfiles: async (): Promise<any> => {
    const response = await api.get(`${API_URL}/risk-profiles`);
    return response.data;
  },

   getBotStatus: async (): Promise<any> => {
    try {
      const response = await api.get('/bot/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching bot status:', error);
      throw error;
    }
  },

  updateBotSettings: async (config: Partial<BotConfig>): Promise<any> => {
    try {
      const response = await api.put('/bot/settings', config);
      return response.data;
    } catch (error) {
      console.error('Error updating bot settings:', error);
      throw error;
    }
  }
};