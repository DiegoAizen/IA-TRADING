// frontend/src/pages/ConfigPage.tsx - VERSIÓN CORREGIDA
import React, { useState, useEffect } from 'react';
import Header from '../components/Layout/Header';
import Sidebar from '../components/Layout/Sidebar';
import { configApi, BotConfig } from '../api/configApi';

const ConfigPage: React.FC = () => {
  const [settings, setSettings] = useState<Partial<BotConfig>>({
    max_drawdown: 10,
    daily_loss_limit: 5,
    max_open_trades: 3,
    default_lot_size: 0.1,
    trading_strategy: 'moderate',
    allowed_symbols: 'EURUSD,GBPUSD,USDJPY,XAUUSD',
    auto_trading: false,
    default_stop_loss: 100,
    default_take_profit: 200
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCurrentSettings();
  }, []);

  const loadCurrentSettings = async () => {
    try {
      setLoading(true);
      // Usar getBotStatus en lugar de getBotConfig
      const botStatus = await configApi.getBotStatus();
      if (botStatus) {
        setSettings({
          max_drawdown: botStatus.max_drawdown || 10,
          daily_loss_limit: botStatus.daily_loss_limit || 5,
          max_open_trades: botStatus.max_open_trades || 3,
          default_lot_size: botStatus.default_lot_size || 0.1,
          trading_strategy: botStatus.trading_strategy || 'moderate',
          allowed_symbols: botStatus.allowed_symbols || 'EURUSD,GBPUSD,USDJPY,XAUUSD',
          auto_trading: botStatus.auto_trading || false,
          default_stop_loss: botStatus.default_stop_loss || 100,
          default_take_profit: botStatus.default_take_profit || 200
        });
      }
    } catch (error) {
      console.error('Error loading bot settings:', error);
      alert('Error cargando configuración');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      // Usar updateBotSettings en lugar de updateBotConfig
      await configApi.updateBotSettings(settings);
      alert('Configuración guardada correctamente');
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Error guardando configuración');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Header />
          <main className="flex-1 p-6 flex items-center justify-center">
            <div className="text-white">Cargando configuración...</div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h1 className="text-2xl font-bold text-white mb-6">Configuración Avanzada del Bot</h1>
            <p className="text-gray-400 mb-6">
              Configuración manual avanzada. Para perfiles predefinidos usa el "Modo Rápido" en el dashboard.
            </p>


            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Gestión de Riesgo */}
              <div className="bg-gray-700 p-4 rounded-lg">
                <h2 className="text-lg font-semibold text-white mb-4">Gestión de Riesgo</h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Drawdown Máximo (%)
                    </label>
                    <input
                      type="number"
                      value={settings.max_drawdown}
                      onChange={(e) => setSettings({ ...settings, max_drawdown: Number(e.target.value) })}
                      className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Pérdida Diaria Máxima (%)
                    </label>
                    <input
                      type="number"
                      value={settings.daily_loss_limit}
                      onChange={(e) => setSettings({ ...settings, daily_loss_limit: Number(e.target.value) })}
                      className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Stop Loss Default (pips)
                    </label>
                    <input
                      type="number"
                      value={settings.default_stop_loss}
                      onChange={(e) => setSettings({ ...settings, default_stop_loss: Number(e.target.value) })}
                      className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Take Profit Default (pips)
                    </label>
                    <input
                      type="number"
                      value={settings.default_take_profit}
                      onChange={(e) => setSettings({ ...settings, default_take_profit: Number(e.target.value) })}
                      className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                    />
                  </div>
                </div>
              </div>

              {/* Operaciones */}
              <div className="bg-gray-700 p-4 rounded-lg">
                <h2 className="text-lg font-semibold text-white mb-4">Operaciones</h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Máx. Operaciones Abiertas
                    </label>
                    <input
                      type="number"
                      value={settings.max_open_trades}
                      onChange={(e) => setSettings({ ...settings, max_open_trades: Number(e.target.value) })}
                      className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Tamaño de Lote Default
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={settings.default_lot_size}
                      onChange={(e) => setSettings({ ...settings, default_lot_size: Number(e.target.value) })}
                      className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                    />
                  </div>
                </div>
              </div>

              {/* Estrategia */}
              <div className="bg-gray-700 p-4 rounded-lg">
                <h2 className="text-lg font-semibold text-white mb-4">Estrategia</h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Estrategia de Trading
                    </label>
                    <select
                      value={settings.trading_strategy}
                      onChange={(e) => setSettings({ ...settings, trading_strategy: e.target.value })}
                      className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                    >
                      <option value="conservative">Conservadora</option>
                      <option value="moderate">Moderada</option>
                      <option value="aggressive">Agresiva</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Símbolos Permitidos
                    </label>
                    <input
                      type="text"
                      value={settings.allowed_symbols}
                      onChange={(e) => setSettings({ ...settings, allowed_symbols: e.target.value })}
                      className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                      placeholder="EURUSD,GBPUSD,USDJPY"
                    />
                    <p className="text-xs text-gray-400 mt-1">Separar por comas</p>
                  </div>
                </div>
              </div>

              {/* Trading Automático */}
              <div className="bg-gray-700 p-4 rounded-lg">
                <h2 className="text-lg font-semibold text-white mb-4">Trading Automático</h2>

                <div className="space-y-4">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="auto_trading"
                      checked={settings.auto_trading || false}
                      onChange={(e) => setSettings({ ...settings, auto_trading: e.target.checked })}
                      className="h-4 w-4 text-blue-600 bg-gray-600 border-gray-500 rounded"
                    />
                    <label htmlFor="auto_trading" className="ml-2 text-sm text-gray-300">
                      Trading Automático
                    </label>
                  </div>
                  <p className="text-xs text-gray-400">
                    Cuando está activado, el bot ejecutará operaciones automáticamente
                  </p>
                </div>
              </div>
            </div>

            {/* Botón Guardar */}
            <div className="mt-6 flex justify-end space-x-4">
              <button
                onClick={loadCurrentSettings}
                className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-6 rounded-lg transition duration-200"
              >
                Cancelar
              </button>
              <button
                onClick={handleSave}
                disabled={loading}
                className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-6 rounded-lg transition duration-200 disabled:opacity-50"
              >
                {loading ? 'Guardando...' : 'Guardar Configuración'}
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default ConfigPage;