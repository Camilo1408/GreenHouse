"""
GreenHouse Manager — Tests Selenium: Reporte de Novedades
Autores: [Nombres del equipo]
Fecha: 2026

Pruebas de interfaz para la sección de Novedades del invernadero.
Criterios de aceptación validados:
  - HU-22: La página de novedades carga y muestra el formulario de reporte
  - HU-23: El usuario puede seleccionar el tipo de novedad (enfermedad / falla)
  - HU-24: La navegación a Novedades desde el sidebar funciona correctamente
  - HU-25: El formulario requiere zona y descripción antes de enviar
  - HU-26: El selector de severidad es visible para el tipo "Falla en zona"
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5173"


class TestNovedadesUI:
    """HU-22 a HU-26 — Pruebas de la sección de Novedades."""

    def test_novedades_page_loads(self, authenticated_driver):
        """
        HU-22 — La página de novedades carga y muestra el título y formulario.
        Criterio: La URL es /novedades y el contenido del formulario es visible.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/novedades")
        time.sleep(2)

        assert "/novedades" in driver.current_url, \
            f"No se navegó a /novedades, URL actual: {driver.current_url}"

        page = driver.page_source
        assert (
            "Novedad" in page or "novedad" in page or
            "Report" in page or "Enfermedad" in page or "Falla" in page
        ), "La página de novedades no muestra contenido relevante"

    def test_novedad_type_selector_present(self, authenticated_driver):
        """
        HU-23 — Los dos tipos de novedad (enfermedad y falla) son seleccionables.
        Criterio: Deben aparecer los botones para 'Enfermedad en planta' y 'Falla en zona'.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/novedades")
        time.sleep(2)

        page = driver.page_source
        has_enfermedad = (
            "Enfermedad" in page or "enfermedad" in page or
            "disease" in page.lower() or "Plant disease" in page
        )
        has_falla = (
            "Falla" in page or "falla" in page or
            "failure" in page.lower() or "Zone failure" in page
        )

        assert has_enfermedad, "El tipo 'Enfermedad en planta' no está visible"
        assert has_falla, "El tipo 'Falla en zona' no está visible"

    def test_zona_selector_present(self, authenticated_driver):
        """
        HU-22 — El selector de zona está presente en el formulario.
        Criterio: Debe existir un campo <select> para elegir la zona afectada.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/novedades")
        time.sleep(2)

        selects = driver.find_elements(By.TAG_NAME, "select")
        assert len(selects) >= 1, \
            "No se encontró ningún selector (select) en el formulario de novedades"

    def test_submit_button_disabled_when_empty(self, authenticated_driver):
        """
        HU-25 — El formulario valida campos obligatorios antes de enviar.
        Criterio: El botón de reportar debe estar deshabilitado O al intentar enviar
        sin datos debe permanecer en la misma pagina sin crear la novedad.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/novedades")
        time.sleep(2)

        url_antes = driver.current_url

        buttons = driver.find_elements(By.TAG_NAME, "button")
        submit_btn = None
        for btn in buttons:
            text = btn.text.lower()
            if "report" in text or "novedad" in text or "enviar" in text or "submit" in text:
                submit_btn = btn
                break

        assert submit_btn is not None, "No se encontró el botón de reportar novedad"

        # El boton puede estar deshabilitado (disabled attr o aria-disabled)
        # O puede estar habilitado pero la validacion impide el envio
        btn_disabled = (
            not submit_btn.is_enabled()
            or submit_btn.get_attribute("disabled") is not None
            or submit_btn.get_attribute("aria-disabled") == "true"
        )

        if not btn_disabled:
            # Si el boton esta habilitado, hacer clic y verificar que no navega
            submit_btn.click()
            time.sleep(1)
            # Debe permanecer en /novedades (validacion del lado del cliente)
            assert "/novedades" in driver.current_url, \
                "HU-25: El formulario vacio no deberia navegar fuera de /novedades"
        else:
            # El boton esta correctamente deshabilitado
            assert True, "HU-25: El boton esta deshabilitado correctamente"

    def test_falla_zona_type_shows_severity(self, authenticated_driver):
        """
        HU-26 — Al seleccionar 'Falla en zona', aparecen los botones de severidad.
        Criterio: Los niveles BAJA, MEDIA, ALTA, CRITICA deben ser visibles al seleccionar ese tipo.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/novedades")
        time.sleep(2)

        # Click on "Falla en zona" button
        buttons = driver.find_elements(By.TAG_NAME, "button")
        falla_btn = None
        for btn in buttons:
            text = btn.text
            if "Falla" in text or "falla" in text or "failure" in text.lower() or "Zone" in text:
                falla_btn = btn
                break

        if falla_btn:
            falla_btn.click()
            time.sleep(1)

            page = driver.page_source
            severity_keywords = [
                "BAJA", "MEDIA", "ALTA", "CRITICA",
                "Low", "Medium", "High", "Critical",
                "Baja", "Media", "Alta", "Crítica"
            ]
            found_severity = any(kw in page for kw in severity_keywords)
            assert found_severity, \
                "Los niveles de severidad no aparecen al seleccionar 'Falla en zona'"

    def test_navigation_to_novedades_from_sidebar(self, authenticated_driver):
        """
        HU-24 — El enlace del sidebar lleva a /novedades correctamente.
        Criterio: Al hacer clic en el ítem del menú lateral, la URL cambia a /novedades.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(1)

        novedades_links = driver.find_elements(
            By.XPATH, "//a[contains(@href, '/novedades')]"
        )
        assert len(novedades_links) > 0, \
            "No se encontró el enlace de Novedades en el sidebar"

        novedades_links[0].click()
        time.sleep(2)

        assert "/novedades" in driver.current_url, \
            f"El enlace de Novedades no llevó a /novedades, URL actual: {driver.current_url}"

    def test_novedades_page_i18n_content(self, authenticated_driver):
        """
        HU-22 — El contenido de la página de novedades está en el idioma correcto (i18n).
        Criterio: Con idioma español por defecto, los textos deben estar en español.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/novedades")
        time.sleep(2)

        page = driver.page_source
        # Verify at least one of these Spanish labels exists
        spanish_terms = [
            "Novedad", "Zona afectada", "Reportar", "Enfermedad",
            "Tipo de novedad", "Descripción"
        ]
        found = any(term in page for term in spanish_terms)
        assert found, \
            "No se encontraron textos en español en la página de novedades (posible fallo de i18n)"
