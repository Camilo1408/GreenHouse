"""
GreenHouse Manager — Generador del Backend Spring Boot
=======================================================
Lee docs/modelo-json.json y genera la estructura completa del backend:

  greenhouse-backend/
  ├── pom.xml
  ├── Dockerfile
  ├── railway.toml
  └── src/main/java/com/greenhouse/
      ├── GreenhouseApplication.java
      ├── entity/          ← una clase @Entity por entidad del modelo
      ├── repository/      ← interfaces JpaRepository
      ├── service/         ← lógica de negocio con JavaDoc
      ├── controller/      ← @RestController con Swagger @ApiResponse
      ├── config/
      │   ├── SecurityConfig.java      (OAuth2 Google + login local)
      │   ├── DataInitializer.java     (seed de datos de prueba)
      │   └── SwaggerConfig.java
      ├── dto/             ← RegisterRequest, LoginRequest, AuthResponse
      ├── exception/       ← ResourceNotFoundException, GlobalExceptionHandler
      └── scheduler/
          └── CosechaAlertaScheduler.java  (cron cada 6h)

  src/main/resources/
      application.properties
      messages.properties     (i18n backend)

NOTA: Script DEMOSTRATIVO — no ejecutar directamente.
"""

import json
import textwrap
from pathlib import Path
from datetime import date

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT    = Path(__file__).parent.parent
MODELO  = ROOT / "docs" / "modelo-json.json"
BACKEND = ROOT / "greenhouse-backend"
JAVA    = BACKEND / "src" / "main" / "java" / "com" / "greenhouse"
RESOURCES = BACKEND / "src" / "main" / "resources"
TEST_RESOURCES = BACKEND / "src" / "test" / "resources"

HEADER = f"""\
/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: {date.today().year}
 * Generado automáticamente desde docs/modelo-json.json
 */
"""


# ── Utilidades ─────────────────────────────────────────────────────────────────

def crear_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def escribir(path: Path, contenido: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contenido, encoding="utf-8")
    print(f"  [BACKEND] Creado: {path.relative_to(ROOT)}")

def capitalizar(nombre: str) -> str:
    return nombre[0].upper() + nombre[1:]

def a_nombre_clase(tabla: str) -> str:
    """zona → Zona, tipo_planta → TipoPlanta"""
    return "".join(p.capitalize() for p in tabla.split("_"))

def tipo_java(prop: dict) -> str:
    """Convierte tipo JSON Schema a tipo Java."""
    t = prop.get("type", "string")
    fmt = prop.get("format", "")
    if t == "integer":
        return "Long"
    if t == "number":
        return "Double"
    if t == "boolean":
        return "Boolean"
    if fmt == "date":
        return "LocalDate"
    if fmt == "date-time":
        return "LocalDateTime"
    return "String"


# ── Generadores ────────────────────────────────────────────────────────────────

def generar_pom_xml():
    contenido = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.5</version>
    <relativePath/>
  </parent>

  <groupId>com.greenhouse</groupId>
  <artifactId>greenhouse-backend</artifactId>
  <version>1.0.0</version>
  <name>GreenHouse Manager - Backend</name>
  <description>Sistema de gestión integral para invernaderos</description>

  <properties>
    <java.version>17</java.version>
  </properties>

  <dependencies>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-security</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-oauth2-client</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-mail</artifactId></dependency>
    <dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><scope>runtime</scope></dependency>
    <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
    <dependency><groupId>org.springframework.security</groupId><artifactId>spring-security-crypto</artifactId></dependency>
    <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
      <version>2.5.0</version>
    </dependency>
    <!-- Tests -->
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-test</artifactId><scope>test</scope></dependency>
    <dependency><groupId>org.springframework.security</groupId><artifactId>spring-security-test</artifactId><scope>test</scope></dependency>
    <dependency><groupId>com.h2database</groupId><artifactId>h2</artifactId><scope>test</scope></dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
        <configuration>
          <excludes>
            <exclude><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId></exclude>
          </excludes>
        </configuration>
      </plugin>
      <!-- JavaDoc: solo generación manual con: mvn javadoc:javadoc -->
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-javadoc-plugin</artifactId>
        <version>3.6.3</version>
        <configuration>
          <source>17</source>
          <encoding>UTF-8</encoding>
          <doclint>none</doclint>
          <excludePackageNames>*.config</excludePackageNames>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
"""
    escribir(BACKEND / "pom.xml", contenido)


def generar_application_properties(modelo: dict):
    contenido = """\
# GreenHouse Manager - Configuracion principal
# Generado desde docs/modelo-json.json

# ===== Base de datos PostgreSQL =====
spring.datasource.url=${DB_URL:jdbc:postgresql://localhost:5432/greenhouse_db}
spring.datasource.username=${DB_USERNAME:postgres}
spring.datasource.password=${DB_PASSWORD:postgres}
spring.datasource.driver-class-name=org.postgresql.Driver

# ===== JPA / Hibernate =====
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=false
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect
spring.jpa.properties.hibernate.format_sql=true

# ===== Servidor =====
server.port=8080

# ===== OAuth2 Google =====
spring.security.oauth2.client.registration.google.client-id=${GOOGLE_CLIENT_ID:tu-client-id-aqui}
spring.security.oauth2.client.registration.google.client-secret=${GOOGLE_CLIENT_SECRET:tu-client-secret-aqui}
spring.security.oauth2.client.registration.google.scope=email,profile
spring.security.oauth2.client.registration.google.redirect-uri=${BACKEND_URL:http://localhost:8080}/login/oauth2/code/google

# ===== Correo Gmail (Spring Mail) =====
spring.mail.host=smtp.gmail.com
spring.mail.port=587
spring.mail.username=${MAIL_USERNAME:tu-email@gmail.com}
spring.mail.password=${MAIL_PASSWORD:tu-app-password-aqui}
spring.mail.properties.mail.smtp.auth=true
spring.mail.properties.mail.smtp.starttls.enable=true

# ===== URLs de la app =====
app.base-url=${BACKEND_URL:http://localhost:8080}
app.frontend-url=${FRONTEND_URL:http://localhost:5173}

# ===== Swagger / OpenAPI =====
springdoc.api-docs.path=/v3/api-docs
springdoc.swagger-ui.path=/swagger-ui.html
springdoc.swagger-ui.operationsSorter=method

# ===== Connection pool =====
spring.datasource.hikari.connection-timeout=60000
spring.datasource.hikari.initialization-fail-timeout=0
spring.datasource.hikari.maximum-pool-size=5

# ===== Sesion HTTP (HTTPS Railway) =====
server.servlet.session.cookie.same-site=none
server.servlet.session.cookie.secure=true
server.servlet.session.cookie.http-only=true

# ===== Actuator =====
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=never
management.health.db.enabled=false
management.health.diskspace.enabled=false
management.health.mail.enabled=false

# ===== Taiga proxy (solo ADMINISTRADOR) =====
taiga.url=${TAIGA_URL:https://api.taiga.io/api/v1}
taiga.username=${TAIGA_USERNAME:}
taiga.password=${TAIGA_PASSWORD:}
taiga.project-slug=${TAIGA_PROJECT_SLUG:cesar_camilo-greenhouse-manager}

# ===== Logging =====
logging.level.com.greenhouse=INFO
logging.level.org.springframework.security=WARN
"""
    escribir(RESOURCES / "application.properties", contenido)


def generar_entidad(nombre_clase: str, entidad: dict):
    """Genera el archivo @Entity para cada entidad del modelo."""
    tabla  = entidad.get("table", nombre_clase.lower())
    props  = entidad.get("properties", {})
    desc   = entidad.get("description", "")

    # Detectar imports necesarios
    imports = set([
        "import jakarta.persistence.*;",
        "import lombok.*;",
    ])
    for pname, pdef in props.items():
        tj = tipo_java(pdef)
        if tj == "LocalDate":
            imports.add("import java.time.LocalDate;")
        if tj == "LocalDateTime":
            imports.add("import java.time.LocalDateTime;")
        if "$ref" in pdef:
            imports.add("import jakarta.validation.constraints.*;")

    campos = []
    for pname, pdef in props.items():
        if pname == "id":
            campos.append("    @Id\n    @GeneratedValue(strategy = GenerationType.IDENTITY)\n    private Long id;")
            continue
        if "$ref" in pdef:
            # Relación ManyToOne
            ref_clase = pdef["$ref"].replace("#/entities/", "")
            nullable  = pdef.get("nullable", False)
            fk_col    = pname + "_id"
            campo = f"    @ManyToOne(fetch = FetchType.LAZY)\n    @JoinColumn(name = \"{fk_col}\", nullable = {str(not nullable).lower()})\n    private {ref_clase} {pname};"
            campos.append(campo)
        else:
            tj   = tipo_java(pdef)
            col_anotacion = ""
            # Columna con nombre especial (camelCase → snake_case)
            col_name = "".join(["_" + c.lower() if c.isupper() else c for c in pname]).lstrip("_")
            if col_name != pname:
                col_anotacion = f"    @Column(name = \"{col_name}\")\n"
            enums = pdef.get("enum", [])
            if enums:
                enum_nombre = capitalizar(pname)
                campo = f"    @Enumerated(EnumType.STRING)\n{col_anotacion}    private {enum_nombre} {pname};"
            else:
                campo = f"{col_anotacion}    private {tj} {pname};"
            campos.append(campo)

    campos_str = "\n\n".join(campos)
    imports_str = "\n".join(sorted(imports))

    contenido = f"""{HEADER}
package com.greenhouse.entity;

{imports_str}
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * {desc}
 * <p>Tabla: {@code {tabla}}</p>
 */
@Entity
@Table(name = "{tabla}")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties({{"hibernateLazyInitializer", "handler"}})
public class {nombre_clase} {{

{campos_str}
}}
"""
    escribir(JAVA / "entity" / f"{nombre_clase}.java", contenido)


def generar_repositorio(nombre_clase: str):
    """Genera la interfaz JpaRepository para cada entidad."""
    contenido = f"""{HEADER}
package com.greenhouse.repository;

import com.greenhouse.entity.{nombre_clase};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

/** Repositorio JPA para la entidad {@link {nombre_clase}}. */
@Repository
public interface {nombre_clase}Repository extends JpaRepository<{nombre_clase}, Long> {{
    // Métodos de consulta derivados generados automáticamente por Spring Data JPA.
    // Ejemplo: findByEstado(String estado), existsByNombre(String nombre), etc.
}}
"""
    escribir(JAVA / "repository" / f"{nombre_clase}Repository.java", contenido)


def generar_servicio(nombre_clase: str, entidad: dict):
    """Genera el @Service con operaciones CRUD y JavaDoc."""
    tabla = entidad.get("table", nombre_clase.lower())
    desc  = entidad.get("description", "")

    contenido = f"""{HEADER}
package com.greenhouse.service;

import com.greenhouse.entity.{nombre_clase};
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.{nombre_clase}Repository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

/**
 * Servicio para la gestión de {@link {nombre_clase}}.
 * <p>{desc}</p>
 */
@Service
@RequiredArgsConstructor
@Transactional
public class {nombre_clase}Service {{

    private final {nombre_clase}Repository {nombre_clase[0].lower()}{nombre_clase[1:]}Repository;

    /**
     * Retorna todos los registros de {nombre_clase}.
     *
     * @return lista completa (puede estar vacía)
     */
    public List<{nombre_clase}> findAll() {{
        return {nombre_clase[0].lower()}{nombre_clase[1:]}Repository.findAll();
    }}

    /**
     * Busca un registro de {nombre_clase} por su identificador.
     *
     * @param id identificador único
     * @return el registro encontrado
     * @throws ResourceNotFoundException si no existe un registro con ese ID
     */
    public {nombre_clase} findById(Long id) {{
        return {nombre_clase[0].lower()}{nombre_clase[1:]}Repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("{nombre_clase} no encontrado con id: " + id));
    }}

    /**
     * Persiste un nuevo registro de {nombre_clase}.
     *
     * @param entity datos del nuevo registro
     * @return el registro persistido con su ID asignado
     */
    public {nombre_clase} save({nombre_clase} entity) {{
        return {nombre_clase[0].lower()}{nombre_clase[1:]}Repository.save(entity);
    }}

    /**
     * Actualiza un registro existente de {nombre_clase}.
     *
     * @param id      ID del registro a actualizar
     * @param updated objeto con los nuevos valores
     * @return el registro actualizado
     * @throws ResourceNotFoundException si no existe el registro
     */
    public {nombre_clase} update(Long id, {nombre_clase} updated) {{
        findById(id); // valida existencia
        updated.setId(id);
        return {nombre_clase[0].lower()}{nombre_clase[1:]}Repository.save(updated);
    }}

    /**
     * Elimina un registro de {nombre_clase}.
     *
     * @param id ID del registro a eliminar
     * @throws ResourceNotFoundException si no existe el registro
     */
    public void delete(Long id) {{
        findById(id); // valida existencia
        {nombre_clase[0].lower()}{nombre_clase[1:]}Repository.deleteById(id);
    }}
}}
"""
    escribir(JAVA / "service" / f"{nombre_clase}Service.java", contenido)


def generar_controlador(nombre_clase: str, entidad: dict, endpoints: list):
    """Genera el @RestController con Swagger @ApiResponse y @PreAuthorize."""
    rbac = entidad.get("rbac", {})
    desc = entidad.get("description", "")
    tabla = entidad.get("table", nombre_clase.lower())
    url_base = f"/api/{tabla.replace('_', '-')}s"

    contenido = f"""{HEADER}
package com.greenhouse.controller;

import com.greenhouse.entity.{nombre_clase};
import com.greenhouse.service.{nombre_clase}Service;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import java.util.List;

/**
 * Controlador REST para la gestión de {@link {nombre_clase}}.
 * <p>{desc}</p>
 */
@RestController
@RequestMapping("{url_base}")
@RequiredArgsConstructor
@Tag(name = "{nombre_clase}", description = "Gestión de {nombre_clase.lower()}s del invernadero")
public class {nombre_clase}Controller {{

    private final {nombre_clase}Service {nombre_clase[0].lower()}{nombre_clase[1:]}Service;

    @GetMapping
    @Operation(summary = "Listar todos los registros de {nombre_clase}")
    @ApiResponse(responseCode = "200", description = "Lista retornada correctamente")
    public ResponseEntity<List<{nombre_clase}>> findAll() {{
        return ResponseEntity.ok({nombre_clase[0].lower()}{nombre_clase[1:]}Service.findAll());
    }}

    @GetMapping("/{{id}}")
    @Operation(summary = "Obtener {nombre_clase} por ID")
    @ApiResponses({{
        @ApiResponse(responseCode = "200", description = "Registro encontrado"),
        @ApiResponse(responseCode = "404", description = "Registro no encontrado")
    }})
    public ResponseEntity<{nombre_clase}> findById(
            @Parameter(description = "ID del registro", required = true) @PathVariable Long id) {{
        return ResponseEntity.ok({nombre_clase[0].lower()}{nombre_clase[1:]}Service.findById(id));
    }}

    @PostMapping
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Crear nuevo {nombre_clase}")
    @ApiResponses({{
        @ApiResponse(responseCode = "201", description = "Creado exitosamente"),
        @ApiResponse(responseCode = "400", description = "Datos inválidos"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado")
    }})
    public ResponseEntity<{nombre_clase}> create(@Valid @RequestBody {nombre_clase} entity) {{
        return ResponseEntity.status(HttpStatus.CREATED)
                .body({nombre_clase[0].lower()}{nombre_clase[1:]}Service.save(entity));
    }}

    @PutMapping("/{{id}}")
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Actualizar {nombre_clase} existente")
    @ApiResponses({{
        @ApiResponse(responseCode = "200", description = "Actualizado correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado"),
        @ApiResponse(responseCode = "404", description = "No encontrado")
    }})
    public ResponseEntity<{nombre_clase}> update(
            @Parameter(description = "ID del registro", required = true) @PathVariable Long id,
            @Valid @RequestBody {nombre_clase} entity) {{
        return ResponseEntity.ok({nombre_clase[0].lower()}{nombre_clase[1:]}Service.update(id, entity));
    }}

    @DeleteMapping("/{{id}}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Eliminar {nombre_clase}")
    @ApiResponses({{
        @ApiResponse(responseCode = "204", description = "Eliminado correctamente"),
        @ApiResponse(responseCode = "403", description = "Requiere ADMINISTRADOR"),
        @ApiResponse(responseCode = "404", description = "No encontrado")
    }})
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID del registro", required = true) @PathVariable Long id) {{
        {nombre_clase[0].lower()}{nombre_clase[1:]}Service.delete(id);
        return ResponseEntity.noContent().build();
    }}
}}
"""
    escribir(JAVA / "controller" / f"{nombre_clase}Controller.java", contenido)


def generar_scheduler():
    """Genera CosechaAlertaScheduler.java (cron cada 6h)."""
    contenido = f"""{HEADER}
package com.greenhouse.scheduler;

import com.greenhouse.entity.Alerta;
import com.greenhouse.entity.Planta;
import com.greenhouse.repository.AlertaRepository;
import com.greenhouse.repository.PlantaRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;

/**
 * Scheduler que evalúa el estado de cosecha de todas las plantas activas
 * y genera alertas automáticas según su proximidad o vencimiento.
 *
 * <p>Categorías de alerta:</p>
 * <ul>
 *   <li>COSECHA_PROXIMA     — faltan ≤7 días → BAJA</li>
 *   <li>COSECHA_LISTA       — 0–3 días tarde → MEDIA</li>
 *   <li>COSECHA_VENCIDA     — 4–7 días tarde → ALTA</li>
 *   <li>COSECHA_MUY_VENCIDA — más de 7 días → CRITICA</li>
 * </ul>
 *
 * <p>Deduplicación: usa el marcador [PLT-id] en la descripción.</p>
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class CosechaAlertaScheduler {{

    private final PlantaRepository plantaRepository;
    private final AlertaRepository alertaRepository;

    /**
     * Se ejecuta cada 6 horas: 00:00, 06:00, 12:00, 18:00.
     * Cron: "0 0 0/6 * * ?"
     */
    @Scheduled(cron = "0 0 0/6 * * ?")
    @Transactional
    public void evaluarCosechasPendientes() {{
        log.info("[Scheduler] Evaluando alertas de cosecha...");

        List<Planta> plantas = plantaRepository.findByEstadoIn(List.of(
            Planta.EstadoPlanta.SEMBRADA,
            Planta.EstadoPlanta.EN_CRECIMIENTO,
            Planta.EstadoPlanta.LISTA_PARA_COSECHAR
        ));

        int creadas = 0;
        for (Planta planta : plantas) {{
            if (planta.getTipoPlanta() == null || planta.getTipoPlanta().getCicloDias() == null) continue;

            LocalDate hoy              = LocalDate.now();
            LocalDate fechaCosechaEst  = planta.getFechaSiembra().plusDays(planta.getTipoPlanta().getCicloDias());
            long diasRestantes         = ChronoUnit.DAYS.between(hoy, fechaCosechaEst);

            if (diasRestantes > 7) continue;

            String tipo;
            Alerta.Severidad severidad;
            String mensajeEstado;

            if (diasRestantes > 0) {{
                tipo = "COSECHA_PROXIMA"; severidad = Alerta.Severidad.BAJA;
                mensajeEstado = "Faltan " + diasRestantes + " día(s) para la cosecha estimada";
            }} else if (diasRestantes >= -3) {{
                tipo = "COSECHA_LISTA"; severidad = Alerta.Severidad.MEDIA;
                mensajeEstado = diasRestantes == 0
                    ? "Hoy es el día estimado de cosecha"
                    : "Cosecha con " + Math.abs(diasRestantes) + " día(s) de retraso";
                actualizarEstadoListaParaCosechar(planta);
            }} else if (diasRestantes >= -7) {{
                tipo = "COSECHA_VENCIDA"; severidad = Alerta.Severidad.ALTA;
                mensajeEstado = "Cosecha vencida con " + Math.abs(diasRestantes) + " días de retraso";
                actualizarEstadoListaParaCosechar(planta);
            }} else {{
                tipo = "COSECHA_MUY_VENCIDA"; severidad = Alerta.Severidad.CRITICA;
                mensajeEstado = "VENCIDA — " + Math.abs(diasRestantes) + " días sin cosechar";
                actualizarEstadoListaParaCosechar(planta);
            }}

            String plantaRef = "[PLT-" + planta.getId() + "]";
            if (alertaRepository.existsByTipoAndDescripcionContainingAndEstado(
                    tipo, plantaRef, Alerta.EstadoAlerta.PENDIENTE)) continue;

            String descripcion = String.format(
                "%s Planta %s (%s) en zona '%s'. %s. Fecha estimada: %s.",
                plantaRef, planta.getCodigo(), planta.getTipoPlanta().getNombre(),
                planta.getZona().getNombre(), mensajeEstado, fechaCosechaEst);

            alertaRepository.save(Alerta.builder()
                .tipo(tipo).severidad(severidad)
                .zona(planta.getZona()).sensor(null)
                .fechaGeneracion(LocalDateTime.now())
                .estado(Alerta.EstadoAlerta.PENDIENTE)
                .descripcion(descripcion).build());
            creadas++;
        }}
        log.info("[Scheduler] Evaluación completada — {{}} alerta(s) generada(s)", creadas);
    }}

    private void actualizarEstadoListaParaCosechar(Planta planta) {{
        if (planta.getEstado() == Planta.EstadoPlanta.SEMBRADA
                || planta.getEstado() == Planta.EstadoPlanta.EN_CRECIMIENTO) {{
            planta.setEstado(Planta.EstadoPlanta.LISTA_PARA_COSECHAR);
            plantaRepository.save(planta);
        }}
    }}
}}
"""
    escribir(JAVA / "scheduler" / "CosechaAlertaScheduler.java", contenido)


def generar_exception_handler():
    contenido = f"""{HEADER}
package com.greenhouse.exception;

import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

/** Manejador global de excepciones REST. */
@RestControllerAdvice
public class GlobalExceptionHandler {{

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String,String>> handleNotFound(ResourceNotFoundException ex) {{
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(Map.of("error", ex.getMessage()));
    }}

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String,String>> handleBadRequest(IllegalArgumentException ex) {{
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(Map.of("error", ex.getMessage()));
    }}

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String,String>> handleGeneral(Exception ex) {{
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Error interno del servidor", "detalle", ex.getMessage()));
    }}
}}
"""
    escribir(JAVA / "exception" / "GlobalExceptionHandler.java", contenido)

    contenido_nfe = f"""{HEADER}
package com.greenhouse.exception;

/** Excepción lanzada cuando un recurso no es encontrado en la base de datos. */
public class ResourceNotFoundException extends RuntimeException {{
    public ResourceNotFoundException(String message) {{
        super(message);
    }}
}}
"""
    escribir(JAVA / "exception" / "ResourceNotFoundException.java", contenido_nfe)


def generar_main_application():
    contenido = f"""{HEADER}
package com.greenhouse;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/** Punto de entrada de la aplicación GreenHouse Manager. */
@SpringBootApplication
@EnableScheduling
public class GreenhouseApplication {{
    public static void main(String[] args) {{
        SpringApplication.run(GreenhouseApplication.class, args);
    }}
}}
"""
    escribir(JAVA / "GreenhouseApplication.java", contenido)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  GENERADOR BACKEND SPRING BOOT — GreenHouse Manager")
    print("=" * 60)

    modelo = json.loads(MODELO.read_text(encoding="utf-8"))
    entidades = modelo.get("entities", {})
    endpoints = modelo.get("api_endpoints", {})

    print(f"\n  Modelo: v{modelo.get('version','?')} — {len(entidades)} entidades\n")

    # 1. pom.xml
    generar_pom_xml()

    # 2. application.properties
    generar_application_properties(modelo)

    # 3. Main application
    generar_main_application()

    # 4. Exception handler
    generar_exception_handler()

    # 5. Scheduler de cosechas
    generar_scheduler()

    # 6. Entidades + Repositorios + Servicios + Controladores
    for nombre_clase, entidad in entidades.items():
        generar_entidad(nombre_clase, entidad)
        generar_repositorio(nombre_clase)
        generar_servicio(nombre_clase, entidad)
        eps = endpoints.get(entidad.get("table", nombre_clase.lower()).replace("_", "-") + "s", [])
        generar_controlador(nombre_clase, entidad, eps)

    print(f"\n  ✓ Backend generado en: {BACKEND.relative_to(ROOT)}")
    print(f"    Entidades   : {len(entidades)}")
    print(f"    Archivos Java generados: {len(entidades) * 4 + 4} (entity+repo+service+controller × N + extras)")


if __name__ == "__main__":
    main()
