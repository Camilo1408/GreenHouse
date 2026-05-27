# GreenHouse Manager - Configuración de pruebas Python
# Autores: [Nombres del equipo] | Fecha: 2026
#
# cleanup_registry: fixture de sesión que registra todos los recursos
# creados durante las pruebas y los elimina al terminar la sesión.
# Orden de borrado: sensores → plantas → zonas → tipos_planta → alertas (descartar)

import pytest
import requests

BASE_URL       = "http://localhost:8080"
ADMIN_EMAIL    = "admin@greenhouse.com"
ADMIN_PASSWORD = "Admin1234"

API = {
    "zonas":        f"{BASE_URL}/api/zonas",
    "sensores":     f"{BASE_URL}/api/sensores",
    "plantas":      f"{BASE_URL}/api/plantas",
    "tipos_planta": f"{BASE_URL}/api/tipos-planta",
    "alertas":      f"{BASE_URL}/api/alertas",
    "tratamientos": f"{BASE_URL}/api/tratamientos",
}


# ── Fixtures de sesión ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def auth_session():
    """
    Sesión autenticada como administrador.
    Se crea una sola vez y se reutiliza en todos los tests.
    """
    s = requests.Session()
    resp = s.post(
        f"{BASE_URL}/api/auth/login",
        data={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        allow_redirects=True,
    )
    if resp.status_code not in (200, 302):
        pytest.skip(
            f"No se pudo autenticar en el backend: {resp.status_code} — "
            "¿está corriendo el backend en localhost:8080?"
        )
    return s


@pytest.fixture(scope="session")
def session(auth_session):
    """Alias de auth_session para compatibilidad."""
    return auth_session


@pytest.fixture(scope="session")
def cleanup_registry(auth_session):
    """
    Registro de todos los recursos creados durante la sesión de pruebas.
    Al finalizar la sesión se eliminan en el orden correcto para respetar
    las restricciones de FK:

      sensores → plantas → zonas → tipos_planta
      alertas → PATCH /descartar (no tienen endpoint DELETE)
      tratamientos → DELETE individual

    Uso en los tests:
        cleanup_registry["zonas"].append(zona_id)
        cleanup_registry["sensores"].append(sensor_id)
        ...
    """
    registry = {
        "tratamientos": [],
        "sensores":     [],
        "plantas":      [],
        "zonas":        [],
        "tipos_planta": [],
        "alertas":      [],   # se descartan, no se eliminan
    }

    yield registry

    # ── Teardown: borrar en orden de dependencias ──────────────────────────
    print("\n  🧹 Limpiando datos de prueba...")

    # Tratamientos primero (FK a planta)
    _delete_all(auth_session, API["tratamientos"], registry["tratamientos"], "tratamiento")

    # Sensores (SensorService.delete() ya limpia lecturas y alertas asociadas)
    _delete_all(auth_session, API["sensores"], registry["sensores"], "sensor")

    # Plantas (PlantaService.delete() ya limpia tratamientos y cosechas)
    _delete_all(auth_session, API["plantas"], registry["plantas"], "planta")

    # Zonas (ZonaService.delete() ya limpia sensores, plantas, turnos y alertas)
    _delete_all(auth_session, API["zonas"], registry["zonas"], "zona")

    # Tipos de planta
    _delete_all(auth_session, API["tipos_planta"], registry["tipos_planta"], "tipo_planta")

    # Alertas creadas manualmente → descartar (conservan historial)
    _discard_alertas(auth_session, registry["alertas"])

    print("  ✅ Limpieza completada.\n")


def _delete_all(session, base_endpoint, id_list, label):
    """Elimina todos los IDs registrados para un tipo de recurso."""
    for rid in reversed(id_list):
        try:
            r = session.delete(f"{base_endpoint}/{rid}")
            if r.status_code not in (200, 204, 404):
                print(f"  ⚠️  No se pudo borrar {label} id={rid}: {r.status_code}")
        except Exception as e:
            print(f"  ⚠️  Error borrando {label} id={rid}: {e}")


def _discard_alertas(session, id_list):
    """Descarta alertas PENDIENTE creadas durante las pruebas."""
    for aid in reversed(id_list):
        try:
            r = session.patch(f"{API['alertas']}/{aid}/descartar")
            if r.status_code not in (200, 204, 404):
                print(f"  ⚠️  No se pudo descartar alerta id={aid}: {r.status_code}")
        except Exception as e:
            print(f"  ⚠️  Error descartando alerta id={aid}: {e}")


# ── Fixtures de datos ─────────────────────────────────────────────────────────

@pytest.fixture
def zona_payload():
    """Payload base para crear una zona de prueba."""
    import time
    return {
        "nombre":              f"Zona Test Python {int(time.time())}",
        "dimensionM2":         30.0,
        "capacidadMaxPlantas": 50,
        "estado":              "ACTIVA",
        "ubicacion":           "Sector Test",
    }
