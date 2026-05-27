/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Planta;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

/**
 * Servicio para la gestión del ciclo de vida de las plantas en el invernadero.
 */
@Service
@RequiredArgsConstructor
@Transactional
public class PlantaService {

    private final PlantaRepository plantaRepository;
    private final ZonaRepository zonaRepository;
    private final TipoPlantaRepository tipoPlantaRepository;
    private final TratamientoRepository tratamientoRepository;
    private final CosechaRepository cosechaRepository;

    public List<Planta> findAll() {
        return plantaRepository.findAll();
    }

    public Planta findById(Long id) {
        return plantaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Planta no encontrada con id: " + id));
    }

    public Planta save(Planta planta) {
        if (plantaRepository.existsByCodigo(planta.getCodigo())) {
            throw new IllegalArgumentException("Ya existe una planta con el código: " + planta.getCodigo());
        }
        validarRelaciones(planta);
        return plantaRepository.save(planta);
    }

    public Planta update(Long id, Planta updated) {
        Planta existing = findById(id);
        existing.setTipoPlanta(updated.getTipoPlanta());
        existing.setZona(updated.getZona());
        existing.setFechaSiembra(updated.getFechaSiembra());
        existing.setEstado(updated.getEstado());
        existing.setObservaciones(updated.getObservaciones());
        validarRelaciones(existing);
        return plantaRepository.save(existing);
    }

    /**
     * Elimina una planta y todos sus datos asociados:
     * tratamientos, cosechas y luego la planta.
     */
    public void delete(Long id) {
        findById(id);
        tratamientoRepository.deleteAll(tratamientoRepository.findByPlantaId(id));
        cosechaRepository.deleteAll(cosechaRepository.findByPlantaId(id));
        plantaRepository.deleteById(id);
    }

    public List<Planta> findByZona(Long zonaId) {
        return plantaRepository.findByZonaId(zonaId);
    }

    public List<Planta> findByEstado(Planta.EstadoPlanta estado) {
        return plantaRepository.findByEstado(estado);
    }

    private void validarRelaciones(Planta planta) {
        if (planta.getZona() != null && !zonaRepository.existsById(planta.getZona().getId())) {
            throw new ResourceNotFoundException("Zona no encontrada con id: " + planta.getZona().getId());
        }
        if (planta.getTipoPlanta() != null && !tipoPlantaRepository.existsById(planta.getTipoPlanta().getId())) {
            throw new ResourceNotFoundException("TipoPlanta no encontrado con id: " + planta.getTipoPlanta().getId());
        }
    }
}
