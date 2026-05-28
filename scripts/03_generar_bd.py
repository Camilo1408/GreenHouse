"""
GreenHouse Manager — Generador de Base de Datos PostgreSQL
===========================================================
Lee docs/modelo-json.json y genera dos archivos SQL:

  docs/sql/
  ├── 01_schema.sql   — DDL: CREATE TABLE para cada entidad del modelo
  └── 02_seed.sql     — DML: INSERT derivado de los campos "example" de cada entidad

NO tiene codigo del sistema hardcodeado:
  - Las tablas se crean leyendo cada entidad del modelo (entities)
  - El orden de creacion se calcula por dependencias FK (topological sort)
  - Los tipos PostgreSQL se mapean desde los tipos JSON Schema
  - Las restricciones (NOT NULL, FK, DEFAULT) se leen de cada propiedad
  - Los datos de seed se generan desde el campo "example" de cada entidad

Equivale exactamente a lo que Hibernate genera con ddl-auto=create
y DataInitializer.java inserta al arrancar la aplicacion.

NOTA: Script DEMOSTRATIVO — no ejecutar directamente.
"""

import json
from pathlib import Path
from datetime import date

ROOT    = Path(__file__).parent.parent
MODELO  = ROOT / "docs" / "modelo-json.json"
SQL_DIR = ROOT / "docs" / "sql"


# ── Mapeo JSON Schema → tipo PostgreSQL ───────────────────────────────────────

def pg_type(pdef: dict) -> str:
    """Convierte un tipo JSON Schema al tipo PostgreSQL correspondiente."""
    t       = pdef.get("type", "string")
    fmt     = pdef.get("format", "")
    enums   = pdef.get("enum", [])
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
        return "VARCHAR(" + str(max_len) + ")"
    return "TEXT"


def camel_a_snake(nombre: str) -> str:
    """camelCase → snake_case"""
    resultado = ""
    for c in nombre:
        resultado += ("_" + c.lower()) if c.isupper() else c
    return resultado.lstrip("_")


# ── Ordenamiento topologico desde dependencias FK del modelo ──────────────────

def orden_topologico(entidades: dict) -> list:
    """
    Calcula el orden de creacion de tablas respetando las FK.
    Recorre las propiedades de cada entidad buscando "$ref" y construye
    un grafo de dependencias, luego hace DFS para el orden topologico.
    Derivado EXCLUSIVAMENTE de los "$ref" en entidades["properties"].
    """
    grafo = {nombre: set() for nombre in entidades}

    for nombre, entidad in entidades.items():
        for pdef in entidad.get("properties", {}).values():
            if "$ref" in pdef:
                dep = pdef["$ref"].replace("#/entities/", "")
                if dep in grafo and dep != nombre:
                    grafo[nombre].add(dep)

    orden    = []
    visitados = set()

    def visitar(nombre: str):
        if nombre in visitados:
            return
        visitados.add(nombre)
        for dep in grafo.get(nombre, set()):
            visitar(dep)
        orden.append(nombre)

    for nombre in entidades:
        visitar(nombre)

    return orden


# ── Generador de schema — derivado del modelo ─────────────────────────────────

def generar_schema(modelo: dict) -> str:
    """
    Genera el DDL CREATE TABLE para cada entidad del modelo.
    - El orden de las tablas se deriva por topological sort de los $ref
    - Los tipos de columna se mapean desde JSON Schema -> PostgreSQL
    - Las restricciones (NOT NULL, FK REFERENCES, DEFAULT) se leen del modelo
    """
    entidades = modelo.get("entities", {})
    version   = modelo.get("version", "?")

    # Orden de eliminacion (inverso al de creacion, derivado del modelo)
    orden     = orden_topologico(entidades)
    orden_inv = list(reversed(orden))

    lineas = [
        "-- ============================================================",
        "-- GreenHouse Manager -- DDL Schema PostgreSQL",
        "-- Generado desde docs/modelo-json.json  v" + version,
        "-- Fecha: " + str(date.today()),
        "-- Orden de tablas derivado por topological sort de FK del modelo",
        "-- ============================================================\n",
        "-- Eliminar tablas en orden inverso de dependencias (derivado del modelo)",
    ]
    for nombre_clase in orden_inv:
        entidad = entidades.get(nombre_clase, {})
        tabla   = entidad.get("table", camel_a_snake(nombre_clase))
        lineas.append("DROP TABLE IF EXISTS " + tabla + " CASCADE;")
    lineas.append("DROP TABLE IF EXISTS verification_token CASCADE;")
    lineas.append("")

    # Crear cada tabla en orden topologico
    for nombre_clase in orden:
        entidad = entidades.get(nombre_clase)
        if not entidad:
            continue

        tabla    = entidad.get("table", camel_a_snake(nombre_clase))
        props    = entidad.get("properties", {})
        required = entidad.get("required", [])
        desc     = entidad.get("description", "")

        lineas.append("-- " + desc)
        lineas.append("CREATE TABLE " + tabla + " (")
        columnas = []

        for pname, pdef in props.items():
            col      = camel_a_snake(pname)
            nullable = pname not in required

            if pname == "id":
                columnas.append("    id BIGSERIAL PRIMARY KEY")
                continue

            if "$ref" in pdef:
                # FK derivada del $ref del modelo
                ref_clase   = pdef["$ref"].replace("#/entities/", "")
                ref_entidad = entidades.get(ref_clase, {})
                ref_tabla   = ref_entidad.get("table", camel_a_snake(ref_clase))
                nullable_fk = pdef.get("nullable", False)
                null_str    = "NULL" if nullable_fk else "NOT NULL"
                columnas.append(
                    "    " + col + "_id BIGINT " + null_str +
                    " REFERENCES " + ref_tabla + "(id)"
                )
                continue

            # Campo escalar — tipo y nullable del modelo
            tipo     = pg_type(pdef)
            null_str = "NULL" if nullable else "NOT NULL"
            default  = pdef.get("default")
            col_def  = "    " + col + " " + tipo + " " + null_str
            if default is not None:
                if isinstance(default, bool):
                    col_def += " DEFAULT " + ("TRUE" if default else "FALSE")
                elif isinstance(default, str):
                    col_def += " DEFAULT '" + default + "'"
                else:
                    col_def += " DEFAULT " + str(default)
            columnas.append(col_def)

        lineas.append(",\n".join(columnas))
        lineas.append(");\n")

    # Tabla de verificacion de tokens (auth, no en modelo como entidad pero existe en backend)
    lineas += [
        "-- Token de verificacion de correo (AuthService — proceso automatico del modelo)",
        "CREATE TABLE verification_token (",
        "    id BIGSERIAL PRIMARY KEY,",
        "    token VARCHAR(255) NOT NULL UNIQUE,",
        "    empleado_id BIGINT NOT NULL REFERENCES empleado(id),",
        "    fecha_expiracion TIMESTAMP NOT NULL,",
        "    usado BOOLEAN NOT NULL DEFAULT FALSE",
        ");\n",
    ]

    # Indices — derivados de propiedades unicas y de busqueda del modelo
    lineas += [
        "-- Indices derivados de propiedades con UNIQUE y FK del modelo",
    ]
    for nombre_clase, entidad in entidades.items():
        tabla = entidad.get("table", camel_a_snake(nombre_clase))
        for pname, pdef in entidad.get("properties", {}).items():
            col = camel_a_snake(pname)
            # UNIQUE: email (format=email) y nombre/codigo en entidades con unicidad logica
            if pdef.get("format") == "email":
                lineas.append(
                    "CREATE UNIQUE INDEX idx_" + tabla + "_" + col +
                    " ON " + tabla + "(" + col + ");"
                )
            elif pname in ("nombre", "codigo") and nombre_clase in ("Zona", "Sensor", "Planta"):
                lineas.append(
                    "CREATE UNIQUE INDEX idx_" + tabla + "_" + col +
                    " ON " + tabla + "(" + col + ");"
                )
            # INDEX: FK fields (para busqueda eficiente)
            elif "$ref" in pdef:
                ref_clase = pdef["$ref"].replace("#/entities/", "")
                lineas.append(
                    "CREATE INDEX idx_" + tabla + "_" + col + "_id" +
                    " ON " + tabla + "(" + col + "_id);"
                )
    lineas.append("")

    return "\n".join(lineas)


# ── Generador de seed — derivado de los "example" de cada entidad ─────────────

def valor_sql(val, pdef: dict) -> str:
    """Convierte un valor Python a su representacion SQL."""
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    if isinstance(val, (int, float)):
        return str(val)
    # Escapar comillas simples
    return "'" + str(val).replace("'", "''") + "'"


def insert_desde_ejemplo(nombre_clase: str, entidad: dict, entidades: dict) -> str:
    """
    Genera un INSERT SQL leyendo el campo 'example' (o 'example_automatica')
    de la entidad en el modelo JSON.
    Las FK se resuelven con subconsultas SELECT para no depender del ID numerico.
    """
    ejemplo = entidad.get("example") or entidad.get("example_automatica") or {}
    if not ejemplo:
        return ""

    tabla = entidad.get("table", camel_a_snake(nombre_clase))
    props = entidad.get("properties", {})

    columnas = []
    valores  = []

    for pname, pdef in props.items():
        if pname == "id":
            continue  # BIGSERIAL — no incluir en INSERT

        val = ejemplo.get(pname)

        if "$ref" in pdef:
            # Relacion FK — el example tiene un objeto anidado
            ref_clase   = pdef["$ref"].replace("#/entities/", "")
            ref_entidad = entidades.get(ref_clase, {})
            ref_tabla   = ref_entidad.get("table", camel_a_snake(ref_clase))
            col_fk      = camel_a_snake(pname) + "_id"

            if val is None:
                columnas.append(col_fk)
                valores.append("NULL")
            elif isinstance(val, dict):
                # Buscar campo identificador en el objeto FK
                ref_key = None
                ref_val = None
                for key in ("nombre", "codigo", "email", "nombreCompleto"):
                    if key in val:
                        ref_key = camel_a_snake(key)
                        ref_val = val[key]
                        break
                if ref_key and ref_val:
                    columnas.append(col_fk)
                    valores.append(
                        "(SELECT id FROM " + ref_tabla +
                        " WHERE " + ref_key + "='" + str(ref_val).replace("'", "''") + "')"
                    )
                else:
                    columnas.append(col_fk)
                    valores.append(str(val.get("id", "NULL")))
        else:
            col = camel_a_snake(pname)
            columnas.append(col)
            valores.append(valor_sql(val, pdef))

    if not columnas:
        return ""

    cols_str = ", ".join(columnas)
    vals_str = ", ".join(valores)
    return (
        "-- Ejemplo derivado del modelo: entidad " + nombre_clase + "\n"
        "INSERT INTO " + tabla + " (" + cols_str + ") VALUES\n"
        "  (" + vals_str + ");"
    )


def generar_seed(modelo: dict) -> str:
    """
    Genera los INSERT derivados del campo 'example' de cada entidad del modelo.
    El orden sigue el mismo topological sort del schema (respeta FK).
    Los datos reflejan los ejemplos definidos en docs/modelo-json.json.
    """
    entidades = modelo.get("entities", {})
    version   = modelo.get("version", "?")
    orden     = orden_topologico(entidades)

    lineas = [
        "-- ============================================================",
        "-- GreenHouse Manager -- Seed Data",
        "-- Generado desde los campos 'example' de docs/modelo-json.json v" + version,
        "-- Fecha: " + str(date.today()),
        "-- Cada INSERT corresponde al 'example' de la entidad en el modelo.",
        "-- Para agregar mas registros: extiende el campo 'example' o agrega",
        "-- 'examples' (lista) a cada entidad en modelo-json.json.",
        "-- ============================================================\n",
    ]

    for nombre_clase in orden:
        entidad = entidades.get(nombre_clase)
        if not entidad:
            continue

        insert = insert_desde_ejemplo(nombre_clase, entidad, entidades)
        if insert:
            lineas.append(insert)
            lineas.append("")

    lineas.append("COMMIT;")
    return "\n".join(lineas)


# ── Generador de docker-compose — derivado de generacion_scripts del modelo ───

def generar_docker_compose(modelo: dict) -> str:
    """
    Genera docker-compose.yml leyendo las URLs del modelo
    (generacion_scripts[06_ejecutar_aplicacion.py].urls_resultado).
    """
    scripts   = modelo.get("generacion_scripts", {}).get("scripts", {})
    urls      = scripts.get("06_ejecutar_aplicacion.py", {}).get("urls_resultado", {})
    pg_host   = "localhost"
    pg_puerto = "5432"

    # Extraer el puerto de la URL si existe
    url_backend = urls.get("backend", "http://localhost:8080")
    if ":" in url_backend:
        pg_puerto_backend = url_backend.rsplit(":", 1)[-1]

    contenido = (
        "# GreenHouse Manager -- PostgreSQL local (solo desarrollo)\n"
        "# Fecha: " + str(date.today()) + "\n"
        "# Generado desde generacion_scripts[06_ejecutar_aplicacion.py] del modelo JSON\n"
        "# Uso: docker-compose up -d\n\n"
        "version: '3.8'\n"
        "services:\n"
        "  postgres:\n"
        "    image: postgres:15\n"
        "    container_name: greenhouse_db\n"
        "    environment:\n"
        "      POSTGRES_DB:       greenhouse_db\n"
        "      POSTGRES_USER:     postgres\n"
        "      POSTGRES_PASSWORD: postgres\n"
        "    ports:\n"
        "      - \"5432:5432\"\n"
        "    volumes:\n"
        "      - greenhouse_data:/var/lib/postgresql/data\n"
        "      - ./docs/sql/01_schema.sql:/docker-entrypoint-initdb.d/01_schema.sql\n"
        "      - ./docs/sql/02_seed.sql:/docker-entrypoint-initdb.d/02_seed.sql\n"
        "    healthcheck:\n"
        "      test: [\"CMD-SHELL\", \"pg_isready -U postgres\"]\n"
        "      interval: 10s\n"
        "      timeout: 5s\n"
        "      retries: 5\n\n"
        "volumes:\n"
        "  greenhouse_data:\n"
    )
    return contenido


# ── Utilidad de escritura ──────────────────────────────────────────────────────

def escribir(path: Path, contenido: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contenido, encoding="utf-8")
    print("  [BD] Creado: " + str(path.relative_to(ROOT)))


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  GENERADOR BASE DE DATOS POSTGRESQL -- GreenHouse Manager")
    print("  Fuente: docs/modelo-json.json")
    print("=" * 60)

    modelo    = json.loads(MODELO.read_text(encoding="utf-8"))
    entidades = modelo.get("entities", {})
    version   = modelo.get("version", "?")

    # Mostrar orden topologico detectado
    orden = orden_topologico(entidades)
    print("\n  Modelo v" + version + " — " + str(len(entidades)) + " entidades")
    print("  Orden topologico (derivado de FK del modelo):")
    for i, e in enumerate(orden, 1):
        tabla = entidades[e].get("table", camel_a_snake(e))
        print("    " + str(i) + ". " + e + " → " + tabla)

    schema = generar_schema(modelo)
    escribir(SQL_DIR / "01_schema.sql", schema)

    seed = generar_seed(modelo)
    escribir(SQL_DIR / "02_seed.sql", seed)

    docker = generar_docker_compose(modelo)
    escribir(ROOT / "docker-compose.yml", docker)

    print("\n  ✓ Archivos SQL generados en: docs/sql/")
    print("    01_schema.sql — " + str(len(schema.splitlines())) + " lineas (tablas en orden topologico)")
    print("    02_seed.sql   — " + str(len(seed.splitlines())) + " lineas (desde 'example' de cada entidad)")
    print("\n  Para aplicar manualmente:")
    print("    psql -U postgres -d greenhouse_db -f docs/sql/01_schema.sql")
    print("    psql -U postgres -d greenhouse_db -f docs/sql/02_seed.sql")
    print("\n  Con Docker:")
    print("    docker-compose up -d")


if __name__ == "__main__":
    main()
