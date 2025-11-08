from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..database.db_connection import get_db
from ..models.trade_model import Trade, TradeAnalysis
from ..models.user_model import User
from ..core.security import get_current_user

router = APIRouter()

@router.get("/")
async def get_trades(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, regex="^(open|closed|cancelled|all)$"),
    symbol: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener historial de operaciones"""
    query = db.query(Trade).filter(Trade.user_id == current_user.id)
    
    # Filtros
    if status and status != "all":
        query = query.filter(Trade.status == status)
    
    if symbol:
        query = query.filter(Trade.symbol == symbol)
    
    # Ordenar por fecha de apertura (más recientes primero)
    trades = query.order_by(Trade.opened_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "trades": [
            {
                "id": trade.id,
                "symbol": trade.symbol,
                "type": trade.operation_type,
                "volume": trade.volume,
                "open_price": trade.open_price,
                "close_price": trade.close_price,
                "current_price": trade.current_price,
                "profit": trade.profit,
                "status": trade.status,
                "ai_confidence": trade.ai_confidence,
                "opened_at": trade.opened_at,
                "closed_at": trade.closed_at
            }
            for trade in trades
        ],
        "total": len(trades),
        "skip": skip,
        "limit": limit
    }

@router.get("/{trade_id}")
async def get_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener detalles de una operación específica"""
    trade = db.query(Trade).filter(
        Trade.id == trade_id,
        Trade.user_id == current_user.id
    ).first()
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operación no encontrada"
        )
    
    # Obtener análisis asociado
    analysis = db.query(TradeAnalysis).filter(
        TradeAnalysis.trade_id == trade_id
    ).first()
    
    return {
        "trade": {
            "id": trade.id,
            "symbol": trade.symbol,
            "type": trade.operation_type,
            "volume": trade.volume,
            "open_price": trade.open_price,
            "close_price": trade.close_price,
            "current_price": trade.current_price,
            "stop_loss": trade.stop_loss,
            "take_profit": trade.take_profit,
            "profit": trade.profit,
            "profit_pips": trade.profit_pips,
            "status": trade.status,
            "ai_confidence": trade.ai_confidence,
            "ai_signal": trade.ai_signal,
            "opened_at": trade.opened_at,
            "closed_at": trade.closed_at,
            "comment": trade.comment
        },
        "analysis": {
            "rsi": analysis.rsi if analysis else None,
            "macd": analysis.macd if analysis else None,
            "market_sentiment": analysis.market_sentiment if analysis else None,
            "analyzed_at": analysis.analyzed_at if analysis else None
        } if analysis else None
    }

@router.get("/stats/summary")
async def get_trading_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas de trading"""
    # Operaciones totales
    total_trades = db.query(Trade).filter(Trade.user_id == current_user.id).count()
    
    # Operaciones abiertas
    open_trades = db.query(Trade).filter(
        Trade.user_id == current_user.id,
        Trade.status == "open"
    ).count()
    
    # Operaciones cerradas
    closed_trades = db.query(Trade).filter(
        Trade.user_id == current_user.id,
        Trade.status == "closed"
    ).count()
    
    # Profit total
    total_profit = db.query(Trade).filter(
        Trade.user_id == current_user.id,
        Trade.status == "closed"
    ).with_entities(db.func.sum(Trade.profit)).scalar() or 0.0
    
    # Operaciones ganadoras
    winning_trades = db.query(Trade).filter(
        Trade.user_id == current_user.id,
        Trade.status == "closed",
        Trade.profit > 0
    ).count()
    
    # Tasa de éxito
    win_rate = (winning_trades / closed_trades * 100) if closed_trades > 0 else 0
    
    return {
        "summary": {
            "total_trades": total_trades,
            "open_trades": open_trades,
            "closed_trades": closed_trades,
            "winning_trades": winning_trades,
            "win_rate": round(win_rate, 2),
            "total_profit": round(total_profit, 2),
            "avg_profit_per_trade": round(total_profit / closed_trades, 2) if closed_trades > 0 else 0
        },
        "current_performance": {
            "profit_today": 150.75,  # Mock data
            "trades_today": 3,       # Mock data
            "best_trade": 45.20,     # Mock data
            "worst_trade": -12.50    # Mock data
        }
    }