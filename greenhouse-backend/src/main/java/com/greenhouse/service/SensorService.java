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

    /**
     * Retorna todos los sensores registrados en el invernadero.
     *
     * @return lista completa de sensores (puede estar vacía)
     */
    public List<Sensor> findAll() {
        return sensorRepository.findAll();
    }

    /**
     * Retorna los sensores instalados en una zona específica.
     *
     * @param zonaId ID de la zona
     * @return lista de sensores en la zona; vacía si no hay ninguno
     */
    public List<Sensor> findByZona(Long zonaId) {
        return sensorRepository.findByZonaId(zonaId);
    }

    /**
     * Busca un sensor por su identificador.
     *
     * @param id ID del sensor
     * @return el sensor encontrado
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe un sensor con ese ID
     */
    public Sensor findById(Long id) {
        return sensorRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Sensor no encontrado con id: " + id));
    }

    /**
     * Registra un nuevo sensor en el sistema.
     * Valida que el código sea único y que la zona exista.
     *
     * @param sensor datos del nuevo sensor
     * @return el sensor persistido con su ID asignado
     * @throws IllegalArgumentException si ya existe un sensor con el mismo código
     * @throws com.greenhouse.exception.ResourceNotFoundException si la zona no existe
     */
    public Sensor save(Sensor sensor) {
        if (sensorRepository.existsByCodigo(sensor.getCodigo())) {
            throw new IllegalArgumentException("Ya existe un sensor con el código: " + sensor.getCodigo());
        }
        if (!zonaRepository.existsById(sensor.getZona().getId())) {
            throw new ResourceNotFoundException("Zona no encontrada con id: " + sensor.getZona().getId());
        }
        return sensorRepository.save(sensor);
    }

    /**
     * Actualiza los datos de un sensor existente (código, tipo, estado, umbrales, zona).
     *
     * @param id      ID del sensor a actualizar
     * @param updated objeto con los nuevos valores
     * @return el sensor actualizado
     * @throws com.greenhouse.exception.ResourceNotFoundException si el sensor o la nueva zona no existen
     */
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

    /**
     * Elimina un sensor junto con sus lecturas.
     * Las alertas asociadas se desvinculan del sensor (FK a null) para preservar el historial.
     *
     * @param id ID del sensor a eliminar
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe el sensor
     */
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
