//fronted//src//app.tsx

import React from 'react';
import { AuthProvider } from './context/AuthContext';
import { BotProvider } from './context/BotContext';
import { MT5Provider } from './context/MT5Context';
import { AIProvider } from './context/AIContext';
import AppRouter from './router';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <BotProvider>
        <MT5Provider>
          <AIProvider>
            <AppRouter />
          </AIProvider>
        </MT5Provider>
      </BotProvider>
    </AuthProvider>
  );
};

export default App;