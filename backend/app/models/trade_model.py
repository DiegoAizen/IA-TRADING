from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from ..database.db_connection import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Información de la operación
    symbol = Column(String, nullable=False)
    operation_type = Column(String, nullable=False)  # BUY/SELL
    volume = Column(Float, nullable=False)
    open_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=True)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    current_price = Column(Float)
    
    # Resultados
    profit = Column(Float, default=0.0)
    profit_pips = Column(Float, default=0.0)
    profit_percentage = Column(Float, default=0.0)
    
    # Estado y metadatos
    status = Column(String, default="open")  # open, closed, cancelled, pending
    magic_number = Column(Integer)  # Número mágico para MT5
    ticket = Column(Integer)  # Ticket de la operación en MT5
    
    # Análisis de IA
    ai_confidence = Column(Float)  # 0-100%
    ai_analysis = Column(Text)     # JSON con el análisis de IA
    ai_signal = Column(String)     # BUY, SELL, HOLD
    
    # Tiempos
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Metadata adicional
    comment = Column(String)
    commission = Column(Float, default=0.0)
    swap = Column(Float, default=0.0)

class TradeAnalysis(Base):
    __tablename__ = "trade_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Análisis técnico
    rsi = Column(Float)
    macd = Column(Float)
    moving_average = Column(Float)
    support_level = Column(Float)
    resistance_level = Column(Float)
    
    # Análisis de sentimiento
    market_sentiment = Column(String)  # bullish, bearish, neutral
    volatility = Column(Float)
    
    # Timestamp
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    analysis_data = Column(Text)  # JSON con datos completos del análisis