from sqlalchemy import Column, Integer, String, Boolean, Text, Float, DateTime
from sqlalchemy.sql import func
from ..database.db_connection import Base

class UserAIConfig(Base):
    __tablename__ = "user_ai_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Proveedor y configuración
    ai_provider = Column(String, default="deepseek")  # deepseek, openai, gemini, claude
    ai_model = Column(String, default="deepseek-chat")
    api_key = Column(Text)  # Encriptar en producción!
    is_active = Column(Boolean, default=True)
    
    # Configuración de análisis
    max_tokens = Column(Integer, default=4000)
    temperature = Column(Float, default=0.7)
    confidence_threshold = Column(Float, default=70.0)
    
    # Metadatos
    last_used = Column(String)
    total_requests = Column(Integer, default=0)
    created_at = Column(String, server_default=func.now())
    updated_at = Column(String, server_default=func.now(), onupdate=func.now())

class AIAnalysisHistory(Base):
    __tablename__ = "ai_analysis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    symbol = Column(String, index=True)
    timeframe = Column(String, default="M5")
    analysis_type = Column(String, default="comprehensive")
    input_prompt = Column(Text)
    ai_response = Column(Text)
    ai_provider = Column(String)
    ai_model = Column(String)
    signal = Column(String)  # BUY, SELL, HOLD
    confidence = Column(Float)
    reasoning = Column(Text)
    processing_time = Column(Float)
    tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())