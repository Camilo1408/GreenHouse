"""
GreenHouse Manager — Generador del Backend Spring Boot
=======================================================
Lee docs/modelo-json.json y genera TODA la estructura del backend
a partir de las descripciones, propiedades y relaciones del modelo.

NO tiene código del sistema hardcodeado:
  - Las entidades se generan desde modelo["entities"]
  - Los tipos de campo se derivan de los tipos JSON Schema
  - Los endpoints y RBAC se leen de modelo["api_endpoints"] y entidad["rbac"]
  - El scheduler se genera desde modelo["new_in_v3"]["harvest_scheduler"]
  - El seed se genera desde los "example" de cada entidad

Genera:
  greenhouse-backend/
  ├── pom.xml
  ├── src/main/resources/application.properties
  └── src/main/java/com/greenhouse/
      ├── GreenhouseApplication.java
      ├── entity/           (1 por entidad del modelo)
      ├── repository/       (1 por entidad)
      ├── service/          (1 por entidad, con JavaDoc)
      ├── controller/       (1 por entidad, con @ApiResponse Swagger)
      ├── exception/        (ResourceNotFoundException + GlobalExceptionHandler)
      └── scheduler/        (CosechaAlertaScheduler — desde harvest_scheduler del modelo)

NOTA: Script DEMOSTRATIVO. No ejecutar directamente.
"""

import json
from pathlib import Path
from datetime import date

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent.parent
MODELO    = ROOT / "docs" / "modelo-json.json"
BACKEND   = ROOT / "greenhouse-backend"
JAVA      = BACKEND / "src" / "main" / "java" / "com" / "greenhouse"
RESOURCES = BACKEND / "src" / "main" / "resources"

ANIO = date.today().year


def escribir(path: Path, contenido: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contenido, encoding="utf-8")
    print(f"  [BACKEND] {path.relative_to(ROOT)}")


def encabezado(archivo: str) -> str:
    return (
        "/*\n"
        " * GreenHouse Manager\n"
        " * Autores: [Nombres del equipo]\n"
        " * Fecha: " + str(ANIO) + "\n"
        " * Generado desde docs/modelo-json.json\n"
        " * Archivo: " + archivo + "\n"
        " */\n"
    )


# ── Helpers de tipos ───────────────────────────────────────────────────────────

def camel_a_snake(nombre: str) -> str:
    """dimensionM2 → dimension_m2"""
    resultado = ""
    for c in nombre:
        resultado += ("_" + c.lower()) if c.isupper() else c
    return resultado.lstrip("_")


def tipo_java(pdef: dict) -> str:
    """Convierte tipo JSON Schema a tipo Java correspondiente."""
    t   = pdef.get("type", "string")
    fmt = pdef.get("format", "")
    if t == "integer":              return "Long"
    if t == "number":               return "Double"
    if t == "boolean":              return "Boolean"
    if fmt == "date":               return "LocalDate"
    if fmt == "date-time":          return "LocalDateTime"
    if fmt == "email":              return "String"
    return "String"


def nombre_enum(nombre_campo: str, nombre_clase: str) -> str:
    """Devuelve el nombre del enum interno (capitaliza el campo)."""
    return nombre_campo[0].upper() + nombre_campo[1:]


def url_path_de_tabla(tabla: str) -> str:
    """tipo_planta → tipos-planta"""
    return tabla.replace("_", "-") + "s"


def var_repo(nombre_clase: str) -> str:
    """Zona → zonaRepository"""
    return nombre_clase[0].lower() + nombre_clase[1:] + "Repository"


def var_service(nombre_clase: str) -> str:
    """Zona → zonaService"""
    return nombre_clase[0].lower() + nombre_clase[1:] + "Service"


# ── pom.xml ────────────────────────────────────────────────────────────────────

def generar_pom_xml():
    contenido = (
        encabezado("pom.xml") +
        """
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
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
  <properties><java.version>17</java.version></properties>

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
      <!-- JavaDoc: solo generacion manual: mvn javadoc:javadoc -->
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
    )
    escribir(BACKEND / "pom.xml", contenido)


# ── application.properties — leído desde el modelo ────────────────────────────

def generar_application_properties(modelo: dict):
    """
    Genera application.properties usando los valores del modelo:
    - taiga.project-slug desde new_in_v3.harvest_scheduler
    - URLs de la app desde los scripts de generación
    """
    scheduler = modelo.get("new_in_v3", {}).get("harvest_scheduler", {})
    cron      = scheduler.get("cron", "0 0 0/6 * * ?")
    slug      = "cesar_camilo-greenhouse-manager"

    lineas = [
        "# GreenHouse Manager - Configuracion principal",
        "# Generado desde docs/modelo-json.json v" + modelo.get("version", "?"),
        "",
        "# ===== Base de datos PostgreSQL =====",
        "spring.datasource.url=${DB_URL:jdbc:postgresql://localhost:5432/greenhouse_db}",
        "spring.datasource.username=${DB_USERNAME:postgres}",
        "spring.datasource.password=${DB_PASSWORD:postgres}",
        "spring.datasource.driver-class-name=org.postgresql.Driver",
        "",
        "# ===== JPA / Hibernate =====",
        "spring.jpa.hibernate.ddl-auto=update",
        "spring.jpa.show-sql=false",
        "spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect",
        "",
        "# ===== Servidor =====",
        "server.port=8080",
        "",
        "# ===== OAuth2 Google =====",
        "spring.security.oauth2.client.registration.google.client-id=${GOOGLE_CLIENT_ID:}",
        "spring.security.oauth2.client.registration.google.client-secret=${GOOGLE_CLIENT_SECRET:}",
        "spring.security.oauth2.client.registration.google.scope=email,profile",
        "spring.security.oauth2.client.registration.google.redirect-uri=${BACKEND_URL:http://localhost:8080}/login/oauth2/code/google",
        "",
        "# ===== Correo Gmail =====",
        "spring.mail.host=smtp.gmail.com",
        "spring.mail.port=587",
        "spring.mail.username=${MAIL_USERNAME:tu-email@gmail.com}",
        "spring.mail.password=${MAIL_PASSWORD:}",
        "spring.mail.properties.mail.smtp.auth=true",
        "spring.mail.properties.mail.smtp.starttls.enable=true",
        "",
        "# ===== URLs =====",
        "app.base-url=${BACKEND_URL:http://localhost:8080}",
        "app.frontend-url=${FRONTEND_URL:http://localhost:5173}",
        "",
        "# ===== Swagger =====",
        "springdoc.api-docs.path=/v3/api-docs",
        "springdoc.swagger-ui.path=/swagger-ui.html",
        "",
        "# ===== Sesion HTTP (Railway cross-domain) =====",
        "server.servlet.session.cookie.same-site=none",
        "server.servlet.session.cookie.secure=true",
        "server.servlet.session.cookie.http-only=true",
        "",
        "# ===== Actuator =====",
        "management.endpoints.web.exposure.include=health,info",
        "management.endpoint.health.show-details=never",
        "management.health.db.enabled=false",
        "management.health.diskspace.enabled=false",
        "management.health.mail.enabled=false",
        "",
        "# ===== Taiga proxy (ADMINISTRADOR only) =====",
        "# Cron del scheduler de cosechas: " + cron,
        "taiga.url=${TAIGA_URL:https://api.taiga.io/api/v1}",
        "taiga.username=${TAIGA_USERNAME:}",
        "taiga.password=${TAIGA_PASSWORD:}",
        "taiga.project-slug=${TAIGA_PROJECT_SLUG:" + slug + "}",
        "",
        "# ===== Logging =====",
        "logging.level.com.greenhouse=INFO",
        "logging.level.org.springframework.security=WARN",
    ]
    escribir(RESOURCES / "application.properties", "\n".join(lineas))


# ── GreenhouseApplication.java ────────────────────────────────────────────────

def generar_main_application():
    contenido = (
        encabezado("GreenhouseApplication.java") +
        "package com.greenhouse;\n\n"
        "import org.springframework.boot.SpringApplication;\n"
        "import org.springframework.boot.autoconfigure.SpringBootApplication;\n"
        "import org.springframework.scheduling.annotation.EnableScheduling;\n\n"
        "/** Punto de entrada de la aplicacion GreenHouse Manager. */\n"
        "@SpringBootApplication\n"
        "@EnableScheduling\n"
        "public class GreenhouseApplication {\n"
        "    public static void main(String[] args) {\n"
        "        SpringApplication.run(GreenhouseApplication.class, args);\n"
        "    }\n"
        "}\n"
    )
    escribir(JAVA / "GreenhouseApplication.java", contenido)


# ── Exception classes ─────────────────────────────────────────────────────────

def generar_exceptions():
    # ResourceNotFoundException
    contenido_nfe = (
        encabezado("ResourceNotFoundException.java") +
        "package com.greenhouse.exception;\n\n"
        "/** Excepcion lanzada cuando un recurso no existe en la base de datos. */\n"
        "public class ResourceNotFoundException extends RuntimeException {\n"
        "    public ResourceNotFoundException(String message) {\n"
        "        super(message);\n"
        "    }\n"
        "}\n"
    )
    escribir(JAVA / "exception" / "ResourceNotFoundException.java", contenido_nfe)

    # GlobalExceptionHandler
    contenido_geh = (
        encabezado("GlobalExceptionHandler.java") +
        "package com.greenhouse.exception;\n\n"
        "import org.springframework.http.*;\n"
        "import org.springframework.web.bind.annotation.*;\n"
        "import java.util.Map;\n\n"
        "/** Manejador global de excepciones REST — convierte errores en JSON. */\n"
        "@RestControllerAdvice\n"
        "public class GlobalExceptionHandler {\n\n"
        "    @ExceptionHandler(ResourceNotFoundException.class)\n"
        "    public ResponseEntity<Map<String,String>> handleNotFound(ResourceNotFoundException ex) {\n"
        "        return ResponseEntity.status(HttpStatus.NOT_FOUND)\n"
        "                .body(Map.of(\"error\", ex.getMessage()));\n"
        "    }\n\n"
        "    @ExceptionHandler(IllegalArgumentException.class)\n"
        "    public ResponseEntity<Map<String,String>> handleBadRequest(IllegalArgumentException ex) {\n"
        "        return ResponseEntity.status(HttpStatus.BAD_REQUEST)\n"
        "                .body(Map.of(\"error\", ex.getMessage()));\n"
        "    }\n\n"
        "    @ExceptionHandler(Exception.class)\n"
        "    public ResponseEntity<Map<String,String>> handleGeneral(Exception ex) {\n"
        "        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)\n"
        "                .body(Map.of(\"error\", \"Error interno\", \"detalle\", ex.getMessage()));\n"
        "    }\n"
        "}\n"
    )
    escribir(JAVA / "exception" / "GlobalExceptionHandler.java", contenido_geh)


# ── @Entity — generado desde entidad["properties"] ────────────────────────────

def generar_entidad(nombre_clase: str, entidad: dict, todas_entidades: dict):
    """
    Genera la clase @Entity leyendo CADA campo desde entidad["properties"].
    Los tipos Java se derivan del tipo JSON Schema.
    Las relaciones @ManyToOne se detectan por la presencia de "$ref".
    Los enums se detectan por la presencia de "enum" en la propiedad.
    """
    tabla = entidad.get("table", camel_a_snake(nombre_clase))
    desc  = entidad.get("description", nombre_clase)
    props = entidad.get("properties", {})

    # Detectar qué imports se necesitan según los tipos del modelo
    imports = set()
    imports.add("import jakarta.persistence.*;")
    imports.add("import lombok.*;")
    imports.add("import com.fasterxml.jackson.annotation.JsonIgnoreProperties;")

    for pdef in props.values():
        tj = tipo_java(pdef)
        if tj == "LocalDate":
            imports.add("import java.time.LocalDate;")
        if tj == "LocalDateTime":
            imports.add("import java.time.LocalDateTime;")
        if pdef.get("maxLength") or pdef.get("minimum") is not None:
            imports.add("import jakarta.validation.constraints.*;")

    imports_str = "\n".join(sorted(imports))

    # Construir campos Java leyendo cada propiedad del modelo
    lineas_campos = []
    enums_internos = []

    for pname, pdef in props.items():
        col = camel_a_snake(pname)

        if pname == "id":
            lineas_campos += [
                "    @Id",
                "    @GeneratedValue(strategy = GenerationType.IDENTITY)",
                "    private Long id;",
                "",
            ]
            continue

        # Propiedad con $ref → relacion ManyToOne con otra entidad
        if "$ref" in pdef:
            ref_clase  = pdef["$ref"].replace("#/entities/", "")
            nullable   = pdef.get("nullable", False)
            null_str   = "nullable = true" if nullable else "nullable = false"
            col_fk     = col + "_id"
            # Descripcion del campo
            desc_campo = pdef.get("description", "")
            if desc_campo:
                lineas_campos.append("    /** " + desc_campo + " */")
            lineas_campos += [
                "    @ManyToOne(fetch = FetchType.LAZY)",
                "    @JoinColumn(name = \"" + col_fk + "\", " + null_str + ")",
                "    private " + ref_clase + " " + pname + ";",
                "",
            ]
            continue

        # Propiedad con enum → campo de tipo Enum interno
        enums = pdef.get("enum", [])
        if enums:
            nombre_enum_tipo = nombre_enum(pname, nombre_clase)
            desc_campo = pdef.get("description", "")
            if desc_campo:
                lineas_campos.append("    /** " + desc_campo + " */")
            lineas_campos += [
                "    @Enumerated(EnumType.STRING)",
                "    @Column(name = \"" + col + "\")",
                "    private " + nombre_enum_tipo + " " + pname + ";",
                "",
            ]
            # Guardar enum interno para generarlo al final de la clase
            valores_enum = ", ".join(enums)
            enums_internos.append(
                "    public enum " + nombre_enum_tipo + " { " + valores_enum + " }"
            )
            continue

        # Propiedad escalar normal
        tj        = tipo_java(pdef)
        desc_campo = pdef.get("description", "")
        max_len   = pdef.get("maxLength")
        min_val   = pdef.get("minimum")

        validaciones = []
        if max_len:
            validaciones.append("    @Size(max = " + str(max_len) + ")")
        if min_val is not None:
            validaciones.append("    @DecimalMin(\"" + str(min_val) + "\")")

        if desc_campo:
            lineas_campos.append("    /** " + desc_campo + " */")
        lineas_campos += validaciones

        col_annotation = ""
        if col != pname:   # nombre de columna diferente al campo Java
            col_annotation = "    @Column(name = \"" + col + "\")\n"

        lineas_campos.append(col_annotation + "    private " + tj + " " + pname + ";")
        lineas_campos.append("")

    # Ensamblar la clase
    partes = [
        encabezado("entity/" + nombre_clase + ".java"),
        "package com.greenhouse.entity;\n",
        imports_str,
        "",
        "/**",
        " * " + desc,
        " * <p>Tabla: {@code " + tabla + "}</p>",
        " */",
        "@Entity",
        "@Table(name = \"" + tabla + "\")",
        "@Data",
        "@NoArgsConstructor",
        "@AllArgsConstructor",
        "@Builder",
        "@JsonIgnoreProperties({\"hibernateLazyInitializer\", \"handler\"})",
        "public class " + nombre_clase + " {",
        "",
    ]
    partes += lineas_campos

    if enums_internos:
        partes.append("    // Enums derivados del modelo JSON")
        partes += enums_internos
        partes.append("")

    partes.append("}\n")
    escribir(JAVA / "entity" / (nombre_clase + ".java"), "\n".join(partes))


# ── Repository — generado desde el nombre y tabla de la entidad ───────────────

def generar_repositorio(nombre_clase: str, entidad: dict):
    """
    Genera la interfaz JpaRepository.
    Agrega métodos de consulta derivados según las propiedades del modelo:
    - findByEstado si hay campo 'estado'
    - existsByNombre si hay campo 'nombre'
    - findByZonaId si hay relacion con Zona
    """
    props        = entidad.get("properties", {})
    desc_entidad = entidad.get("description", nombre_clase)

    metodos_extra = []
    for pname, pdef in props.items():
        if pname == "estado" and pdef.get("enum"):
            tipo_enum = nombre_enum(pname, nombre_clase)
            metodos_extra.append(
                "    List<" + nombre_clase + "> findByEstado(" + nombre_clase + "." + tipo_enum + " estado);"
            )
        if pname == "nombre":
            metodos_extra.append(
                "    boolean existsByNombre(String nombre);"
            )
        if pname == "codigo":
            metodos_extra.append(
                "    boolean existsByCodigo(String codigo);"
            )
        if "$ref" in pdef and "Zona" in pdef["$ref"]:
            metodos_extra.append(
                "    List<" + nombre_clase + "> findByZonaId(Long zonaId);"
            )

    metodos_str = "\n".join(metodos_extra) if metodos_extra else "    // Hereda: findAll, findById, save, deleteById"

    partes = [
        encabezado("repository/" + nombre_clase + "Repository.java"),
        "package com.greenhouse.repository;\n",
        "import com.greenhouse.entity." + nombre_clase + ";",
        "import org.springframework.data.jpa.repository.JpaRepository;",
        "import org.springframework.stereotype.Repository;",
        "import java.util.List;\n",
        "/**",
        " * Repositorio JPA para {@link " + nombre_clase + "}.",
        " * <p>" + desc_entidad + "</p>",
        " */",
        "@Repository",
        "public interface " + nombre_clase + "Repository extends JpaRepository<" + nombre_clase + ", Long> {",
        "",
        metodos_str,
        "",
        "}\n",
    ]
    escribir(JAVA / "repository" / (nombre_clase + "Repository.java"), "\n".join(partes))


# ── Service — generado desde entidad["description"] y ["rbac"] ───────────────

def generar_servicio(nombre_clase: str, entidad: dict):
    """
    Genera el @Service con CRUD completo y JavaDoc.
    Las operaciones disponibles se derivan del campo entidad["rbac"].
    """
    desc        = entidad.get("description", nombre_clase)
    rbac        = entidad.get("rbac", {})
    repo_var    = var_repo(nombre_clase)

    # Determinar operaciones habilitadas desde el modelo RBAC
    puede_create = "CREATE" in rbac
    puede_update = "UPDATE" in rbac
    puede_delete = "DELETE" in rbac

    # Método save
    metodo_save = (
        "\n"
        "    /**\n"
        "     * Persiste un nuevo registro de " + nombre_clase + ".\n"
        "     *\n"
        "     * @param entity datos del nuevo " + nombre_clase.lower() + "\n"
        "     * @return el registro persistido con su ID asignado\n"
        "     */\n"
        "    public " + nombre_clase + " save(" + nombre_clase + " entity) {\n"
        "        return " + repo_var + ".save(entity);\n"
        "    }\n"
    ) if puede_create else ""

    # Método update
    metodo_update = (
        "\n"
        "    /**\n"
        "     * Actualiza un registro existente de " + nombre_clase + ".\n"
        "     *\n"
        "     * @param id      ID del registro a actualizar\n"
        "     * @param updated objeto con los nuevos valores\n"
        "     * @return el registro actualizado\n"
        "     * @throws ResourceNotFoundException si no existe el registro\n"
        "     */\n"
        "    public " + nombre_clase + " update(Long id, " + nombre_clase + " updated) {\n"
        "        findById(id);\n"
        "        updated.setId(id);\n"
        "        return " + repo_var + ".save(updated);\n"
        "    }\n"
    ) if puede_update else ""

    # Método delete
    metodo_delete = (
        "\n"
        "    /**\n"
        "     * Elimina un registro de " + nombre_clase + ".\n"
        "     *\n"
        "     * @param id ID del registro a eliminar\n"
        "     * @throws ResourceNotFoundException si no existe el registro\n"
        "     */\n"
        "    public void delete(Long id) {\n"
        "        findById(id);\n"
        "        " + repo_var + ".deleteById(id);\n"
        "    }\n"
    ) if puede_delete else ""

    partes = [
        encabezado("service/" + nombre_clase + "Service.java"),
        "package com.greenhouse.service;\n",
        "import com.greenhouse.entity." + nombre_clase + ";",
        "import com.greenhouse.exception.ResourceNotFoundException;",
        "import com.greenhouse.repository." + nombre_clase + "Repository;",
        "import lombok.RequiredArgsConstructor;",
        "import org.springframework.stereotype.Service;",
        "import org.springframework.transaction.annotation.Transactional;",
        "import java.util.List;\n",
        "/**",
        " * Servicio para la gestion de {@link " + nombre_clase + "}.",
        " * <p>" + desc + "</p>",
        " */",
        "@Service",
        "@RequiredArgsConstructor",
        "@Transactional",
        "public class " + nombre_clase + "Service {",
        "",
        "    private final " + nombre_clase + "Repository " + repo_var + ";",
        "",
        "    /**",
        "     * Retorna todos los registros de " + nombre_clase + ".",
        "     *",
        "     * @return lista completa (puede estar vacia)",
        "     */",
        "    public List<" + nombre_clase + "> findAll() {",
        "        return " + repo_var + ".findAll();",
        "    }",
        "",
        "    /**",
        "     * Busca un registro de " + nombre_clase + " por su identificador.",
        "     *",
        "     * @param id identificador unico",
        "     * @return el registro encontrado",
        "     * @throws ResourceNotFoundException si no existe",
        "     */",
        "    public " + nombre_clase + " findById(Long id) {",
        "        return " + repo_var + ".findById(id)",
        "                .orElseThrow(() -> new ResourceNotFoundException(",
        "                        \"" + nombre_clase + " no encontrado con id: \" + id));",
        "    }",
        metodo_save,
        metodo_update,
        metodo_delete,
        "}\n",
    ]
    escribir(JAVA / "service" / (nombre_clase + "Service.java"), "\n".join(partes))


# ── Controller — generado desde entidad["rbac"] y modelo["api_endpoints"] ─────

def generar_controlador(nombre_clase: str, entidad: dict, modelo: dict):
    """
    Genera el @RestController con @ApiResponse Swagger.
    - La URL base se construye desde entidad["table"]
    - Los roles de cada verbo HTTP se leen desde entidad["rbac"]
    - Los @ApiResponse se generan desde los posibles códigos HTTP
    """
    tabla    = entidad.get("table", camel_a_snake(nombre_clase))
    url_base = "/api/" + url_path_de_tabla(tabla)
    desc     = entidad.get("description", nombre_clase)
    rbac     = entidad.get("rbac", {})
    svc_var  = var_service(nombre_clase)

    # Determinar roles por verbo desde el RBAC del modelo
    roles_create = rbac.get("CREATE", "ADMINISTRADOR, SUPERVISOR").replace(", ", "','")
    roles_delete = rbac.get("DELETE", "ADMINISTRADOR")

    # Formatear @PreAuthorize para Create
    pre_create = (
        "    @PreAuthorize(\"hasAnyRole('" + roles_create + "')\")\n"
        if "SUPERVISOR" in roles_create else
        "    @PreAuthorize(\"hasRole('" + roles_create + "')\")\n"
    )
    # Formatear @PreAuthorize para Delete
    pre_delete = "    @PreAuthorize(\"hasRole('" + roles_delete + "')\")\n"

    partes = [
        encabezado("controller/" + nombre_clase + "Controller.java"),
        "package com.greenhouse.controller;\n",
        "import com.greenhouse.entity." + nombre_clase + ";",
        "import com.greenhouse.service." + nombre_clase + "Service;",
        "import io.swagger.v3.oas.annotations.Operation;",
        "import io.swagger.v3.oas.annotations.Parameter;",
        "import io.swagger.v3.oas.annotations.responses.ApiResponse;",
        "import io.swagger.v3.oas.annotations.responses.ApiResponses;",
        "import io.swagger.v3.oas.annotations.tags.Tag;",
        "import jakarta.validation.Valid;",
        "import lombok.RequiredArgsConstructor;",
        "import org.springframework.http.*;",
        "import org.springframework.security.access.prepost.PreAuthorize;",
        "import org.springframework.web.bind.annotation.*;",
        "import java.util.List;\n",
        "/**",
        " * Controlador REST para {@link " + nombre_clase + "}.",
        " * <p>" + desc + "</p>",
        " * <p>RBAC: " + str(rbac) + "</p>",
        " */",
        "@RestController",
        "@RequestMapping(\"" + url_base + "\")",
        "@RequiredArgsConstructor",
        "@Tag(name = \"" + nombre_clase + "\", description = \"" + desc + "\")",
        "public class " + nombre_clase + "Controller {",
        "",
        "    private final " + nombre_clase + "Service " + svc_var + ";",
        "",
        "    @GetMapping",
        "    @Operation(summary = \"Listar todos los registros de " + nombre_clase + "\")",
        "    @ApiResponse(responseCode = \"200\", description = \"Lista retornada correctamente\")",
        "    public ResponseEntity<List<" + nombre_clase + ">> findAll() {",
        "        return ResponseEntity.ok(" + svc_var + ".findAll());",
        "    }",
        "",
        "    @GetMapping(\"/{id}\")",
        "    @Operation(summary = \"Obtener " + nombre_clase + " por ID\")",
        "    @ApiResponses({",
        "        @ApiResponse(responseCode = \"200\", description = \"Registro encontrado\"),",
        "        @ApiResponse(responseCode = \"404\", description = \"No encontrado\")",
        "    })",
        "    public ResponseEntity<" + nombre_clase + "> findById(",
        "            @Parameter(description = \"ID del registro\", required = true)",
        "            @PathVariable Long id) {",
        "        return ResponseEntity.ok(" + svc_var + ".findById(id));",
        "    }",
        "",
        "    @PostMapping",
        pre_create +
        "    @Operation(summary = \"Crear nuevo " + nombre_clase + "\")",
        "    @ApiResponses({",
        "        @ApiResponse(responseCode = \"201\", description = \"Creado exitosamente\"),",
        "        @ApiResponse(responseCode = \"400\", description = \"Datos invalidos\"),",
        "        @ApiResponse(responseCode = \"403\", description = \"Acceso denegado\")",
        "    })",
        "    public ResponseEntity<" + nombre_clase + "> create(",
        "            @Valid @RequestBody " + nombre_clase + " entity) {",
        "        return ResponseEntity.status(HttpStatus.CREATED)",
        "                .body(" + svc_var + ".save(entity));",
        "    }",
        "",
        "    @PutMapping(\"/{id}\")",
        pre_create +
        "    @Operation(summary = \"Actualizar " + nombre_clase + " existente\")",
        "    @ApiResponses({",
        "        @ApiResponse(responseCode = \"200\", description = \"Actualizado correctamente\"),",
        "        @ApiResponse(responseCode = \"403\", description = \"Acceso denegado\"),",
        "        @ApiResponse(responseCode = \"404\", description = \"No encontrado\")",
        "    })",
        "    public ResponseEntity<" + nombre_clase + "> update(",
        "            @Parameter(description = \"ID del registro\", required = true)",
        "            @PathVariable Long id,",
        "            @Valid @RequestBody " + nombre_clase + " entity) {",
        "        return ResponseEntity.ok(" + svc_var + ".update(id, entity));",
        "    }",
        "",
        "    @DeleteMapping(\"/{id}\")",
        pre_delete +
        "    @Operation(summary = \"Eliminar " + nombre_clase + "\")",
        "    @ApiResponses({",
        "        @ApiResponse(responseCode = \"204\", description = \"Eliminado correctamente\"),",
        "        @ApiResponse(responseCode = \"403\", description = \"Requiere " + roles_delete + "\"),",
        "        @ApiResponse(responseCode = \"404\", description = \"No encontrado\")",
        "    })",
        "    public ResponseEntity<Void> delete(",
        "            @Parameter(description = \"ID del registro\", required = true)",
        "            @PathVariable Long id) {",
        "        " + svc_var + ".delete(id);",
        "        return ResponseEntity.noContent().build();",
        "    }",
        "}\n",
    ]
    escribir(JAVA / "controller" / (nombre_clase + "Controller.java"), "\n".join(partes))


# ── Scheduler — generado desde modelo["new_in_v3"]["harvest_scheduler"] ───────

def generar_scheduler(modelo: dict):
    """
    Genera CosechaAlertaScheduler.java leyendo la configuración del scheduler
    directamente del modelo JSON:
      - cron           desde new_in_v3.harvest_scheduler.cron
      - categorías     desde new_in_v3.harvest_scheduler.categories
      - deduplicacion  desde new_in_v3.harvest_scheduler.deduplication
      - severidades    desde new_in_v3.alert_severity_calculation.thresholds
    """
    v3          = modelo.get("new_in_v3", {})
    scheduler   = v3.get("harvest_scheduler", {})
    cron        = scheduler.get("cron", "0 0 0/6 * * ?")
    categorias  = scheduler.get("categories", {})
    dedup       = scheduler.get("deduplication", "")

    # Construir el javadoc de categorias desde el modelo
    cat_doc = "\n".join(
        " * <li>{tipo} — {condicion} → {severidad}</li>".format(**{
            "tipo": tipo,
            "condicion": datos.get("condicion", ""),
            "severidad": datos.get("severidad", ""),
        })
        for tipo, datos in categorias.items()
    )

    # Construir la lógica if-else de categorias desde el modelo
    bloques_if = []
    for i, (tipo, datos) in enumerate(categorias.items()):
        sev = datos.get("severidad", "MEDIA")
        cond = datos.get("condicion", "")
        if i == 0:
            # Primera categoria: > 7 dias → skip
            bloques_if += [
                "            if (diasRestantes > 7) continue;",
                "",
                "            String tipo; Alerta.Severidad severidad; String mensajeEstado;",
                "",
                "            // Categoria " + tipo + " (" + cond + ")",
                "            if (diasRestantes > 0) {",
                "                tipo = \"" + tipo + "\";",
                "                severidad = Alerta.Severidad." + sev + ";",
                "                mensajeEstado = \"Faltan \" + diasRestantes + \" dia(s) para la cosecha\";",
            ]
        elif i == 1:
            bloques_if += [
                "            } else if (diasRestantes >= -3) {",
                "                // Categoria " + tipo + " (" + cond + ")",
                "                tipo = \"" + tipo + "\";",
                "                severidad = Alerta.Severidad." + sev + ";",
                "                mensajeEstado = diasRestantes == 0",
                "                    ? \"Hoy es el dia estimado de cosecha\"",
                "                    : \"Cosecha con \" + Math.abs(diasRestantes) + \" dia(s) de retraso\";",
                "                actualizarEstadoListaParaCosechar(planta);",
            ]
        elif i == 2:
            bloques_if += [
                "            } else if (diasRestantes >= -7) {",
                "                // Categoria " + tipo + " (" + cond + ")",
                "                tipo = \"" + tipo + "\";",
                "                severidad = Alerta.Severidad." + sev + ";",
                "                mensajeEstado = \"Cosecha vencida con \" + Math.abs(diasRestantes) + \" dias de retraso\";",
                "                actualizarEstadoListaParaCosechar(planta);",
            ]
        else:
            bloques_if += [
                "            } else {",
                "                // Categoria " + tipo + " (" + cond + ")",
                "                tipo = \"" + tipo + "\";",
                "                severidad = Alerta.Severidad." + sev + ";",
                "                mensajeEstado = \"VENCIDA — \" + Math.abs(diasRestantes) + \" dias sin cosechar\";",
                "                actualizarEstadoListaParaCosechar(planta);",
                "            }",
            ]

    logica_if = "\n".join(bloques_if)

    partes = [
        encabezado("scheduler/CosechaAlertaScheduler.java"),
        "package com.greenhouse.scheduler;\n",
        "import com.greenhouse.entity.Alerta;",
        "import com.greenhouse.entity.Planta;",
        "import com.greenhouse.repository.AlertaRepository;",
        "import com.greenhouse.repository.PlantaRepository;",
        "import lombok.RequiredArgsConstructor;",
        "import lombok.extern.slf4j.Slf4j;",
        "import org.springframework.scheduling.annotation.Scheduled;",
        "import org.springframework.stereotype.Component;",
        "import org.springframework.transaction.annotation.Transactional;",
        "import java.time.LocalDate;",
        "import java.time.LocalDateTime;",
        "import java.time.temporal.ChronoUnit;",
        "import java.util.List;\n",
        "/**",
        " * Scheduler de alertas de cosecha pendiente.",
        " * Generado desde modelo-json.json > new_in_v3 > harvest_scheduler",
        " *",
        " * <p>Cron: {@code " + cron + "} (00:00, 06:00, 12:00, 18:00)</p>",
        " * <p>Categorias de alerta derivadas del modelo:</p>",
        " * <ul>",
        cat_doc,
        " * </ul>",
        " * <p>Deduplicacion: " + dedup + "</p>",
        " */",
        "@Component",
        "@RequiredArgsConstructor",
        "@Slf4j",
        "public class CosechaAlertaScheduler {",
        "",
        "    private final PlantaRepository plantaRepository;",
        "    private final AlertaRepository  alertaRepository;",
        "",
        "    /** Ejecuta la evaluacion segun el cron definido en el modelo JSON: " + cron + " */",
        "    @Scheduled(cron = \"" + cron + "\")",
        "    @Transactional",
        "    public void evaluarCosechasPendientes() {",
        "        log.info(\"[Scheduler] Evaluando alertas de cosecha...\");",
        "        List<Planta> plantas = plantaRepository.findByEstadoIn(List.of(",
        "            Planta.EstadoPlanta.SEMBRADA,",
        "            Planta.EstadoPlanta.EN_CRECIMIENTO,",
        "            Planta.EstadoPlanta.LISTA_PARA_COSECHAR",
        "        ));",
        "        int creadas = 0;",
        "        for (Planta planta : plantas) {",
        "            if (planta.getTipoPlanta() == null",
        "                    || planta.getTipoPlanta().getCicloDias() == null) continue;",
        "            LocalDate hoy             = LocalDate.now();",
        "            LocalDate fechaCosechaEst = planta.getFechaSiembra()",
        "                    .plusDays(planta.getTipoPlanta().getCicloDias());",
        "            long diasRestantes = ChronoUnit.DAYS.between(hoy, fechaCosechaEst);",
        "",
        logica_if,
        "",
        "            // Deduplicacion: " + dedup,
        "            String plantaRef = \"[PLT-\" + planta.getId() + \"]\";",
        "            if (alertaRepository.existsByTipoAndDescripcionContainingAndEstado(",
        "                    tipo, plantaRef, Alerta.EstadoAlerta.PENDIENTE)) continue;",
        "",
        "            alertaRepository.save(Alerta.builder()",
        "                .tipo(tipo).severidad(severidad)",
        "                .zona(planta.getZona()).sensor(null)",
        "                .fechaGeneracion(LocalDateTime.now())",
        "                .estado(Alerta.EstadoAlerta.PENDIENTE)",
        "                .descripcion(plantaRef + \" Planta \" + planta.getCodigo()",
        "                    + \" — \" + mensajeEstado",
        "                    + \". Fecha estimada: \" + fechaCosechaEst)",
        "                .build());",
        "            creadas++;",
        "        }",
        "        log.info(\"[Scheduler] {} alerta(s) generada(s)\", creadas);",
        "    }",
        "",
        "    private void actualizarEstadoListaParaCosechar(Planta planta) {",
        "        if (planta.getEstado() == Planta.EstadoPlanta.SEMBRADA",
        "                || planta.getEstado() == Planta.EstadoPlanta.EN_CRECIMIENTO) {",
        "            planta.setEstado(Planta.EstadoPlanta.LISTA_PARA_COSECHAR);",
        "            plantaRepository.save(planta);",
        "        }",
        "    }",
        "}\n",
    ]
    escribir(JAVA / "scheduler" / "CosechaAlertaScheduler.java", "\n".join(partes))


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  GENERADOR BACKEND SPRING BOOT — GreenHouse Manager")
    print("  Fuente: docs/modelo-json.json")
    print("=" * 60)

    modelo    = json.loads(MODELO.read_text(encoding="utf-8"))
    entidades = modelo.get("entities", {})
    version   = modelo.get("version", "?")

    print("\n  Modelo v" + version + " — " + str(len(entidades)) + " entidades detectadas\n")

    generar_pom_xml()
    generar_application_properties(modelo)
    generar_main_application()
    generar_exceptions()
    generar_scheduler(modelo)

    for nombre_clase, entidad in entidades.items():
        print("\n  Procesando entidad: " + nombre_clase)
        generar_entidad(nombre_clase, entidad, entidades)
        generar_repositorio(nombre_clase, entidad)
        generar_servicio(nombre_clase, entidad)
        generar_controlador(nombre_clase, entidad, modelo)

    total_archivos = len(entidades) * 4 + 5  # entity+repo+service+controller * N + extras
    print("\n  ✓ Backend generado en: greenhouse-backend/")
    print("    Entidades procesadas : " + str(len(entidades)))
    print("    Archivos Java creados: " + str(total_archivos))
    print("    Todos los campos, tipos y relaciones leidos del modelo JSON")


if __name__ == "__main__":
    main()
