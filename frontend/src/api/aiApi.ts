//fronted//src/api/aiAPis.tsx
import api from './axiosConfig';

const API_URL = '/api/ai';

// Renombrar la interfaz para evitar conflicto
export interface AIProviderInfo {
  id: string;
  name: string;
  models: string[];
  api_url: string;
}

export interface AIConfig {
  id?: number;
  ai_provider: string;
  ai_model: string;
  api_key?: string;
  is_active: boolean;
  max_tokens: number;
  temperature: number;
  confidence_threshold: number;
  last_used?: string;
  total_requests?: number;
}

export interface AnalysisRequest {
  symbol: string;
  analysis_type?: string;
}

export interface AnalysisResult {
  success: boolean;
  symbol: string;
  analysis_type: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reasoning: string;
  additional_data: any;
  processing_time: number;
  ai_provider: string;
  ai_model: string;
}

export interface MultipleAnalysisResult {
  success: boolean;
  total_analyzed: number;
  successful: number;
  failed: number;
  buy_opportunities: AnalysisResult[];
  sell_opportunities: AnalysisResult[];
  all_results: AnalysisResult[];
  errors: any[];
}

export interface AnalysisHistory {
  id: number;
  symbol: string;
  analysis_type: string;
  signal: string;
  confidence: number;
  ai_provider: string;
  ai_model: string;
  processing_time: number;
  created_at: string;
}

export const aiApi = {
  // Configuración
  getConfig: async (): Promise<AIConfig> => {
    const response = await api.get(`${API_URL}/config`);
    return response.data;
  },

  updateConfig: async (config: Partial<AIConfig>): Promise<AIConfig> => {
    const response = await api.put(`${API_URL}/config`, config);
    return response.data;
  },

  getProviders: async (): Promise<{ providers: AIProviderInfo[]; default_provider: string }> => {
    const response = await api.get(`${API_URL}/providers`);
    return response.data;
  },

  testApiKey: async (provider: string, apiKey: string): Promise<{ valid: boolean; message: string }> => {
    const response = await api.post(`${API_URL}/test-api-key`, {
      provider,
      api_key: apiKey
    });
    return response.data;
  },

  // Análisis
  analyzeSymbol: async (symbol: string, analysisType: string = 'comprehensive'): Promise<AnalysisResult> => {
    const response = await api.post(`${API_URL}/analyze/${symbol}?analysis_type=${analysisType}`);
    return response.data;
  },

  analyzeMultiple: async (symbols: string[], analysisType: string = 'technical'): Promise<MultipleAnalysisResult> => {
    const response = await api.post(`${API_URL}/analyze-multiple`, {
      symbols,
      analysis_type: analysisType
    });
    return response.data;
  },

  getAnalysisHistory: async (symbol?: string, limit: number = 20): Promise<{ history: AnalysisHistory[]; total: number }> => {
    const url = symbol 
      ? `${API_URL}/analysis-history?symbol=${symbol}&limit=${limit}`
      : `${API_URL}/analysis-history?limit=${limit}`;
    
    const response = await api.get(url);
    return response.data;
  }
};