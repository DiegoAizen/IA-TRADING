#// En services/analysis_service.py
#// Intervalos de reanálisis y cómo se programan
#// Contexto histórico que se pasa a la IA para cada reanálisis
#// Cómo se deciden ajustes de SL/TP dinámicos

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..core.logger import logger
from ..ai.ai_interface import ai_interface
from ..models.ai_config_model import UserAIConfig, AIAnalysisHistory
from ..database.db_connection import get_db
from sqlalchemy.orm import Session
from .data_fetcher import data_fetcher
import MetaTrader5 as mt5
from .intelligent_news_service import intelligent_news_service

class AnalysisService:
    def __init__(self):
        self.active_analyses = {}
        self.analysis_lock = asyncio.Lock()
    
    async def analyze_symbol(self, symbol: str, user_id: int, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analizar símbolo con manejo SEGURO de sesiones"""
        async with self.analysis_lock:  # 🔒 ANÁLISIS SECUENCIAL, NO PARALELO
            try:
                logger.info(f"🔍 Iniciando análisis para {symbol} - Usuario: {user_id}")
                
                # ✅ OBTENER CONFIGURACIÓN IA (sesión separada y CERRADA)
                db_config = next(get_db())
                try:
                    ai_config = db_config.query(UserAIConfig).filter(UserAIConfig.user_id == user_id).first()
                    if not ai_config or not ai_config.is_active:
                        return {
                            "success": False,
                            "error": "Configuración de IA no encontrada o inactiva",
                            "symbol": symbol,
                            "signal": "HOLD",
                            "confidence": 0.0
                        }
                finally:
                    db_config.close()  # ✅ CERRAR SESIÓN INMEDIATAMENTE
                
                # ✅ OBTENER DATOS MERCADO (sin sesión BD)
                market_data = await self._get_real_market_data(symbol)
                if not market_data:
                    return {
                        "success": False,
                        "error": f"No se pudieron obtener datos de {symbol} desde MT5",
                        "symbol": symbol,
                        "signal": "HOLD",
                        "confidence": 0.0
                    }
                
                # ✅ CALCULAR INDICADORES (sin sesión BD)
                market_data = await self._get_real_market_data(symbol)
                if not market_data:
                    return {"success": False, "error": f"Sin datos de {symbol}", "signal": "HOLD"}
                
                # 3. ✅ NUEVO: Obtener noticias inteligentes
                news_context = await intelligent_news_service.get_news_for_analysis(symbol, user_id)
                logger.info(f"📰 Contexto de noticias: {news_context['news_count']} noticias, sentimiento: {news_context['overall_sentiment']}")
                
                # 4. Calcular indicadores técnicos
                technical_indicators = self._calculate_real_technical_indicators(symbol)
                
                # ✅ ANÁLISIS IA
                ai_config_dict = {
                    "provider": ai_config.ai_provider,
                    "api_key": ai_config.api_key,
                    "model": ai_config.ai_model,
                    "analysis_type": analysis_type,
                    "risk_profile": "moderate"
                }
                
                analysis_result = await ai_interface.analyze_market(
                    symbol=symbol,
                    user_id=user_id,
                    market_data=market_data,
                    technical_indicators=technical_indicators,
                    news=news_context,  # ← Ahora pasa el contexto completo de noticias
                    ai_config=ai_config_dict
                )
                
                # ✅ GUARDAR RESULTADOS (sesión separada y CERRADA)
                db_save = next(get_db())
                try:
                    analysis_history = AIAnalysisHistory(
                        user_id=user_id,
                        symbol=symbol,
                        timeframe="M5",
                        analysis_type=analysis_type,
                        ai_provider=ai_config.ai_provider,
                        ai_model=ai_config.ai_model,
                        signal=analysis_result.get("signal", "HOLD"),
                        confidence=analysis_result.get("confidence", 0.0),
                        reasoning=analysis_result.get("reasoning", ""),
                        processing_time=0.0
                    )
                    
                    db_save.add(analysis_history)
                    
                    # Actualizar contador de requests
                    ai_config_update = db_save.query(UserAIConfig).filter(UserAIConfig.user_id == user_id).first()
                    if ai_config_update:
                        ai_config_update.total_requests += 1
                        ai_config_update.last_used = datetime.now()
                    
                    db_save.commit()
                    
                finally:
                    db_save.close()  # ✅ CERRAR SESIÓN INMEDIATAMENTE
                
                logger.info(f"✅ Análisis completado - {symbol} | Señal: {analysis_result.get('signal')}")
                
                return {
                    "success": True,
                    "symbol": symbol,
                    "signal": analysis_result.get("signal", "HOLD"),
                    "confidence": analysis_result.get("confidence", 0.0),
                    "reasoning": analysis_result.get("reasoning", ""),
                    "news_used": news_context.get("news_count", 0),
                    "market_sentiment": news_context.get("overall_sentiment", "neutral"),
                    "processing_time": 0.0
                }
                
            except Exception as e:
                logger.error(f"❌ Error crítico en análisis de {symbol}: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "symbol": symbol,
                    "signal": "HOLD",
                    "confidence": 0.0
                }
    
    async def analyze_multiple_symbols(self, symbols: List[str], user_id: int, 
                                     analysis_type: str = "technical") -> Dict[str, Any]:
        """Analizar múltiples símbolos de forma SECUENCIAL"""
        try:
            results = []
            
            # 🔄 ANÁLISIS SECUENCIAL - NO PARALELO
            for symbol in symbols:
                try:
                    result = await self.analyze_symbol(symbol, user_id, analysis_type)
                    results.append(result)
                    
                    # ⏸️ PEQUEÑA PAUSA ENTRE SÍMBOLOS
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Error analizando {symbol}: {str(e)}")
                    results.append({
                        "success": False,
                        "symbol": symbol,
                        "error": str(e)
                    })
            
            # Procesar resultados
            successful_analyses = [r for r in results if r.get("success")]
            failed_analyses = [r for r in results if not r.get("success")]
            
            return {
                "success": True,
                "total_analyzed": len(symbols),
                "successful": len(successful_analyses),
                "failed": len(failed_analyses),
                "buy_opportunities": [a for a in successful_analyses if a.get("signal") == "BUY"],
                "sell_opportunities": [a for a in successful_analyses if a.get("signal") == "SELL"],
                "all_results": successful_analyses,
                "errors": failed_analyses
            }
            
        except Exception as e:
            logger.error(f"❌ Error en análisis múltiple: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        
    async def _get_real_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtener datos reales de mercado desde MT5"""
        try:
            # Verificar conexión MT5
            if not data_fetcher.connected:
                logger.error("MT5 no está conectado")
                return None
            
            # Verificar que el símbolo existe
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Símbolo {symbol} no encontrado en MT5")
                return None
            
            logger.info(f"✅ Símbolo {symbol} disponible en MT5")
            
            # Obtener precio actual
            current_price = data_fetcher.get_current_price(symbol)
            if not current_price:
                logger.error(f"No se pudo obtener precio actual para {symbol}")
                return None
            
            # Obtener datos históricos para análisis
            historical_data = data_fetcher.get_market_data(symbol, mt5.TIMEFRAME_H1, 200)
            if historical_data is None or historical_data.empty:
                logger.error(f"No se pudieron obtener datos históricos para {symbol}")
                return None
            
            # Calcular métricas básicas
            recent_data = historical_data.tail(50)
            high_24h = recent_data['high'].max()
            low_24h = recent_data['low'].min()
            volume_avg = recent_data['tick_volume'].mean()
            
            # Determinar tendencia
            ma_20 = recent_data['close'].rolling(20).mean().iloc[-1]
            ma_50 = recent_data['close'].rolling(50).mean().iloc[-1]
            trend = "bullish" if ma_20 > ma_50 else "bearish"
            
            # Calcular volatilidad
            volatility = recent_data['high'].std() / recent_data['close'].mean() * 100
            
            market_data = {
                "symbol": symbol,
                "current_price": current_price['bid'],
                "bid": current_price['bid'],
                "ask": current_price['ask'],
                "spread": current_price['spread'],
                "high": high_24h,
                "low": low_24h,
                "volume": volume_avg,
                "trend": trend,
                "volatility": "high" if volatility > 1.0 else "medium" if volatility > 0.5 else "low",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"📊 Datos de mercado obtenidos para {symbol}: Precio {current_price['bid']}, Tendencia {trend}")
            return market_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos reales para {symbol}: {str(e)}")
            return None
    
    def _calculate_real_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """Calcular indicadores técnicos reales desde MT5"""
        try:
            # Obtener datos históricos
            data = data_fetcher.get_market_data(symbol, mt5.TIMEFRAME_M5, 200)
            if data is None or data.empty:
                logger.warning(f"No hay datos suficientes para calcular indicadores de {symbol}")
                return self._get_fallback_indicators()
            
            closes = data['close']
            highs = data['high']
            lows = data['low']
            
            # Calcular RSI
            rsi = self._calculate_rsi(closes, 14)
            
            # Calcular MACD
            macd_line, signal_line, macd_histogram = self._calculate_macd(closes)
            
            # Medias móviles
            ma_20 = closes.rolling(20).mean().iloc[-1]
            ma_50 = closes.rolling(50).mean().iloc[-1]
            ma_200 = closes.rolling(200).mean().iloc[-1]
            
            # Soporte y resistencia
            support = lows.tail(20).min()
            resistance = highs.tail(20).max()
            
            # Bollinger Bands
            bb_upper, bb_lower = self._calculate_bollinger_bands(closes, 20)
            
            # Stochastic
            stochastic = self._calculate_stochastic(highs, lows, closes, 14)
            
            indicators = {
                "rsi": round(rsi, 2) if not pd.isna(rsi) else 50.0,
                "macd": round(macd_histogram, 6) if not pd.isna(macd_histogram) else 0.0,
                "ma_20": round(ma_20, 5) if not pd.isna(ma_20) else closes.iloc[-1],
                "ma_50": round(ma_50, 5) if not pd.isna(ma_50) else closes.iloc[-1],
                "ma_200": round(ma_200, 5) if not pd.isna(ma_200) else closes.iloc[-1],
                "support": round(support, 5) if not pd.isna(support) else closes.iloc[-1] * 0.99,
                "resistance": round(resistance, 5) if not pd.isna(resistance) else closes.iloc[-1] * 1.01,
                "bollinger_upper": round(bb_upper, 5) if not pd.isna(bb_upper) else closes.iloc[-1] * 1.02,
                "bollinger_lower": round(bb_lower, 5) if not pd.isna(bb_lower) else closes.iloc[-1] * 0.98,
                "stochastic": round(stochastic, 2) if not pd.isna(stochastic) else 50.0
            }
            
            logger.info(f"📈 Indicadores calculados para {symbol}: RSI {indicators['rsi']}, MACD {indicators['macd']}")
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculando indicadores para {symbol}: {str(e)}")
            return self._get_fallback_indicators()
    
    async def _get_market_news(self, symbol: str, market_data: Dict[str, Any], technical_indicators: Dict[str, Any]) -> List[str]:
        """Obtener contexto de mercado basado en datos técnicos"""
        try:
            news_items = []
            
            # Analizar tendencia
            trend = market_data.get('trend', 'neutral')
            if trend == 'bullish':
                news_items.append(f"Tendencia alcista detectada en {symbol}")
            elif trend == 'bearish':
                news_items.append(f"Tendencia bajista detectada en {symbol}")
            else:
                news_items.append(f"Tendencia lateral en {symbol}")
            
            # Analizar volatilidad
            volatility = market_data.get('volatility', 'medium')
            if volatility == 'high':
                news_items.append(f"Alta volatilidad en {symbol} - Mercado activo")
            elif volatility == 'low':
                news_items.append(f"Baja volatilidad en {symbol} - Mercado tranquilo")
            
            # Analizar indicadores técnicos
            rsi = technical_indicators.get('rsi', 50)
            if rsi > 70:
                news_items.append(f"RSI en {rsi} - Posible sobrecompra")
            elif rsi < 30:
                news_items.append(f"RSI en {rsi} - Posible sobreventa")
            else:
                news_items.append(f"RSI en {rsi} - Zona neutral")
            
            # Analizar posición respecto a medias móviles
            current_price = market_data.get('current_price', 0)
            ma_20 = technical_indicators.get('ma_20', 0)
            ma_50 = technical_indicators.get('ma_50', 0)
            
            if current_price > ma_20 and current_price > ma_50:
                news_items.append(f"Precio por encima de medias móviles - Fortaleza")
            elif current_price < ma_20 and current_price < ma_50:
                news_items.append(f"Precio por debajo de medias móviles - Debilidad")
            
            # Agregar información de sesión de trading
            current_hour = datetime.now().hour
            if 8 <= current_hour < 17:
                news_items.append("Sesión europea/americana activa")
            elif 0 <= current_hour < 8:
                news_items.append("Sesión asiática activa")
            
            logger.info(f"📰 Contexto de mercado generado para {symbol}: {len(news_items)} elementos")
            return news_items
            
        except Exception as e:
            logger.error(f"Error generando contexto de mercado: {str(e)}")
            return ["Contexto de mercado no disponible temporalmente"]
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calcular RSI"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not rsi.empty and not pd.isna(rsi.iloc[-1]) else 50.0
        except:
            return 50.0
    
    def _calculate_macd(self, prices: pd.Series) -> tuple:
        """Calcular MACD"""
        try:
            exp1 = prices.ewm(span=12).mean()
            exp2 = prices.ewm(span=26).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9).mean()
            macd_histogram = macd_line - signal_line
            return (
                macd_line.iloc[-1] if not macd_line.empty else 0.0,
                signal_line.iloc[-1] if not signal_line.empty else 0.0,
                macd_histogram.iloc[-1] if not macd_histogram.empty else 0.0
            )
        except:
            return 0.0, 0.0, 0.0
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20):
        """Calcular Bollinger Bands"""
        try:
            sma = prices.rolling(period).mean()
            std = prices.rolling(period).std()
            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)
            return (
                upper_band.iloc[-1] if not upper_band.empty else prices.iloc[-1] * 1.02,
                lower_band.iloc[-1] if not lower_band.empty else prices.iloc[-1] * 0.98
            )
        except:
            return prices.iloc[-1] * 1.02, prices.iloc[-1] * 0.98
    
    def _calculate_stochastic(self, highs: pd.Series, lows: pd.Series, closes: pd.Series, period: int = 14):
        """Calcular Stochastic"""
        try:
            lowest_low = lows.rolling(period).min()
            highest_high = highs.rolling(period).max()
            stoch = 100 * ((closes - lowest_low) / (highest_high - lowest_low))
            return stoch.iloc[-1] if not stoch.empty else 50.0
        except:
            return 50.0
    
    def _get_fallback_indicators(self) -> Dict[str, Any]:
        """Indicadores de fallback en caso de error"""
        return {
            "rsi": 50.0,
            "macd": 0.0,
            "ma_20": 0.0,
            "ma_50": 0.0,
            "ma_200": 0.0,
            "support": 0.0,
            "resistance": 0.0,
            "bollinger_upper": 0.0,
            "bollinger_lower": 0.0,
            "stochastic": 50.0
        }
    
    def get_analysis_history(self, user_id: int, symbol: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener historial de análisis"""
        with get_db() as db:
            query = db.query(AIAnalysisHistory).filter(AIAnalysisHistory.user_id == user_id)
            
            if symbol:
                query = query.filter(AIAnalysisHistory.symbol == symbol)
            
            history = query.order_by(AIAnalysisHistory.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": item.id,
                    "symbol": item.symbol,
                    "analysis_type": item.analysis_type,
                    "signal": item.signal,
                    "confidence": item.confidence,
                    "ai_provider": item.ai_provider,
                    "ai_model": item.ai_model,
                    "processing_time": item.processing_time,
                    "created_at": item.created_at
                }
                for item in history
                
            ]

# Instancia global
analysis_service = AnalysisService()