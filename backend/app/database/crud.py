# En database/crud.py
# Qué datos específicos se guardan para cada análisis/reanálisis
# Cómo se estructura el historial para aprendizaje futuro
# Optimización de consultas para datos frecuentes

from sqlalchemy.orm import Session
from ..models.user_model import User, UserConfig
from ..models.config_model import BotConfig
from ..core.security import get_password_hash, verify_password
from ..core.config import settings

def create_default_user(db: Session):
    """Crea usuario demo - versión debug"""
    existing_user = db.query(User).filter(User.email == settings.DEFAULT_USER_EMAIL).first()
    
    if not existing_user:
        print("🔧 CREANDO NUEVO USUARIO DEMO...")
        
        # Generar hash
        plain_password = settings.DEFAULT_USER_PASSWORD
        hashed = get_password_hash(plain_password)
        
        print(f"📧 Email: {settings.DEFAULT_USER_EMAIL}")
        print(f"🔑 Password: {plain_password}")
        print(f"🔐 Hash generado: {hashed}")
        
        # Verificar inmediatamente
        test_verify = verify_password(plain_password, hashed)
        print(f"✅ Verificación inmediata: {test_verify}")
        
        default_user = User(
            email=settings.DEFAULT_USER_EMAIL,
            username=settings.DEFAULT_USERNAME,
            hashed_password=hashed,
            full_name="Demo Trader",
            risk_level="moderate",
            confidence_threshold=75.0,
            default_lot_size=0.1,
            theme="dark"
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
        
        # Configuraciones
        default_config = UserConfig(
            user_id=default_user.id,
            selected_assets="EURUSD,GBPUSD,USDJPY,XAUUSD,BTCUSD,ETHUSD",
            auto_trading=False,
            notifications_enabled=True
        )
        db.add(default_config)
        
        bot_config = BotConfig(
            user_id=default_user.id,
            bot_name="Bot Principal",
            is_active=False,
            auto_trading=False,  # ⬅️ NUEVO CAMPO
            max_drawdown=10.0,
            daily_loss_limit=5.0,
            max_open_trades=3,
            trading_strategy="moderate"
        )

        db.add(bot_config)
        db.commit()
        
        print("🎉 USUARIO DEMO CREADO EXITOSAMENTE")
        
    else:
        print("📊 USUARIO EXISTENTE ENCONTRADO:")
        print(f"   Email: {existing_user.email}")
        print(f"   Hash: {existing_user.hashed_password}")
        
        # Probar contraseña con el usuario existente
        test_result = verify_password(settings.DEFAULT_USER_PASSWORD, existing_user.hashed_password)
        print(f"   🔑 Test login: {'✅ ÉXITO' if test_result else '❌ FALLO'}")
    
    return existing_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()