from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..database.db_connection import get_db
from ..models.user_model import User
from ..models.mt5_config_model import MT5Config
from ..services.broker_api import broker_api
from ..services.data_fetcher import data_fetcher
from ..core.security import get_current_user

router = APIRouter()

@router.post("/connect")
async def connect_mt5(
    config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Conectar a MT5 con credenciales específicas"""
    try:
        # Validar campos requeridos
        required_fields = ['server', 'login', 'password']
        for field in required_fields:
            if field not in config:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo requerido faltante: {field}"
                )

        # Intentar conexión
        connection_result = broker_api.connect_to_mt5(
            server=config['server'],
            login=config['login'],
            password=config['password'],
            timeout=config.get('timeout', 60000)
        )

        if connection_result['success']:
            # Guardar/actualizar configuración en base de datos
            mt5_config = db.query(MT5Config).filter(MT5Config.user_id == current_user.id).first()
            
            if mt5_config:
                # Actualizar configuración existente
                mt5_config.server = config['server']
                mt5_config.login = config['login']
                mt5_config.password = config['password']  # En producción, encriptar!
                mt5_config.timeout = config.get('timeout', 60000)
                mt5_config.portable = config.get('portable', False)
                mt5_config.is_connected = True
                mt5_config.last_connection = "2024-01-01T00:00:00Z"  # Usar datetime real
            else:
                # Crear nueva configuración
                mt5_config = MT5Config(
                    user_id=current_user.id,
                    server=config['server'],
                    login=config['login'],
                    password=config['password'],  # En producción, encriptar!
                    timeout=config.get('timeout', 60000),
                    portable=config.get('portable', False),
                    is_connected=True,
                    last_connection="2024-01-01T00:00:00Z"
                )
                db.add(mt5_config)
            
            db.commit()

            return {
                "success": True,
                "message": "Conexión exitosa a MT5",
                "account_info": connection_result['account_info'],
                "config_id": mt5_config.id
            }
        else:
            # Guardar error en la configuración
            mt5_config = db.query(MT5Config).filter(MT5Config.user_id == current_user.id).first()
            if mt5_config:
                mt5_config.is_connected = False
                mt5_config.error_message = connection_result.get('error', 'Error desconocido')
                db.commit()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=connection_result.get('error', 'Error de conexión')
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/disconnect")
async def disconnect_mt5(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Desconectar de MT5"""
    try:
        disconnect_result = broker_api.disconnect_mt5()
        
        # Actualizar estado en base de datos
        mt5_config = db.query(MT5Config).filter(MT5Config.user_id == current_user.id).first()
        if mt5_config:
            mt5_config.is_connected = False
            db.commit()

        return disconnect_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error desconectando: {str(e)}"
        )

@router.get("/status")
async def get_mt5_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estado de conexión MT5"""
    try:
        # Obtener configuración de la base de datos
        mt5_config = db.query(MT5Config).filter(MT5Config.user_id == current_user.id).first()
        
        # Obtener estado actual de conexión
        connection_status = broker_api.get_connection_status()
        
        return {
            "config": {
                "server": mt5_config.server if mt5_config else None,
                "login": mt5_config.login if mt5_config else None,
                "is_connected": mt5_config.is_connected if mt5_config else False,
                "last_connection": mt5_config.last_connection if mt5_config else None
            } if mt5_config else None,
            "connection": connection_status
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estado: {str(e)}"
        )

@router.get("/account-info")
async def get_account_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener información detallada de la cuenta MT5"""
    try:
        if not broker_api.connected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay conexión activa con MT5"
            )

        portfolio_status = broker_api.get_portfolio_status()
        
        return portfolio_status

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo información de cuenta: {str(e)}"
        )

@router.get("/symbols")
async def get_available_symbols(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener símbolos disponibles en MT5"""
    try:
        if not broker_api.connected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay conexión activa con MT5"
            )

        symbols = data_fetcher.get_symbols()
        
        # Filtrar símbolos populares para demo
        popular_symbols = [s for s in symbols if any(x in s for x in ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD'])]
        
        return {
            "success": True,
            "symbols": popular_symbols[:20],  # Limitar para demo
            "total_count": len(symbols)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo símbolos: {str(e)}"
        )

@router.get("/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener datos de mercado para un símbolo específico"""
    try:
        if not broker_api.connected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay conexión activa con MT5"
            )

        # Obtener precio actual
        current_price = data_fetcher.get_current_price(symbol)
        if not current_price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Símbolo no encontrado: {symbol}"
            )

        # Obtener datos históricos (últimas 100 velas)
        historical_data = data_fetcher.get_market_data(symbol, count=100)
        
        return {
            "success": True,
            "symbol": symbol,
            "current_price": current_price,
            "historical_data": historical_data.to_dict('records') if historical_data is not None else []
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo datos de mercado: {str(e)}"
        )

@router.post("/test-order")
async def test_order(
    order_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ejecutar una orden de prueba (solo para demo)"""
    try:
        if not broker_api.connected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay conexión activa con MT5"
            )

        # Validar datos de la orden
        required_fields = ['symbol', 'operation', 'volume']
        for field in required_fields:
            if field not in order_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo requerido faltante: {field}"
                )

        # Ejecutar orden de prueba
        result = broker_api.execute_trade(
            symbol=order_data['symbol'],
            signal=order_data['operation'],
            volume=order_data['volume'],
            risk_percent=order_data.get('risk_percent', 2.0),
            stop_loss_pips=order_data.get('stop_loss_pips', 50.0)
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ejecutando orden de prueba: {str(e)}"
        )