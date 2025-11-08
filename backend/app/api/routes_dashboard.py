# backend/app/api/routes_dashboard.py - DATOS REALES
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database.db_connection import get_db
from ..models.user_model import User
from ..models.trade_model import Trade
from ..models.config_model import BotConfig
from ..core.security import get_current_user
from ..services.broker_api import broker_api
from ..services.data_fetcher import data_fetcher
from ..core.logger import logger

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas para el dashboard con datos reales de MT5"""
    try:
        # Obtener información de la cuenta desde MT5
        portfolio_status = broker_api.get_portfolio_status()
        
        # Datos de cuenta desde MT5
        account_info = portfolio_status.get("account_info", {}) if portfolio_status["success"] else {}
        open_positions = portfolio_status.get("open_positions", []) if portfolio_status["success"] else []
        
        # Operaciones del día desde base de datos
        today = datetime.now().date()
        today_trades = db.query(Trade).filter(
            Trade.user_id == current_user.id,
            Trade.opened_at >= today
        ).all()
        
        # Estadísticas básicas
        total_trades = db.query(Trade).filter(Trade.user_id == current_user.id).count()
        open_trades = len(open_positions)  # ✅ Operaciones reales de MT5
        
        # Profit del día
        profit_today = sum(trade.profit for trade in today_trades if trade.profit)
        
        # Operaciones ganadoras del día
        winning_trades_today = len([t for t in today_trades if t.profit and t.profit > 0])
        win_rate_today = (winning_trades_today / len(today_trades) * 100) if today_trades else 0
        
        # Calcular win rate general basado en historial
        all_trades = db.query(Trade).filter(Trade.user_id == current_user.id).all()
        winning_trades_total = len([t for t in all_trades if t.profit and t.profit > 0])
        win_rate_total = (winning_trades_total / len(all_trades) * 100) if all_trades else 0
        
        # Profit total real
        total_profit = sum(trade.profit for trade in all_trades if trade.profit)
        
        # Estado del bot
        bot_config = db.query(BotConfig).filter(BotConfig.user_id == current_user.id).first()
        bot_status = "active" if bot_config and bot_config.is_active else "stopped"
        
        # Obtener última actividad del bot
        last_activity = None
        if bot_config and bot_config.is_active:
            last_trade = db.query(Trade).filter(
                Trade.user_id == current_user.id
            ).order_by(Trade.opened_at.desc()).first()
            last_activity = last_trade.opened_at if last_trade else datetime.now()
        
        return {
            # ✅ DATOS REALES DE MT5
            "balance": account_info.get("balance", 0.0),
            "equity": account_info.get("equity", 0.0),
            "margin": account_info.get("margin", 0.0),
            "free_margin": account_info.get("free_margin", 0.0),
            "performance": {
                "profit_today": round(profit_today, 2),
                "trades_today": len(today_trades),
                "win_rate_today": round(win_rate_today, 2),
                "best_trade_today": max([t.profit for t in today_trades], default=0),
                "worst_trade_today": min([t.profit for t in today_trades], default=0)
            },
            "bot_status": {
                "status": bot_status,
                "auto_trading": bot_config.auto_trading if bot_config else False,
                "strategy": bot_config.trading_strategy if bot_config else "moderate",
                "last_activity": last_activity.isoformat() if last_activity else None
            },
            "summary": {
                "total_trades": total_trades,
                "open_trades": open_trades,  # ✅ Operaciones reales abiertas
                "win_rate": round(win_rate_total, 2),  # ✅ Win rate real
                "total_profit": round(total_profit, 2)  # ✅ Profit real
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del dashboard: {str(e)}")
        # Fallback a datos básicos en caso de error
        return {
            "balance": 0.0,
            "equity": 0.0,
            "margin": 0.0,
            "free_margin": 0.0,
            "performance": {
                "profit_today": 0.0,
                "trades_today": 0,
                "win_rate_today": 0.0,
                "best_trade_today": 0.0,
                "worst_trade_today": 0.0
            },
            "bot_status": {
                "status": "stopped",
                "auto_trading": False,
                "strategy": "moderate",
                "last_activity": None
            },
            "summary": {
                "total_trades": 0,
                "open_trades": 0,
                "win_rate": 0.0,
                "total_profit": 0.0
            }
        }

@router.get("/market-overview")
async def get_market_overview():
    """Obtener overview del mercado con datos reales de MT5"""
    try:
        # Obtener símbolos populares
        popular_symbols = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "USDJPY", "AUDUSD"]
        market_data = []
        
        for symbol in popular_symbols:
            try:
                # Obtener precio actual desde MT5
                price_data = data_fetcher.get_current_price(symbol)
                if price_data:
                    # Obtener datos históricos para calcular cambios
                    historical_data = data_fetcher.get_market_data(symbol, timeframe=1, count=2)  # M1 para cambio reciente
                    
                    if historical_data is not None and not historical_data.empty:
                        current_price = price_data['bid']
                        previous_price = historical_data['close'].iloc[-2] if len(historical_data) > 1 else current_price
                        price_change = ((current_price - previous_price) / previous_price) * 100
                        
                        # Determinar tendencia y volumen
                        trend = "up" if price_change > 0 else "down" if price_change < 0 else "flat"
                        
                        # Clasificar volumen (simplificado)
                        spread = price_data['spread']
                        if spread <= 0.0003:
                            volume_category = "high"
                        elif spread <= 0.0006:
                            volume_category = "medium"
                        else:
                            volume_category = "low"
                        
                        market_data.append({
                            "symbol": symbol,
                            "bid": round(price_data['bid'], 5),
                            "ask": round(price_data['ask'], 5),
                            "spread": round(spread, 5),
                            "change": round(price_change, 2),
                            "trend": trend,
                            "volume": volume_category
                        })
            except Exception as e:
                logger.warning(f"Error obteniendo datos para {symbol}: {str(e)}")
                continue
        
        # Noticias del mercado (placeholder - podrías integrar una API de noticias)
        market_news = [
            {
                "title": "Mercado Forex operando normalmente",
                "impact": "low",
                "currency": "GLOBAL",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        return {
            "market_status": "open",  # Podrías verificar horarios de trading
            "active_symbols": market_data,
            "market_news": market_news
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo overview del mercado: {str(e)}")
        # Fallback básico
        return {
            "market_status": "unknown",
            "active_symbols": [],
            "market_news": []
        }

@router.get("/recent-activity")
async def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener actividad reciente con datos reales"""
    try:
        # Últimas operaciones de la base de datos
        recent_trades = db.query(Trade).filter(
            Trade.user_id == current_user.id
        ).order_by(Trade.opened_at.desc()).limit(5).all()
        
        # Operaciones abiertas actuales desde MT5
        portfolio_status = broker_api.get_portfolio_status()
        open_positions = portfolio_status.get("open_positions", []) if portfolio_status["success"] else []
        
        # Señales recientes de análisis de IA (desde base de datos)
        from ..models.ai_config_model import AIAnalysisHistory
        
        recent_analyses = db.query(AIAnalysisHistory).filter(
            AIAnalysisHistory.user_id == current_user.id
        ).order_by(AIAnalysisHistory.created_at.desc()).limit(5).all()
        
        recent_signals = [
            {
                "symbol": analysis.symbol,
                "signal": analysis.signal,
                "confidence": analysis.confidence,
                "timestamp": analysis.created_at.isoformat() if analysis.created_at else datetime.now().isoformat(),
                "strength": "strong" if analysis.confidence >= 80 else "moderate" if analysis.confidence >= 60 else "weak"
            }
            for analysis in recent_analyses
        ]
        
        # Alertas del sistema basadas en estado actual
        system_alerts = []
        
        # Verificar conexión MT5
        if not data_fetcher.connected:
            system_alerts.append({
                "type": "warning",
                "message": "MT5 desconectado - Conecta para operar",
                "timestamp": datetime.now().isoformat()
            })
        
        # Verificar límites de riesgo
        bot_config = db.query(BotConfig).filter(BotConfig.user_id == current_user.id).first()
        if bot_config and bot_config.is_active:
            if len(open_positions) >= bot_config.max_open_trades:
                system_alerts.append({
                    "type": "info", 
                    "message": f"Límite de operaciones alcanzado ({len(open_positions)}/{bot_config.max_open_trades})",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Si no hay alertas, agregar una de estado normal
        if not system_alerts:
            system_alerts.append({
                "type": "info",
                "message": "Sistema operando normalmente",
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "recent_trades": [
                {
                    "id": trade.id,
                    "symbol": trade.symbol,
                    "type": trade.operation_type,
                    "volume": trade.volume,
                    "profit": trade.profit,
                    "status": trade.status,
                    "timestamp": trade.opened_at
                }
                for trade in recent_trades
            ],
            "recent_signals": recent_signals,
            "system_alerts": system_alerts,
            "open_positions": [  # ✅ Información de operaciones abiertas actuales
                {
                    "symbol": pos["symbol"],
                    "type": pos["type"],
                    "volume": pos["volume"],
                    "profit": pos["profit"],
                    "open_price": pos["open_price"]
                }
                for pos in open_positions[:3]  # Solo mostrar primeras 3
            ]
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo actividad reciente: {str(e)}")
        return {
            "recent_trades": [],
            "recent_signals": [],
            "system_alerts": [{
                "type": "error",
                "message": "Error cargando actividad reciente",
                "timestamp": datetime.now().isoformat()
            }],
            "open_positions": []
        }