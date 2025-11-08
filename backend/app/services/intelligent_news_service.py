# backend/app/services/intelligent_news_service.py - NUEVO ARCHIVO
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from ..core.logger import logger
from ..database.db_connection import get_db
from .news_service import news_service
from ..models import MarketNews, NewsAnalysisHistory

class IntelligentNewsService:
    def __init__(self):
        self.news_cache = {}  # Cache simple en memoria
        self.news_cache_hours = 6
        self.last_api_call = 0  # Timestamp de última llamada a API
        self.min_call_interval = 120  # 2 minutos entre llamadas a Finnhub
        self.request_queue = asyncio.Queue()
        self.is_processing = False
    
    async def get_news_for_analysis(self, symbol: str, user_id: int) -> Dict[str, Any]:
        """
        Obtener noticias relevantes para análisis con RATE LIMITING
        """
        try:
            logger.info(f"📰 Obteniendo noticias inteligentes para {symbol}")
            
            # Verificar cache primero
            cache_key = f"{symbol}_{user_id}"
            cached_data = self.news_cache.get(cache_key)
            
            if cached_data and not self._should_refresh_cache(cached_data):
                logger.info(f"✅ Usando noticias en caché para {symbol}")
                return cached_data
            
            # ✅ NUEVO: Sistema de rate limiting
            await self._wait_for_api_slot()
            
            # Obtener nuevas noticias
            category = self._symbol_to_category(symbol)
            all_news = await news_service.get_market_news(category)
            
            # Filtrar noticias relevantes
            relevant_news = self._filter_relevant_news(all_news, symbol)
            
            # Formatear respuesta
            news_context = self._format_news_context(relevant_news, symbol)
            
            # Guardar en cache
            self.news_cache[cache_key] = news_context
            self.news_cache[cache_key]['cached_at'] = datetime.now().isoformat()
            
            # ✅ Actualizar timestamp de última llamada
            self.last_api_call = time.time()
            
            return news_context
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo noticias para {symbol}: {str(e)}")
            return self._get_fallback_news_context(symbol)
    
    async def _wait_for_api_slot(self):
        """Esperar hasta que podamos hacer una nueva llamada a la API"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.min_call_interval:
            wait_time = self.min_call_interval - time_since_last_call
            logger.info(f"⏳ Rate limiting: Esperando {wait_time:.1f} segundos antes de nueva llamada a API")
            await asyncio.sleep(wait_time)
        
    def _is_relevant_news(self, news: Dict, keywords: List[str]) -> bool:
        """Verificar si la noticia es relevante"""
        title = news.get('title', '').lower()
        summary = news.get('summary', '').lower()
        
        content = title + " " + summary
        return any(keyword.lower() in content for keyword in keywords)
    
    def _format_news_context(self, news_list: List[Dict], symbol: str) -> Dict[str, Any]:
        """Formatear noticias para el análisis de IA"""
        if not news_list:
            return {
                "has_news": False,
                "market_context": f"No hay noticias recientes relevantes para {symbol}.",
                "news_count": 0,
                "overall_sentiment": "neutral"
            }
        
        # Construir contexto
        context_parts = [f"📰 NOTICIAS RECIENTES PARA {symbol.upper()}:"]
        
        for i, news in enumerate(news_list[:3], 1):
            sentiment = self._analyze_news_sentiment(news)
            context_parts.append(f"{i}. [{sentiment.upper()}] {news.get('title', 'Sin título')}")
            if news.get('summary'):
                context_parts.append(f"   📝 {news.get('summary')[:120]}...")
        
        # Calcular sentimiento general
        overall_sentiment = self._calculate_overall_sentiment(news_list)
        
        context_parts.append(f"\n💡 Resumen: {len(news_list)} noticias relevantes, sentimiento general {overall_sentiment}")
        
        return {
            "has_news": True,
            "market_context": "\n".join(context_parts),
            "news_count": len(news_list),
            "overall_sentiment": overall_sentiment,
            "symbol": symbol
        }
        
    def _analyze_news_sentiment(self, news: Dict) -> str:
        """Analizar sentimiento de una noticia individual"""
        content = (news.get('title', '') + " " + news.get('summary', '')).lower()
        
        positive_words = ['bull', 'rally', 'gain', 'up', 'positive', 'strong', 'growth', 'surge', 'jump', 'optimistic']
        negative_words = ['bear', 'drop', 'fall', 'down', 'negative', 'weak', 'loss', 'crash', 'plunge', 'pessimistic']
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    async def _get_cached_news(self, symbol: str) -> List[MarketNews]:
        """Obtener noticias en caché de la base de datos"""
        db = next(get_db())
        try:
            # Obtener noticias de las últimas 24 horas, ordenadas por relevancia
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            news = db.query(MarketNews).filter(
                MarketNews.symbol == symbol,
                MarketNews.published_at >= cutoff_time
            ).order_by(
                MarketNews.impact_level.desc(),
                MarketNews.relevance_score.desc(),
                MarketNews.published_at.desc()
            ).limit(self.max_news_per_symbol).all()
            
            return news
        finally:
            db.close()
    
    def _should_refresh_cache(self, cached_data: Dict) -> bool:
        """Determinar si necesitamos refrescar el cache"""
        cached_at = cached_data.get('cached_at')
        if not cached_at:
            return True
        
        if isinstance(cached_at, str):
            cached_at = datetime.fromisoformat(cached_at)
        
        hours_since_cache = (datetime.now() - cached_at).total_seconds() / 3600
        return hours_since_cache > self.news_cache_hours
     
    async def _fetch_and_process_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Obtener y procesar noticias nuevas para un símbolo"""
        # Determinar categoría basada en el símbolo
        category = self._symbol_to_category(symbol)
        
        # Obtener noticias generales
        all_news = await news_service.get_market_news(category)
        
        # Filtrar y rankear noticias relevantes para el símbolo
        relevant_news = self._filter_relevant_news(all_news, symbol)
        
        return relevant_news
    
    def _symbol_to_category(self, symbol: str) -> str:
        """Mapear símbolo a categoría de noticias"""
        symbol_upper = symbol.upper()
        
        if any(forex in symbol_upper for forex in ['USD', 'EUR', 'JPY', 'GBP', 'CHF', 'CAD', 'AUD', 'NZD']):
            return "forex"
        elif any(crypto in symbol_upper for crypto in ['BTC', 'ETH', 'XRP', 'LTC', 'ADA', 'DOT']):
            return "crypto"
        elif any(metal in symbol_upper for metal in ['XAU', 'XAG', 'GOLD', 'SILVER']):
            return "commodities"
        else:
            return "general"
    
    def _filter_relevant_news(self, news_list: List[Dict], symbol: str) -> List[Dict]:
        """Filtrar noticias relevantes para el símbolo específico"""
        relevant_news = []
        symbol_keywords = self._get_symbol_keywords(symbol)
        
        for news in news_list:
            relevance_score = self._calculate_relevance_score(news, symbol_keywords)
            
            if relevance_score > 0.3:  # Umbral mínimo de relevancia
                news['relevance_score'] = relevance_score
                news['impact_level'] = self._determine_impact_level(news)
                news['symbol'] = symbol
                relevant_news.append(news)

        for news in news_list:
            if self._is_relevant_news(news, symbol_keywords):
                relevant_news.append(news)
        
        return relevant_news[:5] 
        
        # Ordenar por relevancia y tomar las mejores
        relevant_news.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_news[:self.max_news_per_symbol]
    
    def _get_symbol_keywords(self, symbol: str) -> List[str]:
        """Obtener palabras clave relacionadas con el símbolo"""
        symbol_upper = symbol.upper()
        keywords = [symbol_upper]
        
        if 'XAU' in symbol_upper or 'GOLD' in symbol_upper:
            keywords.extend(['gold', 'oro', 'precious metal', 'fed', 'inflation', 'safe haven', 'bullion'])
        elif 'USD' in symbol_upper:
            keywords.extend(['dollar', 'usd', 'fed', 'interest rates', 'inflation', 'employment', 'federal reserve'])
        elif 'BTC' in symbol_upper:
            keywords.extend(['bitcoin', 'crypto', 'blockchain', 'regulation', 'halving', 'digital gold'])
        elif 'JPY' in symbol_upper:
            keywords.extend(['yen', 'jpy', 'bank of japan', 'boj', 'intervention'])
        elif 'GBP' in symbol_upper:
            keywords.extend(['pound', 'gbp', 'bank of england', 'boe', 'brexit'])
        
        return keywords
    
    def _calculate_relevance_score(self, news: Dict, keywords: List[str]) -> float:
        """Calcular score de relevancia para la noticia"""
        title = news.get('title', '').lower()
        summary = news.get('summary', '').lower()
        
        score = 0.0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in title:
                score += 0.5
            if keyword_lower in summary:
                score += 0.3
        
        # Bonus por alta relevancia temporal (noticias muy recientes)
        if news.get('time'):
            # Asumir que 'time' está en formato HH:MM o timestamp
            score += 0.2
        
        return min(score, 1.0)  # Normalizar a 0-1
    
    def _determine_impact_level(self, news: Dict) -> str:
        """Determinar nivel de impacto de la noticia"""
        title = news.get('title', '').lower()
        
        # Palabras clave de alto impacto
        high_impact_keywords = [
            'fed', 'interest rate', 'inflation', 'employment', 'gdp', 
            'crisis', 'war', 'election', 'breakthrough', 'surge', 'crash',
            'emergency', 'ban', 'regulation'
        ]
        
        medium_impact_keywords = [
            'data', 'report', 'earnings', 'meeting', 'speech',
            'growth', 'decline', 'rally', 'drop'
        ]
        
        if any(keyword in title for keyword in high_impact_keywords):
            return "high"
        elif any(keyword in title for keyword in medium_impact_keywords):
            return "medium"
        else:
            return "low"
    
    async def _save_news_to_db(self, symbol: str, news_list: List[Dict]) -> List[MarketNews]:
        """Guardar noticias procesadas en la base de datos"""
        db = next(get_db())
        try:
            saved_news = []
            
            for news_data in news_list:
                # Verificar si ya existe (basado en título y fecha)
                existing = db.query(MarketNews).filter(
                    MarketNews.title == news_data['title'],
                    MarketNews.symbol == symbol
                ).first()
                
                if not existing:
                    news_obj = MarketNews(
                        symbol=symbol,
                        title=news_data['title'],
                        summary=news_data.get('summary', ''),
                        source=news_data.get('source', ''),
                        url=news_data.get('url', '#'),
                        image_url=news_data.get('image_url', ''),
                        published_at=datetime.now(),  # Usar fecha real si está disponible
                        category=news_data.get('category', 'general'),
                        impact_level=news_data.get('impact_level', 'low'),
                        sentiment=news_data.get('sentiment', 'neutral'),
                        relevance_score=news_data.get('relevance_score', 0.0),
                        is_high_impact=news_data.get('impact_level') == 'high'
                    )
                    
                    db.add(news_obj)
                    db.commit()
                    db.refresh(news_obj)
                    saved_news.append(news_obj)
                else:
                    saved_news.append(existing)
            
            return saved_news
        finally:
            db.close()
    
    def _format_news_for_ai(self, news_list: List[MarketNews], symbol: str) -> Dict[str, Any]:
        """Formatear noticias para el análisis de IA"""
        if not news_list:
            return {
                "has_news": False,
                "market_context": f"No hay noticias recientes relevantes para {symbol}.",
                "news_count": 0,
                "overall_sentiment": "neutral"
            }
        
        # Agrupar por nivel de impacto
        high_impact = [n for n in news_list if n.impact_level == "high"]
        medium_impact = [n for n in news_list if n.impact_level == "medium"]
        low_impact = [n for n in news_list if n.impact_level == "low"]
        
        # Calcular sentimiento general
        sentiments = [n.sentiment for n in news_list]
        positive_count = sentiments.count("positive")
        negative_count = sentiments.count("negative")
        
        if positive_count > negative_count:
            overall_sentiment = "positive"
        elif negative_count > positive_count:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        # Construir contexto para IA
        context_parts = []
        
        if high_impact:
            context_parts.append("📢 NOTICIAS DE ALTO IMPACTO:")
            for news in high_impact[:2]:  # Máximo 2 de alto impacto
                context_parts.append(f"• {news.title} ({news.sentiment})")
        
        if medium_impact:
            context_parts.append("\n📈 NOTICIAS RELEVANTES:")
            for news in medium_impact[:3]:
                context_parts.append(f"• {news.title}")
        
        context_parts.append(f"\n💡 Contexto general: Sentimiento {overall_sentiment}")
        context_parts.append(f"Total noticias consideradas: {len(news_list)}")
        
        return {
            "has_news": True,
            "market_context": "\n".join(context_parts),
            "news_count": len(news_list),
            "high_impact_count": len(high_impact),
            "overall_sentiment": overall_sentiment,
            "symbol": symbol,
            "last_updated": datetime.now().isoformat()
        }
    
    async def _update_news_usage(self, symbol: str, news_ids: List[int]):
        """Actualizar contador de uso de noticias"""
        db = next(get_db())
        try:
            for news_id in news_ids:
                news = db.query(MarketNews).filter(MarketNews.id == news_id).first()
                if news:
                    news.usage_count += 1
                    news.last_used_in_analysis = datetime.now()
            
            db.commit()
        finally:
            db.close()
    
    async def _record_news_analysis(self, user_id: int, symbol: str, news_used: List[MarketNews]):
        """Registrar análisis de noticias en el historial"""
        db = next(get_db())
        try:
            high_impact_count = sum(1 for n in news_used if n.is_high_impact)
            
            history = NewsAnalysisHistory(
                user_id=user_id,
                symbol=symbol,
                news_used=[n.id for n in news_used],
                total_news_considered=len(news_used),
                high_impact_count=high_impact_count
            )
            
            db.add(history)
            db.commit()
        finally:
            db.close()
    
    def _calculate_overall_sentiment(self, news_list: List[Dict]) -> str:
        """Calcular sentimiento general de las noticias"""
        sentiments = [self._analyze_news_sentiment(news) for news in news_list]
        
        positive_count = sentiments.count("positive")
        negative_count = sentiments.count("negative")
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _get_fallback_news_context(self, symbol: str) -> Dict[str, Any]:
        """Contexto de fallback cuando no hay noticias"""
        return {
            "has_news": False,
            "market_context": f"Contexto de mercado general para {symbol}. No hay noticias recientes específicas disponibles.",
            "news_count": 0,
            "overall_sentiment": "neutral",
            "symbol": symbol
        }

# Instancia global
intelligent_news_service = IntelligentNewsService()