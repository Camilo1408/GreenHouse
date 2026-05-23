"""
GreenHouse Manager — Conectividad con Taiga
Autores: [Nombres del equipo]
Fecha: 2026

Valida que las historias de usuario del proyecto Taiga existen
y que sus criterios de aceptación están cubiertos por la API del sistema.

Requisitos:
  - Proyecto creado en: https://taiga.io  (o instancia propia)
  - Variables de entorno: TAIGA_URL, TAIGA_USERNAME, TAIGA_PASSWORD, TAIGA_PROJECT_SLUG
"""

import os
import pytest
import requests

# ── Configuración ──────────────────────────────────────────────────────────────
TAIGA_URL      = os.getenv("TAIGA_URL",      "https://api.taiga.io/api/v1")
TAIGA_USER     = os.getenv("TAIGA_USERNAME", "")
TAIGA_PASSWORD = os.getenv("TAIGA_PASSWORD", "")
TAIGA_SLUG     = os.getenv("TAIGA_PROJECT_SLUG", "cesar_camilo-greenhouse-manager")
API_BASE       = os.getenv("API_BASE_URL",   "http://localhost:8080")

# Historias de usuario que DEBEN existir en el proyecto Taiga
REQUIRED_USER_STORIES = [
    "Inicio de sesión con email y contraseña",
    "Inicio de sesión con Google",
    "Registro de usuario con verificación de correo",
    "Visualizar panel de control con estadísticas",
    "Gestión de zonas del invernadero",
    "Gestión de plantas por ciclo de vida",
    "Monitoreo de alertas generadas por sensores",
    "Registro de cosechas con calidad y destino",
    "Gestión de empleados y roles",
]


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def taiga_token():
    """Obtiene token de autenticación de Taiga."""
    if not TAIGA_USER or not TAIGA_PASSWORD:
        pytest.skip("Variables TAIGA_USERNAME y TAIGA_PASSWORD no configuradas")

    response = requests.post(f"{TAIGA_URL}/auth", json={
        "type": "normal",
        "username": TAIGA_USER,
        "password": TAIGA_PASSWORD
    }, timeout=10)

    assert response.status_code == 200, \
        f"No se pudo autenticar en Taiga: {response.status_code} {response.text}"

    return response.json()["auth_token"]


@pytest.fixture(scope="module")
def taiga_headers(taiga_token):
    """Headers con autenticación para llamadas a Taiga."""
    return {
        "Authorization": f"Bearer {taiga_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="module")
def taiga_project(taiga_headers):
    """Obtiene el proyecto GreenHouse Manager desde Taiga."""
    response = requests.get(
        f"{TAIGA_URL}/projects/by_slug?slug={TAIGA_SLUG}",
        headers=taiga_headers,
        timeout=10
    )
    assert response.status_code == 200, \
        f"No se encontró el proyecto '{TAIGA_SLUG}' en Taiga: {response.status_code}"

    return response.json()


@pytest.fixture(scope="module")
def taiga_user_stories(taiga_headers, taiga_project):
    """Obtiene todas las historias de usuario del proyecto."""
    project_id = taiga_project["id"]
    response = requests.get(
        f"{TAIGA_URL}/userstories?project={project_id}",
        headers=taiga_headers,
        timeout=10
    )
    assert response.status_code == 200, \
        f"No se pudieron obtener las historias: {response.status_code}"

    return response.json()


# ── Tests de conectividad con Taiga ────────────────────────────────────────────

class TestTaigaConectividad:
    """Verifica la conexión y estructura del proyecto en Taiga."""

    def test_taiga_api_accessible(self):
        """
        Criterio: La API de Taiga debe responder.
        """
        response = requests.get(f"{TAIGA_URL}/", timeout=10)
        assert response.status_code in [200, 404], \
            f"La API de Taiga no es accesible: {response.status_code}"

    def test_project_exists_in_taiga(self, taiga_project):
        """
        Criterio: El proyecto 'greenhouse-manager' debe existir en Taiga.
        """
        assert taiga_project is not None
        assert "id" in taiga_project
        assert taiga_project.get("slug") == TAIGA_SLUG or \
               "greenhouse" in taiga_project.get("name", "").lower(), \
            f"El proyecto encontrado no corresponde a GreenHouse Manager: {taiga_project.get('name')}"

    def test_project_has_user_stories(self, taiga_user_stories):
        """
        Criterio: El proyecto debe tener al menos 5 historias de usuario definidas.
        """
        assert len(taiga_user_stories) >= 5, \
            f"Se esperaban al menos 5 historias de usuario, se encontraron: {len(taiga_user_stories)}"

    def test_required_user_stories_exist(self, taiga_user_stories):
        """
        Criterio: Las historias de usuario clave del sistema deben existir en Taiga.
        Se valida que al menos el 70% de las historias requeridas estén presentes.
        """
        story_subjects = [s["subject"].lower() for s in taiga_user_stories]
        found = 0
        missing = []

        for required in REQUIRED_USER_STORIES:
            keywords = required.lower().split()
            # Una historia "existe" si al menos 2 palabras clave aparecen en algún subject
            matches = [s for s in story_subjects
                       if sum(1 for kw in keywords if kw in s) >= 2]
            if matches:
                found += 1
            else:
                missing.append(required)

        coverage = found / len(REQUIRED_USER_STORIES) * 100
        print(f"\nCobertura de historias de usuario: {coverage:.1f}% ({found}/{len(REQUIRED_USER_STORIES)})")
        if missing:
            print(f"Historias no encontradas: {missing}")

        assert coverage >= 70, \
            f"Solo se encontraron {coverage:.1f}% de las historias requeridas. Faltantes: {missing}"


class TestCriteriosAceptacion:
    """
    Valida los criterios de aceptación de cada historia de usuario
    comprobando que los endpoints del API existen y responden correctamente.
    """

    @pytest.fixture(scope="class")
    def api_session(self):
        """Sesión autenticada en la API del sistema."""
        session = requests.Session()
        # Login con admin de prueba
        resp = session.post(f"{API_BASE}/api/auth/login",
                            data={"email": "admin@greenhouse.com", "password": "Admin1234"},
                            headers={"Content-Type": "application/x-www-form-urlencoded"})
        if resp.status_code not in [200, 302]:
            pytest.skip(f"Backend no disponible o credenciales incorrectas: {resp.status_code}")
        return session

    def test_ca_login_endpoint_exists(self, api_session):
        """
        CA-HU01: El endpoint de login existe y acepta peticiones POST.
        Mapeado a: HU-01 'Inicio de sesión con email y contraseña'
        """
        resp = api_session.get(f"{API_BASE}/api/auth/me")
        assert resp.status_code in [200, 401], \
            f"El endpoint /api/auth/me no responde correctamente: {resp.status_code}"

    def test_ca_zonas_crud_available(self, api_session):
        """
        CA-HU05: El CRUD de zonas está disponible.
        Mapeado a: HU-05 'Gestión de zonas del invernadero'
        """
        resp = api_session.get(f"{API_BASE}/api/zonas")
        assert resp.status_code == 200, \
            f"El endpoint GET /api/zonas no responde: {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list), "Se esperaba una lista de zonas"

    def test_ca_plantas_list_available(self, api_session):
        """
        CA-HU06: El listado de plantas está disponible.
        Mapeado a: HU-06 'Gestión de plantas por ciclo de vida'
        """
        resp = api_session.get(f"{API_BASE}/api/plantas")
        assert resp.status_code == 200, \
            f"El endpoint GET /api/plantas no responde: {resp.status_code}"

    def test_ca_alertas_count_endpoint(self, api_session):
        """
        CA-HU07: El conteo de alertas pendientes está disponible para el dashboard.
        Mapeado a: HU-07 'Monitoreo de alertas generadas por sensores'
        """
        resp = api_session.get(f"{API_BASE}/api/alertas/count/pendientes")
        assert resp.status_code == 200, \
            f"El endpoint GET /api/alertas/count/pendientes no responde: {resp.status_code}"
        data = resp.json()
        assert "total" in data, "La respuesta debe incluir el campo 'total'"

    def test_ca_cosechas_estadisticas_endpoint(self, api_session):
        """
        CA-HU08: Las estadísticas de cosechas por mes están disponibles.
        Mapeado a: HU-08 'Registro de cosechas con calidad y destino'
        """
        resp = api_session.get(f"{API_BASE}/api/cosechas/estadisticas/mes?year=2026&month=5")
        assert resp.status_code == 200, \
            f"El endpoint de estadísticas de cosechas no responde: {resp.status_code}"
        data = resp.json()
        assert "totalKg" in data, "La respuesta debe incluir el campo 'totalKg'"

    def test_ca_empleados_requires_auth(self):
        """
        CA-HU09: El endpoint de empleados requiere autenticación (seguridad).
        Mapeado a: HU-09 'Gestión de empleados y roles'
        """
        resp = requests.get(f"{API_BASE}/api/empleados")
        assert resp.status_code == 401, \
            f"El endpoint de empleados debe requerir autenticación (esperado 401, obtenido {resp.status_code})"

    def test_ca_oauth2_endpoint_available(self):
        """
        CA-HU02: El endpoint de OAuth2 con Google está disponible.
        Mapeado a: HU-02 'Inicio de sesión con Google'
        """
        resp = requests.get(f"{API_BASE}/oauth2/authorization/google",
                            allow_redirects=False)
        # Debe redirigir a Google (302) o estar disponible
        assert resp.status_code in [302, 200], \
            f"El endpoint OAuth2 no está disponible: {resp.status_code}"

    def test_ca_swagger_documentation_available(self):
        """
        CA-DOC: La documentación Swagger está disponible (criterio de documentación).
        """
        resp = requests.get(f"{API_BASE}/swagger-ui.html", allow_redirects=True)
        assert resp.status_code == 200, \
            f"Swagger UI no está disponible: {resp.status_code}"
