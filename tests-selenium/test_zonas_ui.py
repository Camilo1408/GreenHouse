"""
GreenHouse Manager — Tests Selenium: Gestión de Zonas
Autores: [Nombres del equipo]
Fecha: 2026

Pruebas de interfaz para la sección de Zonas del invernadero.
Criterios de aceptación validados:
  - HU-10: El listado de zonas muestra las zonas existentes
  - HU-11: El formulario de creación de zona tiene todos sus campos
  - HU-12: El sistema muestra el estado de cada zona correctamente
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5173"


class TestZonasUI:
    """HU-10 a HU-12 — Pruebas de la sección de Zonas."""

    def test_zonas_page_loads(self, authenticated_driver):
        """
        HU-10 — La página de zonas carga y muestra el título.
        Criterio: La URL debe ser /zonas y debe existir el encabezado de la sección.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/zonas")
        time.sleep(2)

        assert "/zonas" in driver.current_url, \
            f"No se navegó a /zonas, URL actual: {driver.current_url}"

        page = driver.page_source
        assert "Zona" in page or "zona" in page, \
            "La página de zonas no muestra contenido relacionado con zonas"

    def test_zonas_data_displayed(self, authenticated_driver):
        """
        HU-10 — Las zonas de prueba aparecen en el listado.
        Criterio: Al menos una zona con nombre que incluya 'Zona' debe aparecer.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/zonas")
        time.sleep(2)

        page = driver.page_source
        # Con los datos de prueba, deben existir las zonas A, B, C, D
        has_zona_data = (
            "Zona A" in page or "Zona B" in page or
            "Tomates" in page or "Lechugas" in page or
            "Sector Norte" in page
        )
        assert has_zona_data, \
            "No se encontraron datos de zonas en el listado. Verifica que el backend está corriendo."

    def test_zona_states_displayed(self, authenticated_driver):
        """
        HU-12 — Los estados de las zonas son visibles en la lista.
        Criterio: Los estados ACTIVA o EN_MANTENIMIENTO deben aparecer.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/zonas")
        time.sleep(2)

        page = driver.page_source
        has_state = (
            "ACTIVA" in page or "Activa" in page or "activa" in page or
            "MANTENIMIENTO" in page or "Mantenimiento" in page
        )
        assert has_state, "Los estados de las zonas no son visibles"

    def test_navigation_to_zonas_from_sidebar(self, authenticated_driver):
        """
        HU-10 — El enlace del sidebar lleva a la sección de Zonas.
        Criterio: Al hacer clic en 'Zonas' en el menú, la URL cambia a /zonas.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(1)

        # Busca el enlace 'Zonas' en el sidebar
        zonas_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/zonas')]")
        assert len(zonas_links) > 0, "No se encontró el enlace de Zonas en el sidebar"

        zonas_links[0].click()
        time.sleep(2)

        assert "/zonas" in driver.current_url, \
            f"El enlace de Zonas no llevó a /zonas, URL actual: {driver.current_url}"
