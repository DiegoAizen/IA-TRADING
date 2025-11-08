import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useBot } from '../../context/BotContext';
import { configApi } from '../../api/configApi';

type RiskLevel = 'low' | 'moderate' | 'aggressive';

const RiskSelector: React.FC = () => {
  const { user } = useAuth();
  const { updateBotSettings } = useBot();
  const [riskLevel, setRiskLevel] = useState<RiskLevel>('moderate');
  const [loading, setLoading] = useState(false);

  // Cargar perfil de riesgo actual del usuario
  useEffect(() => {
    if (user?.risk_level) {
      setRiskLevel(user.risk_level as RiskLevel);
    }
  }, [user]);

  const riskConfig = {
    low: {
      label: 'Conservador',
      description: 'Bajo riesgo, ganancias estables',
      color: 'bg-green-500',
      maxDrawdown: '5%',
      dailyTrades: '1-2',
      profitTarget: '2%',
      botSettings: {
        trading_strategy: 'conservative',
        max_open_trades: 2,
        max_drawdown: 5.0,
        daily_loss_limit: 2.0,
        default_lot_size: 0.05
      }
    },
    moderate: {
      label: 'Moderado',
      description: 'Balance entre riesgo y recompensa',
      color: 'bg-yellow-500',
      maxDrawdown: '10%',
      dailyTrades: '3-5',
      profitTarget: '5%',
      botSettings: {
        trading_strategy: 'moderate',
        max_open_trades: 5,
        max_drawdown: 10.0,
        daily_loss_limit: 5.0,
        default_lot_size: 0.1
      }
    },
    aggressive: {
      label: 'Agresivo',
      description: 'Alto riesgo, máximo potencial',
      color: 'bg-red-500',
      maxDrawdown: '20%',
      dailyTrades: '5-10',
      profitTarget: '10%',
      botSettings: {
        trading_strategy: 'aggressive',
        max_open_trades: 10,
        max_drawdown: 20.0,
        daily_loss_limit: 10.0,
        default_lot_size: 0.2
      }
    }
  };

  const handleRiskChange = async (level: RiskLevel) => {
    setLoading(true);
    try {
      // Actualizar perfil de riesgo del usuario
      await configApi.updateUserConfig({
        risk_level: level,
        confidence_threshold: riskConfig[level].botSettings.default_lot_size * 100
      });

      // Actualizar configuración del bot
      await updateBotSettings(riskConfig[level].botSettings);
      
      setRiskLevel(level);
      
      console.log(`✅ Perfil de riesgo actualizado a: ${level}`);
      console.log(`🤖 Configuración del bot:`, riskConfig[level].botSettings);
    } catch (error) {
      console.error('Error al actualizar perfil de riesgo:', error);
    } finally {
      setLoading(false);
    }
  };

  const currentConfig = riskConfig[riskLevel];

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4">Perfil de Riesgo</h3>
      
      {/* Selector de riesgo */}
      <div className="flex space-x-2 mb-6">
        {(['low', 'moderate', 'aggressive'] as RiskLevel[]).map((level) => (
          <button
            key={level}
            onClick={() => handleRiskChange(level)}
            disabled={loading}
            className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-all ${
              riskLevel === level
                ? `${riskConfig[level].color} text-white shadow-lg`
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {loading && riskLevel === level ? '⏳' : riskConfig[level].label}
          </button>
        ))}
      </div>

      {/* Información del nivel seleccionado */}
      <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center mb-3">
          <div className={`w-3 h-3 rounded-full ${currentConfig.color} mr-2`}></div>
          <span className="text-white font-medium">{currentConfig.label}</span>
          {loading && <span className="ml-2 text-yellow-400 text-sm">Actualizando...</span>}
        </div>
        
        <p className="text-gray-400 text-sm mb-4">{currentConfig.description}</p>
        
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-xs text-gray-500 mb-1">Max Drawdown</div>
            <div className="text-white font-medium">{currentConfig.maxDrawdown}</div>
          </div>
          <div>
            <div className="text-xs text-gray-500 mb-1">Operaciones/día</div>
            <div className="text-white font-medium">{currentConfig.dailyTrades}</div>
          </div>
          <div>
            <div className="text-xs text-gray-500 mb-1">Objetivo</div>
            <div className="text-white font-medium">{currentConfig.profitTarget}</div>
          </div>
        </div>

        {/* Configuración actual del bot */}
        <div className="mt-4 p-3 bg-blue-500/20 rounded border border-blue-500/30">
          <div className="text-xs text-blue-400">
            <div>🤖 Estrategia: <strong>{currentConfig.botSettings.trading_strategy}</strong></div>
            <div>📊 Lote: <strong>{currentConfig.botSettings.default_lot_size}</strong></div>
            <div>⚡ Máx. operaciones: <strong>{currentConfig.botSettings.max_open_trades}</strong></div>
          </div>
        </div>
      </div>

      <div className="mt-4 p-3 bg-green-500/20 rounded-lg border border-green-500/30">
        <p className="text-green-400 text-sm text-center">
          ✅ La IA usará este perfil para tomar decisiones
        </p>
      </div>
    </div>
  );
};

export default RiskSelector;