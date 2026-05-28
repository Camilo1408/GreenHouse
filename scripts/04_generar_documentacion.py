"""
GreenHouse Manager — Generador de Documentación Técnica
========================================================
Lee docs/modelo-json.json y genera:

  docs/
  ├── README.md               — Guía de instalación y uso del proyecto
  ├── arquitectura.md         — Diagrama de capas y decisiones técnicas
  ├── api-reference.md        — Referencia completa de endpoints REST
  ├── modelo-er.md            — Relaciones entre entidades (texto)
  └── swagger-config.md       — Cómo acceder al Swagger UI

  greenhouse-backend/
  └── (javadoc generado con: mvn javadoc:javadoc)
      → target/site/apidocs/index.html

NOTA: Script DEMOSTRATIVO — no ejecutar directamente.
"""

import json
import subprocess
from pathlib import Path
from datetime import date

ROOT   = Path(__file__).parent.parent
MODELO = ROOT / "docs" / "modelo-json.json"
DOCS   = ROOT / "docs"


def escribir(path: Path, contenido: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contenido, encoding="utf-8")
    print(f"  [DOCS] Creado: {path.relative_to(ROOT)}")


# ── README.md ──────────────────────────────────────────────────────────────────

def generar_readme(modelo: dict):
    version  = modelo.get("version", "3.0.0")
    entidades = list(modelo.get("entities", {}).keys())

    contenido = f"""\
# 🌿 GreenHouse Manager

Sistema integral de gestión de invernaderos con monitoreo en tiempo real,
alertas automáticas por sensores y trazabilidad completa del ciclo de vida
de las plantas.

**Versión del modelo:** {version} | **Fecha:** {date.today()}

---

## 📋 Entidades del sistema

{chr(10).join(f'- `{e}`' for e in entidades)}

---

## 🏗️ Stack tecnológico

| Capa       | Tecnología                           |
|------------|--------------------------------------|
| Backend    | Spring Boot 3.2.5 + Java 17          |
| Base de datos | PostgreSQL 15                     |
| Frontend   | React 18 + Vite + TypeScript         |
| UI         | TailwindCSS + lucide-react           |
| Estado     | @tanstack/react-query                |
| HTTP       | Axios                                |
| i18n       | i18next (español / inglés)           |
| Auth       | Spring Security + OAuth2 Google      |
| Docs API   | springdoc-openapi (Swagger UI)       |
| Deploy     | Railway (backend + frontend)         |
| CI/CD      | GitHub Actions (7 jobs)              |

---

## 🚀 Instalación local

### Prerrequisitos
- Java 17+
- Node.js 20+
- PostgreSQL 15+ (o Docker)
- Maven 3.9+

### 1. Clonar el repositorio
```bash
git clone https://github.com/Camilo1408/GreenHouse.git
cd GreenHouse
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales de Google OAuth y Gmail
```

### 3. Base de datos
```bash
# Con Docker (recomendado):
docker-compose up -d

# O manualmente:
createdb greenhouse_db
psql -d greenhouse_db -f docs/sql/01_schema.sql
psql -d greenhouse_db -f docs/sql/02_seed.sql
```

### 4. Arrancar el backend
```bash
cd greenhouse-backend
mvn spring-boot:run -Dspring-boot.run.profiles=local
```

### 5. Arrancar el frontend
```bash
cd greenhouse-frontend
npm install
npm run dev
```

### 6. Acceder a la aplicación
- **Frontend:** http://localhost:5173
- **Swagger UI:** http://localhost:8080/swagger-ui.html
- **Health check:** http://localhost:8080/actuator/health

---

## 👥 Usuarios de prueba (seed)

| Email | Contraseña | Rol |
|-------|-----------|-----|
| admin@greenhouse.com | Admin1234 | ADMINISTRADOR |
| supervisor@greenhouse.com | Super1234 | SUPERVISOR |
| juan@greenhouse.com | Juan1234 | EMPLEADO |
| empleado@greenhouse.com | Empleado1234 | EMPLEADO |

---

## 🔄 Pipeline CI/CD

```
push → main
  ├─ 1. JUnit Tests
  ├─ 2. Backend JAR Build
  ├─ 3. Frontend TypeScript + Build
  ├─ 4. Python API Tests (pytest)
  ├─ 5. Selenium UI Tests
  ├─ 6. Taiga Validation
  └─ 7. Deploy Railway (solo main)
```

---

## 📖 Documentación adicional

- [Referencia de API](api-reference.md)
- [Modelo ER](modelo-er.md)
- [Diccionario de datos](diccionario-datos.md)
- [Swagger UI (producción)](https://greenhouse-backend-production-c720.up.railway.app/swagger-ui.html)
"""
    escribir(DOCS / "README.md", contenido)


# ── api-reference.md ───────────────────────────────────────────────────────────

def generar_api_reference(modelo: dict):
    endpoints  = modelo.get("api_endpoints", {})
    roles      = modelo.get("roles", {})
    version    = modelo.get("version", "3.0.0")

    lineas = [
        "# GreenHouse Manager — Referencia de API REST",
        f"",
        f"**Versión:** {version} | **Base URL:** `http://localhost:8080/api`",
        f"**Swagger UI:** `/swagger-ui.html`",
        f"",
        "## Roles y permisos",
        "",
    ]

    for rol, rdef in roles.items():
        lineas.append(f"### `{rol}`")
        lineas.append(f"{rdef.get('description', '')}")
        perms = rdef.get("permissions", [])
        lineas.append(f"- **Permisos:** {', '.join(perms)}")
        if "denied" in rdef:
            lineas.append(f"- **Denegado:** {', '.join(rdef['denied'])}")
        if "additional" in rdef:
            lineas.append("- **Adicional:**")
            for a in rdef["additional"]:
                lineas.append(f"  - `{a}`")
        lineas.append("")

    lineas += ["---", "## Endpoints por módulo", ""]

    for modulo, eps in endpoints.items():
        lineas.append(f"### `/api/{modulo}`")
        lineas.append("")
        lineas.append("| Método | Endpoint | Roles permitidos |")
        lineas.append("|--------|----------|-----------------|")
        for ep in eps:
            partes = ep.split()
            metodo = partes[0] if partes else ""
            ruta   = partes[1] if len(partes) > 1 else ""
            roles_ep = ep.split("[")[1].rstrip("]").strip() if "[" in ep else "Autenticado"
            lineas.append(f"| `{metodo}` | `{ruta}` | {roles_ep} |")
        lineas.append("")

    lineas += [
        "---",
        "## Códigos de respuesta HTTP comunes",
        "",
        "| Código | Significado |",
        "|--------|-------------|",
        "| 200 | OK — Operación exitosa |",
        "| 201 | Created — Recurso creado |",
        "| 204 | No Content — Eliminación exitosa |",
        "| 400 | Bad Request — Datos inválidos o duplicados |",
        "| 401 | Unauthorized — No autenticado |",
        "| 403 | Forbidden — Sin permisos (rol insuficiente) |",
        "| 404 | Not Found — Recurso no existe |",
        "| 503 | Service Unavailable — API externa no disponible (Taiga) |",
    ]

    escribir(DOCS / "api-reference.md", "\n".join(lineas))


# ── arquitectura.md ────────────────────────────────────────────────────────────

def generar_arquitectura():
    contenido = f"""\
# GreenHouse Manager — Arquitectura del Sistema

**Fecha:** {date.today()}

## Diagrama de capas

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENTE (Browser)                    │
│              React 18 + Vite + TailwindCSS               │
│    React Query (caché) · Axios (HTTP) · i18next (i18n)  │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTP/JSON (CORS)
                            │ Cookie JSESSIONID
┌───────────────────────────▼─────────────────────────────┐
│                  BACKEND (Spring Boot 3.2.5)             │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Controllers  │  │  Services    │  │  Schedulers  │  │
│  │ @RestController  │  @Service   │  │  @Scheduled  │  │
│  │ + Swagger    │  │ + JavaDoc    │  │  (cron 6h)   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│  ┌──────▼─────────────────▼──────────────────▼───────┐  │
│  │               Repositories (JPA)                   │  │
│  │         JpaRepository<Entity, Long>                 │  │
│  └──────────────────────────┬────────────────────────┘  │
│                              │                           │
│  ┌───────────────────────────▼──────────────────────┐   │
│  │           Spring Security                         │   │
│  │   Login local · OAuth2 Google · RBAC (@PreAuth)  │   │
│  └──────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────┘
                            │ JDBC
┌───────────────────────────▼─────────────────────────────┐
│                   PostgreSQL 15                           │
│  zona · tipo_planta · empleado · planta · sensor         │
│  lectura_sensor · alerta · cosecha · tratamiento · turno │
└─────────────────────────────────────────────────────────┘
```

## Procesos automatizados

| Proceso | Trigger | Archivo |
|---------|---------|---------|
| Alerta por umbral sensor | POST /api/lecturas | `LecturaSensorService.java` |
| Alerta de cosecha pendiente | Cron cada 6h (00/06/12/18) | `CosechaAlertaScheduler.java` |
| Auto-registro usuarios Google | Login OAuth2 | `SecurityConfig.java` |
| Seed de datos de prueba | Arranque app (1 vez) | `DataInitializer.java` |
| Verificación de correo | Registro local | `AuthService.java` |
| Deploy automático | Push a main (CI pasa) | `.github/workflows/ci.yml` |

## Decisiones de diseño

### Backend
- **Sin DTOs propios**: las entidades JPA se serializan directamente con Jackson.
  `@JsonIgnoreProperties` evita serializar proxies de Hibernate.
- **Sesión HTTP en lugar de JWT**: más simple para una SPA con mismo dominio.
  Cookie `JSESSIONID` con `SameSite=None; Secure` para Railway (dominios distintos).
- **Severidad de alertas calculada dinámicamente** según desviación porcentual
  del rango `[umbralMin, umbralMax]` del sensor.
- **Taiga proxy en backend**: evita exponer credenciales en el frontend;
  token cacheado 23h en memoria.

### Frontend
- **React Query** para caché automático, refetch y estados loading/error.
- **TailwindCSS** sin CSS custom: diseño verde (#166534) coherente con el dominio.
- **i18next** con namespace único `translation`, switching en runtime.
- **Sidebar con RBAC**: items `adminOnly: true` se filtran según `isAdmin`.
"""
    escribir(DOCS / "arquitectura.md", contenido)


# ── JavaDoc (mvn) ──────────────────────────────────────────────────────────────

def generar_javadoc_instrucciones():
    """
    Muestra cómo generar el JavaDoc HTML.
    No ejecuta mvn para no depender del entorno.
    """
    instrucciones = f"""\
# Generación de JavaDoc — GreenHouse Manager

El `pom.xml` incluye `maven-javadoc-plugin` configurado SIN ejecución
automática para no interferir con `mvn package` en CI.

## Generar manualmente

```bash
cd greenhouse-backend
mvn javadoc:javadoc
```

Genera el sitio HTML en:
  `greenhouse-backend/target/site/apidocs/index.html`

## Contenido documentado

Todos los métodos públicos de las clases @Service están anotados con:
- `@param`   — descripción de cada parámetro
- `@return`  — descripción del valor de retorno
- `@throws`  — excepciones lanzadas (ResourceNotFoundException, IllegalArgumentException)

Todos los endpoints @RestController están anotados con:
- `@Operation(summary = "...")` — descripción del endpoint
- `@ApiResponse(responseCode = "...", description = "...")` — códigos HTTP posibles
- `@Parameter(description = "...", required = true)` — parámetros de ruta/query

## Swagger UI (runtime)

Disponible automáticamente al arrancar el backend:
- Local:      http://localhost:8080/swagger-ui.html
- Producción: https://greenhouse-backend-production-c720.up.railway.app/swagger-ui.html

La documentación Swagger se genera en runtime desde las anotaciones
`springdoc-openapi-starter-webmvc-ui 2.5.0`.
"""
    escribir(DOCS / "javadoc-instrucciones.md", instrucciones)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  GENERADOR DOCUMENTACIÓN — GreenHouse Manager")
    print("=" * 60)

    modelo = json.loads(MODELO.read_text(encoding="utf-8"))

    generar_readme(modelo)
    generar_api_reference(modelo)
    generar_arquitectura()
    generar_javadoc_instrucciones()

    print(f"\n  ✓ Documentación generada en: docs/")
    print(f"    - README.md")
    print(f"    - api-reference.md  ({len(modelo.get('api_endpoints',{}))} módulos)")
    print(f"    - arquitectura.md")
    print(f"    - javadoc-instrucciones.md")
    print(f"\n  Para generar JavaDoc HTML:")
    print(f"    cd greenhouse-backend && mvn javadoc:javadoc")
    print(f"    → target/site/apidocs/index.html")


if __name__ == "__main__":
    main()
