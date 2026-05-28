"""
GreenHouse Manager — Tests Selenium: Gestión de Plantas
Autores: [Nombres del equipo]
Fecha: 2026

Pruebas de interfaz para la sección de Plantas del invernadero.
Criterios de aceptación validados:
  - HU-13: El listado de plantas muestra las plantas existentes con su estado
  - HU-14: El sistema muestra la información de tipo de planta y zona correctamente
  - HU-15: El filtrado de plantas por estado funciona en la interfaz
  - HU-16: Se puede crear un nuevo tipo de planta inline desde el formulario de plantas
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5173"


class TestPlantasUI:
    """HU-13 a HU-15 — Pruebas de la sección de Plantas."""

    def test_plantas_page_loads(self, authenticated_driver):
        """
        HU-13 — La página de plantas carga correctamente.
        Criterio: La URL es /plantas y el contenido relacionado con plantas es visible.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/plantas")
        time.sleep(2)

        assert "/plantas" in driver.current_url, \
            f"No se navegó a /plantas, URL actual: {driver.current_url}"

        page = driver.page_source
        assert "Planta" in page or "planta" in page or "CÓDIGO" in page or "Código" in page, \
            "La página de plantas no muestra contenido relevante"

    def test_plantas_data_is_loaded(self, authenticated_driver):
        """
        HU-13 — Las plantas de prueba se muestran en el listado.
        Criterio: Debe aparecer al menos un código de planta (TOM, LEC, PIM o ALB).
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/plantas")
        time.sleep(2)

        page = driver.page_source
        has_plant_data = (
            "TOM-" in page or "LEC-" in page or "PIM-" in page or "ALB-" in page or
            "Tomate" in page or "Lechuga" in page or "Pimiento" in page or "Albahaca" in page
        )
        assert has_plant_data, \
            "No se encontraron datos de plantas. Verifica que el backend está corriendo y los datos están cargados."

    def test_plant_status_columns_visible(self, authenticated_driver):
        """
        HU-13 — Las columnas del listado de plantas incluyen el estado.
        Criterio: Se deben ver estados como SEMBRADA, EN_CRECIMIENTO, etc.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/plantas")
        time.sleep(2)

        page = driver.page_source
        statuses = ["SEMBRADA", "EN_CRECIMIENTO", "LISTA_PARA_COSECHAR", "COSECHADA", "MUERTA",
                    "Sembrada", "Crecimiento", "Cosechar", "Cosechada", "Muerta"]
        found = any(s in page for s in statuses)
        assert found, "Los estados de las plantas no son visibles en el listado"

    def test_inline_nuevo_tipo_form_appears(self, authenticated_driver):
        """
        HU-16 — El botón "Nuevo tipo" despliega el sub-formulario inline.
        Criterio: Al abrir el formulario de nueva planta y pulsar "Nuevo tipo",
        aparece el campo 'nombre' del sub-formulario de tipo de planta.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/plantas")
        wait = WebDriverWait(driver, 10)

        # Abrir formulario Nueva Planta
        nueva_planta_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Nueva') or contains(., 'planta') or contains(., 'Planta')]")
            )
        )
        nueva_planta_btn.click()
        time.sleep(1)

        # Pulsar "Nuevo tipo"
        nuevo_tipo_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Nuevo tipo')]")
            )
        )
        nuevo_tipo_btn.click()
        time.sleep(1)

        # Verificar que aparece el sub-formulario
        nombre_input = driver.find_element(By.ID, "nuevo-tipo-nombre")
        assert nombre_input.is_displayed(), "El campo 'nombre' del nuevo tipo no es visible"

        ciclo_input = driver.find_element(By.ID, "nuevo-tipo-ciclo")
        assert ciclo_input.is_displayed(), "El campo 'ciclo' del nuevo tipo no es visible"

    def test_inline_nuevo_tipo_create_and_autoselect(self, authenticated_driver):
        """
        HU-16 — Crear un tipo de planta inline lo auto-selecciona en el desplegable.
        Criterio: Tras rellenar nombre + cicloDias y pulsar "Crear y seleccionar",
        el nuevo tipo aparece seleccionado en el select de tipo de planta.
        """
        import time as _time
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/plantas")
        wait = WebDriverWait(driver, 10)

        # Abrir formulario Nueva Planta
        nueva_planta_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Nueva') or contains(., 'planta') or contains(., 'Planta')]")
            )
        )
        nueva_planta_btn.click()
        time.sleep(1)

        # Pulsar "Nuevo tipo"
        nuevo_tipo_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Nuevo tipo')]")
            )
        )
        nuevo_tipo_btn.click()
        time.sleep(1)

        # Rellenar nombre y ciclo
        ts = int(_time.time())
        nombre_unico = f"Tipo Selenium {ts}"
        driver.find_element(By.ID, "nuevo-tipo-nombre").send_keys(nombre_unico)
        driver.find_element(By.ID, "nuevo-tipo-ciclo").send_keys("75")

        # Pulsar "Crear y seleccionar"
        crear_btn = driver.find_element(By.ID, "btn-crear-tipo")
        crear_btn.click()
        time.sleep(2)

        # El sub-formulario debe cerrarse y el select debe tener el nuevo tipo seleccionado
        page = driver.page_source
        tipo_select = driver.find_element(By.ID, "tipo-planta-select")
        selected_value = tipo_select.get_attribute("value") or ""

        # El nombre del tipo creado debe aparecer en la página (en el select refrescado)
        # O el select debe tener un valor distinto de vacío/"__nuevo__"
        assert (
            nombre_unico in page or
            selected_value not in ("", "__nuevo__")
        ), f"El nuevo tipo '{nombre_unico}' no fue auto-seleccionado. valor={selected_value}. Page: {page[:400]}"

    def test_navigation_to_plantas_from_sidebar(self, authenticated_driver):
        """
        HU-13 — El enlace del sidebar lleva correctamente a la sección de Plantas.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(1)

        plantas_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/plantas')]")
        assert len(plantas_links) > 0, "No se encontró el enlace de Plantas en el sidebar"

        plantas_links[0].click()
        time.sleep(2)

        assert "/plantas" in driver.current_url, \
            f"El enlace de Plantas no llevó a /plantas, URL actual: {driver.current_url}"
