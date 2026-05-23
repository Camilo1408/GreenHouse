# GreenHouse Manager - Pruebas de API: Plantas
# Autores: [Nombres del equipo] | Fecha: 2026

import pytest
from datetime import date

BASE_PLANTAS = "http://localhost:8080/api/plantas"
BASE_ZONAS   = "http://localhost:8080/api/zonas"
BASE_TIPOS   = "http://localhost:8080/api/tipos-planta"


class TestPlantasAPI:
    """Pruebas de integración para el endpoint /api/plantas (requiere auth)."""

    zona_id   = None
    tipo_id   = None
    planta_id = None

    def test_get_all_plantas_retorna_200(self, auth_session):
        """GET /api/plantas debe retornar 200 con lista."""
        r = auth_session.get(BASE_PLANTAS)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_apoyo_y_planta(self, auth_session):
        """Crea zona + tipo + planta usando auth. Retorna 201."""
        zona = auth_session.post(BASE_ZONAS, json={
            "nombre": "Zona Plantas Test", "estado": "ACTIVA",
            "dimensionM2": 20.0, "capacidadMaxPlantas": 30
        })
        tipo = auth_session.post(BASE_TIPOS, json={
            "nombre": "Tipo Test Python",
            "temperaturaMin": 15.0, "temperaturaMax": 30.0,
            "humedadMin": 40.0, "humedadMax": 80.0,
            "cicloDias": 60
        })

        if zona.status_code != 201 or tipo.status_code != 201:
            pytest.skip("No se pudo crear zona/tipo de apoyo")

        TestPlantasAPI.zona_id = zona.json()["id"]
        TestPlantasAPI.tipo_id = tipo.json()["id"]

        payload = {
            "codigo": "PLT-PY-001",
            "tipoPlanta": {"id": TestPlantasAPI.tipo_id},
            "zona": {"id": TestPlantasAPI.zona_id},
            "fechaSiembra": str(date.today()),
            "estado": "SEMBRADA"
        }
        r = auth_session.post(BASE_PLANTAS, json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["codigo"] == "PLT-PY-001"
        TestPlantasAPI.planta_id = data["id"]

    def test_get_plantas_por_estado(self, auth_session):
        """GET /api/plantas/estado/SEMBRADA debe retornar solo plantas sembradas."""
        r = auth_session.get(f"{BASE_PLANTAS}/estado/SEMBRADA")
        assert r.status_code == 200
        for p in r.json():
            assert p["estado"] == "SEMBRADA"

    def test_get_planta_inexistente_retorna_404(self, auth_session):
        """GET /api/plantas/99999 debe retornar 404."""
        r = auth_session.get(f"{BASE_PLANTAS}/99999")
        assert r.status_code == 404
