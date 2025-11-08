from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database.db_connection import get_db
from ..database.crud import create_default_user, get_user_by_username, get_user_by_email
from ..models.user_model import User
from ..core.security import verify_password, create_access_token
from ..core.config import settings

router = APIRouter()

@router.post("/login")
def login_for_desktop_app(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Login optimizado para aplicación de escritorio
    """
    # Crear usuario demo automáticamente si no existe
    create_default_user(db)
    
    # Buscar usuario por email o username
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Token de larga duración para app de escritorio (24 horas)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # segundos
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "risk_level": user.risk_level,
            "theme": user.theme,
            "is_active": user.is_active
        }
    }

@router.post("/register")
def register():
    """Para app de escritorio, solo permitimos usuario demo"""
    return {
        "message": "Para esta versión de escritorio, usa el usuario demo",
        "demo_credentials": {
            "email": settings.DEFAULT_USER_EMAIL,
            "password": settings.DEFAULT_USER_PASSWORD,
            "username": settings.DEFAULT_USERNAME
        }
    }

@router.get("/demo-info")
def get_demo_info():
    """Endpoint para obtener información del usuario demo"""
    return {
        "demo_user": {
            "email": settings.DEFAULT_USER_EMAIL,
            "password": settings.DEFAULT_USER_PASSWORD,
            "username": settings.DEFAULT_USERNAME
        },
        "app_info": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION
        }
    }