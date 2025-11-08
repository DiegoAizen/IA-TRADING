# En services/trading_service.py
#  Cómo manejas el estado "activo/inactivo" del bot
#  Mecanismos de bloqueo para evitar operaciones duplicadas
#  Manejo de hilos/asyncio para análisis en segundo plano

import MetaTrader5 as mt5
from datetime import datetime
from typing import Dict, Optional, Tuple
from ..core.logger import logger
from .data_fetcher import data_fetcher

class TradingService:
    def __init__(self):
        self.is_running = False
    
    def place_order(self, symbol: str, order_type: str, volume: float, 
                   stop_loss: float = 0.0, take_profit: float = 0.0,
                   magic: int = 123456, comment: str = "AI Trading") -> Dict:
        """Colocar una orden de trading"""
        try:
            if not data_fetcher.connected:
                return {"success": False, "error": "MT5 no conectado"}
            
            # Preparar la solicitud de orden
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL,
                "price": mt5.symbol_info_tick(symbol).ask if order_type == "BUY" else mt5.symbol_info_tick(symbol).bid,
                "deviation": 20,
                "magic": magic,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Agregar stops si se especifican
            if stop_loss > 0:
                request["sl"] = stop_loss
            if take_profit > 0:
                request["tp"] = take_profit
            
            # Enviar orden
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    "success": False,
                    "error": f"Error en orden: {result.retcode} - {self._get_error_description(result.retcode)}",
                    "retcode": result.retcode
                }
            
            logger.info(f"✅ Orden ejecutada - {order_type} {volume} {symbol}")
            return {
                "success": True,
                "order_id": result.order,
                "price": result.price,
                "volume": result.volume,
                "message": "Orden ejecutada exitosamente"
            }
            
        except Exception as e:
            logger.error(f"❌ Error colocando orden: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def close_position(self, ticket: int) -> Dict:
        """Cerrar una posición existente"""
        try:
            if not data_fetcher.connected:
                return {"success": False, "error": "MT5 no conectado"}
            
            # Obtener información de la posición
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return {"success": False, "error": "Posición no encontrada"}
            
            position = position[0]
            
            # Preparar solicitud de cierre
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": ticket,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "price": mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask,
                "deviation": 20,
                "magic": position.magic,
                "comment": "AI Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Enviar orden de cierre
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    "success": False,
                    "error": f"Error cerrando posición: {result.retcode}",
                    "retcode": result.retcode
                }
            
            logger.info(f"🔒 Posición cerrada - Ticket: {ticket}")
            return {
                "success": True,
                "order_id": result.order,
                "price": result.price,
                "profit": position.profit,
                "message": "Posición cerrada exitosamente"
            }
            
        except Exception as e:
            logger.error(f"❌ Error cerrando posición: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def modify_position(self, ticket: int, stop_loss: float = None, take_profit: float = None) -> Dict:
        """Modificar stops de una posición existente"""
        try:
            if not data_fetcher.connected:
                return {"success": False, "error": "MT5 no conectado"}
            
            # Obtener información de la posición
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return {"success": False, "error": "Posición no encontrada"}
            
            position = position[0]
            
            # Preparar solicitud de modificación
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "symbol": position.symbol,
                "sl": stop_loss if stop_loss is not None else position.sl,
                "tp": take_profit if take_profit is not None else position.tp,
                "magic": position.magic,
                "comment": position.comment,
            }
            
            # Enviar modificación
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    "success": False,
                    "error": f"Error modificando posición: {result.retcode}",
                    "retcode": result.retcode
                }
            
            logger.info(f"⚙️ Posición modificada - Ticket: {ticket}")
            return {
                "success": True,
                "message": "Posición modificada exitosamente",
                "new_sl": stop_loss,
                "new_tp": take_profit
            }
            
        except Exception as e:
            logger.error(f"❌ Error modificando posición: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def calculate_position_size(self, symbol: str, risk_percent: float, stop_loss_pips: float) -> float:
        """Calcular tamaño de posición basado en riesgo"""
        try:
            if not data_fetcher.connected:
                return 0.01  # Tamaño por defecto
            
            account_info = data_fetcher.get_account_info()
            if not account_info:
                return 0.01
            
            # Calcular riesgo en dinero
            risk_amount = account_info["balance"] * (risk_percent / 100)
            
            # Obtener información del símbolo
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                return 0.01
            
            # Calcular valor del pip
            pip_value = self._calculate_pip_value(symbol, symbol_info)
            
            # Calcular tamaño de posición
            if pip_value > 0 and stop_loss_pips > 0:
                position_size = risk_amount / (stop_loss_pips * pip_value)
                # Ajustar al lote mínimo/máximo permitido
                position_size = max(symbol_info.volume_min, min(symbol_info.volume_max, position_size))
                return round(position_size, 2)
            else:
                return 0.01
                
        except Exception as e:
            logger.error(f"Error calculando tamaño posición: {str(e)}")
            return 0.01
    
    def _calculate_pip_value(self, symbol: str, symbol_info) -> float:
        """Calcular valor de un pip de forma precisa para todos los símbolos"""
        try:
            if not symbol_info:
                return 1.0  # Valor por defecto seguro
            
            # Determinar el tamaño del pip según el símbolo
            if "JPY" in symbol:
                pip_size = 0.01  # Pares JPY
            elif "XAU" in symbol or "GOLD" in symbol:
                pip_size = 0.1   # Oro
            elif "XAG" in symbol:
                pip_size = 0.001 # Plata
            elif "BTC" in symbol or "ETH" in symbol or "LTC" in symbol:
                pip_size = 1.0   # Cryptos (generalmente en dólares)
            else:
                pip_size = 0.0001  # Mayoría de pares Forex
            
            # Obtener información de la cuenta para conversión
            account_info = data_fetcher.get_account_info()
            account_currency = account_info.get("currency", "USD") if account_info else "USD"
            
            # Calcular pip value basado en el símbolo
            if "XAU" in symbol or "GOLD" in symbol:
                # Para oro, el pip value es más complejo
                contract_size = getattr(symbol_info, 'trade_contract_size', 100)
                return pip_size * contract_size  # Aproximado
                
            elif "BTC" in symbol or "ETH" in symbol:
                # Para cryptos, el pip value es más simple
                return pip_size
                
            else:
                # Para Forex y otros
                contract_size = getattr(symbol_info, 'trade_contract_size', 100000)
                
                # Si el símbolo incluye la moneda de la cuenta, cálculo directo
                if account_currency in symbol:
                    if symbol.startswith(account_currency):
                        # Ejemplo: USDJPY con cuenta USD
                        return pip_size * contract_size
                    else:
                        # Ejemplo: EURUSD con cuenta USD  
                        return pip_size * contract_size
                else:
                    # Necesitaríamos conversión de divisa (simplificado por ahora)
                    return pip_size * 10  # Aproximación para la mayoría de pares
                    
        except Exception as e:
            logger.error(f"Error calculando pip value para {symbol}: {str(e)}")
            return 1.0  # Valor por defecto seguro
    
    def _get_error_description(self, retcode: int) -> str:
        """Obtener descripción del error de MT5 - ACTUALIZADO"""
        error_descriptions = {
            10004: "Requote - Precio cambió",
            10006: "Request rechazada",
            10007: "Request cancelada por trader", 
            10008: "Orden colocada",
            10009: "Request completada",
            10010: "Solo parcialmente ejecutada",
            10011: "Error de request",
            10012: "Request cancelada",
            10013: "Error de colocación de orden",
            10014: "Volumen muy bajo",
            10015: "Volumen muy alto", 
            10016: "Precio inválido",
            10017: "Símbolo inválido",
            10018: "Orden no encontrada",
            10019: "Operación no permitida",
            10020: "Operación pendiente",
            10021: "Fondos insuficientes",
            10022: "Precio no actualizado",
            10023: "Símbolo no disponible",
            10024: "Cuenta inválida",
            10025: "Tipo de orden inválido",
            10026: "Posición no encontrada",
            10027: "Operación rechazada (trading prohibido)",
            10028: "Límites de trading excedidos",
            10029: "Mercado cerrado",
            10030: "Error general de trading",  # ⬅️ AÑADIDO
            10031: "Orden modificada",
            10032: "Timeout de orden",
            10033: "Error de margen",
        }
        return error_descriptions.get(retcode, f"Error desconocido: {retcode}")

trading_service = TradingService()