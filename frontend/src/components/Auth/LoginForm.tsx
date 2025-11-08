import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';


const LoginForm: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  // Cargar credenciales demo automáticamente en desarrollo
  useEffect(() => {
    if ((import.meta as any).env.DEV) {
      setUsername('trader@example.com');
      setPassword('password123');
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(username, password);
    } catch (err) {
      setError('Credenciales incorrectas. Usa el usuario demo.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoCredentials = () => {
    setUsername('trader@example.com');
    setPassword('password123');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-center">
          <h1 className="text-2xl font-bold text-white">Trading Bot AI</h1>
          <p className="text-blue-100 text-sm mt-1">Aplicación de Escritorio</p>
        </div>

        {/* Form */}
        <div className="p-8">
          <div className="text-center mb-8">
            <h2 className="text-xl font-semibold text-white">Iniciar Sesión</h2>
            <p className="text-gray-400 text-sm mt-2">
              Accede a tu cuenta de trading
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-900/50 border border-red-700 text-red-200 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email o Usuario
              </label>
              <input
                type="text"
                required
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="tu@email.com"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Contraseña
              </label>
              <input
                type="password"
                required
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02]"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Iniciando sesión...
                </div>
              ) : (
                'Iniciar Sesión'
              )}
            </button>

            <div className="text-center">
              <button
                type="button"
                onClick={fillDemoCredentials}
                className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
              >
                Usar credenciales de demo
              </button>
            </div>
          </form>

          {/* Demo Info Box */}
          <div className="mt-8 p-4 bg-gray-700/50 rounded-lg border border-gray-600">
            <h3 className="text-sm font-medium text-gray-300 mb-2">
              💡 Usuario Demo para Pruebas
            </h3>
            <div className="text-xs text-gray-400 space-y-1">
              <p><span className="text-gray-300">Email:</span> trader@example.com</p>
              <p><span className="text-gray-300">Usuario:</span> demo_trader</p>
              <p><span className="text-gray-300">Contraseña:</span> password123</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-900 px-6 py-4 border-t border-gray-700">
          <p className="text-xs text-gray-500 text-center">
            Versión 1.0.0 • Aplicación de Escritorio Segura
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;