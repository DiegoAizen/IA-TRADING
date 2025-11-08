# backend/app/models/__init__.py - ACTUALIZAR
from .user_model import User, UserConfig
from .trade_model import Trade
from .config_model import BotConfig
from .ai_config_model import UserAIConfig, AIAnalysisHistory
from .news_model import MarketNews, NewsAnalysisHistory  # ✅ AÑADIR

__all__ = [
    "User",
    "UserConfig", 
    "Trade",
    "BotConfig",
    "UserAIConfig",
    "AIAnalysisHistory",
    "MarketNews",           # ✅ AÑADIR
    "NewsAnalysisHistory"   # ✅ AÑADIR
]