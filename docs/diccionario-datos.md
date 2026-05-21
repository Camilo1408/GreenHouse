# GreenHouse Manager — Diccionario de Datos

**Autores:** Cesar Camilo Hoyos Diaz - Alvaro Julian Delgado Mena  
**Fecha:** 2026  
**Asignatura:** Electiva de Ingeniería de Software  
**Base de datos:** PostgreSQL 18 | **Esquema:** `public`

---

## Tabla: `zona`

Representa una zona física dentro del invernadero. Las zonas agrupan plantas y sensores con condiciones ambientales similares.

| Columna                 | Tipo           | Nulo |  Único  | Default        | Restricción                        | Descripción                                             |
| ----------------------- | -------------- | :--: | :-----: | -------------- | ---------------------------------- | ------------------------------------------------------- |
| `id`                    | `BIGINT`       |  No  | Sí (PK) | auto_increment | PK                                 | Identificador único autogenerado                        |
| `nombre`                | `VARCHAR(100)` |  No  |   Sí    | —              | NOT NULL, UNIQUE                   | Nombre descriptivo de la zona (ej: "Zona A - Tomates")  |
| `dimension_m2`          | `DOUBLE`       |  Sí  |   No    | —              | > 0.1                              | Superficie en metros cuadrados                          |
| `capacidad_max_plantas` | `INT`          |  Sí  |   No    | —              | ≥ 1                                | Cantidad máxima de plantas que caben en la zona         |
| `estado`                | `VARCHAR(20)`  |  No  |   No    | —              | ACTIVA, EN_MANTENIMIENTO, INACTIVA | Estado operativo actual                                 |
| `ubicacion`             | `VARCHAR(200)` |  Sí  |   No    | —              | —                                  | Descripción física de la ubicación (ej: "Sector Norte") |

---

## Tabla: `tipo_planta`

Catálogo de especies o variedades de plantas cultivables. Define los parámetros ambientales ideales para cada especie.

| Columna               | Tipo           | Nulo |  Único  | Default        | Restricción      | Descripción                                |
| --------------------- | -------------- | :--: | :-----: | -------------- | ---------------- | ------------------------------------------ |
| `id`                  | `BIGINT`       |  No  | Sí (PK) | auto_increment | PK               | Identificador único autogenerado           |
| `nombre`              | `VARCHAR(100)` |  No  |   Sí    | —              | NOT NULL, UNIQUE | Nombre de la especie (ej: "Tomate Cherry") |
| `descripcion`         | `VARCHAR(500)` |  Sí  |   No    | —              | —                | Descripción general de la especie          |
| `temp_min`            | `DOUBLE`       |  No  |   No    | —              | 0.0 – 60.0°C     | Temperatura mínima óptima en °C            |
| `temp_max`            | `DOUBLE`       |  No  |   No    | —              | 0.0 – 60.0°C     | Temperatura máxima óptima en °C            |
| `humedad_min`         | `DOUBLE`       |  No  |   No    | —              | 0.0 – 100.0%     | Humedad relativa mínima óptima             |
| `humedad_max`         | `DOUBLE`       |  No  |   No    | —              | 0.0 – 100.0%     | Humedad relativa máxima óptima             |
| `ciclo_dias`          | `INT`          |  No  |   No    | —              | ≥ 1              | Días desde siembra hasta cosecha           |
| `cuidados_especiales` | `VARCHAR(500)` |  Sí  |   No    | —              | —                | Instrucciones específicas de manejo        |

---

## Tabla: `empleado`

Usuarios del sistema con acceso y responsabilidades dentro del invernadero. Soporta autenticación local y OAuth2 con Google.

| Columna            | Tipo           | Nulo |  Único  | Default        | Restricción                         | Descripción                                                         |
| ------------------ | -------------- | :--: | :-----: | -------------- | ----------------------------------- | ------------------------------------------------------------------- |
| `id`               | `BIGINT`       |  No  | Sí (PK) | auto_increment | PK                                  | Identificador único autogenerado                                    |
| `nombre_completo`  | `VARCHAR(150)` |  No  |   No    | —              | NOT NULL                            | Nombre y apellidos del empleado                                     |
| `email`            | `VARCHAR(255)` |  No  |   Sí    | —              | NOT NULL, UNIQUE                    | Correo electrónico (usado como username)                            |
| `password_hash`    | `VARCHAR(255)` |  Sí  |   No    | NULL           | —                                   | Hash BCrypt de la contraseña (NULL si usa Google)                   |
| `rol`              | `VARCHAR(20)`  |  No  |   No    | —              | ADMINISTRADOR, SUPERVISOR, EMPLEADO | Nivel de acceso en el sistema                                       |
| `telefono`         | `VARCHAR(20)`  |  Sí  |   No    | —              | —                                   | Número de contacto                                                  |
| `estado`           | `VARCHAR(10)`  |  No  |   No    | `ACTIVO`       | ACTIVO, INACTIVO                    | Estado de la cuenta                                                 |
| `fecha_ingreso`    | `DATE`         |  Sí  |   No    | —              | —                                   | Fecha de contratación                                               |
| `email_verificado` | `BOOLEAN`      |  Sí  |   No    | `false`        | —                                   | `true` cuando el correo fue confirmado (requerido para login local) |
| `auth_provider`    | `VARCHAR(10)`  |  Sí  |   No    | `LOCAL`        | LOCAL, GOOGLE                       | Origen del registro del usuario                                     |

---

## Tabla: `planta`

Registro individual de cada planta cultivada. Permite trazabilidad completa desde siembra hasta cosecha.

| Columna          | Tipo           | Nulo |  Único  | Default        | Restricción                                                      | Descripción                                |
| ---------------- | -------------- | :--: | :-----: | -------------- | ---------------------------------------------------------------- | ------------------------------------------ |
| `id`             | `BIGINT`       |  No  | Sí (PK) | auto_increment | PK                                                               | Identificador único autogenerado           |
| `codigo`         | `VARCHAR(50)`  |  No  |   Sí    | —              | NOT NULL, UNIQUE                                                 | Código físico del ejemplar (ej: "TOM-001") |
| `tipo_planta_id` | `BIGINT`       |  No  |   No    | —              | FK → tipo_planta                                                 | Especie de la planta                       |
| `zona_id`        | `BIGINT`       |  No  |   No    | —              | FK → zona                                                        | Zona donde está ubicada físicamente        |
| `fecha_siembra`  | `DATE`         |  No  |   No    | —              | NOT NULL                                                         | Fecha en que se sembró                     |
| `estado`         | `VARCHAR(25)`  |  No  |   No    | —              | SEMBRADA, EN_CRECIMIENTO, LISTA_PARA_COSECHAR, COSECHADA, MUERTA | Etapa actual del ciclo de vida             |
| `observaciones`  | `VARCHAR(500)` |  Sí  |   No    | —              | —                                                                | Notas libres sobre el ejemplar             |

---

## Tabla: `sensor`

Dispositivos físicos instalados en las zonas para medir variables ambientales.

| Columna             | Tipo          | Nulo |  Único  | Default        | Restricción                        | Descripción                                        |
| ------------------- | ------------- | :--: | :-----: | -------------- | ---------------------------------- | -------------------------------------------------- |
| `id`                | `BIGINT`      |  No  | Sí (PK) | auto_increment | PK                                 | Identificador único autogenerado                   |
| `codigo`            | `VARCHAR(50)` |  No  |   Sí    | —              | NOT NULL, UNIQUE                   | Código físico del sensor (ej: "SENS-TA-01")        |
| `tipo_sensor`       | `VARCHAR(15)` |  No  |   No    | —              | TEMPERATURA, HUMEDAD, PH, CO2, LUZ | Variable ambiental que mide                        |
| `zona_id`           | `BIGINT`      |  No  |   No    | —              | FK → zona                          | Zona donde está instalado                          |
| `estado`            | `VARCHAR(20)` |  No  |   No    | `ACTIVO`       | ACTIVO, INACTIVO, EN_MANTENIMIENTO | Estado operativo                                   |
| `fecha_instalacion` | `DATE`        |  Sí  |   No    | —              | —                                  | Fecha en que se instaló                            |
| `umbral_min`        | `DOUBLE`      |  Sí  |   No    | —              | —                                  | Valor mínimo aceptable (genera alerta si se cruza) |
| `umbral_max`        | `DOUBLE`      |  Sí  |   No    | —              | —                                  | Valor máximo aceptable (genera alerta si se cruza) |

---

## Tabla: `lectura_sensor`

Registro histórico de todas las mediciones tomadas por los sensores. Base de datos de telemetría ambiental.

| Columna      | Tipo          | Nulo |  Único  | Default        | Restricción        | Descripción                            |
| ------------ | ------------- | :--: | :-----: | -------------- | ------------------ | -------------------------------------- |
| `id`         | `BIGINT`      |  No  | Sí (PK) | auto_increment | PK                 | Identificador único autogenerado       |
| `sensor_id`  | `BIGINT`      |  No  |   No    | —              | FK → sensor        | Sensor que tomó la lectura             |
| `valor`      | `DOUBLE`      |  No  |   No    | —              | NOT NULL           | Valor medido                           |
| `unidad`     | `VARCHAR(20)` |  No  |   No    | —              | NOT NULL           | Unidad de medida (°C, %, pH, ppm, lux) |
| `fecha_hora` | `TIMESTAMP`   |  No  |   No    | —              | NOT NULL           | Momento exacto de la lectura           |
| `fuente`     | `VARCHAR(15)` |  No  |   No    | —              | AUTOMATICA, MANUAL | Origen de la lectura                   |

> **Nota:** Al persistir una lectura, el sistema evalúa automáticamente si el valor supera los umbrales del sensor y genera una `alerta` si es necesario.

---

## Tabla: `alerta`

Avisos generados automáticamente cuando las lecturas de sensores superan los umbrales configurados.

| Columna            | Tipo           | Nulo |  Único  | Default        | Restricción                     | Descripción                                     |
| ------------------ | -------------- | :--: | :-----: | -------------- | ------------------------------- | ----------------------------------------------- |
| `id`               | `BIGINT`       |  No  | Sí (PK) | auto_increment | PK                              | Identificador único autogenerado                |
| `tipo`             | `VARCHAR(200)` |  No  |   No    | —              | NOT NULL                        | Categoría del evento (ej: "UMBRAL_TEMPERATURA") |
| `severidad`        | `VARCHAR(10)`  |  No  |   No    | —              | BAJA, MEDIA, ALTA, CRITICA      | Nivel de urgencia según desviación del umbral   |
| `zona_id`          | `BIGINT`       |  No  |   No    | —              | FK → zona                       | Zona afectada                                   |
| `sensor_id`        | `BIGINT`       |  Sí  |   No    | —              | FK → sensor                     | Sensor que disparó la alerta (opcional)         |
| `fecha_generacion` | `TIMESTAMP`    |  No  |   No    | —              | NOT NULL                        | Momento en que se generó la alerta              |
| `estado`           | `VARCHAR(12)`  |  No  |   No    | `PENDIENTE`    | PENDIENTE, ATENDIDA, DESCARTADA | Estado de resolución                            |
| `descripcion`      | `VARCHAR(500)` |  Sí  |   No    | —              | —                               | Detalle del evento con valores exactos          |

---

## Tabla: `cosecha`

Registro de producción obtenida de cada planta, con datos de calidad y destino del producto.

| Columna         | Tipo           | Nulo |  Único  | Default        | Restricción                      | Descripción                           |
| --------------- | -------------- | :--: | :-----: | -------------- | -------------------------------- | ------------------------------------- |
| `id`            | `BIGINT`       |  No  | Sí (PK) | auto_increment | PK                               | Identificador único autogenerado      |
| `planta_id`     | `BIGINT`       |  No  |   No    | —              | FK → planta                      | Planta cosechada                      |
| `empleado_id`   | `BIGINT`       |  No  |   No    | —              | FK → empleado                    | Empleado que realizó la cosecha       |
| `fecha_cosecha` | `DATE`         |  No  |   No    | —              | NOT NULL                         | Fecha de recolección                  |
| `peso_kg`       | `DOUBLE`       |  No  |   No    | —              | > 0.01                           | Peso en kilogramos obtenido           |
| `calidad`       | `VARCHAR(5)`   |  No  |   No    | —              | A, B, C                          | Clasificación de calidad del producto |
| `destino`       | `VARCHAR(20)`  |  No  |   No    | —              | VENTA, CONSUMO_INTERNO, DESCARTE | Destino final del producto            |
| `observaciones` | `VARCHAR(500)` |  Sí  |   No    | —              | —                                | Notas adicionales sobre la cosecha    |

---

## Tabla: `tratamiento`

Intervenciones realizadas sobre plantas individuales (fertilización, poda, pesticidas, etc.).

| Columna               | Tipo           | Nulo |  Único  | Default        | Restricción                                            | Descripción                              |
| --------------------- | -------------- | :--: | :-----: | -------------- | ------------------------------------------------------ | ---------------------------------------- |
| `id`                  | `BIGINT`       |  No  | Sí (PK) | auto_increment | PK                                                     | Identificador único autogenerado         |
| `planta_id`           | `BIGINT`       |  No  |   No    | —              | FK → planta                                            | Planta que recibió el tratamiento        |
| `empleado_id`         | `BIGINT`       |  No  |   No    | —              | FK → empleado                                          | Empleado que aplicó el tratamiento       |
| `tipo_tratamiento`    | `VARCHAR(20)`  |  No  |   No    | —              | FERTILIZACION, PESTICIDA, PODA, RIEGO_MANUAL, REVISION | Tipo de intervención                     |
| `producto_utilizado`  | `VARCHAR(150)` |  Sí  |   No    | —              | —                                                      | Nombre del producto aplicado (si aplica) |
| `dosis`               | `VARCHAR(100)` |  Sí  |   No    | —              | —                                                      | Cantidad o concentración utilizada       |
| `fecha_hora`          | `TIMESTAMP`    |  No  |   No    | —              | NOT NULL                                               | Fecha y hora de aplicación               |
| `resultado_observado` | `VARCHAR(500)` |  Sí  |   No    | —              | —                                                      | Efecto observado tras el tratamiento     |

---

## Tabla: `turno`

Asignación de empleados a zonas específicas en intervalos de tiempo para organizar el trabajo.

| Columna                  | Tipo            | Nulo |  Único  | Default        | Restricción   | Descripción                           |
| ------------------------ | --------------- | :--: | :-----: | -------------- | ------------- | ------------------------------------- |
| `id`                     | `BIGINT`        |  No  | Sí (PK) | auto_increment | PK            | Identificador único autogenerado      |
| `empleado_id`            | `BIGINT`        |  No  |   No    | —              | FK → empleado | Empleado asignado al turno            |
| `zona_id`                | `BIGINT`        |  No  |   No    | —              | FK → zona     | Zona de trabajo                       |
| `fecha_hora_inicio`      | `TIMESTAMP`     |  No  |   No    | —              | NOT NULL      | Inicio del turno                      |
| `fecha_hora_fin`         | `TIMESTAMP`     |  Sí  |   No    | —              | —             | Fin del turno (NULL si está en curso) |
| `actividades_realizadas` | `VARCHAR(1000)` |  Sí  |   No    | —              | —             | Descripción de las tareas realizadas  |

---

## Tabla: `verification_token`

Tokens de verificación de correo electrónico generados al registrar usuarios con autenticación local.

| Columna            | Tipo           | Nulo |  Único  | Default        | Restricción           | Descripción                                      |
| ------------------ | -------------- | :--: | :-----: | -------------- | --------------------- | ------------------------------------------------ |
| `id`               | `BIGINT`       |  No  | Sí (PK) | auto_increment | PK                    | Identificador único autogenerado                 |
| `token`            | `VARCHAR(255)` |  No  |   Sí    | —              | NOT NULL, UNIQUE      | UUID de un solo uso enviado por correo           |
| `empleado_id`      | `BIGINT`       |  No  |   Sí    | —              | FK → empleado, UNIQUE | Empleado dueño del token                         |
| `fecha_expiracion` | `TIMESTAMP`    |  No  |   No    | —              | NOT NULL              | Momento en que el token deja de ser válido (24h) |
| `usado`            | `BOOLEAN`      |  No  |   No    | `false`        | —                     | `true` una vez que el enlace fue cliqueado       |

---

## Resumen de tablas

| Tabla                | Propósito                     | Filas típicas |
| -------------------- | ----------------------------- | :-----------: |
| `zona`               | Áreas físicas del invernadero |    5 – 50     |
| `tipo_planta`        | Catálogo de especies          |   10 – 100    |
| `empleado`           | Usuarios del sistema          |    5 – 200    |
| `planta`             | Ejemplares individuales       |  50 – 10.000  |
| `sensor`             | Dispositivos de medición      |   10 – 500    |
| `lectura_sensor`     | Telemetría ambiental          |   100.000+    |
| `alerta`             | Eventos críticos detectados   |    1.000+     |
| `cosecha`            | Producción registrada         |     500+      |
| `tratamiento`        | Intervenciones a plantas      |    1.000+     |
| `turno`              | Asignaciones de personal      |     200+      |
| `verification_token` | Tokens de correo (temporal)   |  = empleados  |
