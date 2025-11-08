# backend/app/services/bot_analysis_service.py - ACTUALIZADO CON NOTICIAS
import asyncio
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..core.logger import logger
from ..ai.ai_interface import ai_interface
from ..models.ai_config_model import UserAIConfig, AIAnalysisHistory
from ..database.db_connection import get_db
from .trading_service import trading_service
from .broker_api import broker_api
from .data_fetcher import data_fetcher
from .intelligent_news_service import intelligent_news_service  
import MetaTrader5 as mt5

class BotAnalysisService:
    def __init__(self):
        self.active_analyses = {}
        self.analysis_lock = asyncio.Lock()
    
    async def analyze_and_execute(self, symbol: str, user_id: int, bot_config: Any) -> Dict[str, Any]:
        """Análisis ESPECÍFICO para el bot que EJECUTA operaciones - CON NOTICIAS"""
        async with self.analysis_lock:
            try:
                logger.info(f"🤖 BOT Analizando y ejecutando: {symbol}")
                
                # 1. Obtener configuración IA
                db_config = next(get_db())
                try:
                    ai_config = db_config.query(UserAIConfig).filter(UserAIConfig.user_id == user_id).first()
                    if not ai_config or not ai_config.is_active:
                        return {
                            "success": False,
                            "error": "Configuración de IA no activa",
                            "symbol": symbol,
                            "signal": "HOLD"
                        }
                finally:
                    db_config.close()
                
                # 2. Obtener datos de mercado
                market_data = await self._get_real_market_data(symbol)
                if not market_data:
                    return {
                        "success": False,
                        "error": f"Sin datos de {symbol}",
                        "symbol": symbol,
                        "signal": "HOLD"
                    }
                
                # 3. ✅ NUEVO: Obtener noticias inteligentes para el símbolo
                news_context = await intelligent_news_service.get_news_for_analysis(symbol, user_id)
                logger.info(f"📰 BOT Contexto de noticias: {news_context['news_count']} noticias, sentimiento: {news_context['overall_sentiment']}")
                
                # 4. Calcular indicadores técnicos
                technical_indicators = self._calculate_technical_indicators(symbol)
                
                # 5. Análisis IA CON NOTICIAS
                ai_config_dict = {
                    "provider": ai_config.ai_provider,
                    "api_key": ai_config.api_key,
                    "model": ai_config.ai_model,
                    "analysis_type": "comprehensive",
                    "risk_profile": bot_config.trading_strategy
                }
                
                # ✅ ACTUALIZADO: Pasar news_context en lugar de lista simple de noticias
                analysis_result = await ai_interface.analyze_market(
                    symbol=symbol,
                    user_id=user_id,  # ✅ Añadir user_id
                    market_data=market_data,
                    technical_indicators=technical_indicators,
                    news=news_context,  # ✅ Ahora pasa el contexto completo de noticias
                    ai_config=ai_config_dict
                )
                
                # 6. EJECUTAR OPERACIÓN si cumple condiciones
                execution_result = await self._execute_trade_if_valid(
                    symbol, analysis_result, bot_config, market_data
                )
                
                # 7. Guardar en historial CON INFORMACIÓN DE NOTICIAS
                db_save = next(get_db())
                try:
                    analysis_history = AIAnalysisHistory(
                        user_id=user_id,
                        symbol=symbol,
                        timeframe="M5",
                        analysis_type="bot_execution",
                        ai_provider=ai_config.ai_provider,
                        ai_model=ai_config.ai_model,
                        signal=analysis_result.get("signal", "HOLD"),
                        confidence=analysis_result.get("confidence", 0.0),
                        reasoning=analysis_result.get("reasoning", ""),
                        processing_time=0.0
                    )
                    db_save.add(analysis_history)
                    db_save.commit()
                finally:
                    db_save.close()
                
                # 8. Devolver resultado combinado CON INFO DE NOTICIAS
                return {
                    "success": True,
                    "symbol": symbol,
                    "signal": analysis_result.get("signal", "HOLD"),
                    "confidence": analysis_result.get("confidence", 0.0),
                    "reasoning": analysis_result.get("reasoning", ""),
                    "execution_result": execution_result,
                    "stop_loss": analysis_result.get("stop_loss"),
                    "take_profit": analysis_result.get("take_profit"),
                    "news_used": news_context.get("news_count", 0),  # ✅ NUEVO
                    "market_sentiment": news_context.get("overall_sentiment", "neutral")  # ✅ NUEVO
                }
                
            except Exception as e:
                logger.error(f"❌ Error en análisis bot para {symbol}: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "symbol": symbol,
                    "signal": "HOLD"
                }

    async def _execute_trade_if_valid(self, symbol: str, analysis_result: Dict, bot_config: Any, market_data: Dict) -> Dict[str, Any]:
        """Ejecutar operación si cumple todas las condiciones - ACTUALIZADO"""
        try:
            signal = analysis_result.get("signal", "HOLD")
            confidence = analysis_result.get("confidence", 0)
            
            logger.info(f"🔍 BOT Verificando {symbol}: {signal} con {confidence}% confianza")
            
            # 1. Verificar señal válida
            if signal not in ["BUY", "SELL"]:
                logger.info(f"⏹️ BOT Señal no válida: {signal}")
                return {"executed": False, "reason": "Señal no válida"}
            
            # 2. Verificar confianza
            confidence_threshold = 60.0
            logger.info(f"🔍 BOT Umbral confianza: {confidence_threshold}% vs actual: {confidence}%")
            
            if confidence < confidence_threshold:
                logger.info(f"⏹️ BOT Confianza insuficiente: {confidence}% < {confidence_threshold}%")
                return {"executed": False, "reason": f"Confianza insuficiente: {confidence}%"}
            
            # 3. Verificar operación existente
            portfolio = broker_api.get_portfolio_status()
            if not portfolio["success"]:
                return {"executed": False, "reason": "Error obteniendo portfolio"}
            
            open_positions = portfolio.get("open_positions", [])
            logger.info(f"🔍 BOT Operaciones abiertas: {len(open_positions)}")
            
            existing_trade = any(pos["symbol"] == symbol for pos in open_positions)
            if existing_trade:
                logger.info(f"⏹️ BOT Ya existe operación en {symbol}")
                return {"executed": False, "reason": "Operación existente"}
            
            # 4. Verificar límite de operaciones
            current_trades = len(open_positions)
            max_trades = bot_config.max_open_trades
            logger.info(f"🔍 BOT Límite operaciones: {current_trades}/{max_trades}")
            
            if current_trades >= max_trades:
                logger.info(f"⏹️ BOT Límite alcanzado: {current_trades}/{max_trades}")
                return {"executed": False, "reason": "Límite de operaciones alcanzado"}
            
            # 5. Convertir stops de string a float
            stop_loss_str = analysis_result.get("stop_loss")
            take_profit_str = analysis_result.get("take_profit")
            
            stop_loss = None
            take_profit = None
            
            if stop_loss_str and take_profit_str:
                try:
                    stop_loss = float(stop_loss_str)
                    take_profit = float(take_profit_str)
                    logger.info(f"✅ BOT Stops IA: SL={stop_loss:.5f}, TP={take_profit:.5f}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"⚠️ BOT Error convirtiendo stops IA: {e}")
                    stop_loss = None
                    take_profit = None
            
            # Si no hay stops válidos de la IA, calcular automáticamente
            if not stop_loss or not take_profit:
                current_price = market_data.get("bid")
                if current_price:
                    stop_loss_pips = bot_config.default_stop_loss or 50.0
                    stop_loss, take_profit = self._calculate_stops(symbol, signal, float(current_price), stop_loss_pips)
                    logger.info(f"⚠️ BOT Stops calculados: SL={stop_loss:.5f}, TP={take_profit:.5f}")
                else:
                    logger.error("❌ BOT No se pudo obtener precio para calcular stops")
                    return {"executed": False, "reason": "Error obteniendo precio"}
            
            # 6. Ejecutar operación
            volume = bot_config.default_lot_size or 0.1
            logger.info(f"🚀 BOT Ejecutando: {symbol} {signal} {volume} lots - SL: {stop_loss:.5f}, TP: {take_profit:.5f}")
            
            # Asegurar que todos los parámetros sean del tipo correcto
            trade_result = trading_service.place_order(
                symbol=symbol,
                order_type=signal,
                volume=float(volume),
                stop_loss=float(stop_loss),
                take_profit=float(take_profit),
                magic=123456,
                comment=f"🤖 BOT - Conf: {confidence}%"
            )
            
            logger.info(f"📋 BOT Resultado: {trade_result}")
            
            if trade_result["success"]:
                logger.info(f"🎯 BOT OPERACIÓN EJECUTADA: {symbol} {signal}")
                return {
                    "executed": True,
                    "order_id": trade_result.get("order_id"),
                    "price": trade_result.get("price"),
                    "volume": volume,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit
                }
            else:
                logger.error(f"❌ BOT Error: {trade_result.get('error')}")
                return {
                    "executed": False,
                    "reason": f"Error MT5: {trade_result.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error en _execute_trade_if_valid: {str(e)}")
            return {"executed": False, "reason": f"Error interno: {str(e)}"}

    def _calculate_stops(self, symbol: str, signal: str, entry_price: float, stop_loss_pips: float) -> tuple:
        """Calcular stop loss y take profit - CORREGIDO"""
        try:
            # Determinar pip size según el símbolo
            if "JPY" in symbol:
                pip_size = 0.01
            elif "XAU" in symbol or "GOLD" in symbol:
                pip_size = 0.1
            elif "XAG" in symbol:
                pip_size = 0.001
            elif any(crypto in symbol for crypto in ['BTC', 'ETH', 'LTC', 'XRP', 'ADA']):
                pip_size = 1.0
            else:
                pip_size = 0.0001
            
            # Calcular stops con ratio 1:2
            stop_distance = stop_loss_pips * pip_size
            
            if signal == "BUY":
                stop_loss = entry_price - stop_distance
                take_profit = entry_price + (stop_distance * 2)  # 1:2 ratio
            else:  # SELL
                stop_loss = entry_price + stop_distance
                take_profit = entry_price - (stop_distance * 2)
            
            # Ajustar decimales según el símbolo
            if "JPY" in symbol:
                stop_loss = round(stop_loss, 2)
                take_profit = round(take_profit, 2)
            elif "XAU" in symbol:
                stop_loss = round(stop_loss, 1)
                take_profit = round(take_profit, 1)
            elif any(crypto in symbol for crypto in ['BTC', 'ETH']):
                stop_loss = round(stop_loss, 0)
                take_profit = round(take_profit, 0)
            else:
                stop_loss = round(stop_loss, 5)
                take_profit = round(take_profit, 5)
            
            logger.info(f"🎯 BOT Stops calculados para {symbol}: Entry={entry_price}, SL={stop_loss}, TP={take_profit}")
            return stop_loss, take_profit
            
        except Exception as e:
            logger.error(f"❌ Error calculando stops para {symbol}: {str(e)}")
            # Valores por defecto seguros
            if signal == "BUY":
                return entry_price * 0.99, entry_price * 1.02
            else:
                return entry_price * 1.01, entry_price * 0.98

    async def _get_real_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtener datos de mercado - CORREGIDO TIPOS"""
        try:
            if not data_fetcher.connected:
                return None
            
            current_price = data_fetcher.get_current_price(symbol)
            if not current_price:
                return None
            
            # Asegurar que los precios sean floats
            bid = float(current_price['bid']) if current_price['bid'] else None
            ask = float(current_price['ask']) if current_price['ask'] else None
            
            return {
                "symbol": symbol,
                "bid": bid,
                "ask": ask,
                "spread": current_price['spread'],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error obteniendo datos para {symbol}: {str(e)}")
            return None

    def _calculate_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """Calcular indicadores técnicos simplificados"""
        try:
            data = data_fetcher.get_market_data(symbol, mt5.TIMEFRAME_M5, 100)
            if data is None or data.empty:
                return {"rsi": 50.0, "macd": 0.0}
            
            closes = data['close']
            
            # RSI simplificado
            delta = closes.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD simplificado
            exp1 = closes.ewm(span=12).mean()
            exp2 = closes.ewm(span=26).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9).mean()
            macd_histogram = macd_line - signal_line
            
            # Medias móviles
            ma_20 = closes.rolling(20).mean().iloc[-1] if len(closes) >= 20 else closes.iloc[-1]
            ma_50 = closes.rolling(50).mean().iloc[-1] if len(closes) >= 50 else closes.iloc[-1]
            
            # Soporte y resistencia básicos
            support = closes.tail(20).min()
            resistance = closes.tail(20).max()
            
            return {
                "rsi": round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else 50.0,
                "macd": round(macd_histogram.iloc[-1], 6) if not pd.isna(macd_histogram.iloc[-1]) else 0.0,
                "ma_20": round(ma_20, 5),
                "ma_50": round(ma_50, 5),
                "support": round(support, 5),
                "resistance": round(resistance, 5),
                "current_price": round(closes.iloc[-1], 5)
            }
        except Exception as e:
            logger.error(f"Error calculando indicadores para {symbol}: {str(e)}")
            return {"rsi": 50.0, "macd": 0.0}

# Instancia global
bot_analysis_service = BotAnalysisService()