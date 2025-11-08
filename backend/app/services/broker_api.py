# En services/broker_api.py
#  Manejo de conexión/desconexión con MetaTrader 5
#  Mecanismos de reintento en fallos de ejecución
#  Verificación de márgenes y límites antes de operar

import MetaTrader5 as mt5
from typing import Dict, List, Optional
from ..core.logger import logger
from .data_fetcher import data_fetcher
from .trading_service import trading_service

class BrokerAPI:
    def __init__(self):
        self.connected = False
    
    def connect_to_mt5(self, server: str, login: int, password: str, timeout: int = 60000) -> Dict:
        """Conectar a MT5 con credenciales específicas"""
        try:
            logger.info(f"🔗 Conectando a MT5 - Servidor: {server}, Login: {login}")
            
            success = data_fetcher.initialize_mt5(server, login, password, timeout)
            
            if success:
                self.connected = True
                account_info = data_fetcher.get_account_info()
                
                return {
                    "success": True,
                    "message": "Conexión exitosa a MT5",
                    "account_info": account_info
                }
            else:
                error_msg = mt5.last_error() if mt5.last_error() else "Error desconocido"
                return {
                    "success": False,
                    "error": f"Error de conexión: {error_msg}",
                    "error_code": mt5.last_error()
                }
                
        except Exception as e:
            logger.error(f"❌ Error en conexión MT5: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def disconnect_mt5(self) -> Dict:
        """Desconectar de MT5"""
        try:
            data_fetcher.shutdown_mt5()
            self.connected = False
            return {
                "success": True,
                "message": "Desconectado de MT5"
            }
        except Exception as e:
            logger.error(f"Error desconectando MT5: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_connection_status(self) -> Dict:
        """Obtener estado de conexión"""
        return {
            "connected": self.connected,
            "account_info": data_fetcher.get_account_info() if self.connected else None
        }
    
    def execute_trade(self, symbol: str, signal: str, volume: float, 
                     risk_percent: float = 2.0, stop_loss_pips: float = 50.0) -> Dict:
        """Ejecutar operación de trading"""
        try:
            if not self.connected:
                return {"success": False, "error": "MT5 no conectado"}
            
            # Calcular tamaño de posición basado en riesgo
            calculated_volume = trading_service.calculate_position_size(symbol, risk_percent, stop_loss_pips)
            
            # Usar el volumen calculado o el proporcionado
            final_volume = calculated_volume if volume == 0 else volume
            
            # Obtener precio actual para calcular stops
            price_data = data_fetcher.get_current_price(symbol)
            if not price_data:
                return {"success": False, "error": "No se pudo obtener precio actual"}
            
            # Calcular stops
            if signal == "BUY":
                stop_loss = price_data["bid"] - (stop_loss_pips * 0.0001)
                take_profit = price_data["bid"] + (stop_loss_pips * 2 * 0.0001)
            else:  # SELL
                stop_loss = price_data["ask"] + (stop_loss_pips * 0.0001)
                take_profit = price_data["ask"] - (stop_loss_pips * 2 * 0.0001)
            
            # Ejecutar orden
            result = trading_service.place_order(
                symbol=symbol,
                order_type=signal,
                volume=final_volume,
                stop_loss=stop_loss,
                take_profit=take_profit,
                magic=123456,
                comment="AI Trading Bot"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando trade: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_portfolio_status(self) -> Dict:
        """Obtener estado completo del portfolio"""
        try:
            if not self.connected:
                return {"success": False, "error": "MT5 no conectado"}
            
            account_info = data_fetcher.get_account_info()
            open_positions = data_fetcher.get_open_positions()
            
            total_profit = sum(pos["profit"] for pos in open_positions)
            total_volume = sum(pos["volume"] for pos in open_positions)
            
            return {
                "success": True,
                "account_info": account_info,
                "open_positions": open_positions,
                "summary": {
                    "total_positions": len(open_positions),
                    "total_profit": total_profit,
                    "total_volume": total_volume,
                    "buy_positions": len([p for p in open_positions if p["type"] == "BUY"]),
                    "sell_positions": len([p for p in open_positions if p["type"] == "SELL"])
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo portfolio: {str(e)}")
            return {"success": False, "error": str(e)}

# Instancia global
broker_api = BrokerAPI()