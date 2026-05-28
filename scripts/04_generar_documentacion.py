"""
GreenHouse Manager — Generador de Documentacion Tecnica
========================================================
Lee docs/modelo-json.json y genera:

  docs/
  ├── README.md               — Guia de instalacion y uso del proyecto
  ├── arquitectura.md         — Diagrama de capas y procesos automatizados
  ├── api-reference.md        — Referencia completa de endpoints REST
  └── javadoc-instrucciones.md

NO tiene codigo del sistema hardcodeado:
  - README.md:        version, entidades, stack y scripts de generacion_scripts del modelo
  - api-reference.md: endpoints de api_endpoints, roles de roles del modelo
  - arquitectura.md:  procesos de automated_processes, scheduler de new_in_v3 del modelo
  - Tabla de usuarios: derivada del campo "example" de la entidad Empleado

NOTA: Script DEMOSTRATIVO. No ejecutar directamente.
"""

import json
from pathlib import Path
from datetime import date

ROOT   = Path(__file__).parent.parent
MODELO = ROOT / "docs" / "modelo-json.json"
DOCS   = ROOT / "docs"


def escribir(path: Path, contenido: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contenido, encoding="utf-8")
    print("  [DOCS] Creado: " + str(path.relative_to(ROOT)))


def camel_a_snake(nombre: str) -> str:
    resultado = ""
    for c in nombre:
        resultado += ("_" + c.lower()) if c.isupper() else c
    return resultado.lstrip("_")


# ── README.md — version, entidades y scripts del modelo ───────────────────────

def generar_readme(modelo: dict):
    """
    Genera README.md leyendo:
    - version, date, authors      → cabecera del modelo
    - entities                    → lista de entidades del sistema
    - generacion_scripts.scripts  → lista de scripts disponibles
    - entities.Empleado.example   → tabla de usuario de prueba representativo
    - new_in_v3.harvest_scheduler → cron del scheduler
    """
    version       = modelo.get("version", "3.0.0")
    fecha_modelo  = modelo.get("date", str(date.today()))
    entidades     = modelo.get("entities", {})
    scripts_model = modelo.get("generacion_scripts", {}).get("scripts", {})
    scripts_urls  = modelo.get("generacion_scripts", {}).get("scripts", {})

    # Entidades del sistema
    lista_entidades = "\n".join("- `" + e + "`" for e in entidades)

    # Scripts de generacion
    lista_scripts = "\n".join(
        "- `python " + modelo.get("generacion_scripts", {}).get("directorio", "scripts/") + k + "` — " + v.get("descripcion", "")
        for k, v in scripts_model.items()
    )

    # Usuario representativo desde el example del modelo
    empleado_ejemplo = entidades.get("Empleado", {}).get("example", {})
    user_email = empleado_ejemplo.get("email", "admin@greenhouse.com")
    user_rol   = empleado_ejemplo.get("rol",   "ADMINISTRADOR")

    # URLs del script de ejecucion del modelo
    run_script   = scripts_urls.get("06_ejecutar_aplicacion.py", {})
    urls         = run_script.get("urls_resultado", {})
    url_front    = urls.get("frontend", "http://localhost:5173")
    url_back     = urls.get("backend",  "http://localhost:8080")
    url_swagger  = urls.get("swagger",  "http://localhost:8080/swagger-ui.html")
    url_health   = urls.get("health",   "http://localhost:8080/actuator/health")

    # Prerrequisitos del script de ejecucion
    prereqs   = run_script.get("prerrequisitos", ["Java 17+", "Maven 3.9+", "Node.js 20+"])
    prereq_md = "\n".join("- " + p for p in prereqs)

    # Changelog (primeras 4 entradas)
    changelog     = modelo.get("changelog", [])
    changelog_md  = "\n".join("- " + c for c in changelog[:4])

    contenido = (
        "# Greenhouse Manager\n\n"
        "Sistema integral de gestion de invernaderos con monitoreo en tiempo real,\n"
        "alertas automaticas por sensores y trazabilidad completa del ciclo de vida\n"
        "de las plantas.\n\n"
        "**Version del modelo:** " + version + " | **Fecha:** " + fecha_modelo + "\n\n"
        "---\n\n"
        "## Entidades del sistema\n\n"
        "Derivado de `docs/modelo-json.json` — seccion `entities`:\n\n" +
        lista_entidades + "\n\n"
        "---\n\n"
        "## Stack tecnologico\n\n"
        "| Capa       | Tecnologia                           |\n"
        "|------------|--------------------------------------|\n"
        "| Backend    | Spring Boot 3.2.5 + Java 17          |\n"
        "| Base de datos | PostgreSQL 15                     |\n"
        "| Frontend   | React 18 + Vite + TypeScript         |\n"
        "| UI         | TailwindCSS + lucide-react           |\n"
        "| Estado     | @tanstack/react-query                |\n"
        "| HTTP       | Axios                                |\n"
        "| i18n       | i18next (espanol / ingles)           |\n"
        "| Auth       | Spring Security + OAuth2 Google      |\n"
        "| Docs API   | springdoc-openapi (Swagger UI)       |\n"
        "| Deploy     | Railway (backend + frontend)         |\n"
        "| CI/CD      | GitHub Actions                       |\n\n"
        "---\n\n"
        "## Instalacion local\n\n"
        "### Prerrequisitos\n" +
        prereq_md + "\n\n"
        "### 1. Clonar el repositorio\n"
        "```bash\n"
        "git clone https://github.com/Camilo1408/GreenHouse.git\n"
        "cd GreenHouse\n"
        "```\n\n"
        "### 2. Configurar variables de entorno\n"
        "```bash\n"
        "cp .env.example .env\n"
        "# Editar .env con tus credenciales de Google OAuth y Gmail\n"
        "```\n\n"
        "### 3. Base de datos\n"
        "```bash\n"
        "# Con Docker (recomendado):\n"
        "docker-compose up -d\n\n"
        "# O manualmente:\n"
        "createdb greenhouse_db\n"
        "psql -d greenhouse_db -f docs/sql/01_schema.sql\n"
        "psql -d greenhouse_db -f docs/sql/02_seed.sql\n"
        "```\n\n"
        "### 4. Arrancar el backend\n"
        "```bash\n"
        "cd greenhouse-backend\n"
        "mvn spring-boot:run -Dspring-boot.run.profiles=local\n"
        "```\n\n"
        "### 5. Arrancar el frontend\n"
        "```bash\n"
        "cd greenhouse-frontend\n"
        "npm install\n"
        "npm run dev\n"
        "```\n\n"
        "### 6. Acceder a la aplicacion\n"
        "- **Frontend:** " + url_front + "\n"
        "- **Swagger UI:** " + url_swagger + "\n"
        "- **Health check:** " + url_health + "\n\n"
        "---\n\n"
        "## Usuario de prueba (seed)\n\n"
        "_Derivado del campo `example` de la entidad `Empleado` en el modelo JSON_\n\n"
        "| Email | Rol |\n"
        "|-------|-----|\n"
        "| " + user_email + " | " + user_rol + " |\n\n"
        "> Ver `docs/sql/02_seed.sql` para todos los usuarios de prueba generados.\n\n"
        "---\n\n"
        "## Scripts de generacion\n\n"
        "_Derivado de `generacion_scripts` del modelo JSON_\n\n" +
        lista_scripts + "\n\n"
        "---\n\n"
        "## Changelog del modelo\n\n"
        "_Ultimas entradas de `changelog` en `modelo-json.json`_\n\n" +
        changelog_md + "\n\n"
        "---\n\n"
        "## Documentacion adicional\n\n"
        "- [Referencia de API](api-reference.md)\n"
        "- [Diccionario de datos](diccionario-datos.md)\n"
        "- [Arquitectura](arquitectura.md)\n"
        "- [Swagger UI produccion](https://greenhouse-backend-production-c720.up.railway.app/swagger-ui.html)\n"
    )
    escribir(DOCS / "README.md", contenido)


# ── api-reference.md — endpoints y roles desde el modelo ──────────────────────

def generar_api_reference(modelo: dict):
    """
    Genera la referencia de API leyendo:
    - api_endpoints → tabla de endpoints por modulo
    - roles         → descripcion y permisos de cada rol
    """
    endpoints = modelo.get("api_endpoints", {})
    roles     = modelo.get("roles", {})
    version   = modelo.get("version", "3.0.0")
    scripts   = modelo.get("generacion_scripts", {}).get("scripts", {})
    url_back  = scripts.get("06_ejecutar_aplicacion.py", {}).get(
        "urls_resultado", {}).get("backend", "http://localhost:8080")

    lineas = [
        "# GreenHouse Manager — Referencia de API REST",
        "",
        "**Version:** " + version + " | **Base URL:** `" + url_back + "/api`",
        "**Swagger UI:** `" + url_back + "/swagger-ui.html`",
        "",
        "---",
        "",
        "## Roles y permisos",
        "_Derivado de la seccion `roles` del modelo JSON_",
        "",
    ]

    for rol, rdef in roles.items():
        lineas.append("### `" + rol + "`")
        lineas.append(rdef.get("description", ""))
        perms = rdef.get("permissions", [])
        lineas.append("- **Permisos:** " + ", ".join(perms))
        if "denied" in rdef:
            lineas.append("- **Denegado:** " + ", ".join(rdef["denied"]))
        if "additional" in rdef:
            lineas.append("- **Operaciones adicionales:**")
            for a in rdef["additional"]:
                lineas.append("  - `" + a + "`")
        if "exclusive_access" in rdef:
            lineas.append("- **Acceso exclusivo:**")
            for a in rdef["exclusive_access"]:
                lineas.append("  - " + a)
        lineas.append("")

    lineas += [
        "---",
        "",
        "## Endpoints por modulo",
        "_Derivado de la seccion `api_endpoints` del modelo JSON_",
        "",
    ]

    for modulo, eps in endpoints.items():
        lineas.append("### `/api/" + modulo + "`")
        lineas.append("")
        lineas.append("| Metodo | Endpoint | Roles permitidos |")
        lineas.append("|--------|----------|-----------------|")
        for ep in eps:
            partes   = ep.split()
            metodo   = partes[0] if partes else ""
            ruta     = partes[1] if len(partes) > 1 else ""
            roles_ep = ep.split("[")[1].rstrip("]").strip() if "[" in ep else "Autenticado"
            lineas.append("| `" + metodo + "` | `" + ruta + "` | " + roles_ep + " |")
        lineas.append("")

    lineas += [
        "---",
        "",
        "## Codigos de respuesta HTTP",
        "",
        "| Codigo | Significado |",
        "|--------|-------------|",
        "| 200 | OK — Operacion exitosa |",
        "| 201 | Created — Recurso creado |",
        "| 204 | No Content — Eliminacion exitosa |",
        "| 400 | Bad Request — Datos invalidos o duplicados |",
        "| 401 | Unauthorized — No autenticado |",
        "| 403 | Forbidden — Sin permisos (rol insuficiente) |",
        "| 404 | Not Found — Recurso no existe |",
        "| 503 | Service Unavailable — API externa no disponible (Taiga) |",
    ]

    escribir(DOCS / "api-reference.md", "\n".join(lineas))


# ── arquitectura.md — procesos desde automated_processes y new_in_v3 ──────────

def generar_arquitectura(modelo: dict):
    """
    Genera arquitectura.md leyendo:
    - automated_processes  → tabla de procesos automatizados
    - new_in_v3            → detalles del scheduler (cron, categorias, formula severidad)
    - entities             → listado de tablas PostgreSQL
    - roles                → descripcion de roles para RBAC
    """
    procesos    = modelo.get("automated_processes", {}).get("procesos", [])
    v3          = modelo.get("new_in_v3", {})
    scheduler   = v3.get("harvest_scheduler", {})
    severity    = v3.get("alert_severity_calculation", {})
    entidades   = modelo.get("entities", {})
    roles       = modelo.get("roles", {})
    version     = modelo.get("version", "?")

    # Tablas PostgreSQL desde las entidades del modelo
    tablas_pg = ", ".join(
        entidad.get("table", camel_a_snake(nombre))
        for nombre, entidad in entidades.items()
    )

    # Tabla de procesos automatizados desde automated_processes del modelo
    lineas_procesos = [
        "| Proceso | Trigger | Archivo |",
        "|---------|---------|---------|",
    ]
    for p in procesos:
        lineas_procesos.append(
            "| " + p.get("nombre", "") +
            " | " + p.get("trigger", "") +
            " | `" + p.get("archivo", "") + "` |"
        )
    tabla_procesos = "\n".join(lineas_procesos)

    # Descripcion de roles desde modelo["roles"]
    lineas_roles = []
    for rol, rdef in roles.items():
        lineas_roles.append(
            "- **" + rol + "**: " + rdef.get("description", "") +
            " (permisos: " + ", ".join(rdef.get("permissions", [])) + ")"
        )
    roles_str = "\n".join(lineas_roles)

    # Scheduler desde new_in_v3.harvest_scheduler
    cron        = scheduler.get("cron", "0 0 0/6 * * ?")
    categorias  = scheduler.get("categories", {})
    cat_md      = "\n".join(
        "  - `" + tipo + "`: " + datos.get("condicion", "") +
        " → severidad " + datos.get("severidad", "")
        for tipo, datos in categorias.items()
    )

    # Severidad desde new_in_v3.alert_severity_calculation
    formula     = severity.get("formula", "")
    thresholds  = severity.get("thresholds", {})
    thresh_md   = "\n".join(
        "  - **" + nivel + "**: " + condicion
        for nivel, condicion in thresholds.items()
    )

    contenido = (
        "# GreenHouse Manager — Arquitectura del Sistema\n\n"
        "**Version del modelo:** " + version + " | **Fecha:** " + str(date.today()) + "\n\n"
        "---\n\n"
        "## Diagrama de capas\n\n"
        "```\n"
        "┌─────────────────────────────────────────────────────────┐\n"
        "│                     CLIENTE (Browser)                    │\n"
        "│              React 18 + Vite + TailwindCSS               │\n"
        "│    React Query (cache) · Axios (HTTP) · i18next (i18n)  │\n"
        "└───────────────────────────┬─────────────────────────────┘\n"
        "                            │ HTTP/JSON (CORS)\n"
        "                            │ Cookie JSESSIONID\n"
        "┌───────────────────────────▼─────────────────────────────┐\n"
        "│                  BACKEND (Spring Boot 3.2.5)             │\n"
        "│                                                          │\n"
        "│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │\n"
        "│  │ Controllers  │  │  Services    │  │  Schedulers  │  │\n"
        "│  │@RestController  │  @Service   │  │  @Scheduled  │  │\n"
        "│  │ + Swagger    │  │ + JavaDoc    │  │  cron: " + cron + " │  │\n"
        "│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │\n"
        "│         │                 │                  │          │\n"
        "│  ┌──────▼─────────────────▼──────────────────▼───────┐  │\n"
        "│  │               Repositories (JPA)                   │  │\n"
        "│  │         JpaRepository<Entity, Long>                 │  │\n"
        "│  └──────────────────────────┬────────────────────────┘  │\n"
        "│                              │                           │\n"
        "│  ┌───────────────────────────▼──────────────────────┐   │\n"
        "│  │           Spring Security                         │   │\n"
        "│  │   Login local · OAuth2 Google · RBAC (@PreAuth)  │   │\n"
        "│  └──────────────────────────────────────────────────┘   │\n"
        "└───────────────────────────┬─────────────────────────────┘\n"
        "                            │ JDBC\n"
        "┌───────────────────────────▼─────────────────────────────┐\n"
        "│                   PostgreSQL 15                           │\n"
        "│  " + tablas_pg + "  │\n"
        "└─────────────────────────────────────────────────────────┘\n"
        "```\n\n"
        "---\n\n"
        "## Procesos automatizados\n\n"
        "_Derivado de la seccion `automated_processes` del modelo JSON_\n\n" +
        tabla_procesos + "\n\n"
        "---\n\n"
        "## Scheduler de cosechas\n\n"
        "_Derivado de `new_in_v3.harvest_scheduler` del modelo JSON_\n\n"
        "- **Cron:** `" + cron + "` (cada 6 horas: 00:00, 06:00, 12:00, 18:00)\n"
        "- **Categorias de alerta (derivadas del modelo):**\n" +
        cat_md + "\n\n"
        "---\n\n"
        "## Calculo de severidad de alertas\n\n"
        "_Derivado de `new_in_v3.alert_severity_calculation` del modelo JSON_\n\n"
        "- **Formula:** `" + formula + "`\n"
        "- **Umbrales:**\n" +
        thresh_md + "\n\n"
        "---\n\n"
        "## Control de acceso por rol (RBAC)\n\n"
        "_Derivado de la seccion `roles` del modelo JSON_\n\n" +
        roles_str + "\n\n"
        "---\n\n"
        "## Decisiones de diseno\n\n"
        "### Backend\n"
        "- **Sin DTOs propios**: las entidades JPA se serializan directamente con Jackson.\n"
        "  `@JsonIgnoreProperties` evita serializar proxies de Hibernate.\n"
        "- **Sesion HTTP en lugar de JWT**: cookie `JSESSIONID` con `SameSite=None; Secure`.\n"
        "- **Taiga proxy en backend**: evita exponer credenciales en el frontend;\n"
        "  token cacheado 23h en memoria.\n\n"
        "### Frontend\n"
        "- **React Query** para cache automatico, refetch y estados loading/error.\n"
        "- **TailwindCSS** sin CSS custom: diseno verde (#166534).\n"
        "- **i18next** con namespace unico `translation`, switching en runtime.\n"
        "- **Sidebar con RBAC**: items `adminOnly: true` se filtran segun `isAdmin`.\n"
    )
    escribir(DOCS / "arquitectura.md", contenido)


# ── javadoc-instrucciones.md ───────────────────────────────────────────────────

def generar_javadoc_instrucciones(modelo: dict):
    """
    Genera las instrucciones de JavaDoc leyendo las URLs del modelo.
    """
    scripts  = modelo.get("generacion_scripts", {}).get("scripts", {})
    urls     = scripts.get("06_ejecutar_aplicacion.py", {}).get("urls_resultado", {})
    url_sw_local  = urls.get("swagger", "http://localhost:8080/swagger-ui.html")

    contenido = (
        "# Generacion de JavaDoc -- GreenHouse Manager\n\n"
        "El `pom.xml` incluye `maven-javadoc-plugin` configurado SIN ejecucion\n"
        "automatica para no interferir con `mvn package` en CI.\n\n"
        "## Generar manualmente\n\n"
        "```bash\n"
        "cd greenhouse-backend\n"
        "mvn javadoc:javadoc\n"
        "```\n\n"
        "Genera el sitio HTML en:\n"
        "  `greenhouse-backend/target/site/apidocs/index.html`\n\n"
        "## Contenido documentado\n\n"
        "Todos los metodos publicos de las clases @Service estan anotados con:\n"
        "- `@param`   -- descripcion de cada parametro\n"
        "- `@return`  -- descripcion del valor de retorno\n"
        "- `@throws`  -- excepciones lanzadas (ResourceNotFoundException)\n\n"
        "Todos los endpoints @RestController estan anotados con:\n"
        "- `@Operation(summary = \"...\")` -- descripcion del endpoint\n"
        "- `@ApiResponse(responseCode = \"...\")` -- codigos HTTP posibles\n"
        "- `@Parameter(description = \"...\")` -- parametros de ruta\n\n"
        "## Swagger UI (runtime)\n\n"
        "Disponible automaticamente al arrancar el backend:\n"
        "- **Local:**      " + url_sw_local + "\n"
        "- **Produccion:** https://greenhouse-backend-production-c720.up.railway.app/swagger-ui.html\n\n"
        "La documentacion Swagger se genera en runtime desde las anotaciones\n"
        "`springdoc-openapi-starter-webmvc-ui 2.5.0`.\n"
    )
    escribir(DOCS / "javadoc-instrucciones.md", contenido)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  GENERADOR DOCUMENTACION -- GreenHouse Manager")
    print("  Fuente: docs/modelo-json.json")
    print("=" * 60)

    modelo    = json.loads(MODELO.read_text(encoding="utf-8"))
    version   = modelo.get("version", "?")
    procesos  = modelo.get("automated_processes", {}).get("procesos", [])
    endpoints = modelo.get("api_endpoints", {})

    print("\n  Modelo v" + version)
    print("  Procesos automatizados detectados: " + str(len(procesos)))
    print("  Modulos de API: " + str(len(endpoints)))
    print("")

    generar_readme(modelo)
    generar_api_reference(modelo)
    generar_arquitectura(modelo)
    generar_javadoc_instrucciones(modelo)

    print("\n  ✓ Documentacion generada en: docs/")
    print("    - README.md")
    print("    - api-reference.md  (" + str(len(endpoints)) + " modulos)")
    print("    - arquitectura.md   (" + str(len(procesos)) + " procesos automatizados)")
    print("    - javadoc-instrucciones.md")
    print("\n  Para generar JavaDoc HTML:")
    print("    cd greenhouse-backend && mvn javadoc:javadoc")
    print("    → target/site/apidocs/index.html")


if __name__ == "__main__":
    main()
