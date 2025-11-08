// frontend/src/context/AIContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { aiApi, AIConfig, AIProviderInfo, AnalysisResult, AnalysisHistory } from '../api/aiApi';
import { useAuth } from './AuthContext';

interface AIContextType {
  // Configuración
  aiConfig: AIConfig | null;
  providers: AIProviderInfo[];
  loading: boolean;
  error: string | null;
  
  // Acciones
  loadAIConfig: () => Promise<void>;
  updateAIConfig: (config: Partial<AIConfig>) => Promise<void>;
  testApiKey: (provider: string, apiKey: string) => Promise<boolean>;
  
  // Análisis
  analyzing: boolean;
  analyzeSymbol: (symbol: string, analysisType?: string) => Promise<AnalysisResult | null>;
  analysisHistory: AnalysisHistory[];
  loadAnalysisHistory: (symbol?: string) => Promise<void>;
}

const AIContext = createContext<AIContextType | undefined>(undefined);

export const AIProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [aiConfig, setAiConfig] = useState<AIConfig | null>(null);
  const [providers, setProviders] = useState<AIProviderInfo[]>([]);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth(); 

  useEffect(() => {
    if (isAuthenticated) {
      loadAIConfig();
      loadProviders();
      loadAnalysisHistory();
    } else {

      setAiConfig(null);
      setProviders([]);
      setAnalysisHistory([]);
      setError(null);
    }
  }, [isAuthenticated]);

  const loadAIConfig = async () => {
    if (!isAuthenticated) return; 

    try {
      setLoading(true);
      const config = await aiApi.getConfig();
      setAiConfig(config);
    } catch (err) {
      console.error('Error loading AI config:', err);
      setError('Error cargando configuración de IA');
    } finally {
      setLoading(false);
    }
  };

  const loadProviders = async () => {
    if (!isAuthenticated) return;

    try {
      const data = await aiApi.getProviders();
      setProviders(data.providers);
    } catch (err) {
      console.error('Error loading AI providers:', err);
    }
  };

  const loadAnalysisHistory = async (symbol?: string) => {
    if (!isAuthenticated) {
      setAnalysisHistory([]);
      return;
    }

    try {
      const data = await aiApi.getAnalysisHistory(symbol);
      setAnalysisHistory(data.history|| []);
    } catch (err) {
      console.error('Error loading analysis history:', err);
      setAnalysisHistory([]);
    }
  };

  const updateAIConfig = async (config: Partial<AIConfig>): Promise<void> => {
    if (!isAuthenticated) {
      throw new Error('Usuario no autenticado');
    }

    try {
      setLoading(true);
      setError(null);
      const updatedConfig = await aiApi.updateConfig(config);
      setAiConfig(updatedConfig);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error actualizando configuración';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const testApiKey = async (provider: string, apiKey: string): Promise<boolean> => {
    if (!isAuthenticated) {
      throw new Error('Usuario no autenticado');
    }

    try {
      setLoading(true);
      const result = await aiApi.testApiKey(provider, apiKey);
      return result.valid;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error probando API key';
      setError(errorMsg);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const analyzeSymbol = async (symbol: string, analysisType: string = 'comprehensive'): Promise<AnalysisResult | null> => {
    if (!isAuthenticated) {
      throw new Error('Usuario no autenticado');
    }

    try {
      setAnalyzing(true);
      setError(null);
      const result = await aiApi.analyzeSymbol(symbol, analysisType);
      
      await loadAnalysisHistory();
      
      return result;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error en análisis';
      setError(errorMsg);
      return null;
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <AIContext.Provider value={{
      aiConfig,
      providers,
      loading,
      error,
      loadAIConfig,
      updateAIConfig,
      testApiKey,
      analyzing,
      analyzeSymbol,
      analysisHistory,
      loadAnalysisHistory
    }}>
      {children}
    </AIContext.Provider>
  );
};

export const useAI = () => {
  const context = useContext(AIContext);
  if (context === undefined) {
    throw new Error('useAI must be used within a AIProvider');
  }
  return context;
};