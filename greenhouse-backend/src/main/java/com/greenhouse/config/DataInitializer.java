/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.config;

import com.greenhouse.entity.*;
import com.greenhouse.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/**
 * Inicializador de datos de prueba.
 * Solo inserta datos si la base de datos está vacía.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final EmpleadoRepository empleadoRepo;
    private final ZonaRepository zonaRepo;
    private final TipoPlantaRepository tipoPlantaRepo;
    private final PlantaRepository plantaRepo;
    private final SensorRepository sensorRepo;
    private final LecturaSensorRepository lecturaRepo;
    private final AlertaRepository alertaRepo;
    private final TratamientoRepository tratamientoRepo;
    private final CosechaRepository cosechaRepo;
    private final TurnoRepository turnoRepo;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        if (empleadoRepo.existsByEmail("admin@greenhouse.com")) {
            log.info("Datos de prueba ya existen. Omitiendo inicialización.");
            // Asegurar que usuarios OAuth existentes tengan emailVerificado=true
            empleadoRepo.findAll().forEach(e -> {
                if (!e.isEmailVerificado()) {
                    e.setEmailVerificado(true);
                    if (e.getAuthProvider() == null) e.setAuthProvider(Empleado.AuthProvider.GOOGLE);
                    empleadoRepo.save(e);
                }
            });
            return;
        }
        log.info("Inicializando datos de prueba...");
        seed();
        log.info("Datos de prueba cargados exitosamente.");
    }

    private void seed() {

        // ── Empleados ──
        Empleado admin = empleadoRepo.save(Empleado.builder()
            .nombreCompleto("Carlos Administrador")
            .email("admin@greenhouse.com")
            .passwordHash(passwordEncoder.encode("Admin1234"))
            .rol(Empleado.RolEmpleado.ADMINISTRADOR)
            .estado(Empleado.EstadoEmpleado.ACTIVO)
            .emailVerificado(true)
            .authProvider(Empleado.AuthProvider.LOCAL)
            .telefono("3001234567")
            .fechaIngreso(LocalDate.of(2024, 1, 15))
            .build());

        Empleado supervisor = empleadoRepo.save(Empleado.builder()
            .nombreCompleto("María Supervisora")
            .email("supervisor@greenhouse.com")
            .passwordHash(passwordEncoder.encode("Super1234"))
            .rol(Empleado.RolEmpleado.SUPERVISOR)
            .estado(Empleado.EstadoEmpleado.ACTIVO)
            .emailVerificado(true)
            .authProvider(Empleado.AuthProvider.LOCAL)
            .telefono("3109876543")
            .fechaIngreso(LocalDate.of(2024, 3, 1))
            .build());

        Empleado emp1 = empleadoRepo.save(Empleado.builder()
            .nombreCompleto("Juan Pérez")
            .email("juan@greenhouse.com")
            .passwordHash(passwordEncoder.encode("Juan1234"))
            .rol(Empleado.RolEmpleado.EMPLEADO)
            .estado(Empleado.EstadoEmpleado.ACTIVO)
            .emailVerificado(true)
            .authProvider(Empleado.AuthProvider.LOCAL)
            .telefono("3207654321")
            .fechaIngreso(LocalDate.of(2024, 6, 10))
            .build());

        Empleado emp2 = empleadoRepo.save(Empleado.builder()
            .nombreCompleto("Ana Gómez")
            .email("ana@greenhouse.com")
            .passwordHash(passwordEncoder.encode("Ana12345"))
            .rol(Empleado.RolEmpleado.EMPLEADO)
            .estado(Empleado.EstadoEmpleado.ACTIVO)
            .emailVerificado(true)
            .authProvider(Empleado.AuthProvider.LOCAL)
            .telefono("3154321098")
            .fechaIngreso(LocalDate.of(2025, 1, 20))
            .build());

        // Usuario genérico con rol EMPLEADO para pruebas automatizadas (Python/Selenium)
        empleadoRepo.save(Empleado.builder()
            .nombreCompleto("Empleado Test")
            .email("empleado@greenhouse.com")
            .passwordHash(passwordEncoder.encode("Empleado1234"))
            .rol(Empleado.RolEmpleado.EMPLEADO)
            .estado(Empleado.EstadoEmpleado.ACTIVO)
            .emailVerificado(true)
            .authProvider(Empleado.AuthProvider.LOCAL)
            .telefono("3001112233")
            .fechaIngreso(LocalDate.of(2025, 6, 1))
            .build());

        // ── Zonas ──
        Zona zonaA = zonaRepo.save(Zona.builder()
            .nombre("Zona A - Tomates").dimensionM2(120.0).capacidadMaxPlantas(200)
            .estado(Zona.EstadoZona.ACTIVA).ubicacion("Sector Norte").build());

        Zona zonaB = zonaRepo.save(Zona.builder()
            .nombre("Zona B - Lechugas").dimensionM2(80.0).capacidadMaxPlantas(300)
            .estado(Zona.EstadoZona.ACTIVA).ubicacion("Sector Centro").build());

        Zona zonaC = zonaRepo.save(Zona.builder()
            .nombre("Zona C - Pimientos").dimensionM2(60.0).capacidadMaxPlantas(150)
            .estado(Zona.EstadoZona.ACTIVA).ubicacion("Sector Sur").build());

        Zona zonaD = zonaRepo.save(Zona.builder()
            .nombre("Zona D - Hierbas").dimensionM2(40.0).capacidadMaxPlantas(100)
            .estado(Zona.EstadoZona.EN_MANTENIMIENTO).ubicacion("Sector Este").build());

        // ── Tipos de planta ──
        TipoPlanta tipoTomate = tipoPlantaRepo.save(TipoPlanta.builder()
            .nombre("Tomate Cherry").temperaturaMin(18.0).temperaturaMax(28.0)
            .humedadMin(60.0).humedadMax(80.0).cicloDias(75)
            .descripcion("Tomate de fruto pequeño, ideal para ensaladas")
            .cuidadosEspeciales("Tutorear cuando alcance 30cm. Podar brotes laterales.")
            .build());

        TipoPlanta tipoLechuga = tipoPlantaRepo.save(TipoPlanta.builder()
            .nombre("Lechuga Romana").temperaturaMin(12.0).temperaturaMax(22.0)
            .humedadMin(50.0).humedadMax(70.0).cicloDias(45)
            .descripcion("Lechuga de hojas alargadas, muy nutritiva")
            .cuidadosEspeciales("Sensible al calor excesivo. Riego frecuente.")
            .build());

        TipoPlanta tipoPimiento = tipoPlantaRepo.save(TipoPlanta.builder()
            .nombre("Pimiento Rojo").temperaturaMin(20.0).temperaturaMax(30.0)
            .humedadMin(55.0).humedadMax(75.0).cicloDias(90)
            .descripcion("Pimiento dulce de color rojo")
            .cuidadosEspeciales("Requiere soporte cuando fructifica.")
            .build());

        TipoPlanta tipoAlbahaca = tipoPlantaRepo.save(TipoPlanta.builder()
            .nombre("Albahaca").temperaturaMin(16.0).temperaturaMax(26.0)
            .humedadMin(40.0).humedadMax(65.0).cicloDias(30)
            .descripcion("Hierba aromática de uso culinario")
            .cuidadosEspeciales("Pinzar flores para prolongar producción de hojas.")
            .build());

        // ── Plantas ──
        List<Planta> plantas = plantaRepo.saveAll(List.of(
            planta("TOM-001", tipoTomate, zonaA, LocalDate.of(2026, 3, 1),  Planta.EstadoPlanta.LISTA_PARA_COSECHAR),
            planta("TOM-002", tipoTomate, zonaA, LocalDate.of(2026, 3, 5),  Planta.EstadoPlanta.EN_CRECIMIENTO),
            planta("TOM-003", tipoTomate, zonaA, LocalDate.of(2026, 3,10),  Planta.EstadoPlanta.EN_CRECIMIENTO),
            planta("TOM-004", tipoTomate, zonaA, LocalDate.of(2026, 4, 1),  Planta.EstadoPlanta.SEMBRADA),
            planta("TOM-005", tipoTomate, zonaA, LocalDate.of(2026, 1,15),  Planta.EstadoPlanta.COSECHADA),
            planta("LEC-001", tipoLechuga, zonaB, LocalDate.of(2026, 4, 1), Planta.EstadoPlanta.LISTA_PARA_COSECHAR),
            planta("LEC-002", tipoLechuga, zonaB, LocalDate.of(2026, 4, 5), Planta.EstadoPlanta.EN_CRECIMIENTO),
            planta("LEC-003", tipoLechuga, zonaB, LocalDate.of(2026, 4,10), Planta.EstadoPlanta.EN_CRECIMIENTO),
            planta("LEC-004", tipoLechuga, zonaB, LocalDate.of(2026, 4,15), Planta.EstadoPlanta.SEMBRADA),
            planta("PIM-001", tipoPimiento, zonaC, LocalDate.of(2026, 2, 1),Planta.EstadoPlanta.LISTA_PARA_COSECHAR),
            planta("PIM-002", tipoPimiento, zonaC, LocalDate.of(2026, 2,15),Planta.EstadoPlanta.EN_CRECIMIENTO),
            planta("ALB-001", tipoAlbahaca, zonaB, LocalDate.of(2026, 4,20),Planta.EstadoPlanta.EN_CRECIMIENTO),
            planta("ALB-002", tipoAlbahaca, zonaB, LocalDate.of(2026, 4,25),Planta.EstadoPlanta.SEMBRADA),
            planta("TOM-006", tipoTomate, zonaA, LocalDate.of(2025,12, 1),  Planta.EstadoPlanta.MUERTA)
        ));

        // ── Sensores ──
        Sensor sTempA = sensorRepo.save(sensor("SENS-TA-01", Sensor.TipoSensor.TEMPERATURA, zonaA, 18.0, 28.0));
        Sensor sHumA  = sensorRepo.save(sensor("SENS-HA-01", Sensor.TipoSensor.HUMEDAD,     zonaA, 60.0, 80.0));
        Sensor sPhA   = sensorRepo.save(sensor("SENS-PA-01", Sensor.TipoSensor.PH,          zonaA,  5.5,  7.0));
        Sensor sTempB = sensorRepo.save(sensor("SENS-TB-01", Sensor.TipoSensor.TEMPERATURA, zonaB, 12.0, 22.0));
        Sensor sHumB  = sensorRepo.save(sensor("SENS-HB-01", Sensor.TipoSensor.HUMEDAD,     zonaB, 50.0, 70.0));
        Sensor sTempC = sensorRepo.save(sensor("SENS-TC-01", Sensor.TipoSensor.TEMPERATURA, zonaC, 20.0, 30.0));
        Sensor sCO2A  = sensorRepo.save(sensor("SENS-CO2-01", Sensor.TipoSensor.CO2,        zonaA, 400.0, 1200.0));

        // ── Lecturas de sensores ──
        LocalDateTime ahora = LocalDateTime.now();
        lecturaRepo.saveAll(List.of(
            lectura(sTempA, 24.5, "°C", ahora.minusHours(1)),
            lectura(sTempA, 25.1, "°C", ahora.minusHours(2)),
            lectura(sTempA, 31.0, "°C", ahora.minusMinutes(30)), // fuera de rango → alerta
            lectura(sHumA,  72.0, "%",  ahora.minusHours(1)),
            lectura(sHumA,  55.0, "%",  ahora.minusHours(3)),
            lectura(sPhA,    6.2, "pH", ahora.minusHours(2)),
            lectura(sTempB, 18.0, "°C", ahora.minusHours(1)),
            lectura(sHumB,  65.0, "%",  ahora.minusHours(1)),
            lectura(sTempC, 25.0, "°C", ahora.minusHours(2)),
            lectura(sCO2A, 850.0, "ppm", ahora.minusHours(1)),
            lectura(sCO2A,1350.0, "ppm", ahora.minusMinutes(45)) // fuera de rango → alerta
        ));

        // ── Alertas ──
        alertaRepo.saveAll(List.of(
            Alerta.builder().tipo("UMBRAL_TEMPERATURA").severidad(Alerta.Severidad.ALTA)
                .zona(zonaA).sensor(sTempA).fechaGeneracion(ahora.minusMinutes(30))
                .estado(Alerta.EstadoAlerta.PENDIENTE)
                .descripcion("Sensor SENS-TA-01 en Zona A: temperatura 31.0°C supera el máximo de 28.0°C").build(),
            Alerta.builder().tipo("UMBRAL_CO2").severidad(Alerta.Severidad.MEDIA)
                .zona(zonaA).sensor(sCO2A).fechaGeneracion(ahora.minusMinutes(45))
                .estado(Alerta.EstadoAlerta.PENDIENTE)
                .descripcion("Sensor SENS-CO2-01 en Zona A: CO2 1350ppm supera el máximo de 1200ppm").build(),
            Alerta.builder().tipo("UMBRAL_HUMEDAD").severidad(Alerta.Severidad.BAJA)
                .zona(zonaB).sensor(sHumB).fechaGeneracion(ahora.minusHours(5))
                .estado(Alerta.EstadoAlerta.ATENDIDA)
                .descripcion("Humedad baja en Zona B - corregida").build(),
            Alerta.builder().tipo("UMBRAL_TEMPERATURA").severidad(Alerta.Severidad.CRITICA)
                .zona(zonaC).sensor(sTempC).fechaGeneracion(ahora.minusHours(24))
                .estado(Alerta.EstadoAlerta.DESCARTADA)
                .descripcion("Falsa alarma - sensor descalibrado").build()
        ));

        // ── Tratamientos ──
        tratamientoRepo.saveAll(List.of(
            Tratamiento.builder().planta(plantas.get(0)).empleado(emp1)
                .tipoTratamiento(Tratamiento.TipoTratamiento.FERTILIZACION)
                .productoUtilizado("Nitrofoska").dosis("5g/L")
                .fechaHora(ahora.minusDays(7)).resultadoObservado("Mejora visible en color de hojas").build(),
            Tratamiento.builder().planta(plantas.get(1)).empleado(emp1)
                .tipoTratamiento(Tratamiento.TipoTratamiento.PODA)
                .fechaHora(ahora.minusDays(5)).resultadoObservado("Brotes laterales eliminados").build(),
            Tratamiento.builder().planta(plantas.get(5)).empleado(emp2)
                .tipoTratamiento(Tratamiento.TipoTratamiento.RIEGO_MANUAL)
                .fechaHora(ahora.minusDays(2)).resultadoObservado("Suelo con humedad adecuada").build(),
            Tratamiento.builder().planta(plantas.get(9)).empleado(emp2)
                .tipoTratamiento(Tratamiento.TipoTratamiento.PESTICIDA)
                .productoUtilizado("Neem oil").dosis("10mL/L")
                .fechaHora(ahora.minusDays(3)).resultadoObservado("Plaga controlada").build(),
            Tratamiento.builder().planta(plantas.get(0)).empleado(supervisor)
                .tipoTratamiento(Tratamiento.TipoTratamiento.REVISION)
                .fechaHora(ahora.minusDays(1)).resultadoObservado("Planta lista para cosechar").build()
        ));

        // ── Cosechas ──
        cosechaRepo.saveAll(List.of(
            Cosecha.builder().planta(plantas.get(4)).empleado(emp1)
                .fechaCosecha(LocalDate.of(2026, 3, 28)).pesoKg(4.2)
                .calidad(Cosecha.CalidadCosecha.A).destino(Cosecha.DestinoCosecha.VENTA)
                .observaciones("Excelente calidad. Frutos uniformes.").build(),
            Cosecha.builder().planta(plantas.get(4)).empleado(emp1)
                .fechaCosecha(LocalDate.of(2026, 4, 10)).pesoKg(3.8)
                .calidad(Cosecha.CalidadCosecha.B).destino(Cosecha.DestinoCosecha.VENTA).build(),
            Cosecha.builder().planta(plantas.get(4)).empleado(emp2)
                .fechaCosecha(LocalDate.of(2026, 5, 2)).pesoKg(5.1)
                .calidad(Cosecha.CalidadCosecha.A).destino(Cosecha.DestinoCosecha.VENTA)
                .observaciones("Mejor cosecha del mes").build(),
            Cosecha.builder().planta(plantas.get(4)).empleado(emp2)
                .fechaCosecha(LocalDate.of(2026, 5, 8)).pesoKg(2.5)
                .calidad(Cosecha.CalidadCosecha.C).destino(Cosecha.DestinoCosecha.CONSUMO_INTERNO)
                .observaciones("Algunos frutos con manchas").build(),
            Cosecha.builder().planta(plantas.get(4)).empleado(emp1)
                .fechaCosecha(LocalDate.of(2026, 5,14)).pesoKg(6.0)
                .calidad(Cosecha.CalidadCosecha.A).destino(Cosecha.DestinoCosecha.VENTA).build()
        ));

        // ── Turnos ──
        turnoRepo.saveAll(List.of(
            Turno.builder().empleado(emp1).zona(zonaA)
                .fechaHoraInicio(ahora.minusDays(1).withHour(7))
                .fechaHoraFin(ahora.minusDays(1).withHour(15))
                .actividadesRealizadas("Riego manual zona A, revisión de sensores, registro de lecturas").build(),
            Turno.builder().empleado(emp2).zona(zonaB)
                .fechaHoraInicio(ahora.minusDays(1).withHour(7))
                .fechaHoraFin(ahora.minusDays(1).withHour(15))
                .actividadesRealizadas("Fertilización lechugas, poda de brotes, limpieza general").build(),
            Turno.builder().empleado(emp1).zona(zonaC)
                .fechaHoraInicio(ahora.withHour(7))
                .actividadesRealizadas("Turno en curso - revisión de pimientos").build(),
            Turno.builder().empleado(supervisor).zona(zonaA)
                .fechaHoraInicio(ahora.minusDays(2).withHour(8))
                .fechaHoraFin(ahora.minusDays(2).withHour(17))
                .actividadesRealizadas("Supervisión general, atención de alertas de temperatura").build()
        ));
    }

    private Planta planta(String cod, TipoPlanta tipo, Zona zona, LocalDate siembra, Planta.EstadoPlanta estado) {
        return Planta.builder().codigo(cod).tipoPlanta(tipo).zona(zona)
                .fechaSiembra(siembra).estado(estado).build();
    }

    private Sensor sensor(String cod, Sensor.TipoSensor tipo, Zona zona, Double min, Double max) {
        return Sensor.builder().codigo(cod).tipoSensor(tipo).zona(zona)
                .estado(Sensor.EstadoSensor.ACTIVO)
                .fechaInstalacion(LocalDate.of(2024, 1, 1))
                .umbralMin(min).umbralMax(max).build();
    }

    private LecturaSensor lectura(Sensor sensor, Double valor, String unidad, LocalDateTime fechaHora) {
        return LecturaSensor.builder().sensor(sensor).valor(valor).unidad(unidad)
                .fechaHora(fechaHora).fuente(LecturaSensor.FuenteLectura.MANUAL).build();
    }
}
