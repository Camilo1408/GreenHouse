# GreenHouse Manager - Pruebas de API: Sensores
# Autores: [Nombres del equipo] | Fecha: 2026
# Cubre: HU-34 (Sensores por zona), HU-35 (Creacion de sensores al crear zona),
#        HU-36 (Generacion de alertas por lectura fuera de umbral)

import pytest
import time

BASE_SENSORES = "http://localhost:8080/api/sensores"
BASE_ZONAS    = "http://localhost:8080/api/zonas"
BASE_LECTURAS = "http://localhost:8080/api/lecturas"
BASE_ALERTAS  = "http://localhost:8080/api/alertas"

# Sufijo único por ejecución para evitar colisiones de nombres/códigos en DB
_TS = int(time.time())


class TestSensoresAPI:
    """Pruebas de integración para el endpoint /api/sensores."""

    zona_id       = None
    sensor_id     = None
    sensor_codigo = None

    def test_get_all_sensores_retorna_200(self, auth_session):
        """GET /api/sensores debe retornar 200 con lista de sensores."""
        r = auth_session.get(BASE_SENSORES)
        assert r.status_code == 200, f"Esperado 200, obtenido {r.status_code}"
        assert isinstance(r.json(), list), "Se esperaba una lista de sensores"

    def test_crear_zona_y_sensor_secuencialmente(self, auth_session, cleanup_registry):
        """
        HU-35 — Al crear una zona se pueden crear sensores para ella inmediatamente.
        Crea zona primero, luego sensor asignado a esa zona.
        """
        zona_resp = auth_session.post(BASE_ZONAS, json={
            "nombre":              f"Zona Sensores Test {_TS}",
            "estado":              "ACTIVA",
            "dimensionM2":         35.0,
            "capacidadMaxPlantas": 80,
            "ubicacion":           "Sector Prueba",
        })
        assert zona_resp.status_code == 201, \
            f"No se pudo crear zona de prueba: {zona_resp.status_code} — {zona_resp.text}"
        TestSensoresAPI.zona_id = zona_resp.json()["id"]
        # Zona registrada: ZonaService.delete() limpiará sensores en cascada
        cleanup_registry["zonas"].append(TestSensoresAPI.zona_id)

        codigo_sensor = f"SENS-TEST-{_TS}"
        sensor_resp = auth_session.post(BASE_SENSORES, json={
            "codigo":          codigo_sensor,
            "tipoSensor":      "TEMPERATURA",
            "zona":            {"id": TestSensoresAPI.zona_id},
            "estado":          "ACTIVO",
            "fechaInstalacion": "2026-01-01",
            "umbralMin":       15.0,
            "umbralMax":       30.0,
        })
        assert sensor_resp.status_code == 201, \
            f"No se pudo crear sensor: {sensor_resp.status_code} — {sensor_resp.text}"
        data = sensor_resp.json()
        TestSensoresAPI.sensor_id    = data["id"]
        TestSensoresAPI.sensor_codigo = codigo_sensor
        # Sensor NO se registra en cleanup_registry: la zona lo eliminará en cascada
        assert data["codigo"]    == codigo_sensor
        assert data["tipoSensor"] == "TEMPERATURA"
        assert data["umbralMin"]  == 15.0
        assert data["umbralMax"]  == 30.0

    def test_get_sensores_por_zona(self, auth_session):
        """
        HU-34 — GET /api/sensores/zona/{id} retorna los sensores de una zona.
        """
        if TestSensoresAPI.zona_id is None:
            pytest.skip("Necesita ejecutar test_crear_zona_y_sensor_secuencialmente primero")
        r = auth_session.get(f"{BASE_SENSORES}/zona/{TestSensoresAPI.zona_id}")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        codigos = [s["codigo"] for s in data]
        assert TestSensoresAPI.sensor_codigo in codigos, \
            "El sensor creado debe aparecer al listar por zona"

    def test_get_sensor_por_id(self, auth_session):
        """GET /api/sensores/{id} debe retornar el sensor correcto."""
        if TestSensoresAPI.sensor_id is None:
            pytest.skip("Necesita crear sensor primero")
        r = auth_session.get(f"{BASE_SENSORES}/{TestSensoresAPI.sensor_id}")
        assert r.status_code == 200
        assert r.json()["id"] == TestSensoresAPI.sensor_id

    def test_get_sensor_inexistente_retorna_404(self, auth_session):
        """GET /api/sensores/99999 debe retornar 404."""
        r = auth_session.get(f"{BASE_SENSORES}/99999")
        assert r.status_code == 404

    def test_lectura_dentro_umbral_no_genera_alerta(self, auth_session):
        """
        HU-36 — Una lectura dentro del umbral NO debe generar alerta nueva.
        """
        if TestSensoresAPI.sensor_id is None:
            pytest.skip("Necesita crear sensor primero")
        prev_count = _get_count_pendientes(auth_session)
        # 22°C está dentro del rango 15-30°C
        r = auth_session.post(BASE_LECTURAS, json={
            "sensor": {"id": TestSensoresAPI.sensor_id},
            "valor":  22.0,
            "unidad": "°C",
            "fuente": "MANUAL",
        })
        assert r.status_code == 201, \
            f"No se pudo registrar lectura: {r.status_code} — {r.text}"
        new_count = _get_count_pendientes(auth_session)
        assert new_count == prev_count, \
            f"Se generó alerta inesperada: antes={prev_count}, después={new_count}"

    def test_lectura_fuera_umbral_genera_alerta(self, auth_session, cleanup_registry):
        """
        HU-36 — Una lectura fuera del umbral DEBE generar una alerta PENDIENTE.
        La alerta generada se registra para descartarla en el teardown.
        """
        if TestSensoresAPI.sensor_id is None:
            pytest.skip("Necesita crear sensor primero")
        prev_count = _get_count_pendientes(auth_session)
        # 40°C > máximo 30°C → debe generar alerta
        r = auth_session.post(BASE_LECTURAS, json={
            "sensor": {"id": TestSensoresAPI.sensor_id},
            "valor":  40.0,
            "unidad": "°C",
            "fuente": "MANUAL",
        })
        assert r.status_code == 201, \
            f"No se pudo registrar lectura fuera de rango: {r.status_code}"
        new_count = _get_count_pendientes(auth_session)
        assert new_count > prev_count, \
            "Se esperaba que se generara al menos 1 alerta por lectura fuera de umbral"
        # Registrar la nueva alerta generada para descartarla en teardown
        _register_new_alertas(auth_session, prev_count, cleanup_registry)

    def test_update_sensor_umbral(self, auth_session):
        """PUT /api/sensores/{id} debe actualizar los umbrales del sensor."""
        if TestSensoresAPI.sensor_id is None:
            pytest.skip("Necesita crear sensor primero")
        r = auth_session.put(f"{BASE_SENSORES}/{TestSensoresAPI.sensor_id}", json={
            "codigo":          TestSensoresAPI.sensor_codigo,
            "tipoSensor":      "TEMPERATURA",
            "zona":            {"id": TestSensoresAPI.zona_id},
            "estado":          "ACTIVO",
            "fechaInstalacion": "2026-01-01",
            "umbralMin":       10.0,
            "umbralMax":       35.0,
        })
        assert r.status_code == 200, f"PUT falló: {r.status_code} — {r.text}"
        assert r.json()["umbralMin"] == 10.0
        assert r.json()["umbralMax"] == 35.0

    def test_delete_sensor_retorna_204(self, auth_session, cleanup_registry):
        """DELETE /api/sensores/{id} debe retornar 204 y limpiar sus dependencias."""
        if TestSensoresAPI.sensor_id is None:
            pytest.skip("Necesita crear sensor primero")
        r = auth_session.delete(f"{BASE_SENSORES}/{TestSensoresAPI.sensor_id}")
        assert r.status_code == 204, f"DELETE falló: {r.status_code}"
        # Sensor eliminado manualmente: la zona ya no necesita borrarlo en cascada
        TestSensoresAPI.sensor_id    = None
        TestSensoresAPI.sensor_codigo = None


class TestSensoresRBAC:
    """Verifica que los permisos RBAC se aplican correctamente a los sensores."""

    def test_empleado_no_puede_crear_sensor(self):
        """
        HU-27 RBAC — Un usuario EMPLEADO no puede crear sensores (403 o 401).
        """
        import requests
        session = requests.Session()
        resp = session.post(
            "http://localhost:8080/api/auth/login",
            data={"email": "empleado@greenhouse.com", "password": "Empleado1234"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code not in (200, 302):
            pytest.skip("Usuario empleado no disponible en el backend")

        r = session.post(BASE_SENSORES, json={
            "codigo":          "SENS-HACK-01",
            "tipoSensor":      "TEMPERATURA",
            "zona":            {"id": 1},
            "estado":          "ACTIVO",
            "fechaInstalacion": "2026-01-01",
        })
        assert r.status_code in (403, 401), \
            f"Un EMPLEADO NO debe poder crear sensores (esperado 403/401, obtenido {r.status_code})"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_count_pendientes(session) -> int:
    """Devuelve el número actual de alertas pendientes."""
    r = session.get(f"{BASE_ALERTAS}/count/pendientes")
    return r.json().get("total", 0) if r.status_code == 200 else 0


def _register_new_alertas(session, prev_count: int, cleanup_registry: dict):
    """Registra las alertas nuevas generadas desde prev_count para descartarlas al final."""
    r = session.get(f"{BASE_ALERTAS}/pendientes")
    if r.status_code != 200:
        return
    todas = r.json()
    # Las últimas alertas son las recién generadas (orden DESC por fecha)
    nuevas = todas[:max(0, len(todas) - prev_count)]
    for a in nuevas:
        aid = a.get("id")
        if aid and aid not in cleanup_registry["alertas"]:
            cleanup_registry["alertas"].append(aid)
