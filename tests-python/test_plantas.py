# GreenHouse Manager - Pruebas de API: Plantas
# Autores: [Nombres del equipo] | Fecha: 2026

import pytest
import requests
from datetime import date

BASE_PLANTAS = "http://localhost:8080/api/plantas"
BASE_ZONAS   = "http://localhost:8080/api/zonas"
BASE_TIPOS   = "http://localhost:8080/api/tipos-planta"


class TestPlantasAPI:
    """Pruebas de integración para el endpoint /api/plantas."""

    zona_id = None
    tipo_id = None
    planta_id = None

    @classmethod
    def setup_class(cls):
        """Crea una zona y tipo de planta de apoyo para las pruebas."""
        zona = requests.post(BASE_ZONAS, json={
            "nombre": "Zona Plantas Test", "estado": "ACTIVA"
        })
        if zona.status_code == 201:
            cls.zona_id = zona.json()["id"]

        tipo = requests.post(BASE_TIPOS, json={
            "nombre": "Tipo Test Python",
            "temperaturaMin": 15.0, "temperaturaMax": 30.0,
            "humedadMin": 40.0, "humedadMax": 80.0,
            "cicloDias": 60
        })
        if tipo.status_code == 201:
            cls.tipo_id = tipo.json()["id"]

    def test_get_all_plantas_retorna_200(self):
        """GET /api/plantas debe retornar 200 con lista."""
        r = requests.get(BASE_PLANTAS)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_planta_retorna_201(self):
        """POST /api/plantas debe crear planta y retornar 201."""
        if not (self.zona_id and self.tipo_id):
            pytest.skip("Setup no pudo crear zona/tipo de apoyo")

        payload = {
            "codigo": "PLT-PY-001",
            "tipoPlanta": {"id": self.tipo_id},
            "zona": {"id": self.zona_id},
            "fechaSiembra": str(date.today()),
            "estado": "SEMBRADA"
        }
        r = requests.post(BASE_PLANTAS, json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["codigo"] == "PLT-PY-001"
        TestPlantasAPI.planta_id = data["id"]

    def test_get_plantas_por_estado(self):
        """GET /api/plantas/estado/SEMBRADA debe retornar solo plantas sembradas."""
        r = requests.get(f"{BASE_PLANTAS}/estado/SEMBRADA")
        assert r.status_code == 200
        for p in r.json():
            assert p["estado"] == "SEMBRADA"

    def test_get_planta_inexistente_retorna_404(self):
        """GET /api/plantas/99999 debe retornar 404."""
        r = requests.get(f"{BASE_PLANTAS}/99999")
        assert r.status_code == 404
