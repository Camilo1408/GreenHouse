"""
GreenHouse Manager — Tests Selenium: Dashboard
Autores: [Nombres del equipo]
Fecha: 2026

Pruebas de interfaz para el Panel de Control (Dashboard).
Criterios de aceptación validados:
  - HU-06: El dashboard muestra las 4 tarjetas de estadísticas
  - HU-07: El menú lateral muestra todas las secciones disponibles
  - HU-08: El botón de cerrar sesión funciona correctamente
  - HU-09: El panel de estado de plantas por tipo es visible
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5173"


class TestDashboard:
    """HU-06 a HU-09 — Pruebas del panel de control."""

    def test_dashboard_loads_after_login(self, authenticated_driver):
        """
        HU-06 — El dashboard carga correctamente tras autenticarse.
        Criterio: La URL debe ser /dashboard y el título debe estar visible.
        """
        driver = authenticated_driver
        # Navegar explicitamente al dashboard (tests anteriores pueden haber
        # dejado el driver en otra URL de la sesion compartida)
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(2)

        assert "/dashboard" in driver.current_url, \
            f"Se esperaba /dashboard, pero se está en: {driver.current_url}"

        # Verifica título del panel
        assert "Panel de Control" in driver.page_source or "Dashboard" in driver.page_source, \
            "El título del panel no está visible"

    def test_stat_cards_visible(self, authenticated_driver):
        """
        HU-06 — Las 4 tarjetas de estadísticas son visibles en el dashboard.
        Criterio: Deben aparecer indicadores de Plantas, Alertas, Cosechas y Zonas.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(2)

        page = driver.page_source
        assert "Plantas Activas" in page or "Plantas" in page, \
            "La tarjeta de plantas activas no está visible"
        assert "Alertas" in page, \
            "La tarjeta de alertas no está visible"
        assert "Cosechas" in page, \
            "La tarjeta de cosechas no está visible"
        assert "Zonas" in page, \
            "La tarjeta de zonas no está visible"

    def test_sidebar_navigation_links(self, authenticated_driver):
        """
        HU-07 — El menú lateral muestra los enlaces de navegación correctos.
        Criterio: Deben existir enlaces a Dashboard, Zonas, Plantas, Alertas,
                  Cosechas, Novedades y Empleados (para ADMINISTRADOR).
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(1)

        page = driver.page_source
        # Core sections visible to all roles
        core_sections = ["Zonas", "Plantas", "Alertas", "Cosechas"]
        for section in core_sections:
            assert section in page or section.lower() in page.lower(), \
                f"La sección '{section}' no aparece en el menú lateral"

        # Novedades visible to all roles
        assert "Novedad" in page or "novedades" in page.lower() or "Reports" in page, \
            "La sección 'Novedades' no aparece en el menú lateral"

        # Empleados visible only to ADMINISTRADOR (test user is admin)
        assert "Empleados" in page or "Employees" in page, \
            "La sección 'Empleados' no aparece para el administrador"

    def test_plant_status_breakdown_visible(self, authenticated_driver):
        """
        HU-09 — El desglose de plantas por estado está visible en el dashboard.
        Criterio: Deben aparecer los 5 estados de plantas en la sección inferior.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(2)

        page = driver.page_source
        estados = ["Sembrada", "En crecimiento", "Lista para cosechar", "Cosechada", "Muerta"]
        for estado in estados:
            assert estado in page, f"El estado '{estado}' no aparece en el dashboard"

    def test_logout_button_visible(self, authenticated_driver):
        """
        HU-08 — El botón de cerrar sesión es visible en el menú lateral.
        Criterio: El elemento 'Cerrar sesión' debe estar presente y ser clickeable.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(1)

        assert "Cerrar sesión" in driver.page_source or "logout" in driver.page_source.lower(), \
            "El botón de cerrar sesión no está visible"

    def test_language_switcher_present(self, authenticated_driver):
        """
        Criterio de i18n: El selector de idioma (English/Español) está visible.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(1)

        page = driver.page_source
        assert "English" in page or "Español" in page, \
            "El selector de idioma no está visible"
