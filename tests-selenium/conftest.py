"""
GreenHouse Manager — Configuración de Selenium
Autores: [Nombres del equipo]
Fecha: 2026

Fixture compartida que levanta Chrome con ventana visible para poder
observar las pruebas en ejecucion. Reutiliza el mismo driver en toda
la sesion para mayor velocidad.
"""

import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

BASE_URL       = "http://localhost:5173"
ADMIN_EMAIL    = "admin@greenhouse.com"
ADMIN_PASSWORD = "Admin1234"

# Cambiar a True solo en CI/GitHub Actions; False = ventana visible localmente
HEADLESS = os.environ.get("CI", "").lower() in ("true", "1", "yes")


def _find_chromedriver() -> str:
    """
    Resuelve el path al chromedriver.exe real.

    webdriver-manager tiene un bug conocido: .install() puede devolver el path a
    THIRD_PARTY_NOTICES.chromedriver en vez del ejecutable, causando WinError 193.
    Esta funcion busca chromedriver.exe en el mismo directorio que sea devuelto.
    """
    from pathlib import Path
    from webdriver_manager.chrome import ChromeDriverManager

    raw_path = ChromeDriverManager().install()
    driver_dir = Path(raw_path).parent

    # Buscar el ejecutable real en el directorio
    for name in ("chromedriver.exe", "chromedriver"):
        candidate = driver_dir / name
        if candidate.exists():
            return str(candidate)

    # Si no lo encontro en el directorio inmediato, busca un nivel arriba
    for name in ("chromedriver.exe", "chromedriver"):
        candidate = driver_dir.parent / name
        if candidate.exists():
            return str(candidate)

    # Fallback: devolver lo que retorno webdriver-manager (puede fallar)
    return raw_path


def get_driver(headless: bool = False) -> webdriver.Chrome:
    """Instancia Chrome. Sin headless: ventana visible para revisar las pruebas."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    # Flags estables en Windows
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1400,900")
    options.add_argument("--start-maximized")

    # En CI usa el chromedriver del PATH; localmente descarga con webdriver-manager
    chrome_driver_path = os.environ.get("CHROMEDRIVER_PATH", "")
    if chrome_driver_path:
        service = Service(executable_path=chrome_driver_path)
    else:
        try:
            driver_exe = _find_chromedriver()
            print(f"\n[Selenium] ChromeDriver: {driver_exe}")
            service = Service(executable_path=driver_exe)
        except Exception as e:
            print(f"\n[Selenium] webdriver-manager fallo ({e}), usando chromedriver del PATH")
            service = Service()  # usa el chromedriver del PATH del sistema

    return webdriver.Chrome(service=service, options=options)


@pytest.fixture(scope="session")
def driver():
    """
    Driver de sesion: se crea UNA sola vez y se reutiliza en todos los tests.
    Corre con ventana visible (no headless) para poder observar las pruebas.
    Al terminar la suite, el navegador se cierra automaticamente.
    """
    drv = get_driver(headless=HEADLESS)
    drv.implicitly_wait(10)
    yield drv
    drv.quit()


@pytest.fixture(scope="session")
def authenticated_driver(driver):
    """
    Driver ya autenticado como administrador.
    Realiza el login una sola vez para toda la sesión.

    NOTA: Borra cookies antes de navegar a /login para garantizar que no hay
    sesión residual de test_auth.py (que corre primero por orden alfabético).
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # Elimina sesión anterior si test_auth.py ya hizo login
    driver.delete_all_cookies()
    driver.get(f"{BASE_URL}/login")

    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))

    driver.find_element(By.CSS_SELECTOR, "input[type='email']").clear()
    driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(ADMIN_EMAIL)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").clear()
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(ADMIN_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Espera redirección al dashboard
    wait.until(EC.url_contains("/dashboard"))

    yield driver
