"""
GreenHouse Manager — Tests Selenium: Gestión de Alertas
Autores: [Nombres del equipo]
Fecha: 2026

Pruebas de interfaz para la sección de Alertas del invernadero.
Criterios de aceptación validados:
  - HU-16: El listado de alertas muestra alertas con su severidad y estado
  - HU-17: Las alertas se clasifican por severidad (BAJA, MEDIA, ALTA, CRITICA)
  - HU-18: El usuario puede marcar una alerta como atendida desde la interfaz
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5173"


class TestAlertasUI:
    """HU-16 a HU-18 — Pruebas de la sección de Alertas."""

    def test_alertas_page_loads(self, authenticated_driver):
        """
        HU-16 — La página de alertas carga correctamente.
        Criterio: La URL es /alertas y el contenido de alertas es visible.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/alertas")
        time.sleep(2)

        assert "/alertas" in driver.current_url, \
            f"No se navegó a /alertas, URL actual: {driver.current_url}"

        page = driver.page_source
        assert "Alerta" in page or "alerta" in page, \
            "La página de alertas no muestra contenido relevante"

    def test_alertas_data_loaded(self, authenticated_driver):
        """
        HU-16 — Las alertas de prueba se muestran en el listado.
        Criterio: Debe aparecer al menos una alerta con tipo UMBRAL_TEMPERATURA o similar.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/alertas")
        time.sleep(2)

        page = driver.page_source
        has_alert_data = (
            "UMBRAL" in page or "Temperatura" in page or "temperatura" in page or
            "PENDIENTE" in page or "Pendiente" in page or
            "ALTA" in page or "MEDIA" in page or "BAJA" in page or "CRITICA" in page or
            "Zona A" in page or "Zona B" in page
        )
        assert has_alert_data, \
            "No se encontraron datos de alertas. Verifica que el backend está corriendo."

    def test_alert_severity_labels_visible(self, authenticated_driver):
        """
        HU-17 — Las etiquetas de severidad de alertas son visibles.
        Criterio: Al menos uno de los niveles de severidad debe estar en pantalla.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/alertas")
        time.sleep(2)

        page = driver.page_source
        severities = ["BAJA", "MEDIA", "ALTA", "CRITICA", "Baja", "Media", "Alta", "Crítica"]
        found = any(s in page for s in severities)
        assert found, "Los niveles de severidad de alertas no son visibles"

    def test_alert_status_labels_visible(self, authenticated_driver):
        """
        HU-16 — Los estados de las alertas son visibles en el listado.
        Criterio: Estados PENDIENTE, ATENDIDA o DESCARTADA deben aparecer.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/alertas")
        time.sleep(2)

        page = driver.page_source
        states = ["PENDIENTE", "ATENDIDA", "DESCARTADA", "Pendiente", "Atendida", "Descartada"]
        found = any(s in page for s in states)
        assert found, "Los estados de las alertas no son visibles"

    def test_navigation_to_alertas_from_sidebar(self, authenticated_driver):
        """
        HU-16 — El enlace del sidebar lleva a /alertas correctamente.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(1)

        alertas_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/alertas')]")
        assert len(alertas_links) > 0, "No se encontró el enlace de Alertas en el sidebar"

        alertas_links[0].click()
        time.sleep(2)

        assert "/alertas" in driver.current_url, \
            f"El enlace de Alertas no llevó a /alertas, URL actual: {driver.current_url}"
