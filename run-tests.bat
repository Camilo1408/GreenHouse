@echo off
:: ============================================================
::  GreenHouse Manager — Correr pruebas Python
::  Uso: run-tests.bat
::  Requiere: backend corriendo en localhost:8080
::
::  Los tests limpian automaticamente los datos que crean
::  (cleanup_registry en conftest.py).
:: ============================================================

setlocal enabledelayedexpansion

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
echo   Elige que pruebas correr:
echo     [1] Pruebas de API  (zonas, plantas, alertas, sensores)
echo     [2] Integracion con Taiga  (historias de usuario)
echo     [3] Todas las pruebas Python
echo     [4] Subir historias a Taiga  (taiga-upload.py)
echo     [5] Limpiar datos de prueba anteriores  (cleanup_test_data.py)
echo.
set /p CHOICE=  Tu eleccion (1-5):

cd /d "%TESTS%"

if "%CHOICE%"=="1" (
    echo.
    echo   Corriendo pruebas de API...
    echo   Los datos creados se eliminan automaticamente al finalizar.
    echo.
    python -m pytest test_zonas.py test_plantas.py test_alertas.py test_sensores.py ^
        -v -s --html=report-api.html --self-contained-html
    echo.
    echo   Reporte guardado en: tests-python\report-api.html
)

if "%CHOICE%"=="2" (
    echo.
    echo   Corriendo pruebas de Taiga...
    echo   Los datos creados se eliminan automaticamente al finalizar.
    echo.
    python -m pytest test_taiga_integration.py ^
        -v -s --html=report-taiga.html --self-contained-html
    echo.
    echo   Reporte guardado en: tests-python\report-taiga.html
)

if "%CHOICE%"=="3" (
    echo.
    echo   Corriendo todas las pruebas Python...
    echo   Los datos creados se eliminan automaticamente al finalizar.
    echo.
    python -m pytest test_zonas.py test_plantas.py test_alertas.py ^
        test_sensores.py test_taiga_integration.py ^
        -v -s --html=report-full.html --self-contained-html
    echo.
    echo   Reporte guardado en: tests-python\report-full.html
)

if "%CHOICE%"=="4" (
    echo.
    echo   Subiendo historias de usuario a Taiga...
    cd /d "%ROOT%"
    python taiga-upload.py
)

if "%CHOICE%"=="5" (
    echo.
    echo   Opciones de limpieza:
    echo     [a] Limpiar datos de prueba ahora
    echo     [b] Solo mostrar que se borraria ^(dry-run^)
    echo.
    set /p CLEAN_CHOICE=  Tu eleccion (a/b):
    echo.
    if /i "!CLEAN_CHOICE!"=="a" (
        python cleanup_test_data.py
    ) else (
        python cleanup_test_data.py --dry-run
    )
)

echo.
pause
