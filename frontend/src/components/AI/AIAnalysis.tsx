import React, { useState } from 'react';
import { useAI } from '../../context/AIContext';

const AIAnalysis: React.FC = () => {
  const { analyzing, analyzeSymbol, analysisHistory, loadAnalysisHistory } = useAI();
  const [symbol, setSymbol] = useState('EURUSD');
  const [analysisType, setAnalysisType] = useState('comprehensive');
  const [currentAnalysis, setCurrentAnalysis] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!symbol.trim()) return;

    const result = await analyzeSymbol(symbol, analysisType);
    setCurrentAnalysis(result);
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'text-green-400';
      case 'SELL': return 'text-red-400';
      default: return 'text-yellow-400';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-400';
    if (confidence >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white">Análisis con IA</h3>
          <p className="text-sm text-gray-400 mt-1">
            Analiza símbolos en tiempo real usando IA
          </p>
        </div>
      </div>

      {/* Formulario de análisis */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Símbolo
          </label>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Ej: EURUSD, BTCUSD, XAUUSD"
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Tipo de Análisis
          </label>
          <select
            value={analysisType}
            onChange={(e) => setAnalysisType(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="technical">Técnico</option>
            <option value="sentiment">Sentimiento</option>
            <option value="comprehensive">Completo</option>
          </select>
        </div>

        <div className="flex items-end">
          <button
            onClick={handleAnalyze}
            disabled={analyzing || !symbol.trim()}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {analyzing ? '🔄 Analizando...' : '🚀 Analizar'}
          </button>
        </div>
      </div>

      {/* Resultado del análisis actual */}
      {currentAnalysis && (
        <div className="mb-6 p-4 bg-gray-900 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-white font-medium">
              📈 Análisis de {currentAnalysis.symbol}
            </h4>
            <div className="flex items-center space-x-4 text-sm">
              <span className="text-gray-400">
                Proveedor: {currentAnalysis.ai_provider}
              </span>
              <span className="text-gray-400">
                Tiempo: {currentAnalysis.processing_time?.toFixed(2)}s
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center p-3 bg-gray-800 rounded">
              <div className="text-sm text-gray-400 mb-1">Señal</div>
              <div className={`text-xl font-bold ${getSignalColor(currentAnalysis.signal)}`}>
                {currentAnalysis.signal}
              </div>
            </div>

            <div className="text-center p-3 bg-gray-800 rounded">
              <div className="text-sm text-gray-400 mb-1">Confianza</div>
              <div className={`text-xl font-bold ${getConfidenceColor(currentAnalysis.confidence)}`}>
                {currentAnalysis.confidence}%
              </div>
            </div>

            <div className="text-center p-3 bg-gray-800 rounded">
              <div className="text-sm text-gray-400 mb-1">Tipo</div>
              <div className="text-white font-medium capitalize">
                {currentAnalysis.analysis_type}
              </div>
            </div>
          </div>

          <div className="p-3 bg-gray-800 rounded">
            <div className="text-sm text-gray-400 mb-2">Razonamiento:</div>
            <div className="text-white text-sm leading-relaxed">
              {currentAnalysis.reasoning}
            </div>
          </div>

          {currentAnalysis.additional_data && Object.keys(currentAnalysis.additional_data).length > 0 && (
            <div className="mt-3 p-3 bg-gray-800 rounded">
              <div className="text-sm text-gray-400 mb-2">Datos Adicionales:</div>
              <pre className="text-white text-xs overflow-x-auto">
                {JSON.stringify(currentAnalysis.additional_data, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Historial reciente */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-white font-medium">📋 Historial Reciente</h4>
          <button
            onClick={() => loadAnalysisHistory()}
            className="px-3 py-1 text-sm bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
          >
            Actualizar
          </button>
        </div>

        <div className="space-y-2 max-h-60 overflow-y-auto">
           {analysisHistory && analysisHistory.length > 0 ? (
            analysisHistory.map((analysis) => (
              <div
                key={analysis.id}
                className="p-3 bg-gray-900 rounded border border-gray-700 hover:border-gray-600 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className={`text-sm font-medium ${getSignalColor(analysis.signal)}`}>
                      {analysis.signal}
                    </span>
                    <span className="text-white text-sm">{analysis.symbol}</span>
                    <span className="text-gray-400 text-xs">{analysis.analysis_type}</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`text-sm ${getConfidenceColor(analysis.confidence)}`}>
                      {analysis.confidence}%
                    </span>
                    <span className="text-gray-400 text-xs">
                      {new Date(analysis.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-4 text-gray-400">
              No hay análisis recientes
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIAnalysis;