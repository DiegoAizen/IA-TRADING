from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..database.db_connection import get_db
from ..models.user_model import User, UserConfig
from ..models.config_model import BotConfig
from ..core.security import get_current_user

router = APIRouter()

@router.get("/")
async def get_user_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener configuración completa del usuario"""
    user_config = db.query(UserConfig).filter(UserConfig.user_id == current_user.id).first()
    bot_config = db.query(BotConfig).filter(BotConfig.user_id == current_user.id).first()
    
    if not user_config or not bot_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración no encontrada"
        )
    
    return {
        "user_settings": {
            "selected_assets": user_config.selected_assets.split(',') if user_config.selected_assets else [],
            "notifications_enabled": user_config.notifications_enabled,
            "trading_hours": user_config.trading_hours,
            "risk_level": current_user.risk_level,
            "confidence_threshold": current_user.confidence_threshold,
            "default_lot_size": current_user.default_lot_size,
            "theme": current_user.theme
        },
        "bot_settings": {
            "auto_trading": bot_config.auto_trading,
            "trading_strategy": bot_config.trading_strategy,
            "max_open_trades": bot_config.max_open_trades,
            "max_drawdown": bot_config.max_drawdown,
            "daily_loss_limit": bot_config.daily_loss_limit,
            "bot_name": bot_config.bot_name
        }
    }

@router.put("/user")
async def update_user_config(
    config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar configuración de usuario"""
    user_config = db.query(UserConfig).filter(UserConfig.user_id == current_user.id).first()
    
    if not user_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración de usuario no encontrada"
        )
    
    # Actualizar UserConfig
    if 'selected_assets' in config:
        user_config.selected_assets = ','.join(config['selected_assets']) if isinstance(config['selected_assets'], list) else config['selected_assets']
    
    if 'notifications_enabled' in config:
        user_config.notifications_enabled = config['notifications_enabled']
    
    if 'trading_hours' in config:
        user_config.trading_hours = config['trading_hours']
    
    # Actualizar User
    if 'risk_level' in config:
        current_user.risk_level = config['risk_level']
    
    if 'confidence_threshold' in config:
        current_user.confidence_threshold = config['confidence_threshold']
    
    if 'default_lot_size' in config:
        current_user.default_lot_size = config['default_lot_size']
    
    if 'theme' in config:
        current_user.theme = config['theme']
    
    db.commit()
    
    return {
        "message": "Configuración de usuario actualizada",
        "config": {
            "selected_assets": user_config.selected_assets.split(','),
            "notifications_enabled": user_config.notifications_enabled,
            "trading_hours": user_config.trading_hours,
            "risk_level": current_user.risk_level,
            "confidence_threshold": current_user.confidence_threshold,
            "default_lot_size": current_user.default_lot_size,
            "theme": current_user.theme
        }
    }

@router.put("/bot")
async def update_bot_config(
    config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar configuración del bot"""
    bot_config = db.query(BotConfig).filter(BotConfig.user_id == current_user.id).first()
    
    if not bot_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración del bot no encontrada"
        )
    
    # Actualizar BotConfig
    update_fields = [
        'auto_trading', 'trading_strategy', 'max_open_trades', 
        'max_drawdown', 'daily_loss_limit', 'bot_name'
    ]
    
    for field in update_fields:
        if field in config:
            setattr(bot_config, field, config[field])
    
    db.commit()
    
    return {
        "message": "Configuración del bot actualizada",
        "config": {
            "auto_trading": bot_config.auto_trading,
            "trading_strategy": bot_config.trading_strategy,
            "max_open_trades": bot_config.max_open_trades,
            "max_drawdown": bot_config.max_drawdown,
            "daily_loss_limit": bot_config.daily_loss_limit,
            "bot_name": bot_config.bot_name
        }
    }

@router.get("/available-assets")
async def get_available_assets():
    """Obtener lista de activos disponibles para trading"""
    return {
        "forex": [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
            "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "EURCHF", "GBPCHF"
        ],
        "indices": [
            "US30", "US500", "NAS100", "GER30", "UK100", "JPN225"
        ],
        "commodities": [
            "XAUUSD", "XAGUSD", "XPTUSD", "XPDUSD", "OIL", "NATGAS"
        ],
        "cryptos": [
            "BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "BCHUSD", "ADAUSD"
        ]
    }

@router.get("/risk-profiles")
async def get_risk_profiles():
    """Obtener perfiles de riesgo disponibles"""
    return {
        "low": {
            "name": "Conservador",
            "description": "Bajo riesgo, ganancias estables",
            "max_drawdown": 5.0,
            "daily_trades": "1-2",
            "profit_target": 2.0,
            "lot_size_multiplier": 0.5
        },
        "moderate": {
            "name": "Moderado", 
            "description": "Balance entre riesgo y recompensa",
            "max_drawdown": 10.0,
            "daily_trades": "3-5",
            "profit_target": 5.0,
            "lot_size_multiplier": 1.0
        },
        "aggressive": {
            "name": "Agresivo",
            "description": "Alto riesgo, máximo potencial",
            "max_drawdown": 20.0,
            "daily_trades": "5-10", 
            "profit_target": 10.0,
            "lot_size_multiplier": 2.0
        }
    }