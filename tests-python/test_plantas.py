# GreenHouse Manager - Pruebas de API: Plantas
# Autores: [Nombres del equipo] | Fecha: 2026

import pytest
import time
from datetime import date

BASE_PLANTAS = "http://localhost:8080/api/plantas"
BASE_ZONAS   = "http://localhost:8080/api/zonas"
BASE_TIPOS   = "http://localhost:8080/api/tipos-planta"

_TS = int(time.time())


class TestPlantasAPI:
    """Pruebas de integración para el endpoint /api/plantas."""

    zona_id   = None
    tipo_id   = None
    planta_id = None

    def test_get_all_plantas_retorna_200(self, auth_session):
        """GET /api/plantas debe retornar 200 con lista."""
        r = auth_session.get(BASE_PLANTAS)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_apoyo_y_planta(self, auth_session, cleanup_registry):
        """Crea zona + tipo + planta. Registra todo para cleanup al final."""
        zona = auth_session.post(BASE_ZONAS, json={
            "nombre":              f"Zona Plantas Test {_TS}",
            "estado":              "ACTIVA",
            "dimensionM2":         20.0,
            "capacidadMaxPlantas": 30,
        })
        tipo = auth_session.post(BASE_TIPOS, json={
            "nombre":        f"Tipo Test Python {_TS}",
            "temperaturaMin": 15.0,
            "temperaturaMax": 30.0,
            "humedadMin":     40.0,
            "humedadMax":     80.0,
            "cicloDias":      60,
        })

        if zona.status_code != 201 or tipo.status_code != 201:
            # Limpiar lo que se pudo crear antes de saltar
            if zona.status_code == 201:
                cleanup_registry["zonas"].append(zona.json()["id"])
            if tipo.status_code == 201:
                cleanup_registry["tipos_planta"].append(tipo.json()["id"])
            pytest.skip(
                f"No se pudo crear zona ({zona.status_code}) "
                f"o tipo ({tipo.status_code}) de apoyo: "
                f"{zona.text} | {tipo.text}"
            )

        TestPlantasAPI.zona_id = zona.json()["id"]
        TestPlantasAPI.tipo_id = tipo.json()["id"]
        cleanup_registry["zonas"].append(TestPlantasAPI.zona_id)
        cleanup_registry["tipos_planta"].append(TestPlantasAPI.tipo_id)

        planta_codigo = f"PLT-PY-{_TS}"
        payload = {
            "codigo":     planta_codigo,
            "tipoPlanta": {"id": TestPlantasAPI.tipo_id},
            "zona":       {"id": TestPlantasAPI.zona_id},
            "fechaSiembra": str(date.today()),
            "estado":     "SEMBRADA",
        }
        r = auth_session.post(BASE_PLANTAS, json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["codigo"] == planta_codigo
        TestPlantasAPI.planta_id = data["id"]
        cleanup_registry["plantas"].append(TestPlantasAPI.planta_id)

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


class TestTipoPlantaInlineCreacion:
    """
    HU-16 — Pruebas de API para la creación inline de tipos de planta.
    Valida que POST /api/tipos-planta funciona correctamente con los datos
    mínimos que envía el sub-formulario inline del frontend.
    """

    tipo_id = None

    def test_crear_tipo_planta_inline_minimo(self, auth_session, cleanup_registry):
        """
        POST /api/tipos-planta con nombre + cicloDias debe retornar 201
        y devolver el tipo creado con id asignado.
        (Simula el envío mínimo del sub-form inline de PlantasPage)
        """
        payload = {
            "nombre":    f"Tipo Inline Test {_TS}",
            "cicloDias": 75,
        }
        r = auth_session.post(BASE_TIPOS, json=payload)
        assert r.status_code == 201, f"Se esperaba 201, se obtuvo {r.status_code}: {r.text}"
        data = r.json()
        assert "id" in data, "La respuesta debe incluir el id del tipo creado"
        assert data["nombre"] == payload["nombre"]
        assert data["cicloDias"] == payload["cicloDias"]
        TestTipoPlantaInlineCreacion.tipo_id = data["id"]
        cleanup_registry["tipos_planta"].append(data["id"])

    def test_crear_tipo_planta_inline_con_descripcion(self, auth_session, cleanup_registry):
        """
        POST /api/tipos-planta con nombre + cicloDias + descripcion debe retornar 201.
        (Simula el envío opcional con descripción desde el sub-form inline)
        """
        payload = {
            "nombre":      f"Tipo Desc Test {_TS}",
            "cicloDias":   45,
            "descripcion": "Variedad de prueba para CI",
        }
        r = auth_session.post(BASE_TIPOS, json=payload)
        assert r.status_code == 201, f"Se esperaba 201, se obtuvo {r.status_code}: {r.text}"
        data = r.json()
        assert data["nombre"] == payload["nombre"]
        cleanup_registry["tipos_planta"].append(data["id"])

    def test_tipo_creado_aparece_en_listado(self, auth_session):
        """
        Después de crear un tipo, GET /api/tipos-planta debe incluirlo en la lista.
        (Valida que el frontend puede auto-seleccionar el nuevo tipo tras invalidar la query)
        """
        if TestTipoPlantaInlineCreacion.tipo_id is None:
            pytest.skip("test_crear_tipo_planta_inline_minimo no se ejecutó o falló")
        r = auth_session.get(BASE_TIPOS)
        assert r.status_code == 200
        ids = [t["id"] for t in r.json()]
        assert TestTipoPlantaInlineCreacion.tipo_id in ids, \
            f"El tipo {TestTipoPlantaInlineCreacion.tipo_id} no aparece en GET /api/tipos-planta"
