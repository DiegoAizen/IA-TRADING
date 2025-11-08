@echo off
echo ===================================
echo  Iniciando Trading Bot AI
echo ===================================
echo.

REM Iniciar backend en una nueva ventana
echo [1/2] Iniciando Backend...
start "Trading Bot - Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --port 8000"

REM Esperar 3 segundos para que el backend inicie
timeout /t 3 /nobreak >nul

REM Iniciar frontend en una nueva ventana
echo [2/2] Iniciando Frontend...
start "Trading Bot - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ===================================
echo  Servicios iniciados correctamente
echo ===================================
echo  Backend: http://localhost:8000
echo  Frontend: http://localhost:5173
echo ===================================
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
