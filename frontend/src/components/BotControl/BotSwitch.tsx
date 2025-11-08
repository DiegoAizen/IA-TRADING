import React from 'react';
import { useBot } from '../../context/BotContext';

const BotSwitch: React.FC = () => {
  const { botStatus, isBotActive, startBot, stopBot, loading } = useBot();

  const toggleBot = async () => {
    if (isBotActive) {
      await stopBot();
    } else {
      await startBot();
    }
  };

  // Mapeo de estrategias a nombres legibles
  const strategyNames: { [key: string]: string } = {
    'conservative': 'Conservadora',
    'moderate': 'Moderada',
    'aggressive': 'Agresiva'
  };

  if (!botStatus) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div className="text-center text-gray-400">
          Cargando estado del bot...
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-white">Control del Bot</h3>
          <p className={`text-sm mt-1 ${isBotActive ? 'text-green-400' : 'text-gray-400'
            }`}>
            {isBotActive ? 'Bot activo y operando' : 'Bot en espera'}
          </p>
        </div>

        <button
          onClick={toggleBot}
          disabled={loading}
          className={`relative inline-flex h-8 w-14 items-center rounded-full transition-all duration-300 ${isBotActive ? 'bg-green-500' : 'bg-gray-600'
            } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          <span
            className={`inline-block h-6 w-6 transform rounded-full bg-white transition-all duration-300 ${isBotActive ? 'translate-x-7' : 'translate-x-1'
              } ${loading ? 'animate-pulse' : ''}`}
          />
        </button>
      </div>

      <div className="space-y-3 mt-4">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Estado:</span>
          <span className={`font-medium ${isBotActive ? 'text-green-400' : 'text-yellow-400'
            }`}>
            {isBotActive ? 'OPERANDO' : 'EN ESPERA'}
          </span>
        </div>

        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Estrategia:</span>
          <span className="text-blue-400 font-medium capitalize">
            {strategyNames[botStatus.trading_strategy] || botStatus.trading_strategy}
          </span>
        </div>

        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Trading Auto:</span>
          <span className={`font-medium ${botStatus.auto_trading ? 'text-green-400' : 'text-gray-400'
            }`}>
            {botStatus.auto_trading ? 'ACTIVADO' : 'DESACTIVADO'}
          </span>
        </div>

        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Operaciones hoy:</span>
          <span className="text-gray-300">{botStatus.performance_today.trades}</span>
        </div>

        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Tasa de éxito:</span>
          <span className="text-green-400">{botStatus.performance_today.win_rate}%</span>
        </div>

        {/* Información adicional del perfil de riesgo */}
        <div className="mt-4 p-3 bg-gray-700/50 rounded border border-gray-600">
          <div className="text-xs text-gray-300">
            <div>📈 <strong>Perfil activo:</strong> {strategyNames[botStatus.trading_strategy]}</div>
            <div>⚡ <strong>Máx. operaciones:</strong> {botStatus.max_open_trades}</div>
            <div>🛡️ <strong>Drawdown máx.:</strong> {botStatus.max_drawdown || 'N/A'}%</div>
          </div>
        </div>
      </div>

      {loading && (
        <div className="mt-4 p-3 bg-blue-500/20 rounded-lg border border-blue-500/30">
          <p className="text-blue-400 text-sm text-center">
            {isBotActive ? 'Deteniendo bot...' : 'Iniciando bot...'}
          </p>
        </div>
      )}

      {isBotActive && (
        <div className="mt-4 p-3 bg-green-500/20 rounded-lg border border-green-500/30">
          <p className="text-green-400 text-sm text-center">
            🤖 Bot activo con estrategia {strategyNames[botStatus.trading_strategy]}
          </p>
        </div>
      )}
    </div>
  );
};

export default BotSwitch;