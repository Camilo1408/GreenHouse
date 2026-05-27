/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Zona;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

/**
 * Servicio para la gestión de zonas del invernadero.
 */
@Service
@RequiredArgsConstructor
@Transactional
public class ZonaService {

    private final ZonaRepository     zonaRepository;
    private final SensorRepository   sensorRepository;
    private final LecturaSensorRepository lecturaRepository;
    private final AlertaRepository   alertaRepository;
    private final PlantaRepository   plantaRepository;
    private final TratamientoRepository tratamientoRepository;
    private final CosechaRepository  cosechaRepository;
    private final TurnoRepository    turnoRepository;

    public List<Zona> findAll() {
        return zonaRepository.findAll();
    }

    public Zona findById(Long id) {
        return zonaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Zona no encontrada con id: " + id));
    }

    public Zona save(Zona zona) {
        if (zonaRepository.existsByNombre(zona.getNombre())) {
            throw new IllegalArgumentException("Ya existe una zona con el nombre: " + zona.getNombre());
        }
        return zonaRepository.save(zona);
    }

    public Zona update(Long id, Zona updated) {
        Zona existing = findById(id);
        existing.setNombre(updated.getNombre());
        existing.setDimensionM2(updated.getDimensionM2());
        existing.setCapacidadMaxPlantas(updated.getCapacidadMaxPlantas());
        existing.setEstado(updated.getEstado());
        existing.setUbicacion(updated.getUbicacion());
        return zonaRepository.save(existing);
    }

    /**
     * Elimina una zona junto con todos sus datos dependientes en orden:
     *  1. Lecturas de sensores → sensores → alertas desasociadas
     *  2. Tratamientos → cosechas → plantas
     *  3. Turnos de la zona
     *  4. Zona
     */
    public void delete(Long id) {
        findById(id);

        // 1. Eliminar sensores y sus dependencias
        sensorRepository.findByZonaId(id).forEach(sensor -> {
            lecturaRepository.deleteAll(lecturaRepository.findBySensorId(sensor.getId()));
            alertaRepository.findBySensorId(sensor.getId()).forEach(a -> {
                a.setSensor(null);
                alertaRepository.save(a);
            });
            sensorRepository.deleteById(sensor.getId());
        });

        // 2. Eliminar plantas y sus dependencias
        plantaRepository.findByZonaId(id).forEach(planta -> {
            tratamientoRepository.deleteAll(tratamientoRepository.findByPlantaId(planta.getId()));
            cosechaRepository.deleteAll(cosechaRepository.findByPlantaId(planta.getId()));
            plantaRepository.deleteById(planta.getId());
        });

        // 3. Eliminar turnos asociados a la zona
        turnoRepository.deleteAll(turnoRepository.findByZonaId(id));

        // 4. Eliminar alertas de zona que quedaron sin sensor (nullificadas arriba)
        //    Las alertas creadas manualmente con zonaId también se eliminan
        alertaRepository.deleteAll(alertaRepository.findByZonaId(id));

        // 5. Eliminar zona
        zonaRepository.deleteById(id);
    }

    public List<Zona> findByEstado(Zona.EstadoZona estado) {
        return zonaRepository.findByEstado(estado);
    }
}
