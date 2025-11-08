# backend/app/api/routes_news.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import requests
from ..services.news_service import news_service
from ..core.security import get_current_user
from ..core.config import settings
from ..models.user_model import User

router = APIRouter()

@router.get("/test-connection")
async def test_finnhub_connection(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Probar conexión con Finnhub API"""
    try:
        # Hacer una llamada simple a Finnhub para probar
        url = "https://finnhub.io/api/v1/quote"
        params = {
            "symbol": "AAPL",
            "token": settings.FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        return {
            "status": "success" if response.status_code == 200 else "error",
            "status_code": response.status_code,
            "finnhub_response": response.json() if response.status_code == 200 else response.text,
            "api_key_length": len(settings.FINNHUB_API_KEY) if settings.FINNHUB_API_KEY else 0,
            "api_key_prefix": settings.FINNHUB_API_KEY[:10] + "..." if settings.FINNHUB_API_KEY else "No API Key"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error probando conexión: {str(e)}")

@router.get("/market-news")
async def get_market_news(
    category: str = "general",
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Obtener noticias del mercado"""
    try:
        if category not in ["general", "forex", "crypto", "stocks"]:
            category = "general"
        
        news = await news_service.get_market_news(category)
        return news
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo noticias: {str(e)}")

@router.get("/crypto-news")
async def get_crypto_news(
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Obtener noticias de criptomonedas"""
    try:
        news = await news_service.get_crypto_news()
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo noticias crypto: {str(e)}")

@router.get("/forex-news") 
async def get_forex_news(
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Obtener noticias de Forex"""
    try:
        news = await news_service.get_forex_news()
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo noticias forex: {str(e)}")