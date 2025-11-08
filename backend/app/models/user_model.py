from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.sql import func
from ..database.db_connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Configuración de trading para aplicación de escritorio
    risk_level = Column(String, default="moderate")  # low, moderate, aggressive
    confidence_threshold = Column(Float, default=70.0)  # 0-100%
    default_lot_size = Column(Float, default=0.1)
    theme = Column(String, default="light")  # light, dark

class UserConfig(Base):
    __tablename__ = "user_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    selected_assets = Column(String, default="EURUSD,GBPUSD,XAUUSD,BTCUSD")
    auto_trading = Column(Boolean, default=False)
    notifications_enabled = Column(Boolean, default=True)
    trading_hours = Column(String, default='{"start": "09:00", "end": "17:00"}')