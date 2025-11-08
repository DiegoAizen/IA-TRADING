import React, { createContext, useContext, useState, useEffect } from 'react';
import { mt5Api, MT5Config, MT5Status, PortfolioStatus } from '../api/mt5Api';
import { useAuth } from './AuthContext'; // ✅ Importar useAuth

interface MT5ContextType {
  mt5Status: MT5Status | null;
  portfolio: PortfolioStatus | null;
  isConnected: boolean;
  connectMT5: (config: MT5Config) => Promise<void>;
  disconnectMT5: () => Promise<void>;
  refreshStatus: () => Promise<void>;
  loading: boolean;
  error: string | null;
}

const MT5Context = createContext<MT5ContextType | undefined>(undefined);

export const MT5Provider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mt5Status, setMt5Status] = useState<MT5Status | null>(null);
  const [portfolio, setPortfolio] = useState<PortfolioStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth(); // ✅ Usar autenticación

  // Cargar estado solo si está autenticado
  useEffect(() => {
    if (isAuthenticated) {
      refreshStatus();
    } else {
      // ✅ Limpiar estado si no está autenticado
      setMt5Status(null);
      setPortfolio(null);
      setError(null);
    }
  }, [isAuthenticated]); // ✅ Dependencia de autenticación

  const refreshStatus = async () => {
    if (!isAuthenticated) {
      return; // ✅ No cargar si no está autenticado
    }

    try {
      setLoading(true);
      const status = await mt5Api.getStatus();
      setMt5Status(status);

      // Si está conectado, cargar información de portfolio
      if (status.connection.connected) {
        const portfolioInfo = await mt5Api.getAccountInfo();
        setPortfolio(portfolioInfo);
      }
    } catch (err) {
      console.error('Error refreshing MT5 status:', err);
    } finally {
      setLoading(false);
    }
  };

  const connectMT5 = async (config: MT5Config) => {
    if (!isAuthenticated) {
      setError('Usuario no autenticado');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await mt5Api.connect(config);
      await refreshStatus(); // Recargar estado completo
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error conectando a MT5');
      console.error('Error connecting to MT5:', err);
    } finally {
      setLoading(false);
    }
  };

  const disconnectMT5 = async () => {
    if (!isAuthenticated) {
      setError('Usuario no autenticado');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await mt5Api.disconnect();
      await refreshStatus(); // Recargar estado completo
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error desconectando de MT5');
      console.error('Error disconnecting from MT5:', err);
    } finally {
      setLoading(false);
    }
  };

  const isConnected = mt5Status?.connection.connected || false;

  return (
    <MT5Context.Provider value={{
      mt5Status,
      portfolio,
      isConnected,
      connectMT5,
      disconnectMT5,
      refreshStatus,
      loading,
      error
    }}>
      {children}
    </MT5Context.Provider>
  );
};

export const useMT5 = () => {
  const context = useContext(MT5Context);
  if (context === undefined) {
    throw new Error('useMT5 must be used within a MT5Provider');
  }
  return context;
};