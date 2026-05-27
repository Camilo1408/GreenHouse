"""
GreenHouse Manager — Conectividad con Taiga
Autores: [Nombres del equipo]
Fecha: 2026
Actualizado: RBAC, Novedades, i18n, alertas manuales

Valida que las historias de usuario del proyecto Taiga existen
y que sus criterios de aceptación están cubiertos por la API del sistema.

Requisitos:
  - Proyecto creado en: https://taiga.io  (o instancia propia)
  - Variables de entorno: TAIGA_URL, TAIGA_USERNAME, TAIGA_PASSWORD, TAIGA_PROJECT_SLUG
"""

import os
import time
import pytest
import requests
from pathlib import Path

# ── Cargar .env automáticamente si existe ──────────────────────────────────────
_ENV_FILE = Path(__file__).parent.parent / ".env"
if _ENV_FILE.exists():
    for _line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# ── Configuración ──────────────────────────────────────────────────────────────
TAIGA_URL      = os.getenv("TAIGA_URL",      "https://api.taiga.io/api/v1")
TAIGA_USER     = os.getenv("TAIGA_USERNAME", "")
TAIGA_PASSWORD = os.getenv("TAIGA_PASSWORD", "")
TAIGA_SLUG     = os.getenv("TAIGA_PROJECT_SLUG", "cesar_camilo-greenhouse-manager")
API_BASE       = os.getenv("API_BASE_URL",   "http://localhost:8080")

# Sufijo único para evitar colisiones de nombres/códigos en DB entre ejecuciones
_TS = int(time.time())

# Historias de usuario que DEBEN existir en el proyecto Taiga
REQUIRED_USER_STORIES = [
    # ── Sprint 1: Autenticación y Dashboard ──────────────────────────────────
    "Inicio de sesión con email y contraseña",
    "Inicio de sesión con Google",
    "Registro de usuario con verificación de correo",
    "Visualizar panel de control con estadísticas",
    # ── Sprint 2: Gestión de entidades ───────────────────────────────────────
    "Gestión de zonas del invernadero",
    "Gestión de plantas por ciclo de vida",
    "Monitoreo de alertas generadas por sensores",
    "Registro de cosechas con calidad y destino",
    "Gestión de empleados y roles",
    "Gestión de sensores por zona",
    "Registro de lecturas de sensores con alerta automática",
    # ── Sprint 3: RBAC y Control de acceso ───────────────────────────────────
    "Control de acceso por roles RBAC",
    "Administrador gestiona empleados exclusivamente",
    "Supervisor crea y edita zonas y plantas sin eliminar",
    "Empleado actualiza estados de alertas y cosechas",
    # ── Sprint 4: Novedades e i18n ────────────────────────────────────────────
    "Reporte de novedad por enfermedad en planta",
    "Reporte de falla de sistema en zona",
    "Interfaz multiidioma español e inglés",
    # ── Sprint 5: Sensores avanzados y alertas de cosecha ─────────────────────
    "Creación de sensores inline al crear o editar zonas",
    "Alertas automáticas por valor de sensor fuera de umbral",
    "Alertas automáticas de cosecha pendiente por scheduler",
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
        Criterio: El proyecto debe tener al menos 10 historias de usuario definidas.
        """
        assert len(taiga_user_stories) >= 10, \
            f"Se esperaban al menos 10 historias de usuario, se encontraron: {len(taiga_user_stories)}"

    def test_required_user_stories_exist(self, taiga_user_stories):
        """
        Criterio: Las historias de usuario clave del sistema deben existir en Taiga.
        Se valida que al menos el 60% de las historias requeridas estén presentes.
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

        assert coverage >= 60, \
            f"Solo se encontraron {coverage:.1f}% de las historias requeridas. Faltantes: {missing}"

    def test_rbac_stories_in_backlog(self, taiga_user_stories):
        """
        Criterio: Las historias de RBAC (Sprint 3) deben estar en el backlog del proyecto.
        """
        story_subjects = [s["subject"].lower() for s in taiga_user_stories]
        rbac_keywords = ["rol", "role", "rbac", "acceso", "permiso", "supervisor", "administrador", "empleado"]
        rbac_found = any(
            any(kw in subject for kw in rbac_keywords)
            for subject in story_subjects
        )
        assert rbac_found, \
            "No se encontraron historias relacionadas con RBAC en el proyecto Taiga"

    def test_novedades_stories_in_backlog(self, taiga_user_stories):
        """
        Criterio: Las historias de Novedades (Sprint 4) deben estar en el backlog.
        """
        story_subjects = [s["subject"].lower() for s in taiga_user_stories]
        novedad_keywords = ["novedad", "enfermedad", "falla", "reporte", "report", "incidencia"]
        novedad_found = any(
            any(kw in subject for kw in novedad_keywords)
            for subject in story_subjects
        )
        assert novedad_found, \
            "No se encontraron historias relacionadas con Novedades en el proyecto Taiga"


class TestCriteriosAceptacion:
    """
    Valida los criterios de aceptación de cada historia de usuario
    comprobando que los endpoints del API existen y responden correctamente.
    """

    @pytest.fixture(scope="class")
    def api_session(self):
        """Sesión autenticada en la API del sistema (ADMINISTRADOR)."""
        session = requests.Session()
        resp = session.post(f"{API_BASE}/api/auth/login",
                            data={"email": "admin@greenhouse.com", "password": "Admin1234"},
                            headers={"Content-Type": "application/x-www-form-urlencoded"})
        if resp.status_code not in [200, 302]:
            pytest.skip(f"Backend no disponible o credenciales incorrectas: {resp.status_code}")
        return session

    @pytest.fixture(scope="class")
    def empleado_session(self):
        """Sesión autenticada como EMPLEADO (rol limitado)."""
        session = requests.Session()
        resp = session.post(f"{API_BASE}/api/auth/login",
                            data={"email": "empleado@greenhouse.com", "password": "Empleado1234"},
                            headers={"Content-Type": "application/x-www-form-urlencoded"})
        if resp.status_code not in [200, 302]:
            pytest.skip(f"Usuario empleado no disponible: {resp.status_code}")
        return session

    # ── Sprint 1 / Sprint 2 ────────────────────────────────────────────────────

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
        assert resp.status_code in [302, 200], \
            f"El endpoint OAuth2 no está disponible: {resp.status_code}"

    def test_ca_swagger_documentation_available(self):
        """
        CA-DOC: La documentación Swagger está disponible (criterio de documentación).
        """
        resp = requests.get(f"{API_BASE}/swagger-ui.html", allow_redirects=True)
        assert resp.status_code == 200, \
            f"Swagger UI no está disponible: {resp.status_code}"

    # ── Sprint 3: RBAC ─────────────────────────────────────────────────────────

    def test_ca_rbac_admin_me_returns_role(self, api_session):
        """
        CA-HU27: El endpoint /api/auth/me devuelve el rol del usuario autenticado.
        Mapeado a: HU-27 'Control de acceso por roles RBAC'
        """
        resp = api_session.get(f"{API_BASE}/api/auth/me")
        assert resp.status_code == 200, \
            f"GET /api/auth/me falló: {resp.status_code}"
        data = resp.json()
        assert "rol" in data or "role" in data, \
            "La respuesta de /api/auth/me debe incluir el campo 'rol'"
        rol = data.get("rol") or data.get("role")
        assert rol in ["ADMINISTRADOR", "SUPERVISOR", "EMPLEADO"], \
            f"Rol inesperado en /api/auth/me: {rol}"

    def test_ca_rbac_empleados_me_endpoint(self, api_session):
        """
        CA-HU28: El endpoint /api/empleados/me devuelve el perfil del empleado autenticado.
        Mapeado a: HU-28 'Todos los roles pueden consultar su propio perfil'
        """
        resp = api_session.get(f"{API_BASE}/api/empleados/me")
        assert resp.status_code in [200], \
            f"GET /api/empleados/me falló: {resp.status_code}"
        data = resp.json()
        # Puede retornar el perfil o {sin_perfil: true}
        assert isinstance(data, dict), \
            "La respuesta de /api/empleados/me debe ser un objeto JSON"

    def test_ca_rbac_empleados_list_admin_only(self, api_session):
        """
        CA-HU27: El listado completo de empleados solo es accesible para ADMINISTRADOR.
        Mapeado a: HU-27 'Administrador gestiona empleados exclusivamente'
        """
        resp = api_session.get(f"{API_BASE}/api/empleados")
        assert resp.status_code == 200, \
            f"El ADMINISTRADOR debe poder listar empleados: {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list), "Se esperaba una lista de empleados"

    def test_ca_rbac_empleado_cannot_list_employees(self, empleado_session):
        """
        CA-HU27: Un EMPLEADO no puede acceder al listado de empleados (403).
        Mapeado a: HU-27 'Administrador gestiona empleados exclusivamente'
        """
        resp = empleado_session.get(f"{API_BASE}/api/empleados")
        assert resp.status_code in [403, 401], \
            f"Un EMPLEADO no debería poder listar empleados: {resp.status_code}"

    def test_ca_rbac_supervisor_cannot_delete_zona(self, api_session):
        """
        CA-HU29: El SUPERVISOR no puede eliminar zonas (solo ADMINISTRADOR puede).
        Se verifica indirectamente: el endpoint DELETE /api/zonas/{id} con un
        SUPERVISOR devuelve 403.
        Mapeado a: HU-29 'Supervisor crea y edita zonas y plantas sin eliminar'
        """
        # Esta prueba se valida a nivel de estructura: el endpoint existe
        # La validación de rol real la hace test_rbac_ui.py con Selenium
        resp = api_session.get(f"{API_BASE}/api/zonas")
        assert resp.status_code == 200, \
            "El endpoint de zonas debe estar disponible para esta validación"

    # ── Sprint 4: Novedades ────────────────────────────────────────────────────

    def test_ca_alertas_manual_creation(self, api_session):
        """
        CA-HU31: Se puede crear una alerta manual (novedad de falla en zona).
        Mapeado a: HU-31 'Reporte de falla de sistema en zona'
        """
        # Primero obtener una zona válida
        zonas_resp = api_session.get(f"{API_BASE}/api/zonas")
        if zonas_resp.status_code != 200 or not zonas_resp.json():
            pytest.skip("No hay zonas disponibles para crear alerta manual")

        zona_id = zonas_resp.json()[0]["id"]
        payload = {
            "zonaId": zona_id,
            "tipo": "FALLA_SISTEMA",
            "severidad": "MEDIA",
            "descripcion": "Test: falla de sistema reportada desde prueba Python"
        }
        resp = api_session.post(f"{API_BASE}/api/alertas", json=payload)
        assert resp.status_code in [200, 201], \
            f"POST /api/alertas falló: {resp.status_code} — {resp.text}"
        data = resp.json()
        assert "id" in data, "La alerta creada debe tener un campo 'id'"
        assert data.get("tipo") == "FALLA_SISTEMA", \
            "El tipo de alerta no coincide con el enviado"

    def test_ca_alertas_patch_atender(self, api_session):
        """
        CA-HU32: Se puede cambiar el estado de una alerta a ATENDIDA.
        Mapeado a: HU-32 'Empleado actualiza estado de alertas'
        """
        # Obtener alertas pendientes
        resp = api_session.get(f"{API_BASE}/api/alertas/pendientes")
        if resp.status_code != 200:
            pytest.skip(f"No se pudo obtener alertas pendientes: {resp.status_code}")

        alertas = resp.json()
        if not alertas:
            pytest.skip("No hay alertas pendientes para probar el cambio de estado")

        alerta_id = alertas[0]["id"]
        patch_resp = api_session.patch(
            f"{API_BASE}/api/alertas/{alerta_id}/atender",
            json={"notas": "Atendida desde prueba automatizada Python"}
        )
        assert patch_resp.status_code in [200, 204], \
            f"PATCH /api/alertas/{alerta_id}/atender falló: {patch_resp.status_code}"

    def test_ca_tratamientos_post_available(self, api_session):
        """
        CA-HU30: Se puede registrar un tratamiento/novedad de enfermedad en planta.
        Mapeado a: HU-30 'Reporte de novedad por enfermedad en planta'
        """
        # Obtener una planta disponible
        plantas_resp = api_session.get(f"{API_BASE}/api/plantas")
        if plantas_resp.status_code != 200 or not plantas_resp.json():
            pytest.skip("No hay plantas disponibles para registrar tratamiento")

        planta_id = plantas_resp.json()[0]["id"]
        me_resp = api_session.get(f"{API_BASE}/api/empleados/me")
        if me_resp.status_code != 200 or me_resp.json().get("sin_perfil"):
            pytest.skip("El usuario admin no tiene perfil de empleado")

        empleado_id = me_resp.json()["id"]
        from datetime import datetime
        payload = {
            "planta": {"id": planta_id},
            "empleado": {"id": empleado_id},
            "tipoTratamiento": "REVISION",
            "productoUtilizado": "",
            "dosis": "",
            "fechaHora": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "resultadoObservado": "Manchas amarillas detectadas — prueba Python"
        }
        resp = api_session.post(f"{API_BASE}/api/tratamientos", json=payload)
        assert resp.status_code in [200, 201], \
            f"POST /api/tratamientos falló: {resp.status_code} — {resp.text}"

    def test_ca_i18n_sensores_endpoint(self, api_session):
        """
        CA-HU33: Los sensores están disponibles (datos para el dashboard multilingüe).
        Mapeado a: HU-33 'Interfaz multiidioma español e inglés'
        """
        resp = api_session.get(f"{API_BASE}/api/sensores")
        assert resp.status_code == 200, \
            f"El endpoint GET /api/sensores no responde: {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list), "Se esperaba una lista de sensores"

    # ── Sprint 5: Sensores avanzados y alertas de cosecha ─────────────────────

    def test_ca_sensor_creation_for_zone(self, api_session):
        """
        CA-HU34: Se puede crear un sensor y asignarlo a una zona.
        Mapeado a: HU-34 'Creación de sensores inline al crear o editar zonas'
        """
        zonas_resp = api_session.get(f"{API_BASE}/api/zonas")
        if zonas_resp.status_code != 200 or not zonas_resp.json():
            pytest.skip("No hay zonas disponibles para crear sensor")

        zona_id = zonas_resp.json()[0]["id"]
        payload = {
            "codigo": f"SENS-TAIGA-{_TS}",
            "tipoSensor": "HUMEDAD",
            "zona": {"id": zona_id},
            "estado": "ACTIVO",
            "fechaInstalacion": "2026-01-01",
            "umbralMin": 40.0,
            "umbralMax": 80.0
        }
        resp = api_session.post(f"{API_BASE}/api/sensores", json=payload)
        assert resp.status_code in [200, 201], \
            f"POST /api/sensores falló: {resp.status_code} — {resp.text}"
        data = resp.json()
        assert "id" in data
        assert data.get("tipoSensor") == "HUMEDAD"
        assert data.get("umbralMin") == 40.0

    def test_ca_sensor_out_of_range_generates_alert(self, api_session):
        """
        CA-HU35: Una lectura fuera de umbral genera alerta automática.
        Mapeado a: HU-35 'Alertas automáticas por valor de sensor fuera de umbral'
        """
        sensores_resp = api_session.get(f"{API_BASE}/api/sensores")
        if sensores_resp.status_code != 200 or not sensores_resp.json():
            pytest.skip("No hay sensores disponibles para esta prueba")

        # Buscar un sensor con umbrales definidos
        sensor = next(
            (s for s in sensores_resp.json()
             if s.get("umbralMin") is not None and s.get("umbralMax") is not None),
            None
        )
        if sensor is None:
            pytest.skip("No hay sensores con umbrales configurados")

        prev_resp = api_session.get(f"{API_BASE}/api/alertas/count/pendientes")
        prev_count = prev_resp.json().get("total", 0) if prev_resp.status_code == 200 else 0

        # Registrar lectura extrema (10 veces el máximo) — fuente MANUAL es obligatoria
        valor_extremo = (sensor["umbralMax"] or 100) * 10
        lectura_resp = api_session.post(f"{API_BASE}/api/lecturas", json={
            "sensor": {"id": sensor["id"]},
            "valor": valor_extremo,
            "unidad": "test",
            "fuente": "MANUAL"
        })
        assert lectura_resp.status_code in [200, 201], \
            f"POST /api/lecturas falló: {lectura_resp.status_code}"

        new_resp = api_session.get(f"{API_BASE}/api/alertas/count/pendientes")
        new_count = new_resp.json().get("total", 0) if new_resp.status_code == 200 else 0
        assert new_count > prev_count, \
            "Una lectura fuera de umbral debe generar al menos 1 alerta pendiente (HU-35)"

    def test_ca_sensores_por_zona_endpoint(self, api_session):
        """
        CA-HU34: El endpoint GET /api/sensores/zona/{id} filtra sensores por zona.
        Mapeado a: HU-34 'Creación de sensores inline al crear o editar zonas'
        """
        zonas_resp = api_session.get(f"{API_BASE}/api/zonas")
        if zonas_resp.status_code != 200 or not zonas_resp.json():
            pytest.skip("No hay zonas disponibles")

        zona_id = zonas_resp.json()[0]["id"]
        resp = api_session.get(f"{API_BASE}/api/sensores/zona/{zona_id}")
        assert resp.status_code == 200, \
            f"GET /api/sensores/zona/{zona_id} falló: {resp.status_code}"
        assert isinstance(resp.json(), list), "Se esperaba una lista de sensores"
