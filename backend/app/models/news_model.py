# backend/app/models/news_model.py - NUEVO ARCHIVO
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.sql import func
from ..database.db_connection import Base

class MarketNews(Base):
    __tablename__ = "market_news"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)  # Símbolo relacionado (EURUSD, XAUUSD, etc.)
    title = Column(String, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    source = Column(String)
    url = Column(String)
    image_url = Column(String)
    published_at = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, default=func.now())
    
    # Categorización
    category = Column(String)  # forex, crypto, commodities, etc.
    impact_level = Column(String)  # low, medium, high, critical
    sentiment = Column(String)  # positive, negative, neutral
    
    # Metadatos para IA
    relevance_score = Column(Float, default=0.0)  # 0-1 qué tan relevante es
    key_points = Column(JSON)  # Puntos clave extraídos
    trading_implications = Column(Text)  # Implicaciones de trading
    
    # Control de caché
    is_high_impact = Column(Boolean, default=False)  # No se borra
    last_used_in_analysis = Column(DateTime)
    usage_count = Column(Integer, default=0)

class NewsAnalysisHistory(Base):
    __tablename__ = "news_analysis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    symbol = Column(String, index=True)
    analysis_timestamp = Column(DateTime, default=func.now())
    
    # Noticias usadas en este análisis
    news_used = Column(JSON)  # Lista de IDs de noticias usadas
    total_news_considered = Column(Integer)
    high_impact_news_count = Column(Integer)
    
    # Resultados
    news_sentiment_score = Column(Float)  # -1 a 1
    market_context = Column(Text)  # Contexto generado para la IA