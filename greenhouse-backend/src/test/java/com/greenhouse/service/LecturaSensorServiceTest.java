/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.*;
import com.greenhouse.repository.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Pruebas unitarias para LecturaSensorService.
 * Valida el registro de lecturas y la generación automática de alertas
 * cuando el valor supera los umbrales configurados en el sensor.
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("Pruebas unitarias - LecturaSensorService")
class LecturaSensorServiceTest {

    @Mock private LecturaSensorRepository lecturaRepository;
    @Mock private SensorRepository sensorRepository;
    @Mock private AlertaRepository alertaRepository;
    @InjectMocks private LecturaSensorService lecturaService;

    private Sensor sensorTemperatura;
    private Zona zona;

    @BeforeEach
    void setUp() {
        zona = Zona.builder().id(1L).nombre("Zona A").estado(Zona.EstadoZona.ACTIVA).build();
        sensorTemperatura = Sensor.builder()
                .id(1L)
                .codigo("SENS-TA-01")
                .tipoSensor(Sensor.TipoSensor.TEMPERATURA)
                .zona(zona)
                .estado(Sensor.EstadoSensor.ACTIVO)
                .umbralMin(18.0)
                .umbralMax(28.0)
                .build();
    }

    @Test
    @DisplayName("Registrar lectura dentro del umbral NO genera alerta")
    void registrar_valorDentroRango_noGeneraAlerta() {
        LecturaSensor lectura = LecturaSensor.builder()
                .sensor(Sensor.builder().id(1L).build())
                .valor(24.5)
                .unidad("°C")
                .fechaHora(LocalDateTime.now())
                .build();

        when(sensorRepository.findById(1L)).thenReturn(Optional.of(sensorTemperatura));
        when(lecturaRepository.save(any())).thenReturn(lectura);

        LecturaSensor result = lecturaService.registrar(lectura);

        assertThat(result.getValor()).isEqualTo(24.5);
        // No debe crearse ninguna alerta
        verify(alertaRepository, never()).save(any());
    }

    @Test
    @DisplayName("Registrar lectura por encima del umbral máximo genera alerta PENDIENTE")
    void registrar_valorSobreUmbralMax_generaAlerta() {
        LecturaSensor lectura = LecturaSensor.builder()
                .sensor(Sensor.builder().id(1L).build())
                .valor(35.0) // muy por encima del máximo 28.0
                .unidad("°C")
                .fechaHora(LocalDateTime.now())
                .build();

        when(sensorRepository.findById(1L)).thenReturn(Optional.of(sensorTemperatura));
        when(lecturaRepository.save(any())).thenReturn(lectura);

        lecturaService.registrar(lectura);

        // Debe crear una alerta
        verify(alertaRepository).save(argThat(alerta ->
                alerta.getEstado() == Alerta.EstadoAlerta.PENDIENTE
                && alerta.getZona().equals(zona)
                && alerta.getTipo().equals("UMBRAL_TEMPERATURA")
        ));
    }

    @Test
    @DisplayName("Registrar lectura por debajo del umbral mínimo genera alerta PENDIENTE")
    void registrar_valorBajoUmbralMin_generaAlerta() {
        LecturaSensor lectura = LecturaSensor.builder()
                .sensor(Sensor.builder().id(1L).build())
                .valor(5.0) // muy por debajo del mínimo 18.0
                .unidad("°C")
                .fechaHora(LocalDateTime.now())
                .build();

        when(sensorRepository.findById(1L)).thenReturn(Optional.of(sensorTemperatura));
        when(lecturaRepository.save(any())).thenReturn(lectura);

        lecturaService.registrar(lectura);

        verify(alertaRepository).save(argThat(alerta ->
                alerta.getEstado() == Alerta.EstadoAlerta.PENDIENTE
                && alerta.getTipo().equals("UMBRAL_TEMPERATURA")
        ));
    }

    @Test
    @DisplayName("Valor justo en el borde superior del umbral NO genera alerta")
    void registrar_valorEnBorde_noGeneraAlerta() {
        LecturaSensor lectura = LecturaSensor.builder()
                .sensor(Sensor.builder().id(1L).build())
                .valor(28.0) // exactamente en el umbral máximo
                .unidad("°C")
                .fechaHora(LocalDateTime.now())
                .build();

        when(sensorRepository.findById(1L)).thenReturn(Optional.of(sensorTemperatura));
        when(lecturaRepository.save(any())).thenReturn(lectura);

        lecturaService.registrar(lectura);

        verify(alertaRepository, never()).save(any());
    }

    @Test
    @DisplayName("Severidad CRITICA cuando la desviación supera el 50% del rango")
    void registrar_desviacionCritica_generaAlertaCritica() {
        // rango: 18-28 = 10 grados. CRITICA si desviación > 50% → > 5 grados sobre máximo → > 33
        LecturaSensor lectura = LecturaSensor.builder()
                .sensor(Sensor.builder().id(1L).build())
                .valor(40.0) // 12 grados sobre el máximo (>50% del rango de 10)
                .unidad("°C")
                .fechaHora(LocalDateTime.now())
                .build();

        when(sensorRepository.findById(1L)).thenReturn(Optional.of(sensorTemperatura));
        when(lecturaRepository.save(any())).thenReturn(lectura);

        lecturaService.registrar(lectura);

        verify(alertaRepository).save(argThat(alerta ->
                alerta.getSeveridad() == Alerta.Severidad.CRITICA
        ));
    }

    @Test
    @DisplayName("fechaHora null se rellena automáticamente con la hora actual")
    void registrar_sinFechaHora_asignaFechaActual() {
        LecturaSensor lectura = LecturaSensor.builder()
                .sensor(Sensor.builder().id(1L).build())
                .valor(22.0)
                .unidad("°C")
                .fechaHora(null) // sin fecha
                .build();

        when(sensorRepository.findById(1L)).thenReturn(Optional.of(sensorTemperatura));
        when(lecturaRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        LecturaSensor result = lecturaService.registrar(lectura);

        assertThat(result.getFechaHora()).isNotNull();
    }
}
