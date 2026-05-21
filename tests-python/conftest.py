# GreenHouse Manager - Configuracion de pruebas Python
# Autores: [Nombres del equipo] | Fecha: 2026

import pytest
import requests

BASE_URL = "http://localhost:8080/api"

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def session():
    """Sesion HTTP compartida para todas las pruebas."""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s

@pytest.fixture
def zona_payload():
    return {
        "nombre": "Zona Test Python",
        "dimensionM2": 30.0,
        "capacidadMaxPlantas": 50,
        "estado": "ACTIVA",
        "ubicacion": "Sector Test"
    }
