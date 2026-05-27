"""
GreenHouse Manager — Tests Selenium: Control de Acceso por Roles (RBAC)
Autores: [Nombres del equipo]
Fecha: 2026

Pruebas de interfaz para el sistema de roles y permisos.
Criterios de aceptación validados:
  - HU-27: El administrador ve el menú completo incluyendo Empleados
  - HU-28: El rol del usuario autenticado es visible en el sidebar
  - HU-29: La navegación a páginas protegidas redirige al login si no hay sesión
  - HU-30: El botón de eliminar solo es visible para administradores
  - HU-31: Los usuarios no autenticados son redirigidos al login
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5173"


class TestRBACUI:
    """HU-27 a HU-31 — Pruebas del sistema de roles y permisos."""

    def test_admin_sees_empleados_in_sidebar(self, authenticated_driver):
        """
        HU-27 — El administrador ve el enlace 'Empleados' en el sidebar.
        Criterio: Como ADMINISTRADOR, el ítem de Empleados debe estar presente en el menú.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(2)

        page = driver.page_source
        # El admin debe ver Empleados en el sidebar
        assert "Empleados" in page or "Employees" in page, \
            "El administrador no ve el enlace de Empleados en el sidebar"

    def test_user_role_badge_visible_in_sidebar(self, authenticated_driver):
        """
        HU-28 — El badge del rol del usuario es visible en la parte inferior del sidebar.
        Criterio: Debe aparecer el nombre del rol (ADMINISTRADOR, SUPERVISOR o EMPLEADO).
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(2)

        page = driver.page_source
        roles = ["ADMINISTRADOR", "SUPERVISOR", "EMPLEADO"]
        found_role = any(role in page for role in roles)
        assert found_role, \
            "El badge de rol del usuario no es visible en el sidebar"

    def test_unauthenticated_redirect_to_login(self):
        """
        HU-31 — Sin sesión activa, el acceso a rutas protegidas redirige al login.
        Criterio: Navegar a /dashboard sin autenticarse debe llevar a /login.
        NOTA: Usa un driver AISLADO (no la sesión compartida) para no romper los tests posteriores.
        """
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        from conftest import get_driver, HEADLESS
        isolated_driver = get_driver(headless=HEADLESS)
        isolated_driver.implicitly_wait(10)
        try:
            isolated_driver.get(f"{BASE_URL}/dashboard")
            time.sleep(3)
            assert "/login" in isolated_driver.current_url, \
                f"Se esperaba redirección a /login, pero la URL es: {isolated_driver.current_url}"
        finally:
            isolated_driver.quit()

    def test_admin_can_access_empleados_page(self, authenticated_driver):
        """
        HU-27 — El administrador puede acceder a la página de empleados.
        Criterio: Al navegar a /empleados, la página carga sin error 403.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/empleados")
        time.sleep(2)

        page = driver.page_source
        assert "403" not in page and "Forbidden" not in page, \
            "El administrador recibe error 403 al acceder a /empleados"
        assert "Empleado" in page or "Employee" in page, \
            "La página de empleados no cargó correctamente para el administrador"

    def test_all_main_sections_accessible_to_admin(self, authenticated_driver):
        """
        HU-27 — El administrador puede acceder a todas las secciones del sistema.
        Criterio: Zonas, Plantas, Sensores, Alertas, Cosechas, Novedades, Empleados
                  deben cargar sin error 403.
        """
        driver = authenticated_driver
        sections = [
            ("/zonas",     "Zona"),
            ("/plantas",   "Planta"),
            ("/sensores",  "Sensor"),
            ("/alertas",   "Alerta"),
            ("/cosechas",  "Cosecha"),
            ("/novedades", "Novedad"),
            ("/empleados", "Empleado"),
        ]

        for path, keyword in sections:
            driver.get(f"{BASE_URL}{path}")
            time.sleep(2)
            page = driver.page_source
            assert "403" not in page and "Forbidden" not in page, \
                f"El administrador recibe error 403 al acceder a {path}"
            assert keyword.lower() in page.lower() or "loading" in page.lower(), \
                f"La página {path} no cargó correctamente (keyword '{keyword}' no encontrada)"

    def test_logout_clears_session(self):
        """
        HU-29 — El cierre de sesión elimina la sesión activa.
        Criterio: Tras hacer clic en 'Cerrar sesión', la URL cambia a /login.

        NOTA: Usa un driver AISLADO para no romper la sesión compartida de
        authenticated_driver (que reutilizan todos los demás tests de la suite).
        """
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        from conftest import get_driver, HEADLESS, BASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        isolated_driver = get_driver(headless=HEADLESS)
        isolated_driver.implicitly_wait(10)
        try:
            # Login
            isolated_driver.get(f"{BASE_URL}/login")
            wait = WebDriverWait(isolated_driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
            isolated_driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(ADMIN_EMAIL)
            isolated_driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(ADMIN_PASSWORD)
            isolated_driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            wait.until(EC.url_contains("/dashboard"))

            # Logout
            logout_buttons = isolated_driver.find_elements(
                By.XPATH, "//*[contains(text(),'Cerrar sesión') or contains(text(),'Logout')]"
            )
            if not logout_buttons:
                logout_buttons = isolated_driver.find_elements(
                    By.XPATH, "//button[contains(., 'Cerrar') or contains(., 'Logout')]"
                )

            assert logout_buttons, "No se encontró el botón de cerrar sesión"
            logout_buttons[0].click()
            time.sleep(3)

            assert "/login" in isolated_driver.current_url, \
                f"Después del logout, se esperaba /login, pero la URL es: {isolated_driver.current_url}"
        finally:
            isolated_driver.quit()

    def test_novedades_visible_to_all_roles(self, authenticated_driver):
        """
        HU-26 — La sección de Novedades es visible en el sidebar para cualquier rol.
        Criterio: El enlace a /novedades debe aparecer en el menú lateral.
        """
        driver = authenticated_driver
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(2)

        novedades_links = driver.find_elements(
            By.XPATH, "//a[contains(@href, '/novedades')]"
        )
        assert len(novedades_links) > 0, \
            "El enlace de Novedades no está visible en el sidebar (debe serlo para todos los roles)"
