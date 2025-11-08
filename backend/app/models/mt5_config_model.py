from sqlalchemy import Column, Integer, String, Boolean, Text
from ..database.db_connection import Base

class MT5Config(Base):
    __tablename__ = "mt5_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Configuración de conexión
    server = Column(String, nullable=False)
    login = Column(Integer, nullable=False)
    password = Column(String, nullable=False)
    timeout = Column(Integer, default=60000)
    portable = Column(Boolean, default=False)
    
    # Configuración de trading
    leverage = Column(Integer, default=100)
    currency = Column(String, default="USD")
    balance = Column(Integer, default=0)
    equity = Column(Integer, default=0)
    margin = Column(Integer, default=0)
    
    # Estado de conexión
    is_connected = Column(Boolean, default=False)
    last_connection = Column(String)
    error_message = Column(Text)
    
    # Configuración adicional
    magic_number = Column(Integer, default=123456)  # Número mágico para las operaciones
    deviation = Column(Integer, default=20)  # Desviación máxima en puntos