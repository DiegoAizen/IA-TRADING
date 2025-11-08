# backend/app/api/routes_bot.py - ARCHIVO COMPLETO
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..database.db_connection import get_db
from ..models.config_model import BotConfig
from ..models.user_model import User
from ..core.security import get_current_user
from ..core.logger import logger
from ..services.bot_orchestrator import bot_orchestrator

router = APIRouter()

@router.get("/status")
async def get_bot_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estado actual del bot"""
    try:
        bot_config = db.query(BotConfig).filter(BotConfig.user_id == current_user.id).first()
        
        if not bot_config:
            # Crear configuración por defecto si no existe
            bot_config = BotConfig(
                user_id=current_user.id,
                bot_name="Mi Bot de Trading",
                is_active=False,
                auto_trading=False,
                max_drawdown=10.0,
                daily_loss_limit=5.0,
                max_open_trades=3,
                trading_strategy="moderate",
                default_lot_size=0.1,
                max_lot_size=1.0,
                min_lot_size=0.01,
                allowed_symbols="EURUSD,GBPUSD,USDJPY,XAUUSD",
                trading_hours_start="00:00",
                trading_hours_end="23:59",
                trading_days="1,2,3,4,5",
                use_trailing_stop=False,
                trailing_stop_distance=50.0,
                default_stop_loss=100.0,
                default_take_profit=200.0,
                email_notifications=True,
                sound_notifications=True
            )
            db.add(bot_config)
            db.commit()
            db.refresh(bot_config)
        
        # Obtener información de operaciones actuales (mock por ahora)
        from ..services.broker_api import broker_api
        portfolio = broker_api.get_portfolio_status()
        
        current_trades = 0
        if portfolio["success"]:
            current_trades = len(portfolio["open_positions"])
        
        return {
            "status": "active" if bot_config.is_active else "stopped",
            "auto_trading": bot_config.auto_trading,
            "trading_strategy": bot_config.trading_strategy,
            "max_open_trades": bot_config.max_open_trades,
            "max_drawdown": bot_config.max_drawdown,
            "daily_loss_limit": bot_config.daily_loss_limit,
            "default_lot_size": bot_config.default_lot_size,
            "allowed_symbols": bot_config.allowed_symbols,
            "default_stop_loss": bot_config.default_stop_loss,
            "default_take_profit": bot_config.default_take_profit,
            "current_trades": current_trades,
            "last_signal": "2024-01-01T10:30:00Z",  # Mock data
            "performance_today": {
                "trades": 5,
                "win_rate": 60.0,
                "profit": 150.75
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_bot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Iniciar el bot de trading"""
    try:
        # Actualizar configuración
        bot_config = db.query(BotConfig).filter(BotConfig.user_id == current_user.id).first()
        if bot_config:
            bot_config.is_active = True
            db.commit()
        
        # Iniciar orchestrator en segundo plano
        asyncio.create_task(bot_orchestrator.start_bot(current_user.id))
        
        return {
            "success": True, 
            "message": "Bot iniciado correctamente",
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Error iniciando bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_bot(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Detener el bot de trading"""
    try:
        bot_orchestrator.stop_bot()
        
        # Actualizar configuración
        bot_config = db.query(BotConfig).filter(BotConfig.user_id == current_user.id).first()
        if bot_config:
            bot_config.is_active = False
            db.commit()
        
        return {
            "success": True,
            "message": "Bot detenido correctamente", 
            "status": "stopped"
        }
        
    except Exception as e:
        logger.error(f"Error deteniendo bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/settings")
async def update_bot_settings(
    settings: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar configuración del bot"""
    try:
        bot_config = db.query(BotConfig).filter(BotConfig.user_id == current_user.id).first()
        
        if not bot_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuración del bot no encontrada"
            )
        
        # Actualizar configuración
        update_fields = [
            'auto_trading', 'trading_strategy', 'max_open_trades', 'max_drawdown',
            'daily_loss_limit', 'default_lot_size', 'allowed_symbols', 
            'default_stop_loss', 'default_take_profit'
        ]
        
        for field in update_fields:
            if field in settings:
                setattr(bot_config, field, settings[field])
        
        db.commit()
        
        return {
            "success": True,
            "message": "Configuración actualizada correctamente",
            "settings": {
                "auto_trading": bot_config.auto_trading,
                "trading_strategy": bot_config.trading_strategy,
                "max_open_trades": bot_config.max_open_trades,
                "max_drawdown": bot_config.max_drawdown,
                "daily_loss_limit": bot_config.daily_loss_limit,
                "default_lot_size": bot_config.default_lot_size,
                "allowed_symbols": bot_config.allowed_symbols,
                "default_stop_loss": bot_config.default_stop_loss,
                "default_take_profit": bot_config.default_take_profit
            }
        }
        
    except Exception as e:
        logger.error(f"Error actualizando configuración del bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))