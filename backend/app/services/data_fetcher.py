import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
from ..core.logger import logger

class DataFetcher:
    def __init__(self):
        self.connected = False
    
    def initialize_mt5(self, server: str, login: int, password: str, timeout: int = 60000) -> bool:
        """Inicializar conexión con MT5"""
        try:
            if not mt5.initialize():
                logger.error(f"Error inicializando MT5: {mt5.last_error()}")
                return False
            
            # Intentar conexión
            connected = mt5.login(login=login, password=password, server=server, timeout=timeout)
            if connected:
                self.connected = True
                logger.info(f"✅ Conectado a MT5 - Cuenta: {login}, Servidor: {server}")
                return True
            else:
                logger.error(f"❌ Error login MT5: {mt5.last_error()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error inicializando MT5: {str(e)}")
            return False
    
    def shutdown_mt5(self):
        """Cerrar conexión con MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("🔌 Conexión MT5 cerrada")
    
    def get_account_info(self) -> Optional[Dict]:
        """Obtener información de la cuenta"""
        if not self.connected:
            return None
            
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return None
                
            return {
                "login": account_info.login,
                "balance": account_info.balance,
                "equity": account_info.equity,
                "margin": account_info.margin,
                "free_margin": account_info.margin_free,
                "leverage": account_info.leverage,
                "currency": account_info.currency,
                "server": account_info.server,
                "profit": account_info.profit
            }
        except Exception as e:
            logger.error(f"Error obteniendo info cuenta: {str(e)}")
            return None
    
    def get_market_data(self, symbol: str, timeframe: int = mt5.TIMEFRAME_M5, count: int = 100) -> Optional[pd.DataFrame]:
        """Obtener datos de mercado para un símbolo"""
        if not self.connected:
            return None
            
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None:
                return None
                
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        except Exception as e:
            logger.error(f"Error obteniendo datos mercado {symbol}: {str(e)}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Obtener precio actual de un símbolo"""
        if not self.connected:
            return None
            
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return None
                
            return {
                "symbol": symbol,
                "bid": tick.bid,
                "ask": tick.ask,
                "last": tick.last,
                "volume": tick.volume,
                "time": datetime.fromtimestamp(tick.time),
                "spread": round(tick.ask - tick.bid, 5)
            }
        except Exception as e:
            logger.error(f"Error obteniendo precio {symbol}: {str(e)}")
            return None
    
    def get_symbols(self) -> List[str]:
        """Obtener lista de símbolos disponibles"""
        if not self.connected:
            return []
            
        try:
            symbols = mt5.symbols_get()
            return [s.name for s in symbols]
        except Exception as e:
            logger.error(f"Error obteniendo símbolos: {str(e)}")
            return []
    
    def get_open_positions(self) -> List[Dict]:
        """Obtener posiciones abiertas - CORREGIDO"""
        if not self.connected:
            return []
            
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []
                
            return [
                {
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": pos.type,  # ✅ MANTENER como número (0=BUY, 1=SELL)
                    "volume": pos.volume,
                    "open_price": pos.price_open,
                    "current_price": pos.price_current,
                    "profit": pos.profit,
                    "sl": pos.sl,
                    "tp": pos.tp,
                    "open_time": datetime.fromtimestamp(pos.time)
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Error obteniendo posiciones: {str(e)}")
            return []

# Instancia global
data_fetcher = DataFetcher()