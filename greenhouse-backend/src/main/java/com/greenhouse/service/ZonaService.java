/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Zona;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.ZonaRepository;
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

    private final ZonaRepository zonaRepository;

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

    public void delete(Long id) {
        findById(id);
        zonaRepository.deleteById(id);
    }

    public List<Zona> findByEstado(Zona.EstadoZona estado) {
        return zonaRepository.findByEstado(estado);
    }
}
