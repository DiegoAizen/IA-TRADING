import React, { useState, useEffect } from 'react';
import { useMT5 } from '../../context/MT5Context';

const MT5Connection: React.FC = () => {
  const { mt5Status, isConnected, connectMT5, disconnectMT5, loading, error } = useMT5();
  const [config, setConfig] = useState({
    server: 'MetaQuotes-Demo',
    login: 10008281701,
    password: 'V@3lQjMu',
    timeout: 60000,
    portable: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [editMode, setEditMode] = useState(false);

  // 🔹 Intentar cargar credenciales guardadas
  useEffect(() => {
    const saved = localStorage.getItem('mt5Config');
    if (saved) {
      const parsed = JSON.parse(saved);
      setConfig(parsed);
      // Auto reconectar si no está conectado
      if (!isConnected) connectMT5(parsed);
    }
  }, []);

  // 🔹 Guardar configuración en localStorage cuando se conecta
  useEffect(() => {
    if (isConnected && config.login && config.password) {
      localStorage.setItem('mt5Config', JSON.stringify(config));
    }
  }, [isConnected]);

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    await connectMT5(config);
    localStorage.setItem('mt5Config', JSON.stringify(config));
  };

  const handleDisconnect = async () => {
    await disconnectMT5();
    localStorage.removeItem('mt5Config');
  };

  if (isConnected && !editMode) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white">Conexión MT5</h3>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-500/20 text-green-400 border border-green-500/30">
            🟢 Conectado
          </span>
        </div>

        <div className="bg-gray-900 rounded-lg p-4 border border-gray-700 mb-4">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-400">Servidor:</span>
              <p className="text-white">{mt5Status?.config.server}</p>
            </div>
            <div>
              <span className="text-gray-400">Cuenta:</span>
              <p className="text-white">{mt5Status?.config.login}</p>
            </div>
          </div>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={() => setEditMode(true)}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500"
          >
            Cambiar Cuenta
          </button>
          <button
            onClick={handleDisconnect}
            className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500"
          >
            Desconectar
          </button>
        </div>
      </div>
    );
  }

  // 🔹 Formulario de conexión (por defecto)
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4">
        {editMode ? 'Cambiar Cuenta MT5' : 'Conectar a MT5'}
      </h3>

      <form onSubmit={handleConnect} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-300">Servidor</label>
            <input
              type="text"
              required
              value={config.server}
              onChange={(e) => setConfig({ ...config, server: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
          </div>
          <div>
            <label className="text-sm text-gray-300">Número de Cuenta</label>
            <input
              type="number"
              required
              value={config.login}
              onChange={(e) => setConfig({ ...config, login: parseInt(e.target.value) })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
          </div>
        </div>

        <div>
          <label className="text-sm text-gray-300">Contraseña</label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              required
              value={config.password}
              onChange={(e) => setConfig({ ...config, password: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white pr-10"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
            >
              {showPassword ? '🙈' : '👁️'}
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {loading ? 'Conectando...' : 'Conectar'}
        </button>
      </form>
    </div>
  );
};

export default MT5Connection;
