from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ..database.db_connection import get_db
from ..models.user_model import User
from ..models.ai_config_model import UserAIConfig, AIAnalysisHistory
from ..core.security import get_current_user
from ..core.ai_config import AIProvider, ai_config
from ..ai.model_manager import model_manager
from ..services.analysis_service import analysis_service
from ..core.logger import logger

router = APIRouter()

@router.get("/config")
async def get_ai_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener configuración de IA del usuario"""
    ai_config = db.query(UserAIConfig).filter(UserAIConfig.user_id == current_user.id).first()
    
    if not ai_config:
        # Crear configuración por defecto
        ai_config = UserAIConfig(
            user_id=current_user.id,
            ai_provider="deepseek",
            ai_model="deepseek-chat",
            max_tokens=4000,
            temperature=0.7
        )
        db.add(ai_config)
        db.commit()
        db.refresh(ai_config)
    
    # No devolver la API key por seguridad
    response = {
        "id": ai_config.id,
        "ai_provider": ai_config.ai_provider,
        "ai_model": ai_config.ai_model,
        "is_active": ai_config.is_active,
        "max_tokens": ai_config.max_tokens,
        "temperature": ai_config.temperature,
        "confidence_threshold": ai_config.confidence_threshold,
        "last_used": ai_config.last_used,
        "total_requests": ai_config.total_requests
    }
    
    return response

@router.put("/config")
async def update_ai_config(
    config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar configuración de IA del usuario"""
    ai_config = db.query(UserAIConfig).filter(UserAIConfig.user_id == current_user.id).first()
    
    if not ai_config:
        ai_config = UserAIConfig(user_id=current_user.id)
        db.add(ai_config)
    
    # Validar proveedor
    if 'ai_provider' in config:
        try:
            AIProvider(config['ai_provider'])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Proveedor no válido: {config['ai_provider']}"
            )
        ai_config.ai_provider = config['ai_provider']
    
    # Validar y actualizar API key si se proporciona
    if 'api_key' in config and config['api_key']:
        # Validar que la API key funciona
        is_valid = model_manager.validate_api_key(
            AIProvider(ai_config.ai_provider), 
            config['api_key']
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key inválida para el proveedor seleccionado"
            )
        
        ai_config.api_key = config['api_key']
    
    # Actualizar otros campos
    update_fields = [
        'ai_model', 'is_active', 'max_tokens', 'temperature', 
        'confidence_threshold'
    ]
    
    for field in update_fields:
        if field in config:
            setattr(ai_config, field, config[field])
    
    db.commit()
    db.refresh(ai_config)
    
    # No devolver la API key por seguridad
    response = {
        "id": ai_config.id,
        "ai_provider": ai_config.ai_provider,
        "ai_model": ai_config.ai_model,
        "is_active": ai_config.is_active,
        "max_tokens": ai_config.max_tokens,
        "temperature": ai_config.temperature,
        "confidence_threshold": ai_config.confidence_threshold,
        "message": "Configuración de IA actualizada correctamente"
    }
    
    return response

@router.get("/providers")
async def get_ai_providers():
    """Obtener lista de proveedores de IA disponibles"""
    providers = []
    
    for provider in AIProvider:
        providers.append({
            "id": provider.value,
            "name": provider.value.upper(),
            "models": ai_config.AVAILABLE_MODELS[provider],
            "api_url": getattr(ai_config, f"{provider.value.upper()}_API_URL")
        })
    
    return {
        "providers": providers,
        "default_provider": ai_config.DEFAULT_PROVIDER.value
    }

@router.post("/analyze/{symbol}")
async def analyze_symbol(
    symbol: str,
    analysis_type: str = "comprehensive",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analizar un símbolo específico usando IA"""
    try:
        # ✅ LLAMADA CORREGIDA - SIN el parámetro 'db'
        result = await analysis_service.analyze_symbol(
            symbol=symbol.upper(),
            user_id=current_user.id,
            analysis_type=analysis_type
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Error en análisis")
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en análisis: {str(e)}"
        )

@router.post("/analyze-multiple")
async def analyze_multiple_symbols(
    symbols: List[str],
    analysis_type: str = "technical",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analizar múltiples símbolos"""
    try:
        if len(symbols) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Máximo 10 símbolos por análisis"
            )
        
        result = await analysis_service.analyze_multiple_symbols(
            symbols=[s.upper() for s in symbols],
            user_id=current_user.id,
            analysis_type=analysis_type
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Error en análisis múltiple")
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en análisis múltiple: {str(e)}"
        )

@router.get("/analysis-history")
async def get_analysis_history(
    limit: int = Query(20, ge=1, le=100),
    symbol: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener historial de análisis de IA"""
    try:
        query = db.query(AIAnalysisHistory).filter(
            AIAnalysisHistory.user_id == current_user.id
        )
        
        if symbol:
            query = query.filter(AIAnalysisHistory.symbol == symbol)
        
        history = query.order_by(AIAnalysisHistory.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": item.id,
                "symbol": item.symbol,
                "analysis_type": item.analysis_type,
                "signal": item.signal,
                "confidence": float(item.confidence) if item.confidence else 0.0,
                "reasoning": item.reasoning,
                "ai_provider": item.ai_provider,
                "ai_model": item.ai_model,
                "processing_time": float(item.processing_time) if item.processing_time else 0.0,
                "tokens_used": item.tokens_used,
                "created_at": item.created_at.isoformat() if item.created_at else None
            }
            for item in history
        ]
        
    except Exception as e:
        logger.error(f"Error obteniendo historial de análisis: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# ✅ AGREGA ESTE MÉTODO FALTANTE (si lo necesitas)
@router.post("/test-api-key")
async def test_api_key(
    test_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Probar una API key de IA"""
    try:
        provider = test_data.get("provider")
        api_key = test_data.get("api_key")
        
        if not provider or not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider y API key son requeridos"
            )
        
        is_valid = model_manager.validate_api_key(
            AIProvider(provider), 
            api_key
        )
        
        return {
            "success": is_valid,
            "message": "API key válida" if is_valid else "API key inválida"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error probando API key: {str(e)}"
        )