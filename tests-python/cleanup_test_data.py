#!/usr/bin/env python3
"""
GreenHouse Manager — Limpieza de datos de prueba generados por tests anteriores
================================================================================
Identifica y elimina todos los recursos que fueron creados por las pruebas
automáticas y que quedaron en la base de datos entre ejecuciones.

Uso:
    python cleanup_test_data.py

Requiere: backend corriendo en localhost:8080
"""

import sys
import requests
from pathlib import Path

BASE = "http://localhost:8080"

# Patrones de nombres/códigos que identifican datos de prueba
TEST_PATTERNS = {
    "zonas": [
        "Zona Test Python",
        "Zona Test Actualizada",
        "Zona Sensores Test",
        "Zona Plantas Test",
        "Zona Taiga Test",
    ],
    "sensores": [
        "SENS-TEST-",
        "SENS-TAIGA-",
        "SENS-HACK-",
    ],
    "tipos_planta": [
        "Tipo Test Python",
    ],
    "plantas": [
        "PLT-PY-",
    ],
}


def login():
    """Autenticación como administrador."""
    s = requests.Session()
    resp = s.post(
        f"{BASE}/api/auth/login",
        data={"email": "admin@greenhouse.com", "password": "Admin1234"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if resp.status_code not in (200, 302):
        print(f"❌ No se pudo autenticar: {resp.status_code}")
        print("   ¿Está corriendo el backend en localhost:8080?")
        sys.exit(1)
    print("✅ Autenticado como admin@greenhouse.com")
    return s


def matches_pattern(name: str, patterns: list) -> bool:
    """Verifica si un nombre coincide con alguno de los patrones de prueba."""
    name_lower = name.lower()
    return any(p.lower() in name_lower for p in patterns)


def cleanup_sensores(session, dry_run=False):
    """Elimina sensores de prueba (SensorService elimina lecturas y desasocia alertas)."""
    resp = session.get(f"{BASE}/api/sensores")
    if resp.status_code != 200:
        print(f"  ⚠️  No se pudo obtener sensores: {resp.status_code}")
        return 0
    deleted = 0
    for s in resp.json():
        if matches_pattern(s.get("codigo", ""), TEST_PATTERNS["sensores"]):
            if dry_run:
                print(f"  [DRY] Sensor: {s['codigo']} (id={s['id']})")
            else:
                r = session.delete(f"{BASE}/api/sensores/{s['id']}")
                if r.status_code in (200, 204):
                    print(f"  🗑️  Sensor eliminado: {s['codigo']} (id={s['id']})")
                    deleted += 1
                else:
                    print(f"  ⚠️  No se pudo eliminar sensor {s['codigo']}: {r.status_code} — {r.text[:80]}")
    return deleted


def cleanup_plantas(session, dry_run=False):
    """Elimina plantas de prueba (PlantaService elimina tratamientos y cosechas)."""
    resp = session.get(f"{BASE}/api/plantas")
    if resp.status_code != 200:
        print(f"  ⚠️  No se pudo obtener plantas: {resp.status_code}")
        return 0
    deleted = 0
    for p in resp.json():
        if matches_pattern(p.get("codigo", ""), TEST_PATTERNS["plantas"]):
            if dry_run:
                print(f"  [DRY] Planta: {p['codigo']} (id={p['id']})")
            else:
                r = session.delete(f"{BASE}/api/plantas/{p['id']}")
                if r.status_code in (200, 204):
                    print(f"  🗑️  Planta eliminada: {p['codigo']} (id={p['id']})")
                    deleted += 1
                else:
                    print(f"  ⚠️  No se pudo eliminar planta {p['codigo']}: {r.status_code} — {r.text[:80]}")
    return deleted


def cleanup_zonas(session, dry_run=False):
    """Elimina zonas de prueba (ZonaService elimina sensores, plantas, turnos y alertas)."""
    resp = session.get(f"{BASE}/api/zonas")
    if resp.status_code != 200:
        print(f"  ⚠️  No se pudo obtener zonas: {resp.status_code}")
        return 0
    deleted = 0
    for z in resp.json():
        if matches_pattern(z.get("nombre", ""), TEST_PATTERNS["zonas"]):
            if dry_run:
                print(f"  [DRY] Zona: {z['nombre']} (id={z['id']})")
            else:
                r = session.delete(f"{BASE}/api/zonas/{z['id']}")
                if r.status_code in (200, 204):
                    print(f"  🗑️  Zona eliminada: {z['nombre']} (id={z['id']})")
                    deleted += 1
                else:
                    print(f"  ⚠️  No se pudo eliminar zona '{z['nombre']}': {r.status_code} — {r.text[:80]}")
    return deleted


def cleanup_tipos_planta(session, dry_run=False):
    """Elimina tipos de planta de prueba."""
    resp = session.get(f"{BASE}/api/tipos-planta")
    if resp.status_code != 200:
        print(f"  ⚠️  No se pudo obtener tipos de planta: {resp.status_code}")
        return 0
    deleted = 0
    for t in resp.json():
        if matches_pattern(t.get("nombre", ""), TEST_PATTERNS["tipos_planta"]):
            if dry_run:
                print(f"  [DRY] TipoPlanta: {t['nombre']} (id={t['id']})")
            else:
                r = session.delete(f"{BASE}/api/tipos-planta/{t['id']}")
                if r.status_code in (200, 204):
                    print(f"  🗑️  TipoPlanta eliminado: {t['nombre']} (id={t['id']})")
                    deleted += 1
                else:
                    print(f"  ⚠️  No se pudo eliminar TipoPlanta '{t['nombre']}': {r.status_code} — {r.text[:80]}")
    return deleted


def cleanup_alertas_prueba(session, dry_run=False):
    """Descarta alertas generadas por las pruebas (FALLA_SISTEMA con descripción de prueba)."""
    resp = session.get(f"{BASE}/api/alertas/pendientes")
    if resp.status_code != 200:
        return 0
    test_markers = [
        "prueba", "test", "python", "taiga", "automatizada",
        "SENS-TEST", "SENS-TAIGA", "PLT-PY",
    ]
    discarded = 0
    for a in resp.json():
        desc = (a.get("descripcion") or "").lower()
        if any(m.lower() in desc for m in test_markers):
            if dry_run:
                print(f"  [DRY] Alerta: id={a['id']} tipo={a['tipo']} desc={a.get('descripcion','')[:60]}")
            else:
                r = session.patch(f"{BASE}/api/alertas/{a['id']}/descartar")
                if r.status_code in (200, 204):
                    print(f"  🗑️  Alerta descartada: id={a['id']} tipo={a['tipo']}")
                    discarded += 1
    return discarded


def main():
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    print()
    print("  🌿  GreenHouse Manager — Limpieza de datos de prueba")
    print("  " + "═" * 50)
    if dry_run:
        print("  ⚠️  MODO DRY-RUN: solo muestra qué se borraría, no borra nada")
    print()

    session = login()
    print()

    # Orden: sensores → plantas → zonas → tipos_planta → alertas
    # (el cascade de ZonaService ya borra sensores/plantas, pero los borramos
    #  primero individualmente para mayor seguridad)
    total = 0

    print("  ── Sensores de prueba ────────────────────────────────")
    total += cleanup_sensores(session, dry_run)

    print("  ── Plantas de prueba ─────────────────────────────────")
    total += cleanup_plantas(session, dry_run)

    print("  ── Zonas de prueba ───────────────────────────────────")
    total += cleanup_zonas(session, dry_run)

    print("  ── Tipos de planta de prueba ─────────────────────────")
    total += cleanup_tipos_planta(session, dry_run)

    print("  ── Alertas generadas por pruebas ─────────────────────")
    total += cleanup_alertas_prueba(session, dry_run)

    print()
    print("  " + "═" * 50)
    if dry_run:
        print(f"  📋 Se encontraron {total} recursos de prueba para limpiar.")
        print("     Ejecuta sin --dry-run para eliminarlos.")
    else:
        print(f"  ✅ Limpieza completada: {total} recursos eliminados/descartados.")
    print()


if __name__ == "__main__":
    main()
