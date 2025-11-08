import React from 'react';
import Header from '../components/Layout/Header';
import Sidebar from '../components/Layout/Sidebar';

const HistoryPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h1 className="text-2xl font-bold text-white mb-4">Historial de Operaciones</h1>
            <p className="text-gray-400">Próximamente: Tabla completa de historial de trading</p>
          </div>
        </main>
      </div>
    </div>
  );
};

export default HistoryPage;