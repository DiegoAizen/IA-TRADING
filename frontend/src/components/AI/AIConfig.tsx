import React, { useState, useEffect } from 'react';
import { useAI } from '../../context/AIContext';

const AIConfig: React.FC = () => {
  const { updateAIConfig, testApiKey, loading, error } = useAI();
  const [formData, setFormData] = useState({
    ai_provider: 'deepseek',
    ai_model: 'deepseek-chat',
    api_key: '',
    is_active: true,
    max_tokens: 4000,
    temperature: 0.7,
    confidence_threshold: 70.0
  });
  const [testing, setTesting] = useState(false);
  const [saved, setSaved] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [testResult, setTestResult] = useState<{ valid: boolean; message: string } | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);

  // 🔹 Cargar configuración guardada en localStorage
  useEffect(() => {
    const savedConfig = localStorage.getItem('aiConfig');
    if (savedConfig) {
      const parsed = JSON.parse(savedConfig);
      setFormData(parsed);
      setSaved(true);
    }
  }, []);

  // 🔹 Guardar configuración al confirmar
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateAIConfig(formData);
    localStorage.setItem('aiConfig', JSON.stringify(formData));
    setSaved(true);
    setEditMode(false);
    setTestResult({ valid: true, message: '✅ Configuración guardada correctamente' });
  };

  // 🔹 Borrar configuración
  const handleReset = () => {
    localStorage.removeItem('aiConfig');
    setSaved(false);
    setEditMode(true);
    setFormData({
      ai_provider: 'deepseek',
      ai_model: 'deepseek-chat',
      api_key: '',
      is_active: true,
      max_tokens: 4000,
      temperature: 0.7,
      confidence_threshold: 70.0
    });
  };

  // 🔹 Probar API Key
  const handleTestApiKey = async () => {
    if (!formData.api_key) {
      setTestResult({ valid: false, message: 'Por favor ingresa una API key' });
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const isValid = await testApiKey(formData.ai_provider, formData.api_key);
      setTestResult({
        valid: isValid,
        message: isValid ? '✅ API key válida' : '❌ API key inválida'
      });
    } catch (err) {
      setTestResult({
        valid: false,
        message: '❌ Error probando API key'
      });
    } finally {
      setTesting(false);
    }
  };

  // 🔹 Vista compacta cuando ya está guardado y no se está editando
  if (saved && !editMode) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div className="flex justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Configuración de IA</h3>
          <span className="px-3 py-1 rounded-full text-sm bg-green-500/20 text-green-400 border border-green-500/30">
            ✅ Activa
          </span>
        </div>

        <div className="text-gray-300 text-sm space-y-2 mb-4">
          <p><strong>Proveedor:</strong> {formData.ai_provider}</p>
          <p><strong>Modelo:</strong> {formData.ai_model}</p>
          <p><strong>Temperatura:</strong> {formData.temperature}</p>
          <p><strong>Tokens Máx:</strong> {formData.max_tokens}</p>
        </div>

        <button
          onClick={() => setEditMode(true)}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500"
        >
          Cambiar configuración
        </button>
      </div>
    );
  }

  // 🔹 Formulario de configuración (modo edición o nuevo)
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4">
        {saved ? 'Editar Configuración de IA' : 'Configurar IA'}
      </h3>

      {error && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {testResult && (
        <div className={`mb-4 p-3 rounded-lg border ${
          testResult.valid
            ? 'bg-green-500/20 border-green-500/30 text-green-400'
            : 'bg-red-500/20 border-red-500/30 text-red-400'
        }`}>
          <p className="text-sm">{testResult.message}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Proveedor */}
        <div>
          <label className="text-sm text-gray-300">Proveedor</label>
          <select
            name="ai_provider"
            value={formData.ai_provider}
            onChange={(e) => setFormData({ ...formData, ai_provider: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          >
            <option value="deepseek">DeepSeek</option>
            <option value="openai">OpenAI</option>
          </select>
        </div>

        {/* Modelo */}
        <div>
          <label className="text-sm text-gray-300">Modelo</label>
          <input
            type="text"
            name="ai_model"
            value={formData.ai_model}
            onChange={(e) => setFormData({ ...formData, ai_model: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          />
        </div>

        {/* API Key */}
        <div>
          <label className="text-sm text-gray-300">API Key</label>
          <div className="relative">
            <input
              type={showApiKey ? "text" : "password"}
              name="api_key"
              value={formData.api_key}
              onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
              placeholder="Tu API key"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white pr-24"
            />
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                className="px-2 py-1 text-xs text-gray-400 hover:text-gray-300"
              >
                {showApiKey ? '🙈' : '👁️'}
              </button>
              <button
                type="button"
                onClick={handleTestApiKey}
                disabled={testing || !formData.api_key}
                className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {testing ? 'Probando...' : 'Probar'}
              </button>
            </div>
          </div>
        </div>

        {/* Parámetros avanzados */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-sm text-gray-300">Máx. Tokens</label>
            <input
              type="number"
              value={formData.max_tokens}
              onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
          </div>
          <div>
            <label className="text-sm text-gray-300">Temperatura</label>
            <input
              type="number"
              value={formData.temperature}
              step="0.1"
              onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
          </div>
          <div>
            <label className="text-sm text-gray-300">Confianza</label>
            <input
              type="number"
              value={formData.confidence_threshold}
              onChange={(e) => setFormData({ ...formData, confidence_threshold: parseFloat(e.target.value) })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
          </div>
        </div>

        {/* Botones */}
        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {loading ? 'Guardando...' : 'Guardar Configuración'}
        </button>

        {saved && (
          <button
            type="button"
            onClick={handleReset}
            className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 mt-2"
          >
            Borrar configuración
          </button>
        )}
      </form>
    </div>
  );
};

export default AIConfig;
