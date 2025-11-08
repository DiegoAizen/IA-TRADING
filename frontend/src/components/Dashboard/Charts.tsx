// frontend/src/components/Dashboard/Charts.tsx - ACTUALIZADO
import React from 'react';

interface MarketSymbol {
  symbol: string;
  bid: number;
  ask: number;
  spread: number;
  change: number;
  trend: string;
  volume: string;
}

interface ChartsProps {
  marketData: MarketSymbol[];
  loading?: boolean;
}

const Charts: React.FC<ChartsProps> = ({ marketData, loading = false }) => {
  if (loading) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div className="text-center text-gray-400">Cargando datos de mercado...</div>
      </div>
    );
  }

  const mainSymbol = marketData[0] || null;

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Análisis de Mercado</h3>
        <div className="flex space-x-2">
          <button className="px-3 py-1 text-xs bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors">
            1D
          </button>
          <button className="px-3 py-1 text-xs bg-blue-600 text-white rounded-lg transition-colors">
            1S
          </button>
          <button className="px-3 py-1 text-xs bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors">
            1M
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Gráfico principal */}
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-gray-300">
              {mainSymbol ? mainSymbol.symbol : 'EUR/USD'}
            </span>
            <span className={`text-sm font-medium ${
              mainSymbol?.change && mainSymbol.change > 0 ? 'text-green-400' : 
              mainSymbol?.change && mainSymbol.change < 0 ? 'text-red-400' : 'text-gray-400'
            }`}>
              {mainSymbol ? `${mainSymbol.change > 0 ? '+' : ''}${mainSymbol.change.toFixed(2)}%` : '0.00%'}
            </span>
          </div>
          <div className="h-48 bg-gradient-to-b from-gray-800 to-gray-900 rounded flex items-center justify-center">
            {mainSymbol ? (
              <div className="text-center">
                <div className="text-4xl mb-2">📈</div>
                <p className="text-white text-lg font-medium">{mainSymbol.bid}</p>
                <p className="text-gray-400 text-sm mt-1">Spread: {mainSymbol.spread}</p>
              </div>
            ) : (
              <div className="text-center">
                <div className="text-4xl mb-2">📊</div>
                <p className="text-gray-400 text-sm">Conecta MT5 para ver datos</p>
              </div>
            )}
          </div>
          <div className="flex justify-between mt-4 text-xs text-gray-400">
            <span>Bid: {mainSymbol?.bid.toFixed(5) || '0.00000'}</span>
            <span>Ask: {mainSymbol?.ask.toFixed(5) || '0.00000'}</span>
          </div>
        </div>

        {/* Mini gráficos */}
        <div className="space-y-4">
          {marketData.slice(0, 4).map((asset, index) => (
            <div key={index} className="bg-gray-900 rounded-lg p-3 border border-gray-700">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-300">{asset.symbol}</span>
                <span className={`text-sm font-medium ${
                  asset.change > 0 ? 'text-green-400' : asset.change < 0 ? 'text-red-400' : 'text-gray-400'
                }`}>
                  {asset.change > 0 ? '+' : ''}{asset.change.toFixed(2)}%
                </span>
              </div>
              <div className="h-8 mt-2 bg-gray-800 rounded flex items-center justify-center">
                <div className={`w-full h-1 rounded-full ${
                  asset.change > 0 ? 'bg-green-500' : asset.change < 0 ? 'bg-red-500' : 'bg-gray-500'
                }`}></div>
              </div>
              <div className="flex justify-between mt-2 text-xs text-gray-400">
                <span>{asset.bid.toFixed(5)}</span>
                <span>Vol: {asset.volume}</span>
              </div>
            </div>
          ))}
          
          {marketData.length === 0 && (
            <div className="text-center py-4 text-gray-400">
              No hay datos de mercado disponibles
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Charts;