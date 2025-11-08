@echo off
echo ===================================
echo  Deteniendo Trading Bot AI
echo ===================================
echo.

echo Cerrando procesos de Python (Backend)...
taskkill /FI "WindowTitle eq Trading Bot - Backend*" /T /F 2>nul

echo Cerrando procesos de Node (Frontend)...
taskkill /FI "WindowTitle eq Trading Bot - Frontend*" /T /F 2>nul

echo.
echo ===================================
echo  Servicios detenidos
echo ===================================
echo.
pause
