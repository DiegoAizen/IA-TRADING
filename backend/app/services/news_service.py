# backend/app/services/news_service.py - CORREGIDO
import requests
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..core.logger import logger
from ..core.config import settings

class NewsService:
    def __init__(self):
        self.api_key = settings.FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"
    
    async def get_market_news(self, category: str = "general") -> List[Dict[str, Any]]:
        """Obtener noticias del mercado desde Finnhub - CORREGIDO"""
        try:
            logger.info(f"📰 Obteniendo noticias de categoría: {category}")
            
            url = f"{self.base_url}/news"
            params = {
                "category": category,
                "token": self.api_key 
            }
            
            logger.info(f"🔗 Llamando a Finnhub: {url}?category={category}")
            
            # Hacer la llamada a la API de Finnhub
            response = requests.get(
                url,
                params=params,
                timeout=10
            )
            
            logger.info(f"📊 Respuesta Finnhub - Status: {response.status_code}")
            
            if response.status_code == 200:
                news_data = response.json()
                logger.info(f"📰 Datos crudos recibidos: {len(news_data)} noticias")
                
                # Procesar y limitar las noticias
                processed_news = self._process_news_data(news_data[:15])  # Últimas 15 noticias
                logger.info(f"✅ Obtenidas {len(processed_news)} noticias procesadas")
                return processed_news
            elif response.status_code == 429:
                logger.error("❌ Límite de tasa excedido en Finnhub")
                return self._get_fallback_news("Límite de API excedido")
            else:
                logger.error(f"❌ Error API Finnhub: {response.status_code} - {response.text}")
                return self._get_fallback_news(f"Error API: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout en llamada a Finnhub")
            return self._get_fallback_news("Timeout")
        except Exception as e:
            logger.error(f"❌ Error obteniendo noticias: {str(e)}")
            return self._get_fallback_news(str(e))
    
    async def get_crypto_news(self) -> List[Dict[str, Any]]:
        """Obtener noticias específicas de criptomonedas"""
        return await self.get_market_news("crypto")
    
    async def get_forex_news(self) -> List[Dict[str, Any]]:
        """Obtener noticias específicas de Forex"""
        return await self.get_market_news("forex")
    
    def _process_news_data(self, news_data: List[Dict]) -> List[Dict[str, Any]]:
        """Procesar y formatear los datos de noticias"""
        processed = []
        
        for news in news_data:
            try:
                # Formatear fecha - Finnhub usa timestamp en segundos
                if 'datetime' in news:
                    # Convertir timestamp de segundos a datetime
                    date_obj = datetime.fromtimestamp(news['datetime'])
                    formatted_date = date_obj.strftime("%H:%M")
                elif 'time' in news:
                    # Algunos endpoints usan 'time' en lugar de 'datetime'
                    date_obj = datetime.fromtimestamp(news['time'])
                    formatted_date = date_obj.strftime("%H:%M")
                else:
                    formatted_date = "Reciente"
                
                # Determinar relevancia/sentimiento básico
                sentiment = self._analyze_sentiment(news.get('headline', ''))
                
                processed_news = {
                    "id": news.get('id', hash(news.get('headline', ''))),
                    "title": news.get('headline', 'Sin título'),
                    "summary": news.get('summary', '')[:150] + "..." if news.get('summary') else "No hay resumen disponible",
                    "source": news.get('source', 'Fuente desconocida'),
                    "url": news.get('url', '#'),
                    "image_url": news.get('image', ''),
                    "time": formatted_date,
                    "sentiment": sentiment,  # positive, negative, neutral
                    "category": self._categorize_news(news.get('headline', ''))
                }
                processed.append(processed_news)
            except Exception as e:
                logger.error(f"Error procesando noticia: {str(e)}")
                continue
        
        return processed
    
    def _analyze_sentiment(self, headline: str) -> str:
        """Análisis básico de sentimiento basado en palabras clave"""
        headline_lower = headline.lower()
        
        positive_words = ['bull', 'rally', 'gain', 'up', 'positive', 'strong', 'growth', 'profit', 'surge', 'jump']
        negative_words = ['bear', 'drop', 'fall', 'down', 'negative', 'weak', 'loss', 'crash', 'plunge', 'slide']
        
        positive_count = sum(1 for word in positive_words if word in headline_lower)
        negative_count = sum(1 for word in negative_words if word in headline_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _categorize_news(self, headline: str) -> str:
        """Categorizar noticia basado en palabras clave"""
        headline_lower = headline.lower()
        
        categories = {
            "forex": ["usd", "eur", "jpy", "gbp", "forex", "currency", "fed", "ecb", "central bank"],
            "crypto": ["bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "digital asset"],
            "stocks": ["stock", "nasdaq", "s&p", "dow", "earnings", "shares", "equity"],
            "economy": ["inflation", "interest", "gdp", "economy", "employment", "economic"],
            "commodities": ["gold", "oil", "silver", "commodity", "xau", "crude"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in headline_lower for keyword in keywords):
                return category
        
        return "general"
    
    def _get_fallback_news(self, reason: str = "") -> List[Dict[str, Any]]:
        """Noticias de fallback en caso de error"""
        logger.info(f"🔄 Usando noticias de fallback. Razón: {reason}")
        
        return [
            {
                "id": 1,
                "title": "Mercados financieros en sesión normal",
                "summary": "Los principales índices y divisas operan dentro de rangos esperados. El bot continúa monitoreando oportunidades.",
                "source": "Sistema Trading Bot",
                "url": "#",
                "image_url": "",
                "time": datetime.now().strftime("%H:%M"),
                "sentiment": "neutral",
                "category": "general"
            },
            {
                "id": 2,
                "title": "Sistema de Trading Activo",
                "summary": "El bot de trading inteligente está analizando mercados y ejecutando operaciones basadas en IA.",
                "source": "Trading AI",
                "url": "#",
                "image_url": "",
                "time": datetime.now().strftime("%H:%M"),
                "sentiment": "positive",
                "category": "general"
            },
            {
                "id": 3,
                "title": "Análisis de Mercado en Tiempo Real",
                "summary": "La inteligencia artificial está procesando datos de mercado para identificar oportunidades de trading.",
                "source": "AI Analysis",
                "url": "#",
                "image_url": "",
                "time": datetime.now().strftime("%H:%M"),
                "sentiment": "positive", 
                "category": "general"
            }
        ]

# Instancia global
news_service = NewsService()