@echo off
:: ============================================================
::  GreenHouse Manager - Correr pruebas Python
::  Uso: run-tests.bat
::  Requiere: backend corriendo en localhost:8080
::
::  Los tests limpian automaticamente los datos que crean
::  (cleanup_registry en conftest.py).
:: ============================================================

setlocal

set ROOT=%~dp0
set TESTS=%ROOT%tests-python

:: ── Verificar Python ──────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo   ERROR: Python no encontrado. Instala Python 3.10+ desde https://python.org
    echo.
    set /p _=  Presiona Enter para cerrar...
    exit /b 1
)

:MENU
echo.
echo   ==============================================
echo    GreenHouse Manager - Suite de Pruebas
echo   ==============================================
echo.
echo   Verificando dependencias...
python -m pip install -q -r "%TESTS%\requirements.txt"
echo.
echo   Elige que pruebas correr:
echo     [1] Pruebas de API        (zonas, plantas, alertas, sensores)
echo     [2] Integracion con Taiga (historias de usuario)
echo     [3] Todas las pruebas Python
echo     [4] Subir historias a Taiga  (taiga-upload.py)
echo     [5] Limpiar datos de prueba anteriores
echo     [0] Salir
echo.
set /p CHOICE=  Tu eleccion (0-5):

if "%CHOICE%"=="0" goto :FIN
if "%CHOICE%"=="1" goto :OPT1
if "%CHOICE%"=="2" goto :OPT2
if "%CHOICE%"=="3" goto :OPT3
if "%CHOICE%"=="4" goto :OPT4
if "%CHOICE%"=="5" goto :OPT5

echo.
echo   Opcion invalida. Intenta de nuevo.
timeout /t 2 /nobreak >nul
goto :MENU

:: ── Opcion 1 ──────────────────────────────────────────────
:OPT1
cd /d "%TESTS%"
echo.
echo   Corriendo pruebas de API...
echo   Los datos creados se eliminan automaticamente al finalizar.
echo.
python -m pytest test_zonas.py test_plantas.py test_alertas.py test_sensores.py ^
    -v -s --html=report-api.html --self-contained-html
set EXITCODE=%errorlevel%
call :RESUMEN "Pruebas de API" "%TESTS%\report-api.html"
goto :CONTINUAR

:: ── Opcion 2 ──────────────────────────────────────────────
:OPT2
cd /d "%TESTS%"
echo.
echo   Corriendo pruebas de Taiga...
echo   Los datos creados se eliminan automaticamente al finalizar.
echo.
python -m pytest test_taiga_integration.py ^
    -v -s --html=report-taiga.html --self-contained-html
set EXITCODE=%errorlevel%
call :RESUMEN "Integracion con Taiga" "%TESTS%\report-taiga.html"
goto :CONTINUAR

:: ── Opcion 3 ──────────────────────────────────────────────
:OPT3
cd /d "%TESTS%"
echo.
echo   Corriendo todas las pruebas Python...
echo   Los datos creados se eliminan automaticamente al finalizar.
echo.
python -m pytest test_zonas.py test_plantas.py test_alertas.py ^
    test_sensores.py test_taiga_integration.py ^
    -v -s --html=report-full.html --self-contained-html
set EXITCODE=%errorlevel%
call :RESUMEN "Suite completa" "%TESTS%\report-full.html"
goto :CONTINUAR

:: ── Opcion 4 ──────────────────────────────────────────────
:OPT4
cd /d "%ROOT%"
echo.
echo   Subiendo historias de usuario a Taiga...
echo.
python taiga-upload.py
set EXITCODE=%errorlevel%
call :RESUMEN "Upload a Taiga" ""
goto :CONTINUAR

:: ── Opcion 5 ──────────────────────────────────────────────
:OPT5
cd /d "%TESTS%"
echo.
echo   Opciones de limpieza:
echo     [a] Limpiar datos de prueba ahora
echo     [b] Solo mostrar que se borraria (dry-run)
echo.
set /p CLEAN_CHOICE=  Tu eleccion (a/b):
echo.
if /i "%CLEAN_CHOICE%"=="a" (
    python cleanup_test_data.py
) else (
    python cleanup_test_data.py --dry-run
)
set EXITCODE=%errorlevel%
call :RESUMEN "Limpieza de datos de prueba" ""
goto :CONTINUAR

:: ── Resumen y continuacion ────────────────────────────────
:CONTINUAR
echo.
set /p OTRA=  Deseas ejecutar otra prueba? [S]i / [Enter] para cerrar:
if /i "%OTRA%"=="S" (
    cd /d "%ROOT%"
    goto :MENU
)
goto :FIN

:: ── Subrutina: imprime el resumen ─────────────────────────
:RESUMEN
echo.
echo   ==============================================
echo    RESUMEN DE EJECUCION
echo   ==============================================
echo.
echo   Suite ejecutada : %~1
echo   Fecha y hora    : %DATE% %TIME:~0,8%
if not "%~2"=="" (
    echo   Reporte HTML    : %~2
)
echo.
if "%EXITCODE%"=="0" (
    echo   RESULTADO: TODAS LAS PRUEBAS PASARON  [OK]
) else (
    echo   RESULTADO: ALGUNAS PRUEBAS FALLARON   [EXIT CODE: %EXITCODE%]
    echo.
    echo   Revisa el reporte HTML o la salida de consola para ver los detalles.
)
echo.
echo   Los datos de prueba creados fueron eliminados automaticamente.
echo   ==============================================
exit /b 0

:: ── Cierre ────────────────────────────────────────────────
:FIN
echo.
set /p _=  Presiona Enter para cerrar...
