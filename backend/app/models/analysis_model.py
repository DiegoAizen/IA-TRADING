from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.sql import func
from ..database.db_connection import Base

class MarketAnalysis(Base):
    __tablename__ = "market_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Información del análisis
    symbol = Column(String, nullable=False)
    timeframe = Column(String, default="M5")  # M1, M5, M15, H1, H4, D1
    analysis_type = Column(String, nullable=False)  # technical, fundamental, sentiment
    
    # Resultados del análisis
    signal = Column(String)  # BUY, SELL, HOLD
    confidence = Column(Float)  # 0-100%
    strength = Column(String)  # weak, moderate, strong
    
    # Niveles clave
    support_level = Column(Float)
    resistance_level = Column(Float)
    pivot_point = Column(Float)
    
    # Indicadores técnicos
    rsi = Column(Float)
    macd = Column(Float)
    moving_average_20 = Column(Float)
    moving_average_50 = Column(Float)
    moving_average_200 = Column(Float)
    bollinger_bands_upper = Column(Float)
    bollinger_bands_lower = Column(Float)
    
    # Metadatos
    analysis_data = Column(Text)  # JSON con datos completos
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))

class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Información de la predicción
    symbol = Column(String, nullable=False)
    model_name = Column(String, nullable=False)  # Nombre del modelo de IA
    prediction_type = Column(String, nullable=False)  # price_direction, volatility, etc.
    
    # Resultados de la predicción
    predicted_value = Column(Float)
    actual_value = Column(Float)
    confidence = Column(Float)
    prediction_range = Column(String)  # short_term, medium_term, long_term
    
    # Metadatos
    input_data = Column(Text)  # JSON con datos de entrada
    output_data = Column(Text)  # JSON con datos de salida
    is_correct = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())