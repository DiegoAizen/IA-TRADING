# backend/app/services/bot_orchestrator.py

import asyncio
from datetime import datetime
from ..core.logger import logger
from .bot_analysis_service import bot_analysis_service
from .analysis_service import analysis_service
from .trading_service import trading_service
from .broker_api import broker_api
from ..database.db_connection import get_db
from typing import Dict

class BotOrchestrator:
    def __init__(self):
        self.is_running = False
        self.analysis_interval = 300
        self.reanalysis_interval = 60
        self.symbol_delay = 120 
        self.current_cycle = 0
    
    async def start_bot(self, user_id: int):
        """Iniciar el ciclo continuo del bot con DELAYS entre símbolos"""
        logger.info(f"🚀 Iniciando Bot Orchestrator para usuario {user_id}")
        self.is_running = True
        
        while self.is_running:
            try:
                self.current_cycle += 1
                logger.info(f"🔄 Ciclo #{self.current_cycle} - {datetime.now()}")
                
                # 1. Reanalizar operaciones abiertas
                await self._reanalyze_open_trades(user_id)
                
                # 2. Buscar nuevas oportunidades (cada 5 minutos)
                if self.current_cycle % 5 == 0:
                    await self._analyze_new_opportunities(user_id)
                
                # 3. Verificar límites de riesgo
                await self._check_risk_limits(user_id)
                
                await asyncio.sleep(self.reanalysis_interval)
                
            except Exception as e:
                logger.error(f"❌ Error en ciclo bot: {str(e)}")
                await asyncio.sleep(30)
    
    async def _reanalyze_open_trades(self, user_id: int):
        """Reanalizar y ajustar operaciones abiertas"""
        try:
            portfolio = broker_api.get_portfolio_status()
            if not portfolio["success"]:
                return
            
            open_positions = portfolio.get("open_positions", [])
            
            for position in open_positions:
                logger.info(f"🔍 Reanalizando posición: {position['symbol']}")
                
                analysis = await analysis_service.analyze_symbol(
                    position['symbol'], 
                    user_id, 
                    "reanalysis"
                )
                
                if analysis["success"]:
                    await self._adjust_trade_based_on_analysis(position, analysis)
                    
        except Exception as e:
            logger.error(f"Error en reanálisis: {str(e)}")
    
    async def _adjust_trade_based_on_analysis(self, position: Dict, analysis: Dict):
        """Ajustar operación basado en análisis - CORREGIDO"""
        try:
            signal = analysis.get("signal", "HOLD")
            confidence = analysis.get("confidence", 0)
            
            # ❌ ELIMINADO: Lógica de "CLOSE" que nunca se ejecuta
            # ✅ NUEVA: Usar stops de la IA para ajustar posición existente
            
            if confidence >= 70 and signal in ["BUY", "SELL"]:
                stop_loss = analysis.get("stop_loss")
                take_profit = analysis.get("take_profit")
                
                # Si la IA proporciona stops, ajustar la posición
                if stop_loss and take_profit:
                    result = trading_service.modify_position(
                        position["ticket"], 
                        stop_loss=stop_loss, 
                        take_profit=take_profit
                    )
                    if result["success"]:
                        logger.info(f"⚙️ Stops ajustados: {position['symbol']} | SL: {stop_loss}, TP: {take_profit}")
            
            # ✅ NUEVA: Cerrar si la confianza es muy baja para la dirección actual
            elif confidence < 30:
                # Verificar si la señal es contraria a la posición actual
                current_direction = "BUY" if position.get("type") == 0 else "SELL"
                if signal != current_direction and signal != "HOLD":
                    result = trading_service.close_position(position["ticket"])
                    if result["success"]:
                        logger.info(f"🛑 Posición cerrada por señal contraria: {position['symbol']}")
                    
        except Exception as e:
            logger.error(f"Error ajustando posición: {str(e)}")
    
    async def _analyze_new_opportunities(self, user_id: int):
        """Buscar nuevas oportunidades con DELAYS entre símbolos"""
        db = None
        try:
            logger.info(f"🤖 BOT Buscando oportunidades para usuario {user_id}")
            
            db = next(get_db())
            from ..models.config_model import BotConfig
            bot_config = db.query(BotConfig).filter(BotConfig.user_id == user_id).first()
            
            if not bot_config or not bot_config.is_active or not bot_config.allowed_symbols:
                logger.info("⏹️ Bot inactivo o sin configuración")
                return
            
            symbols = [s.strip() for s in bot_config.allowed_symbols.split(",")]
            logger.info(f"🤖 BOT Analizando símbolos: {symbols}")
            
            # ✅ NUEVO: Analizar CADA símbolo con delay de 2 minutos
            for i, symbol in enumerate(symbols):
                try:
                    logger.info(f"🔍 BOT Analizando símbolo {i+1}/{len(symbols)}: {symbol}")
                    
                    result = await bot_analysis_service.analyze_and_execute(symbol, user_id, bot_config)
                    
                    if result.get("success"):
                        execution_result = result.get("execution_result", {})
                        if execution_result.get("executed"):
                            logger.info(f"🎯 BOT OPERACIÓN EJECUTADA: {symbol}")
                        else:
                            logger.info(f"⏹️ BOT No ejecutado {symbol}: {execution_result.get('reason')}")
                    else:
                        logger.error(f"❌ BOT Error en análisis de {symbol}: {result.get('error')}")
                    
                    # ✅ NUEVO: Esperar 2 minutos antes del próximo símbolo (excepto el último)
                    if i < len(symbols) - 1:
                        logger.info(f"⏳ Esperando {self.symbol_delay} segundos antes del próximo símbolo...")
                        await asyncio.sleep(self.symbol_delay)
                    
                except Exception as e:
                    logger.error(f"❌ BOT Error con {symbol}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ BOT Error en búsqueda de oportunidades: {str(e)}")
        finally:
            if db:
                db.close()

    async def _execute_best_opportunities(self, analysis_result: Dict, bot_config):
        """Ejecutar mejores oportunidades - CORREGIDO"""
        try:
            best_buy = analysis_result.get("buy_opportunities", [])
            best_sell = analysis_result.get("sell_opportunities", [])
            
            # EJECUTAR operaciones BUY
            for opportunity in best_buy[:2]:  # Máximo 2 operaciones por ciclo
                if opportunity.get("confidence", 0) >= 75:
                    await self._execute_trade(opportunity, "BUY", bot_config)
                    await asyncio.sleep(1)  # Pausa entre ejecuciones
            
            # EJECUTAR operaciones SELL  
            for opportunity in best_sell[:2]:  # Máximo 2 operaciones por ciclo
                if opportunity.get("confidence", 0) >= 75:
                    await self._execute_trade(opportunity, "SELL", bot_config)
                    await asyncio.sleep(1)  # Pausa entre ejecuciones
                        
        except Exception as e:
            logger.error(f"Error ejecutando oportunidades: {str(e)}")
    
    async def _execute_trade(self, opportunity: Dict, order_type: str, bot_config):
        try:
            symbol = opportunity["symbol"]
            confidence = opportunity.get("confidence", 0)
            
            # ✅ LOG TEMPORAL PARA DEBUG
            logger.info(f"🔧 DEBUG _execute_trade INICIADO: {symbol} {order_type} {confidence}%")
            
            # 1. Verificar portfolio
            portfolio = broker_api.get_portfolio_status()
            logger.info(f"🔧 DEBUG Portfolio success: {portfolio.get('success')}")
            
            if portfolio["success"]:
                open_positions = portfolio.get("open_positions", [])
                logger.info(f"🔧 DEBUG Posiciones abiertas: {len(open_positions)}")
                
                # ✅ CORREGIR: Buscar por símbolo sin importar el tipo
                existing_trade = any(pos["symbol"] == symbol for pos in open_positions)
                logger.info(f"🔧 DEBUG Operación existente en {symbol}: {existing_trade}")
                
                if existing_trade:
                    logger.info(f"⏹️ Ya existe operación en {symbol}")
                    return
            else:
                logger.error(f"❌ Error obteniendo portfolio: {portfolio.get('error')}")
                return
            
            # 2. Obtener precio actual
            current_price = await self._get_current_price(symbol)
            logger.info(f"🔧 DEBUG Precio actual {symbol}: {current_price}")
            
            if not current_price:
                logger.error(f"❌ No se pudo obtener precio para {symbol}")
                return
            
            # 3. Calcular stops
            stop_loss, take_profit = self._calculate_stops(
                order_type, current_price, bot_config.default_stop_loss or 50.0
            )
            logger.info(f"🔧 DEBUG Stops calculados: SL={stop_loss:.5f}, TP={take_profit:.5f}")
            
            # 4. Ejecutar orden
            volume = bot_config.default_lot_size or 0.1
            logger.info(f"🔧 DEBUG Ejecutando orden: {symbol} {order_type} {volume} lots")
            
            result = trading_service.place_order(
                symbol=symbol,
                order_type=order_type,
                volume=volume,
                stop_loss=stop_loss,
                take_profit=take_profit,
                magic=123456,
                comment=f"AI Bot - Conf: {confidence}%"
            )
            
            logger.info(f"🔧 DEBUG Resultado place_order: {result}")
            
            if result["success"]:
                logger.info(f"✅ OPERACIÓN EJECUTADA: {symbol} {order_type}")
            else:
                logger.error(f"❌ ERROR ejecutando orden: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"💥 ERROR CRÍTICO en _execute_trade: {str(e)}")

    async def _get_current_price(self, symbol: str) -> float:
        """Obtener precio actual para calcular stops"""
        try:
            from .data_fetcher import data_fetcher
            price_data = data_fetcher.get_current_price(symbol)
            return price_data.get('bid') if price_data else None
        except Exception as e:
            logger.error(f"Error obteniendo precio de {symbol}: {str(e)}")
            return None

    def _calculate_stops(self, signal: str, entry_price: float, stop_loss_pips: float) -> tuple:
        """Calcular stop loss y take profit"""
        pip_value = 0.0001
        
        if signal == "BUY":
            stop_loss = entry_price - (stop_loss_pips * pip_value)
            take_profit = entry_price + (stop_loss_pips * 2 * pip_value)  # 1:2 ratio
        else:  # SELL
            stop_loss = entry_price + (stop_loss_pips * pip_value)
            take_profit = entry_price - (stop_loss_pips * 2 * pip_value)
        
        return stop_loss, take_profit

    async def _check_risk_limits(self, user_id: int):
        """Verificar límites de riesgo - CORREGIDO"""
        db = None
        try:
            db = next(get_db())
            
            from ..models.config_model import BotConfig
            bot_config = db.query(BotConfig).filter(BotConfig.user_id == user_id).first()
            
            if not bot_config:
                return
            
            portfolio = broker_api.get_portfolio_status()
            if not portfolio["success"]:
                return
            
            account_info = portfolio.get("account_info", {})
            balance = account_info.get("balance", 0)
            equity = account_info.get("equity", 0)
            
            if balance > 0:
                drawdown_percent = ((balance - equity) / balance) * 100
                if drawdown_percent >= bot_config.max_drawdown:
                    logger.warning(f"🛑 Drawdown límite alcanzado: {drawdown_percent}%")
                    # Opcional: Cerrar todas las posiciones
                    # await self._emergency_stop()
                    
        except Exception as e:
            logger.error(f"Error verificando límites: {str(e)}")
        finally:
            if db:
                db.close()  # ✅ SIEMPRE cerrar sesión
    
    def stop_bot(self):
        """Detener el bot"""
        logger.info("🛑 Deteniendo Bot Orchestrator")
        self.is_running = False

# Instancia global
bot_orchestrator = BotOrchestrator()