# database/db_connection.py - VERSIÓN CORREGIDA
import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..core.config import settings
from ..core.logger import logger

# Configuración SIMPLIFICADA y FUNCIONAL para SQLiteç

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    },
    echo=False  # Cambiar a True solo para debug
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    """
    Generator ORIGINAL que SÍ funciona - NO CAMBIAR
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # ESTO ES SUFICIENTE para SQLite

def create_tables():
    """Crear todas las tablas en la base de datos"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas de la base de datos creadas exitosamente")
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {str(e)}")
        raise

# Optimizaciones SQLite (OPCIONAL, puedes comentar temporalmente)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA cache_size=-10000")
        cursor.close()
    except Exception as e:
        logger.warning(f"⚠️ No se pudo optimizar SQLite: {str(e)}")