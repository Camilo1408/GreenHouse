# GreenHouse Manager - Pruebas de API: Alertas
# Autores: [Nombres del equipo] | Fecha: 2026

import pytest

BASE = "http://localhost:8080/api/alertas"


class TestAlertasAPI:
    """Pruebas de integración para el endpoint /api/alertas (requiere auth)."""

    def test_get_all_alertas_retorna_200(self, auth_session):
        """GET /api/alertas debe retornar 200 con lista."""
        r = auth_session.get(BASE)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_alertas_pendientes_retorna_200(self, auth_session):
        """GET /api/alertas/pendientes debe retornar 200."""
        r = auth_session.get(f"{BASE}/pendientes")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for alerta in data:
            assert alerta["estado"] == "PENDIENTE"

    def test_count_pendientes_retorna_numero(self, auth_session):
        """GET /api/alertas/count/pendientes debe retornar objeto con campo 'total'."""
        r = auth_session.get(f"{BASE}/count/pendientes")
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert isinstance(data["total"], int)

    def test_atender_alerta_inexistente_retorna_404(self, auth_session):
        """PATCH /api/alertas/99999/atender con ID inexistente debe retornar 404."""
        r = auth_session.patch(f"{BASE}/99999/atender")
        assert r.status_code == 404

    def test_descartar_alerta_inexistente_retorna_404(self, auth_session):
        """PATCH /api/alertas/99999/descartar con ID inexistente debe retornar 404."""
        r = auth_session.patch(f"{BASE}/99999/descartar")
        assert r.status_code == 404
