@echo off
:: ============================================================
::  GreenHouse Manager - Correr pruebas Python y Selenium
::  Uso: run-tests.bat
::  Requiere: backend en localhost:8080 / frontend en localhost:5173
:: ============================================================

:: Forzar UTF-8 para que la salida de Python no cause errores de encoding
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

setlocal

set ROOT=%~dp0
set TESTS=%~dp0tests-python
set SELENIUM=%~dp0tests-selenium

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo   ERROR: Python no encontrado. Instala Python 3.10+
    echo.
    set /p _=  Presiona Enter para cerrar...
    exit /b 1
)

:MENU
cls
echo.
echo   ==============================================
echo    GreenHouse Manager - Suite de Pruebas
echo   ==============================================
echo.
echo   --- Pruebas de API (backend en localhost:8080) ---
echo     [1] Pruebas de API        (zonas, plantas, alertas, sensores)
echo     [2] Integracion con Taiga (historias de usuario)
echo     [3] Todas las pruebas de API
echo.
echo   --- Pruebas de UI (frontend en localhost:5173) ---
echo     [4] Pruebas Selenium      (interfaz de usuario con Chrome)
echo.
echo   --- Utilidades ---
echo     [5] Subir historias a Taiga  (taiga-upload.py)
echo     [6] Limpiar datos de prueba anteriores
echo     [0] Salir
echo.
set CHOICE=
set /p CHOICE=  Tu eleccion (0-6):

if "%CHOICE%"=="0" goto FIN
if "%CHOICE%"=="1" goto OPT1
if "%CHOICE%"=="2" goto OPT2
if "%CHOICE%"=="3" goto OPT3
if "%CHOICE%"=="4" goto OPT4
if "%CHOICE%"=="5" goto OPT5
if "%CHOICE%"=="6" goto OPT6

echo.
echo   Opcion invalida. Intenta de nuevo.
timeout /t 2 /nobreak >nul
goto MENU

:OPT1
cd /d "%TESTS%"
echo.
echo   Corriendo pruebas de API...
echo   Requiere: backend en localhost:8080
echo   Los datos creados se eliminan automaticamente al finalizar.
echo.
python -m pytest test_zonas.py test_plantas.py test_alertas.py test_sensores.py -v -s --html=report-api.html --self-contained-html
set EXITCODE=%errorlevel%
set SUITE=Pruebas de API
set REPORT=%TESTS%\report-api.html
goto RESUMEN

:OPT2
cd /d "%TESTS%"
echo.
echo   Corriendo pruebas de Taiga...
echo   Requiere: backend en localhost:8080
echo   Los datos creados se eliminan automaticamente al finalizar.
echo.
python -m pytest test_taiga_integration.py -v -s --html=report-taiga.html --self-contained-html
set EXITCODE=%errorlevel%
set SUITE=Integracion con Taiga
set REPORT=%TESTS%\report-taiga.html
goto RESUMEN

:OPT3
cd /d "%TESTS%"
echo.
echo   Corriendo todas las pruebas de API...
echo   Requiere: backend en localhost:8080
echo   Los datos creados se eliminan automaticamente al finalizar.
echo.
python -m pytest test_zonas.py test_plantas.py test_alertas.py test_sensores.py test_taiga_integration.py -v -s --html=report-full.html --self-contained-html
set EXITCODE=%errorlevel%
set SUITE=Suite completa de API
set REPORT=%TESTS%\report-full.html
goto RESUMEN

:OPT4
cd /d "%SELENIUM%"
echo.
echo   Corriendo pruebas Selenium (interfaz de usuario)...
echo   Requiere: backend en localhost:8080 Y frontend en localhost:5173
echo   Chrome se abre en modo headless (sin ventana visible).
echo.
echo   Instalando dependencias Selenium...
python -m pip install -q -r requirements.txt
echo.
python -m pytest -v -s
set EXITCODE=%errorlevel%
set SUITE=Pruebas Selenium UI
set REPORT=%SELENIUM%\reporte-selenium.html
goto RESUMEN

:OPT5
cd /d "%ROOT%"
echo.
echo   Subiendo historias de usuario a Taiga...
echo.
python taiga-upload.py
set EXITCODE=%errorlevel%
set SUITE=Upload a Taiga
set REPORT=
goto RESUMEN

:OPT6
cd /d "%TESTS%"
echo.
echo   Opciones de limpieza:
echo     [a] Limpiar datos de prueba ahora
echo     [b] Solo mostrar que se borraria (dry-run)
echo.
set CLEAN_CHOICE=
set /p CLEAN_CHOICE=  Tu eleccion (a/b):
echo.
if /i "%CLEAN_CHOICE%"=="a" goto CLEAN_RUN
python cleanup_test_data.py --dry-run
set EXITCODE=%errorlevel%
set SUITE=Limpieza dry-run
set REPORT=
goto RESUMEN
:CLEAN_RUN
python cleanup_test_data.py
set EXITCODE=%errorlevel%
set SUITE=Limpieza de datos de prueba
set REPORT=
goto RESUMEN

:RESUMEN
echo.
echo   ==============================================
echo    RESUMEN DE EJECUCION
echo   ==============================================
echo.
echo   Suite ejecutada : %SUITE%
echo   Fecha y hora    : %DATE% %TIME:~0,8%
if not "%REPORT%"=="" echo   Reporte HTML    : %REPORT%
echo.
if "%EXITCODE%"=="0" goto RESUMEN_OK
echo   RESULTADO: ALGUNAS PRUEBAS FALLARON   [EXIT CODE: %EXITCODE%]
echo.
echo   Revisa el reporte HTML o la salida de consola para ver los detalles.
goto CONTINUAR
:RESUMEN_OK
echo   RESULTADO: TODAS LAS PRUEBAS PASARON  [OK]

:CONTINUAR
echo.
echo   Los datos de prueba creados fueron eliminados automaticamente.
echo   ==============================================
echo.
set OTRA=
set /p OTRA=  Deseas ejecutar otra prueba? [S]i / [Enter] para cerrar:
if /i "%OTRA%"=="S" goto MENU

:FIN
echo.
set /p _=  Presiona Enter para cerrar...
