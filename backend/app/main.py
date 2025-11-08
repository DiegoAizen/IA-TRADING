#backend/app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database.db_connection import create_tables
from .api import routes_auth, routes_bot, routes_trades, routes_config, routes_dashboard, routes_mt5, routes_ai, routes_news 
from .core.config import settings
from app.api.routes_bot import router as bot_router


# Crear tablas al iniciar
create_tables()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend para aplicación de escritorio de Trading Bot con IA",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración CORS para app de escritorio
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir todas las rutas
app.include_router(routes_auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(routes_bot.router, prefix="/api/bot", tags=["bot"])
app.include_router(bot_router, prefix="/bot", tags=["bot"])
app.include_router(routes_trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(routes_config.router, prefix="/api/config", tags=["configuration"])
app.include_router(routes_dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(routes_mt5.router, prefix="/api/mt5", tags=["mt5"])
app.include_router(routes_ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(routes_news.router, prefix="/api/news", tags=["news"]) 

@app.get("/")
async def root():
    return {
        "message": settings.PROJECT_NAME,
        "status": "running", 
        "version": settings.APP_VERSION
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "database": "connected",
        "app": settings.PROJECT_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)