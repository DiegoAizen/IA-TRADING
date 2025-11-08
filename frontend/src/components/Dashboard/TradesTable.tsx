// frontend/src/components/Dashboard/TradesTable.tsx - ACTUALIZADO
import React from 'react';

interface OpenPosition {
  symbol: string;
  type: string;
  volume: number;
  profit: number;
  open_price: number;
}

interface RecentTrade {
  id: number;
  symbol: string;
  type: string;
  volume: number;
  profit: number;
  status: string;
  timestamp: string;
}

interface TradesTableProps {
  openPositions: OpenPosition[];
  recentTrades: RecentTrade[];
  loading?: boolean;
}

const TradesTable: React.FC<TradesTableProps> = ({ openPositions, recentTrades, loading = false }) => {
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div className="text-center text-gray-400">Cargando operaciones...</div>
      </div>
    );
  }

  const tradesToShow = openPositions.length > 0 ? openPositions : recentTrades.slice(0, 3);

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">
          {openPositions.length > 0 ? 'Operaciones Abiertas' : 'Operaciones Recientes'}
        </h3>
        <span className={`px-3 py-1 text-sm rounded-full ${
          openPositions.length > 0 ? 'bg-blue-600 text-white' : 'bg-gray-600 text-gray-300'
        }`}>
          {openPositions.length > 0 ? `${openPositions.length} activas` : 'Sin operaciones abiertas'}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Símbolo</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Tipo</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Volumen</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Precio</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Beneficio</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Estado</th>
            </tr>
          </thead>
          <tbody>
            {tradesToShow.map((trade, index) => (
              <tr key={index} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors">
                <td className="py-3 px-4">
                  <span className="font-medium text-white">{trade.symbol}</span>
                </td>
                <td className="py-3 px-4">
                  <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                    trade.type === 'BUY' || trade.type === 'buy'
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                      : 'bg-red-500/20 text-red-400 border border-red-500/30'
                  }`}>
                    {trade.type === 'BUY' || trade.type === 'buy' ? '🔼 COMPRA' : '🔻 VENTA'}
                  </span>
                </td>
                <td className="py-3 px-4 text-gray-300">{trade.volume}</td>
                <td className="py-3 px-4 text-gray-300">
                  {'open_price' in trade ? trade.open_price : 'N/A'}
                </td>
                <td className="py-3 px-4">
                  <span className={`font-medium ${
                    trade.profit >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    ${trade.profit.toFixed(2)}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                    'status' in trade && trade.status === 'open'
                      ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                  }`}>
                    {'status' in trade ? trade.status : 'Abierta'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {tradesToShow.length === 0 && (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">📊</div>
            <p className="text-gray-400">No hay operaciones</p>
            <p className="text-gray-500 text-sm mt-1">Las operaciones aparecerán aquí cuando tengas posiciones abiertas</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TradesTable;