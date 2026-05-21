/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.*;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.List;

/**
 * Servicio para registrar lecturas de sensores.
 * Genera alertas automáticamente cuando el valor supera los umbrales configurados en el sensor.
 */
@Service
@RequiredArgsConstructor
@Transactional
public class LecturaSensorService {

    private final LecturaSensorRepository lecturaRepository;
    private final SensorRepository sensorRepository;
    private final AlertaRepository alertaRepository;

    public List<LecturaSensor> findBySensor(Long sensorId) {
        return lecturaRepository.findBySensorId(sensorId);
    }

    public LecturaSensor registrar(LecturaSensor lectura) {
        Sensor sensor = sensorRepository.findById(lectura.getSensor().getId())
                .orElseThrow(() -> new ResourceNotFoundException("Sensor no encontrado con id: " + lectura.getSensor().getId()));

        lectura.setSensor(sensor);
        if (lectura.getFechaHora() == null) {
            lectura.setFechaHora(LocalDateTime.now());
        }

        LecturaSensor saved = lecturaRepository.save(lectura);
        evaluarUmbrales(sensor, lectura.getValor());
        return saved;
    }

    /** Genera una alerta si el valor de la lectura está fuera del umbral configurado en el sensor. */
    private void evaluarUmbrales(Sensor sensor, Double valor) {
        boolean fueraDeRango = (sensor.getUmbralMin() != null && valor < sensor.getUmbralMin())
                || (sensor.getUmbralMax() != null && valor > sensor.getUmbralMax());

        if (!fueraDeRango) return;

        Alerta.Severidad severidad = calcularSeveridad(sensor, valor);
        String descripcion = String.format(
                "Sensor %s en zona %s: valor %.2f fuera del rango [%.2f, %.2f]",
                sensor.getCodigo(), sensor.getZona().getNombre(),
                valor, sensor.getUmbralMin(), sensor.getUmbralMax()
        );

        Alerta alerta = Alerta.builder()
                .tipo("UMBRAL_" + sensor.getTipoSensor().name())
                .severidad(severidad)
                .zona(sensor.getZona())
                .sensor(sensor)
                .fechaGeneracion(LocalDateTime.now())
                .estado(Alerta.EstadoAlerta.PENDIENTE)
                .descripcion(descripcion)
                .build();

        alertaRepository.save(alerta);
    }

    private Alerta.Severidad calcularSeveridad(Sensor sensor, Double valor) {
        if (sensor.getUmbralMin() == null || sensor.getUmbralMax() == null) return Alerta.Severidad.MEDIA;
        double rango = sensor.getUmbralMax() - sensor.getUmbralMin();
        double desviacion = valor < sensor.getUmbralMin()
                ? sensor.getUmbralMin() - valor
                : valor - sensor.getUmbralMax();
        double porcentaje = rango > 0 ? desviacion / rango : 1.0;

        if (porcentaje > 0.5) return Alerta.Severidad.CRITICA;
        if (porcentaje > 0.25) return Alerta.Severidad.ALTA;
        if (porcentaje > 0.1) return Alerta.Severidad.MEDIA;
        return Alerta.Severidad.BAJA;
    }
}
