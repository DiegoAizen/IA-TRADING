// frontend/src/pages/DashboardPage.tsx - ACTUALIZADO
import React from 'react';
import Header from '../components/Layout/Header';
import Sidebar from '../components/Layout/Sidebar';
import StatsCard from '../components/Dashboard/StatsCard';
import Charts from '../components/Dashboard/Charts';
import TradesTable from '../components/Dashboard/TradesTable';
import BotSwitch from '../components/BotControl/BotSwitch';
import RiskSelector from '../components/BotControl/RiskSelector';
import MT5Connection from '../components/MT5/MT5Connection';
import AIConfig from '../components/AI/AIConfig';
import AIAnalysis from '../components/AI/AIAnalysis';
import { useDashboard } from '../hooks/useDashboard';
import NewsSection from '../components/News/NewsSection';


interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: string;
  color?: 'green' | 'red' | 'blue' | 'purple' | 'gray'; // 👈 añade "gray"
}

const DashboardPage: React.FC = () => {
  const { stats, marketOverview, recentActivity, loading, error } = useDashboard();

  // Función para formatear dinero
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  // Función para determinar tendencia
  const getTrend = (value: number): 'up' | 'down' | 'neutral' => {
    if (value > 0) return 'up';
    if (value < 0) return 'down';
    return 'neutral';
  };

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-gray-900 flex">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Header />
          <main className="flex-1 p-6 flex items-center justify-center">
            <div className="text-white text-lg">Cargando dashboard...</div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <Header />

        <main className="flex-1 p-6 overflow-auto">
          {error && (
            <div className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-lg">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {/* Stats Grid con datos reales */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatsCard
              title="Balance Total"
              value={stats ? formatCurrency(stats.balance) : '$0.00'}
              subtitle={stats ? `Equity: ${formatCurrency(stats.equity)}` : 'Sin conexión MT5'}
              trend={stats && stats.equity > stats.balance ? 'up' : stats && stats.equity < stats.balance ? 'down' : 'neutral'}
              icon="💰"
              color={stats && stats.equity > stats.balance ? 'green' : stats && stats.equity < stats.balance ? 'red' : 'blue'}
            />
            <StatsCard
              title="Ganancia Hoy"
              value={stats ? formatCurrency(stats.performance.profit_today) : '$0.00'}
              subtitle={stats ? `${stats.performance.trades_today} operaciones hoy` : 'Sin datos'}
              trend={getTrend(stats?.performance.profit_today || 0)}
              icon="📈"
              color={
                stats?.performance.profit_today && stats.performance.profit_today > 0
                  ? 'green'
                  : stats?.performance.profit_today && stats.performance.profit_today < 0
                    ? 'red'
                    : 'blue'
              }
            />
            <StatsCard
              title="Operaciones Abiertas"
              value={stats ? stats.summary.open_trades.toString() : '0'}
              subtitle={stats ? `${stats.summary.total_trades} totales` : 'Conecta MT5'}
              trend="neutral"
              icon="⚡"
              color="purple"
            />
            <StatsCard
              title="Tasa de Éxito"
              value={stats ? `${stats.summary.win_rate.toFixed(1)}%` : '0%'}
              subtitle={stats ? `${stats.summary.total_trades} operaciones` : 'Sin historial'}
              trend={stats && stats.summary.win_rate > 50 ? 'up' : 'down'}
              icon="🎯"
              color={stats && stats.summary.win_rate > 50 ? 'green' : 'red'}
            />
          </div>

          {/* Sección de IA y MT5 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <AIConfig />
            <MT5Connection />
          </div>

          {/* Análisis IA y Controles */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2">
              <AIAnalysis />
            </div>
            <div className="space-y-6">
              <BotSwitch />
              <RiskSelector />
            </div>
          </div>

          {/* Charts y Trading con datos reales */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div>
              <Charts
                marketData={marketOverview?.active_symbols || []}
                loading={loading}
              />
            </div>
             
            <div>
              <TradesTable
                openPositions={recentActivity?.open_positions || []}
                recentTrades={recentActivity?.recent_trades || []}
                loading={loading}
              />
            </div>
          </div>
            <div className="lg:col-span-2">
              <NewsSection /> {/* ← COMPONENTE NUEVO */}
            </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;