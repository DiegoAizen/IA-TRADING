# backend/app/api/__init__.py
from . import routes_auth
from . import routes_bot
from . import routes_trades
from . import routes_config
from . import routes_dashboard
from . import routes_mt5
from . import routes_ai
from . import routes_news  # ✅ AÑADIR routes_news

__all__ = [
    "routes_auth",
    "routes_bot", 
    "routes_trades",
    "routes_config",
    "routes_dashboard", 
    "routes_mt5",
    "routes_ai",
    "routes_news"  # ✅ AÑADIR
]