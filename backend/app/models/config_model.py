#models/config_model.py

from sqlalchemy import Column, Integer, String, Boolean, Float, Text
from ..database.db_connection import Base

class BotConfig(Base):
    __tablename__ = "bot_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    
    # Configuración básica del bot
    bot_name = Column(String, default="Mi Bot de Trading")
    is_active = Column(Boolean, default=False)
    auto_trading = Column(Boolean, default=False)  # ⬅️ FALTABA ESTE CAMPO
    
    # Gestión de riesgo
    max_drawdown = Column(Float, default=10.0)  # máximo drawdown permitido
    daily_loss_limit = Column(Float, default=5.0)  # pérdida diaria máxima %
    max_open_trades = Column(Integer, default=3)
    
    # Estrategia
    trading_strategy = Column(String, default="conservative")  # conservative, moderate, aggressive
    
    # Configuración de operaciones
    default_lot_size = Column(Float, default=0.1)
    max_lot_size = Column(Float, default=1.0)
    min_lot_size = Column(Float, default=0.01)
    
    # Pares de trading
    allowed_symbols = Column(Text, default="EURUSD,GBPUSD,USDJPY,XAUUSD")
    
    # Horarios de trading
    trading_hours_start = Column(String, default="00:00")
    trading_hours_end = Column(String, default="23:59")
    trading_days = Column(String, default="1,2,3,4,5")  # Lunes a Viernes
    
    # Configuración de stops
    use_trailing_stop = Column(Boolean, default=False)
    trailing_stop_distance = Column(Float, default=50.0)  # en pips
    default_stop_loss = Column(Float, default=100.0)  # en pips
    default_take_profit = Column(Float, default=200.0)  # en pips
    
    # Notificaciones
    email_notifications = Column(Boolean, default=True)
    sound_notifications = Column(Boolean, default=True)