import api from './axiosConfig';

const API_URL = '/api/mt5';

export interface MT5Config {
  server: string;
  login: number;
  password: string;
  timeout?: number;
  portable?: boolean;
}

export interface MT5Status {
  config: {
    server: string;
    login: number;
    is_connected: boolean;
    last_connection: string;
  };
  connection: {
    connected: boolean;
    account_info: any;
  };
}

export interface AccountInfo {
  login: number;
  balance: number;
  equity: number;
  margin: number;
  free_margin: number;
  leverage: number;
  currency: string;
  server: string;
  profit: number;
}

export interface PortfolioStatus {
  success: boolean;
  account_info: AccountInfo;
  open_positions: any[];
  summary: {
    total_positions: number;
    total_profit: number;
    total_volume: number;
    buy_positions: number;
    sell_positions: number;
  };
}

export const mt5Api = {
  connect: async (config: MT5Config): Promise<any> => {
    const response = await api.post(`${API_URL}/connect`, config);
    return response.data;
  },

  disconnect: async (): Promise<any> => {
    const response = await api.post(`${API_URL}/disconnect`);
    return response.data;
  },

  getStatus: async (): Promise<MT5Status> => {
    const response = await api.get(`${API_URL}/status`);
    return response.data;
  },

  getAccountInfo: async (): Promise<PortfolioStatus> => {
    const response = await api.get(`${API_URL}/account-info`);
    return response.data;
  },

  getSymbols: async (): Promise<any> => {
    const response = await api.get(`${API_URL}/symbols`);
    return response.data;
  },

  getMarketData: async (symbol: string): Promise<any> => {
    const response = await api.get(`${API_URL}/market-data/${symbol}`);
    return response.data;
  },

  testOrder: async (orderData: any): Promise<any> => {
    const response = await api.post(`${API_URL}/test-order`, orderData);
    return response.data;
  }
};