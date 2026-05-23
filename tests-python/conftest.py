# GreenHouse Manager - Configuracion de pruebas Python
# Autores: [Nombres del equipo] | Fecha: 2026

import pytest
import requests

BASE_URL  = "http://localhost:8080"
ADMIN_EMAIL    = "admin@greenhouse.com"
ADMIN_PASSWORD = "Admin1234"


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
        pytest.skip(f"No se pudo autenticar en el backend: {resp.status_code} — ¿está corriendo el backend?")
    return s


@pytest.fixture(scope="session")
def session(auth_session):
    """Alias de auth_session para compatibilidad con tests existentes."""
    return auth_session


@pytest.fixture
def zona_payload():
    return {
        "nombre": "Zona Test Python",
        "dimensionM2": 30.0,
        "capacidadMaxPlantas": 50,
        "estado": "ACTIVA",
        "ubicacion": "Sector Test"
    }
