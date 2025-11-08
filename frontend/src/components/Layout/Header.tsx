import React from 'react';
import { useAuth } from '../../context/AuthContext';

const Header: React.FC = () => {
  const { user } = useAuth();
  const currentTime = new Date().toLocaleTimeString('es-ES', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });

  return (
    <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">
            {getGreeting()}, {user?.full_name?.split(' ')[0] || user?.username}!
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Bienvenido a tu panel de trading
          </p>
        </div>
        
        <div className="flex items-center space-x-6">
          <div className="text-right">
            <p className="text-sm text-gray-300">{currentTime}</p>
            <p className="text-xs text-gray-500">Hora local</p>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              user?.risk_level === 'low' ? 'bg-green-500' :
              user?.risk_level === 'moderate' ? 'bg-yellow-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm text-gray-300 capitalize">
              Riesgo {user?.risk_level}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

// Helper para saludo según hora del día
const getGreeting = (): string => {
  const hour = new Date().getHours();
  if (hour < 12) return 'Buenos días';
  if (hour < 18) return 'Buenas tardes';
  return 'Buenas noches';
};

export default Header;