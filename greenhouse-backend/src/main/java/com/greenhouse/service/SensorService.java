/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Sensor;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.AlertaRepository;
import com.greenhouse.repository.LecturaSensorRepository;
import com.greenhouse.repository.SensorRepository;
import com.greenhouse.repository.ZonaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

/**
 * Servicio para la gestión de sensores del invernadero.
 */
@Service
@RequiredArgsConstructor
@Transactional
public class SensorService {

    private final SensorRepository sensorRepository;
    private final ZonaRepository zonaRepository;
    private final LecturaSensorRepository lecturaRepository;
    private final AlertaRepository alertaRepository;

    public List<Sensor> findAll() {
        return sensorRepository.findAll();
    }

    public List<Sensor> findByZona(Long zonaId) {
        return sensorRepository.findByZonaId(zonaId);
    }

    public Sensor findById(Long id) {
        return sensorRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Sensor no encontrado con id: " + id));
    }

    public Sensor save(Sensor sensor) {
        if (sensorRepository.existsByCodigo(sensor.getCodigo())) {
            throw new IllegalArgumentException("Ya existe un sensor con el código: " + sensor.getCodigo());
        }
        if (!zonaRepository.existsById(sensor.getZona().getId())) {
            throw new ResourceNotFoundException("Zona no encontrada con id: " + sensor.getZona().getId());
        }
        return sensorRepository.save(sensor);
    }

    public Sensor update(Long id, Sensor updated) {
        Sensor existing = findById(id);
        existing.setCodigo(updated.getCodigo());
        existing.setTipoSensor(updated.getTipoSensor());
        existing.setEstado(updated.getEstado());
        existing.setFechaInstalacion(updated.getFechaInstalacion());
        existing.setUmbralMin(updated.getUmbralMin());
        existing.setUmbralMax(updated.getUmbralMax());
        if (!zonaRepository.existsById(updated.getZona().getId())) {
            throw new ResourceNotFoundException("Zona no encontrada con id: " + updated.getZona().getId());
        }
        existing.setZona(updated.getZona());
        return sensorRepository.save(existing);
    }

    public void delete(Long id) {
        findById(id);
        // 1. Eliminar lecturas asociadas (FK no nula — deben borrarse primero)
        lecturaRepository.deleteAll(lecturaRepository.findBySensorId(id));
        // 2. Desasociar alertas (FK nullable — se pone a null para conservar el historial)
        alertaRepository.findBySensorId(id).forEach(a -> {
            a.setSensor(null);
            alertaRepository.save(a);
        });
        // 3. Eliminar el sensor
        sensorRepository.deleteById(id);
    }
}
