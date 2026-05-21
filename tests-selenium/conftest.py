"""
GreenHouse Manager — Configuración de Selenium
Autores: [Nombres del equipo]
Fecha: 2026

Fixture compartida que levanta Chrome en modo headless y
navega a la URL base del frontend antes de cada test.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL  = "http://localhost:5173"
ADMIN_EMAIL    = "admin@greenhouse.com"
ADMIN_PASSWORD = "Admin1234"


def get_driver(headless: bool = True) -> webdriver.Chrome:
    """Instancia Chrome con opciones para CI (headless) o local (con ventana)."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


@pytest.fixture(scope="session")
def driver():
    """
    Driver de sesión: se crea UNA sola vez y se reutiliza en todos los tests.
    Al terminar la suite, el navegador se cierra.
    """
    drv = get_driver(headless=True)
    drv.implicitly_wait(8)
    yield drv
    drv.quit()


@pytest.fixture(scope="session")
def authenticated_driver(driver):
    """
    Driver ya autenticado como administrador.
    Realiza el login una sola vez para toda la sesión.
    """
    from selenium.webdriver.common.by import By
    import time

    driver.get(f"{BASE_URL}/login")
    time.sleep(1)

    driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(ADMIN_EMAIL)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(ADMIN_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)

    yield driver
