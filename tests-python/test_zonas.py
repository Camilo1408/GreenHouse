# GreenHouse Manager - Pruebas de API: Zonas
# Autores: [Nombres del equipo] | Fecha: 2026

import pytest

BASE = "http://localhost:8080/api/zonas"


class TestZonasAPI:
    """Pruebas de integración para el endpoint /api/zonas (requiere auth)."""

    created_id = None

    def test_get_all_zonas_retorna_200(self, auth_session):
        """GET /api/zonas debe retornar 200."""
        r = auth_session.get(BASE)
        assert r.status_code == 200, f"Esperado 200, obtenido {r.status_code}"
        assert isinstance(r.json(), list)

    def test_create_zona_retorna_201(self, auth_session, zona_payload):
        """POST /api/zonas debe crear la zona y retornar 201."""
        r = auth_session.post(BASE, json=zona_payload)
        assert r.status_code == 201, f"Esperado 201, obtenido {r.status_code}: {r.text}"
        data = r.json()
        assert data["nombre"] == zona_payload["nombre"]
        assert data["estado"] == "ACTIVA"
        assert "id" in data
        TestZonasAPI.created_id = data["id"]

    def test_get_zona_por_id(self, auth_session):
        """GET /api/zonas/{id} debe retornar la zona creada."""
        assert TestZonasAPI.created_id is not None, "Necesita ejecutar test_create primero"
        r = auth_session.get(f"{BASE}/{TestZonasAPI.created_id}")
        assert r.status_code == 200
        assert r.json()["id"] == TestZonasAPI.created_id

    def test_update_zona(self, auth_session):
        """PUT /api/zonas/{id} debe actualizar la zona correctamente."""
        assert TestZonasAPI.created_id is not None
        updated = {
            "nombre": "Zona Test Actualizada",
            "estado": "EN_MANTENIMIENTO",
            "dimensionM2": 45.0,
            "capacidadMaxPlantas": 60,
            "ubicacion": "Sector Actualizado"
        }
        r = auth_session.put(f"{BASE}/{TestZonasAPI.created_id}", json=updated)
        assert r.status_code == 200
        assert r.json()["estado"] == "EN_MANTENIMIENTO"

    def test_delete_zona(self, auth_session):
        """DELETE /api/zonas/{id} debe eliminar la zona y retornar 204."""
        assert TestZonasAPI.created_id is not None
        r = auth_session.delete(f"{BASE}/{TestZonasAPI.created_id}")
        assert r.status_code == 204

    def test_get_zona_inexistente_retorna_404(self, auth_session):
        """GET /api/zonas/99999 debe retornar 404."""
        r = auth_session.get(f"{BASE}/99999")
        assert r.status_code == 404

    def test_create_zona_sin_nombre_retorna_400(self, auth_session):
        """POST con nombre vacío debe retornar 400."""
        payload = {"nombre": "", "estado": "ACTIVA"}
        r = auth_session.post(BASE, json=payload)
        assert r.status_code == 400
