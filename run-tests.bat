@echo off
:: ============================================================
::  GreenHouse Manager — Correr pruebas Python
::  Uso: run-tests.bat
::  Requiere: backend corriendo en localhost:8080
:: ============================================================

setlocal

set ROOT=%~dp0
set TESTS=%ROOT%tests-python

echo.
echo   GreenHouse Manager - Suite de Pruebas
echo   ========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python no encontrado. Instala Python 3.10+ desde https://python.org
    pause
    exit /b 1
)

:: Instalar dependencias si faltan
echo   Verificando dependencias...
python -m pip install -q -r "%TESTS%\requirements.txt"

echo.
echo   Iniciando pruebas...
echo   -------------------------------------------
echo.

cd /d "%TESTS%"

:: Seleccionar suite
echo   Elige que pruebas correr:
echo     [1] Pruebas de API (zonas, plantas, alertas, sensores)
echo     [2] Integracion con Taiga (historias de usuario)
echo     [3] Todas las pruebas Python
echo     [4] Subir historias a Taiga (taiga-upload.py)
echo.
set /p CHOICE=  Tu eleccion (1-4):

if "%CHOICE%"=="1" (
    echo.
    echo   Corriendo pruebas de API...
    python -m pytest test_zonas.py test_plantas.py test_alertas.py test_sensores.py -v --html=report-api.html --self-contained-html
    echo.
    echo   Reporte guardado en: tests-python\report-api.html
)

if "%CHOICE%"=="2" (
    echo.
    echo   Corriendo pruebas de Taiga...
    python -m pytest test_taiga_integration.py -v --html=report-taiga.html --self-contained-html
    echo.
    echo   Reporte guardado en: tests-python\report-taiga.html
)

if "%CHOICE%"=="3" (
    echo.
    echo   Corriendo todas las pruebas Python...
    python -m pytest test_zonas.py test_plantas.py test_alertas.py test_sensores.py test_taiga_integration.py -v --html=report-full.html --self-contained-html
    echo.
    echo   Reporte guardado en: tests-python\report-full.html
)

if "%CHOICE%"=="4" (
    echo.
    echo   Subiendo historias de usuario a Taiga...
    cd /d "%ROOT%"
    python taiga-upload.py
)

echo.
pause
