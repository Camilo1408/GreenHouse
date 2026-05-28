"""
GreenHouse Manager — Generador de Diccionario de Datos
=======================================================
Lee docs/modelo-json.json y genera docs/diccionario-datos.md
con la documentación detallada de cada tabla, columna, tipo,
restricciones, RBAC y relaciones.

El resultado es el diccionario de datos oficial del proyecto,
derivado directamente del modelo JSON único de verdad.

NOTA: Script DEMOSTRATIVO — no ejecutar directamente.
"""

import json
from pathlib import Path
from datetime import date

ROOT   = Path(__file__).parent.parent
MODELO = ROOT / "docs" / "modelo-json.json"
SALIDA = ROOT / "docs" / "diccionario-datos.md"


def camel_a_snake(nombre: str) -> str:
    resultado = ""
    for c in nombre:
        if c.isupper():
            resultado += "_" + c.lower()
        else:
            resultado += c
    return resultado.lstrip("_")


def pg_type(pdef: dict) -> str:
    t       = pdef.get("type", "string")
    fmt     = pdef.get("format", "")
    enums   = pdef.get("enum", [])
    max_len = pdef.get("maxLength", 0)
    if "$ref" in pdef:
        return "BIGINT (FK)"
    if enums:
        return f"VARCHAR(100) → ENUM({', '.join(enums)})"
    if t == "integer":
        return "BIGINT"
    if t == "number":
        return "DOUBLE PRECISION"
    if t == "boolean":
        return "BOOLEAN"
    if fmt == "date":
        return "DATE"
    if fmt == "date-time":
        return "TIMESTAMP"
    if fmt == "email":
        return "VARCHAR(255)"
    if max_len:
        return f"VARCHAR({max_len})"
    return "TEXT"


def main():
    print("\n" + "=" * 60)
    print("  GENERADOR DICCIONARIO DE DATOS — GreenHouse Manager")
    print("=" * 60)

    modelo    = json.loads(MODELO.read_text(encoding="utf-8"))
    entidades = modelo.get("entities", {})
    relaciones = modelo.get("relationships", {})
    roles      = modelo.get("roles", {})
    version    = modelo.get("version", "?")
    changelog  = modelo.get("changelog", [])

    lineas = [
        "# GreenHouse Manager — Diccionario de Datos",
        f"",
        f"**Versión del modelo:** {version}  |  **Fecha:** {date.today()}",
        f"**Fuente:** `docs/modelo-json.json`  (única fuente de verdad del sistema)",
        f"",
        "---",
        "",
        "## Changelog del modelo",
        "",
    ]
    for c in changelog:
        lineas.append(f"- {c}")

    lineas += [
        "",
        "---",
        "",
        "## Control de acceso por rol (RBAC)",
        "",
        "| Rol | Operaciones permitidas | Restricciones |",
        "|-----|----------------------|---------------|",
    ]
    for rol, rdef in roles.items():
        perms = ", ".join(rdef.get("permissions", []))
        denied = "; ".join(rdef.get("denied", ["-"]))
        lineas.append(f"| **{rol}** | {perms} | {denied} |")

    lineas += [
        "",
        "---",
        "",
        "## Relaciones entre entidades",
        "",
        "| Relación | Cardinalidad |",
        "|----------|-------------|",
    ]
    for rel, desc in relaciones.items():
        lineas.append(f"| `{rel}` | {desc} |")

    lineas += [
        "",
        "---",
        "",
        "## Tablas",
        "",
    ]

    # ── Una sección por entidad ────────────────────────────────────────────────
    for nombre_clase, entidad in entidades.items():
        tabla    = entidad.get("table", camel_a_snake(nombre_clase))
        desc     = entidad.get("description", "")
        props    = entidad.get("properties", {})
        required = entidad.get("required", [])
        rbac     = entidad.get("rbac", {})
        ejemplo  = (entidad.get("example")
                    or entidad.get("example_automatica")
                    or {})

        lineas += [
            f"### `{tabla}` — {nombre_clase}",
            f"",
            f"**Descripción:** {desc}",
            f"",
            "**Control de acceso:**",
        ]
        for operacion, roles_str in rbac.items():
            lineas.append(f"- `{operacion}`: {roles_str}")

        lineas += [
            "",
            "**Columnas:**",
            "",
            "| Columna | Tipo PostgreSQL | Nulo | Restricciones | Descripción |",
            "|---------|---------------|------|--------------|-------------|",
        ]

        for pname, pdef in props.items():
            col       = camel_a_snake(pname)
            tipo_pg   = pg_type(pdef)
            es_nulo   = "✓" if pname not in required else "✗"
            desc_col  = pdef.get("description", "")
            restricciones = []

            if pname == "id":
                restricciones.append("PK, AUTO")
                col = "id"
            if "$ref" in pdef:
                ref_clase  = pdef["$ref"].replace("#/entities/", "")
                ref_tabla  = entidades.get(ref_clase, {}).get("table", camel_a_snake(ref_clase))
                restricciones.append(f"FK → {ref_tabla}.id")
                col = camel_a_snake(pname) + "_id"
                desc_col = f"Referencia a {ref_clase}. {desc_col}"
            if pdef.get("maxLength"):
                restricciones.append(f"MAX({pdef['maxLength']})")
            if pdef.get("minimum") is not None:
                restricciones.append(f"MIN({pdef['minimum']})")
            if pdef.get("maximum") is not None:
                restricciones.append(f"MAX_VAL({pdef['maximum']})")
            if pdef.get("format") == "email":
                restricciones.append("UNIQUE")
            if pname in ("nombre", "codigo") and nombre_clase in ("Zona", "Sensor", "Planta"):
                restricciones.append("UNIQUE")
            if pdef.get("default") is not None:
                restricciones.append(f"DEFAULT({pdef['default']})")

            rest_str = ", ".join(restricciones) if restricciones else "—"
            lineas.append(f"| `{col}` | `{tipo_pg}` | {es_nulo} | {rest_str} | {desc_col} |")

        # Ejemplo de registro
        if ejemplo:
            lineas += [
                "",
                "**Ejemplo de registro:**",
                "```json",
                json.dumps(ejemplo, ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        else:
            lineas.append("")

        lineas.append("---")
        lineas.append("")

    # ── Tabla de tokens (no está en el modelo pero existe en BD) ───────────────
    lineas += [
        "### `verification_token` — VerificationToken",
        "",
        "**Descripción:** Token UUID para verificación de correo electrónico en registro local.",
        "Expira a las 24 horas. Una vez usado, el campo `usado` se marca como `TRUE`.",
        "",
        "| Columna | Tipo | Nulo | Restricciones | Descripción |",
        "|---------|------|------|--------------|-------------|",
        "| `id` | `BIGSERIAL` | ✗ | PK, AUTO | Identificador único |",
        "| `token` | `VARCHAR(255)` | ✗ | UNIQUE | UUID generado al registrarse |",
        "| `empleado_id` | `BIGINT` | ✗ | FK → empleado.id | Empleado propietario del token |",
        "| `fecha_expiracion` | `TIMESTAMP` | ✗ | — | Timestamp de expiración (registro + 24h) |",
        "| `usado` | `BOOLEAN` | ✗ | DEFAULT(false) | Marcado TRUE al verificar |",
        "",
        "---",
        "",
        "## Índices",
        "",
        "| Índice | Tabla | Columna | Tipo |",
        "|--------|-------|---------|------|",
        "| `idx_zona_nombre` | `zona` | `nombre` | UNIQUE |",
        "| `idx_empleado_email` | `empleado` | `email` | UNIQUE |",
        "| `idx_sensor_codigo` | `sensor` | `codigo` | UNIQUE |",
        "| `idx_planta_codigo` | `planta` | `codigo` | UNIQUE |",
        "| `idx_lectura_sensor_id` | `lectura_sensor` | `sensor_id` | INDEX |",
        "| `idx_alerta_estado` | `alerta` | `estado` | INDEX |",
        "| `idx_alerta_zona_id` | `alerta` | `zona_id` | INDEX |",
        "| `idx_cosecha_planta_id` | `cosecha` | `planta_id` | INDEX |",
        "| `idx_tratamiento_planta` | `tratamiento` | `planta_id` | INDEX |",
        "",
        "---",
        "",
        "## Procesos automáticos que modifican la BD",
        "",
        "| Proceso | Tabla afectada | Trigger | Frecuencia |",
        "|---------|---------------|---------|-----------|",
        "| Alerta por umbral sensor | `alerta` | POST /api/lecturas | Tiempo real |",
        "| Scheduler cosecha | `alerta`, `planta` | Cron `0 0 0/6 * * ?` | Cada 6 horas |",
        "| Auto-registro OAuth2 | `empleado` | Login con Google | Al primer login |",
        "| Token de verificación | `verification_token` | POST /api/auth/register | Al registrarse |",
        "| Seed inicial | Todas | Arranque app (CommandLineRunner) | Una sola vez |",
    ]

    contenido = "\n".join(lineas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(contenido, encoding="utf-8")
    print(f"\n  [DICT] Creado: {SALIDA.relative_to(ROOT)}")

    print(f"\n  ✓ Diccionario generado: docs/diccionario-datos.md")
    print(f"    Tablas documentadas: {len(entidades) + 1} (entidades + verification_token)")
    print(f"    Relaciones:          {len(relaciones)}")
    print(f"    Roles RBAC:          {len(roles)}")
    print(f"    Líneas generadas:    {len(lineas)}")


if __name__ == "__main__":
    main()
