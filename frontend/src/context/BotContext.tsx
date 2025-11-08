// frontend/src/context/BotContext.tsx - CORREGIR
import React, { createContext, useContext, useState, useEffect } from 'react';
import { botApi } from '../api/botApi';
import { useAuth } from './AuthContext'; // ✅ Importar useAuth

interface BotStatus {
  status: 'active' | 'stopped' | 'starting' | 'stopping';
  auto_trading: boolean;
  trading_strategy: string;
  max_open_trades: number;
  current_trades: number;
  last_signal: string;
  max_drawdown: number;
  performance_today: {
    trades: number;
    win_rate: number;
    profit: number;
  };
}

interface BotContextType {
  botStatus: BotStatus | null;
  isBotActive: boolean;
  startBot: () => Promise<void>;
  stopBot: () => Promise<void>;
  updateBotSettings: (settings: any) => Promise<void>;
  loading: boolean;
  error: string | null;
}

const BotContext = createContext<BotContextType | undefined>(undefined);

export const BotProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [botStatus, setBotStatus] = useState<BotStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth(); // ✅ Usar autenticación

  // Cargar estado del bot solo si está autenticado
  useEffect(() => {
    if (isAuthenticated) {
      loadBotStatus();
    } else {
      // Limpiar estado si no está autenticado
      setBotStatus(null);
    }
  }, [isAuthenticated]); // ✅ Dependencia de autenticación

  const loadBotStatus = async () => {
    if (!isAuthenticated) {
      return; // ✅ No cargar si no está autenticado
    }

    try {
      setLoading(true);
      const status = await botApi.getStatus();
      setBotStatus(status);
    } catch (err) {
      console.error('Error loading bot status:', err);
      setError('Error al cargar estado del bot');
    } finally {
      setLoading(false);
    }
  };

  const startBot = async () => {
    if (!isAuthenticated) {
      setError('Usuario no autenticado');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await botApi.start();
      setBotStatus(prev => prev ? { ...prev, status: 'active' } : null);
      await loadBotStatus();
    } catch (err) {
      setError('Error al iniciar el bot');
      console.error('Error starting bot:', err);
    } finally {
      setLoading(false);
    }
  };

  const stopBot = async () => {
    if (!isAuthenticated) {
      setError('Usuario no autenticado');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await botApi.stop();
      setBotStatus(prev => prev ? { ...prev, status: 'stopped' } : null);
      await loadBotStatus();
    } catch (err) {
      setError('Error al detener el bot');
      console.error('Error stopping bot:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateBotSettings = async (settings: any) => {
    if (!isAuthenticated) {
      setError('Usuario no autenticado');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await botApi.updateSettings(settings);
      await loadBotStatus();
    } catch (err) {
      setError('Error al actualizar configuración');
      console.error('Error updating bot settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const isBotActive = botStatus?.status === 'active';

  return (
    <BotContext.Provider value={{
      botStatus,
      isBotActive,
      startBot,
      stopBot,
      updateBotSettings,
      loading,
      error
    }}>
      {children}
    </BotContext.Provider>
  );
};

export const useBot = () => {
  const context = useContext(BotContext);
  if (context === undefined) {
    throw new Error('useBot must be used within a BotProvider');
  }
  return context;
};