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
set SUITE_LABEL=
set REPORT_FILE=
set EXIT_CODE=0

echo.
echo   ==============================================
echo    GreenHouse Manager - Suite de Pruebas
echo   ==============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python no encontrado. Instala Python 3.10+ desde https://python.org
    echo.
    set /p _=  Presiona Enter para cerrar...
    exit /b 1
)

:: Instalar dependencias si faltan
echo   Verificando dependencias...
python -m pip install -q -r "%TESTS%\requirements.txt"

echo.
echo   Elige que pruebas correr:
echo     [1] Pruebas de API        (zonas, plantas, alertas, sensores)
echo     [2] Integracion con Taiga (historias de usuario)
echo     [3] Todas las pruebas Python
echo     [4] Subir historias a Taiga  (taiga-upload.py)
echo     [5] Limpiar datos de prueba anteriores
echo.
set /p CHOICE=  Tu eleccion (1-5):

cd /d "%TESTS%"

:: ── Opcion 1 ──────────────────────────────────────────────────────────────
if "%CHOICE%"=="1" (
    set SUITE_LABEL=Pruebas de API
    set REPORT_FILE=report-api.html
    echo.
    echo   Corriendo pruebas de API...
    echo   Los datos creados se eliminan automaticamente al finalizar.
    echo.
    python -m pytest test_zonas.py test_plantas.py test_alertas.py test_sensores.py ^
        -v -s --html=report-api.html --self-contained-html
    set EXIT_CODE=!errorlevel!
)

:: ── Opcion 2 ──────────────────────────────────────────────────────────────
if "%CHOICE%"=="2" (
    set SUITE_LABEL=Integracion con Taiga
    set REPORT_FILE=report-taiga.html
    echo.
    echo   Corriendo pruebas de Taiga...
    echo   Los datos creados se eliminan automaticamente al finalizar.
    echo.
    python -m pytest test_taiga_integration.py ^
        -v -s --html=report-taiga.html --self-contained-html
    set EXIT_CODE=!errorlevel!
)

:: ── Opcion 3 ──────────────────────────────────────────────────────────────
if "%CHOICE%"=="3" (
    set SUITE_LABEL=Suite completa
    set REPORT_FILE=report-full.html
    echo.
    echo   Corriendo todas las pruebas Python...
    echo   Los datos creados se eliminan automaticamente al finalizar.
    echo.
    python -m pytest test_zonas.py test_plantas.py test_alertas.py ^
        test_sensores.py test_taiga_integration.py ^
        -v -s --html=report-full.html --self-contained-html
    set EXIT_CODE=!errorlevel!
)

:: ── Opcion 4 ──────────────────────────────────────────────────────────────
if "%CHOICE%"=="4" (
    set SUITE_LABEL=Upload a Taiga
    echo.
    echo   Subiendo historias de usuario a Taiga...
    cd /d "%ROOT%"
    python taiga-upload.py
    set EXIT_CODE=!errorlevel!
)

:: ── Opcion 5 ──────────────────────────────────────────────────────────────
if "%CHOICE%"=="5" (
    set SUITE_LABEL=Limpieza de datos de prueba
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
    set EXIT_CODE=!errorlevel!
)

:: ── Resumen final ──────────────────────────────────────────────────────────
echo.
echo   ==============================================
echo    RESUMEN DE EJECUCION
echo   ==============================================
echo.
echo   Suite ejecutada : !SUITE_LABEL!
echo   Fecha y hora    : %date% %time:~0,8%

if not "%REPORT_FILE%"=="" (
    echo   Reporte HTML    : %TESTS%\!REPORT_FILE!
)

echo.

if "!EXIT_CODE!"=="0" (
    echo   RESULTADO: TODAS LAS PRUEBAS PASARON  [OK]
) else (
    echo   RESULTADO: ALGUNAS PRUEBAS FALLARON   [EXIT CODE: !EXIT_CODE!]
    echo.
    echo   Revisa el reporte HTML o la salida de consola para ver los detalles.
)

echo.
echo   Los datos de prueba creados fueron eliminados automaticamente.
echo   ==============================================
echo.
set /p _=  Presiona Enter para cerrar...
