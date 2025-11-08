// frontend/src/hooks/useDashboard.ts
import { useState, useEffect } from 'react';
import { dashboardApi } from '../api/dashboardApi';
import { useAuth } from '../context/AuthContext';

interface DashboardStats {
  balance: number;
  equity: number;
  margin: number;
  free_margin: number;
  performance: {
    profit_today: number;
    trades_today: number;
    win_rate_today: number;
    best_trade_today: number;
    worst_trade_today: number;
  };
  bot_status: {
    status: string;
    auto_trading: boolean;
    strategy: string;
    last_activity: string | null;
  };
  summary: {
    total_trades: number;
    open_trades: number;
    win_rate: number;
    total_profit: number;
  };
}

interface MarketOverview {
  market_status: string;
  active_symbols: Array<{
    symbol: string;
    bid: number;
    ask: number;
    spread: number;
    change: number;
    trend: string;
    volume: string;
  }>;
  market_news: Array<{
    title: string;
    impact: string;
    currency: string;
    timestamp: string;
  }>;
}

interface RecentActivity {
  recent_trades: Array<{
    id: number;
    symbol: string;
    type: string;
    volume: number;
    profit: number;
    status: string;
    timestamp: string;
  }>;
  recent_signals: Array<{
    symbol: string;
    signal: string;
    confidence: number;
    timestamp: string;
    strength: string;
  }>;
  system_alerts: Array<{
    type: string;
    message: string;
    timestamp: string;
  }>;
  open_positions: Array<{
    symbol: string;
    type: string;
    volume: number;
    profit: number;
    open_price: number;
  }>;
}

export const useDashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [marketOverview, setMarketOverview] = useState<MarketOverview | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  const loadDashboardData = async () => {
    if (!isAuthenticated) return;

    try {
      setLoading(true);
      setError(null);

      // Cargar datos en paralelo
      const [statsData, marketData, activityData] = await Promise.all([
        dashboardApi.getStats(),
        dashboardApi.getMarketOverview(),
        dashboardApi.getRecentActivity()
      ]);

      setStats(statsData);
      setMarketOverview(marketData);
      setRecentActivity(activityData);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Error cargando datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadDashboardData();
      // Actualizar cada 30 segundos
      const interval = setInterval(loadDashboardData, 30000);
      return () => clearInterval(interval);
    } else {
      setStats(null);
      setMarketOverview(null);
      setRecentActivity(null);
    }
  }, [isAuthenticated]);

  return {
    stats,
    marketOverview,
    recentActivity,
    loading,
    error,
    refresh: loadDashboardData
  };
};