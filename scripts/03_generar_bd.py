"""
GreenHouse Manager — Generador de Base de Datos PostgreSQL
===========================================================
Lee docs/modelo-json.json y genera dos archivos SQL:

  docs/sql/
  ├── 01_schema.sql   — DDL: CREATE TABLE para cada entidad del modelo
  └── 02_seed.sql     — DML: INSERT con datos de prueba (los mismos del DataInitializer)

Equivale exactamente a lo que Hibernate genera con ddl-auto=create
y DataInitializer.java inserta al arrancar la aplicación.

NOTA: Script DEMOSTRATIVO — no ejecutar directamente.
"""

import json
from pathlib import Path
from datetime import date

ROOT   = Path(__file__).parent.parent
MODELO = ROOT / "docs" / "modelo-json.json"
SQL_DIR = ROOT / "docs" / "sql"

# ── Mapeo JSON Schema → tipo PostgreSQL ───────────────────────────────────────

def pg_type(pdef: dict) -> str:
    t   = pdef.get("type", "string")
    fmt = pdef.get("format", "")
    enums = pdef.get("enum", [])
    max_len = pdef.get("maxLength", 0)

    if enums:
        return "VARCHAR(100)"
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


def camel_a_snake(nombre: str) -> str:
    """camelCase → snake_case"""
    resultado = ""
    for c in nombre:
        if c.isupper():
            resultado += "_" + c.lower()
        else:
            resultado += c
    return resultado.lstrip("_")


# ── Generador de schema ────────────────────────────────────────────────────────

def generar_schema(modelo: dict) -> str:
    entidades = modelo.get("entities", {})
    lineas = [
        "-- ============================================================",
        "-- GreenHouse Manager — DDL Schema PostgreSQL",
        f"-- Generado desde docs/modelo-json.json  v{modelo.get('version','?')}",
        f"-- Fecha: {date.today()}",
        "-- Equivalente a Hibernate ddl-auto=create",
        "-- ============================================================\n",
        "-- Eliminar tablas en orden inverso de dependencias",
        "DROP TABLE IF EXISTS cosecha           CASCADE;",
        "DROP TABLE IF EXISTS tratamiento       CASCADE;",
        "DROP TABLE IF EXISTS lectura_sensor    CASCADE;",
        "DROP TABLE IF EXISTS alerta            CASCADE;",
        "DROP TABLE IF EXISTS turno             CASCADE;",
        "DROP TABLE IF EXISTS planta            CASCADE;",
        "DROP TABLE IF EXISTS sensor            CASCADE;",
        "DROP TABLE IF EXISTS verification_token CASCADE;",
        "DROP TABLE IF EXISTS empleado          CASCADE;",
        "DROP TABLE IF EXISTS tipo_planta       CASCADE;",
        "DROP TABLE IF EXISTS zona              CASCADE;",
        "",
    ]

    # Orden de creación (respeta FK)
    orden_creacion = [
        "Zona", "TipoPlanta", "Empleado",
        "Planta", "Sensor",
        "LecturaSensor", "Alerta", "Cosecha", "Tratamiento", "Turno"
    ]

    for nombre_clase in orden_creacion:
        entidad = entidades.get(nombre_clase)
        if not entidad:
            continue

        tabla = entidad.get("table", camel_a_snake(nombre_clase))
        props = entidad.get("properties", {})
        desc  = entidad.get("description", "")

        lineas.append(f"-- {desc}")
        lineas.append(f"CREATE TABLE {tabla} (")
        columnas = []

        for pname, pdef in props.items():
            col = camel_a_snake(pname)
            nullable = pname not in entidad.get("required", [])
            null_str = "NULL" if nullable else "NOT NULL"

            if pname == "id":
                columnas.append(f"    id BIGSERIAL PRIMARY KEY")
            elif "$ref" in pdef:
                ref_clase = pdef["$ref"].replace("#/entities/", "")
                ref_entidad = entidades.get(ref_clase, {})
                ref_tabla = ref_entidad.get("table", camel_a_snake(ref_clase))
                nullable_ref = pdef.get("nullable", False)
                null_ref = "NULL" if nullable_ref else "NOT NULL"
                columnas.append(
                    f"    {col}_id BIGINT {null_ref} REFERENCES {ref_tabla}(id)"
                )
            else:
                tipo = pg_type(pdef)
                columnas.append(f"    {col} {tipo} {null_str}")

        lineas.append(",\n".join(columnas))
        lineas.append(f");\n")

    # Tabla de tokens de verificación (no está en el modelo JSON pero existe en el backend)
    lineas += [
        "-- Token de verificación de correo (AuthService)",
        "CREATE TABLE verification_token (",
        "    id BIGSERIAL PRIMARY KEY,",
        "    token VARCHAR(255) NOT NULL UNIQUE,",
        "    empleado_id BIGINT NOT NULL REFERENCES empleado(id),",
        "    fecha_expiracion TIMESTAMP NOT NULL,",
        "    usado BOOLEAN NOT NULL DEFAULT FALSE",
        ");\n",
    ]

    # Índices para mejorar performance
    lineas += [
        "-- ── Índices ────────────────────────────────────────────────────",
        "CREATE UNIQUE INDEX idx_zona_nombre         ON zona(nombre);",
        "CREATE UNIQUE INDEX idx_empleado_email      ON empleado(email);",
        "CREATE UNIQUE INDEX idx_sensor_codigo       ON sensor(codigo);",
        "CREATE UNIQUE INDEX idx_planta_codigo       ON planta(codigo);",
        "CREATE INDEX        idx_lectura_sensor_id   ON lectura_sensor(sensor_id);",
        "CREATE INDEX        idx_alerta_estado       ON alerta(estado);",
        "CREATE INDEX        idx_alerta_zona_id      ON alerta(zona_id);",
        "CREATE INDEX        idx_cosecha_planta_id   ON cosecha(planta_id);",
        "CREATE INDEX        idx_tratamiento_planta  ON tratamiento(planta_id);",
        "",
    ]

    return "\n".join(lineas)


# ── Generador de seed ──────────────────────────────────────────────────────────

def generar_seed() -> str:
    """
    Genera los INSERT equivalentes a DataInitializer.java.
    Mismos datos de prueba que se insertan al arrancar la aplicación.
    """
    seed = [
        "-- ============================================================",
        "-- GreenHouse Manager — Seed Data",
        f"-- Generado desde docs/modelo-json.json",
        f"-- Fecha: {date.today()}",
        "-- Equivalente a DataInitializer.java (CommandLineRunner)",
        "-- ============================================================\n",

        "-- ── Empleados ──────────────────────────────────────────────",
        "-- NOTA: passwordHash generado con BCrypt (factor 10)",
        "-- Admin1234 → $2a$10$...",
        "INSERT INTO empleado (nombre_completo, email, password_hash, rol, estado, email_verificado, auth_provider, telefono, fecha_ingreso) VALUES",
        "  ('Carlos Administrador', 'admin@greenhouse.com',      '$2a$10$encryptedAdminHash',      'ADMINISTRADOR', 'ACTIVO', TRUE, 'LOCAL', '3001234567', '2024-01-15'),",
        "  ('María Supervisora',    'supervisor@greenhouse.com', '$2a$10$encryptedSuperHash',      'SUPERVISOR',    'ACTIVO', TRUE, 'LOCAL', '3109876543', '2024-03-01'),",
        "  ('Juan Pérez',           'juan@greenhouse.com',       '$2a$10$encryptedJuanHash',       'EMPLEADO',      'ACTIVO', TRUE, 'LOCAL', '3207654321', '2024-06-10'),",
        "  ('Ana Gómez',            'ana@greenhouse.com',        '$2a$10$encryptedAnaHash',        'EMPLEADO',      'ACTIVO', TRUE, 'LOCAL', '3154321098', '2025-01-20'),",
        "  ('Empleado Test',        'empleado@greenhouse.com',   '$2a$10$encryptedEmpleadoHash',   'EMPLEADO',      'ACTIVO', TRUE, 'LOCAL', '3001112233', '2025-06-01');",
        "",

        "-- ── Zonas ──────────────────────────────────────────────────",
        "INSERT INTO zona (nombre, dimension_m2, capacidad_max_plantas, estado, ubicacion) VALUES",
        "  ('Zona A - Tomates',   120.0, 200, 'ACTIVA',           'Sector Norte'),",
        "  ('Zona B - Lechugas',   80.0, 300, 'ACTIVA',           'Sector Centro'),",
        "  ('Zona C - Pimientos',  60.0, 150, 'ACTIVA',           'Sector Sur'),",
        "  ('Zona D - Hierbas',    40.0, 100, 'EN_MANTENIMIENTO', 'Sector Este');",
        "",

        "-- ── Tipos de planta ────────────────────────────────────────",
        "INSERT INTO tipo_planta (nombre, descripcion, temperatura_min, temperatura_max, humedad_min, humedad_max, ciclo_dias, cuidados_especiales) VALUES",
        "  ('Tomate Cherry',  'Tomate de fruto pequeño, ideal para ensaladas',   18.0, 28.0, 60.0, 80.0, 75, 'Tutorear cuando alcance 30cm. Podar brotes laterales.'),",
        "  ('Lechuga Romana', 'Lechuga de hojas alargadas, muy nutritiva',        12.0, 22.0, 50.0, 70.0, 45, 'Sensible al calor excesivo. Riego frecuente.'),",
        "  ('Pimiento Rojo',  'Pimiento dulce de color rojo',                     20.0, 30.0, 55.0, 75.0, 90, 'Requiere soporte cuando fructifica.'),",
        "  ('Albahaca',       'Hierba aromática de uso culinario',                16.0, 26.0, 40.0, 65.0, 30, 'Pinzar flores para prolongar producción de hojas.');",
        "",

        "-- ── Plantas (referencias a zona y tipo_planta por nombre → id) ──",
        "INSERT INTO planta (codigo, tipo_planta_id, zona_id, fecha_siembra, estado) VALUES",
        "  ('TOM-001', (SELECT id FROM tipo_planta WHERE nombre='Tomate Cherry'),  (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), '2026-03-01', 'LISTA_PARA_COSECHAR'),",
        "  ('TOM-002', (SELECT id FROM tipo_planta WHERE nombre='Tomate Cherry'),  (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), '2026-03-05', 'EN_CRECIMIENTO'),",
        "  ('TOM-003', (SELECT id FROM tipo_planta WHERE nombre='Tomate Cherry'),  (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), '2026-03-10', 'EN_CRECIMIENTO'),",
        "  ('TOM-004', (SELECT id FROM tipo_planta WHERE nombre='Tomate Cherry'),  (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), '2026-04-01', 'SEMBRADA'),",
        "  ('TOM-005', (SELECT id FROM tipo_planta WHERE nombre='Tomate Cherry'),  (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), '2026-01-15', 'COSECHADA'),",
        "  ('LEC-001', (SELECT id FROM tipo_planta WHERE nombre='Lechuga Romana'), (SELECT id FROM zona WHERE nombre LIKE 'Zona B%'), '2026-04-01', 'LISTA_PARA_COSECHAR'),",
        "  ('LEC-002', (SELECT id FROM tipo_planta WHERE nombre='Lechuga Romana'), (SELECT id FROM zona WHERE nombre LIKE 'Zona B%'), '2026-04-05', 'EN_CRECIMIENTO'),",
        "  ('PIM-001', (SELECT id FROM tipo_planta WHERE nombre='Pimiento Rojo'),  (SELECT id FROM zona WHERE nombre LIKE 'Zona C%'), '2026-02-01', 'LISTA_PARA_COSECHAR'),",
        "  ('ALB-001', (SELECT id FROM tipo_planta WHERE nombre='Albahaca'),       (SELECT id FROM zona WHERE nombre LIKE 'Zona B%'), '2026-04-20', 'EN_CRECIMIENTO'),",
        "  ('TOM-006', (SELECT id FROM tipo_planta WHERE nombre='Tomate Cherry'),  (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), '2025-12-01', 'MUERTA');",
        "",

        "-- ── Sensores ────────────────────────────────────────────────",
        "INSERT INTO sensor (codigo, tipo_sensor, zona_id, estado, fecha_instalacion, umbral_min, umbral_max) VALUES",
        "  ('SENS-TA-01',  'TEMPERATURA', (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), 'ACTIVO', '2024-01-01', 18.0,  28.0),",
        "  ('SENS-HA-01',  'HUMEDAD',     (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), 'ACTIVO', '2024-01-01', 60.0,  80.0),",
        "  ('SENS-PA-01',  'PH',          (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), 'ACTIVO', '2024-01-01',  5.5,   7.0),",
        "  ('SENS-TB-01',  'TEMPERATURA', (SELECT id FROM zona WHERE nombre LIKE 'Zona B%'), 'ACTIVO', '2024-01-01', 12.0,  22.0),",
        "  ('SENS-HB-01',  'HUMEDAD',     (SELECT id FROM zona WHERE nombre LIKE 'Zona B%'), 'ACTIVO', '2024-01-01', 50.0,  70.0),",
        "  ('SENS-TC-01',  'TEMPERATURA', (SELECT id FROM zona WHERE nombre LIKE 'Zona C%'), 'ACTIVO', '2024-01-01', 20.0,  30.0),",
        "  ('SENS-CO2-01', 'CO2',         (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), 'ACTIVO', '2024-01-01',400.0,1200.0);",
        "",

        "-- ── Lecturas (algunas fuera de umbral para generar alertas) ─",
        "INSERT INTO lectura_sensor (sensor_id, valor, unidad, fecha_hora, fuente) VALUES",
        "  ((SELECT id FROM sensor WHERE codigo='SENS-TA-01'), 24.5, '°C',  NOW() - INTERVAL '1 hour',   'MANUAL'),",
        "  ((SELECT id FROM sensor WHERE codigo='SENS-TA-01'), 31.0, '°C',  NOW() - INTERVAL '30 minutes','MANUAL'),  -- fuera de rango",
        "  ((SELECT id FROM sensor WHERE codigo='SENS-HA-01'), 72.0, '%',   NOW() - INTERVAL '1 hour',   'MANUAL'),",
        "  ((SELECT id FROM sensor WHERE codigo='SENS-PA-01'),  6.2, 'pH',  NOW() - INTERVAL '2 hours',  'MANUAL'),",
        "  ((SELECT id FROM sensor WHERE codigo='SENS-TB-01'), 18.0, '°C',  NOW() - INTERVAL '1 hour',   'MANUAL'),",
        "  ((SELECT id FROM sensor WHERE codigo='SENS-CO2-01'),850.0,'ppm', NOW() - INTERVAL '1 hour',   'MANUAL'),",
        "  ((SELECT id FROM sensor WHERE codigo='SENS-CO2-01'),1350.0,'ppm',NOW() - INTERVAL '45 minutes','MANUAL'); -- fuera de rango",
        "",

        "-- ── Alertas ─────────────────────────────────────────────────",
        "INSERT INTO alerta (tipo, severidad, zona_id, sensor_id, fecha_generacion, estado, descripcion, origen) VALUES",
        "  ('UMBRAL_TEMPERATURA','ALTA',   (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), (SELECT id FROM sensor WHERE codigo='SENS-TA-01'),   NOW()-INTERVAL '30 minutes', 'PENDIENTE', 'Sensor SENS-TA-01 en Zona A: temperatura 31.0°C supera el máximo de 28.0°C', 'AUTOMATICA'),",
        "  ('UMBRAL_CO2',        'MEDIA',  (SELECT id FROM zona WHERE nombre LIKE 'Zona A%'), (SELECT id FROM sensor WHERE codigo='SENS-CO2-01'),  NOW()-INTERVAL '45 minutes', 'PENDIENTE', 'Sensor SENS-CO2-01 en Zona A: CO2 1350ppm supera el máximo de 1200ppm',        'AUTOMATICA'),",
        "  ('UMBRAL_HUMEDAD',    'BAJA',   (SELECT id FROM zona WHERE nombre LIKE 'Zona B%'), (SELECT id FROM sensor WHERE codigo='SENS-HB-01'),   NOW()-INTERVAL '5 hours',    'ATENDIDA',  'Humedad baja en Zona B - corregida',                                            'AUTOMATICA');",
        "",

        "-- ── Cosechas ─────────────────────────────────────────────────",
        "INSERT INTO cosecha (planta_id, empleado_id, fecha_cosecha, peso_kg, calidad, destino, observaciones) VALUES",
        "  ((SELECT id FROM planta WHERE codigo='TOM-005'),(SELECT id FROM empleado WHERE email='juan@greenhouse.com'),  '2026-03-28', 4.2, 'A', 'VENTA', 'Excelente calidad. Frutos uniformes.'),",
        "  ((SELECT id FROM planta WHERE codigo='TOM-005'),(SELECT id FROM empleado WHERE email='juan@greenhouse.com'),  '2026-04-10', 3.8, 'B', 'VENTA', NULL),",
        "  ((SELECT id FROM planta WHERE codigo='TOM-005'),(SELECT id FROM empleado WHERE email='ana@greenhouse.com'),   '2026-05-02', 5.1, 'A', 'VENTA', 'Mejor cosecha del mes'),",
        "  ((SELECT id FROM planta WHERE codigo='TOM-005'),(SELECT id FROM empleado WHERE email='ana@greenhouse.com'),   '2026-05-08', 2.5, 'C', 'CONSUMO_INTERNO', 'Algunos frutos con manchas'),",
        "  ((SELECT id FROM planta WHERE codigo='TOM-005'),(SELECT id FROM empleado WHERE email='juan@greenhouse.com'),  '2026-05-14', 6.0, 'A', 'VENTA', NULL);",
        "",

        "-- ── Tratamientos ─────────────────────────────────────────────",
        "INSERT INTO tratamiento (planta_id, empleado_id, tipo_tratamiento, producto_utilizado, dosis, fecha_hora, resultado_observado) VALUES",
        "  ((SELECT id FROM planta WHERE codigo='TOM-001'),(SELECT id FROM empleado WHERE email='juan@greenhouse.com'),       'FERTILIZACION', 'Nitrofoska', '5g/L', NOW()-INTERVAL '7 days', 'Mejora visible en color de hojas'),",
        "  ((SELECT id FROM planta WHERE codigo='TOM-002'),(SELECT id FROM empleado WHERE email='juan@greenhouse.com'),       'PODA',          NULL,         NULL,   NOW()-INTERVAL '5 days', 'Brotes laterales eliminados'),",
        "  ((SELECT id FROM planta WHERE codigo='LEC-001'),(SELECT id FROM empleado WHERE email='ana@greenhouse.com'),        'RIEGO_MANUAL',  NULL,         NULL,   NOW()-INTERVAL '2 days', 'Suelo con humedad adecuada'),",
        "  ((SELECT id FROM planta WHERE codigo='PIM-001'),(SELECT id FROM empleado WHERE email='ana@greenhouse.com'),        'PESTICIDA',     'Neem oil',  '10mL/L',NOW()-INTERVAL '3 days', 'Plaga controlada');",
        "",

        "COMMIT;",
    ]

    return "\n".join(seed)


# ── Main ───────────────────────────────────────────────────────────────────────

def escribir(path: Path, contenido: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contenido, encoding="utf-8")
    print(f"  [BD] Creado: {path.relative_to(ROOT)}")


def main():
    print("\n" + "=" * 60)
    print("  GENERADOR BASE DE DATOS POSTGRESQL — GreenHouse Manager")
    print("=" * 60)

    modelo = json.loads(MODELO.read_text(encoding="utf-8"))

    schema = generar_schema(modelo)
    escribir(SQL_DIR / "01_schema.sql", schema)

    seed = generar_seed()
    escribir(SQL_DIR / "02_seed.sql", seed)

    # Generar también el docker-compose.yml de la BD
    docker_compose = f"""\
# GreenHouse Manager — PostgreSQL local (solo desarrollo)
# Fecha: {date.today()}
# Uso: docker-compose up -d

version: '3.8'
services:
  postgres:
    image: postgres:15
    container_name: greenhouse_db
    environment:
      POSTGRES_DB:       greenhouse_db
      POSTGRES_USER:     postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - greenhouse_data:/var/lib/postgresql/data
      - ./docs/sql/01_schema.sql:/docker-entrypoint-initdb.d/01_schema.sql
      - ./docs/sql/02_seed.sql:/docker-entrypoint-initdb.d/02_seed.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  greenhouse_data:
"""
    escribir(ROOT / "docker-compose.yml", docker_compose)

    print(f"\n  ✓ Archivos SQL generados en: docs/sql/")
    print(f"    01_schema.sql — {len(schema.splitlines())} líneas")
    print(f"    02_seed.sql   — {len(seed.splitlines())} líneas")
    print(f"\n  Para aplicar manualmente:")
    print(f"    psql -U postgres -d greenhouse_db -f docs/sql/01_schema.sql")
    print(f"    psql -U postgres -d greenhouse_db -f docs/sql/02_seed.sql")
    print(f"\n  Con Docker:")
    print(f"    docker-compose up -d")


if __name__ == "__main__":
    main()
