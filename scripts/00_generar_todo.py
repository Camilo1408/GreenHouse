"""
GreenHouse Manager — Orquestador principal de generación
=========================================================
Ejecuta en orden todos los scripts de generación del proyecto.
Lee docs/modelo-json.json y produce:
  1. Backend  Spring Boot  (greenhouse-backend/)
  2. Frontend React + Vite (greenhouse-frontend/)
  3. Base de datos         (schema SQL + seed SQL)
  4. Documentación técnica (docs/)
  5. Diccionario de datos  (docs/diccionario-datos.md)
  6. Arranque de la app    (instrucciones + proceso)

USO:
    python scripts/00_generar_todo.py

NOTA: Este script es DEMOSTRATIVO. Muestra cómo el proyecto
      completo se puede regenerar desde el modelo-json.json.
      No ejecutar en producción sin revisar cada sub-script.
"""

import subprocess
import sys
import time
from pathlib import Path

# ── Raíz del proyecto ──────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent

SCRIPTS = [
    ("01_generar_backend.py",         "Backend  Spring Boot (entidades, repos, servicios, controladores)"),
    ("02_generar_frontend.py",        "Frontend React + Vite (pages, services, types, i18n)"),
    ("03_generar_bd.py",              "Base de datos PostgreSQL (schema DDL + seed data)"),
    ("04_generar_documentacion.py",   "Documentación técnica (Swagger, JavaDoc, README)"),
    ("05_generar_diccionario_datos.py","Diccionario de datos desde modelo-json.json"),
    ("06_ejecutar_aplicacion.py",     "Arranque de la aplicación (backend + frontend + BD)"),
]

SEPARADOR = "=" * 70


def ejecutar_script(nombre: str, descripcion: str) -> bool:
    script_path = ROOT / "scripts" / nombre
    print(f"\n{SEPARADOR}")
    print(f"  ► {descripcion}")
    print(f"    Archivo: scripts/{nombre}")
    print(SEPARADOR)

    resultado = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=False,
        text=True,
    )
    if resultado.returncode != 0:
        print(f"\n  ✗ Error en {nombre} (código {resultado.returncode})")
        return False

    print(f"\n  ✓ {nombre} completado.")
    return True


def main():
    inicio = time.time()
    print(f"\n{'#' * 70}")
    print("  GREENHOUSE MANAGER — GENERACIÓN COMPLETA DEL PROYECTO")
    print(f"  Modelo fuente: docs/modelo-json.json  v3.0.0")
    print(f"  Fecha: 2026")
    print(f"{'#' * 70}")

    # Verificar que el modelo existe
    modelo = ROOT / "docs" / "modelo-json.json"
    if not modelo.exists():
        print(f"\n  ✗ No se encontró el modelo: {modelo}")
        print("    Asegúrate de estar en la raíz del proyecto.")
        sys.exit(1)

    print(f"\n  Modelo encontrado: {modelo}")
    print(f"  Scripts a ejecutar: {len(SCRIPTS)}\n")

    exitosos = 0
    fallidos  = []

    for nombre, descripcion in SCRIPTS:
        ok = ejecutar_script(nombre, descripcion)
        if ok:
            exitosos += 1
        else:
            fallidos.append(nombre)

    # ── Resumen final ──────────────────────────────────────────────────────────
    duracion = time.time() - inicio
    print(f"\n{'#' * 70}")
    print(f"  RESUMEN DE GENERACIÓN")
    print(f"{'#' * 70}")
    print(f"  ✓ Exitosos : {exitosos}/{len(SCRIPTS)}")
    print(f"  ✗ Fallidos : {len(fallidos)}")
    if fallidos:
        for f in fallidos:
            print(f"      - {f}")
    print(f"  ⏱ Duración : {duracion:.1f}s")
    print(f"\n  Proyecto generado en: {ROOT}")
    print(f"{'#' * 70}\n")

    sys.exit(0 if not fallidos else 1)


if __name__ == "__main__":
    main()
