from sqlalchemy import text
from ..database.db_connection import get_db
from ..core.logger import logger
from datetime import datetime

class HealthService:
    @staticmethod
    def check_database():
        """Verificar estado de la base de datos"""
        try:
            db = next(get_db())
            db.execute(text("SELECT 1"))
            db.close()
            return True
        except Exception as e:
            logger.error(f"❌ Health check BD falló: {str(e)}")
            return False
    
    @staticmethod
    def check_mt5_connection():
        """Verificar conexión MT5"""
        try:
            from .data_fetcher import data_fetcher
            return data_fetcher.connected
        except Exception as e:
            logger.error(f"❌ Health check MT5 falló: {str(e)}")
            return False
    
    @staticmethod
    def get_system_status():
        """Obtener estado completo del sistema"""
        return {
            "database": HealthService.check_database(),
            "metatrader": HealthService.check_mt5_connection(),
            "timestamp": datetime.now().isoformat()
        }