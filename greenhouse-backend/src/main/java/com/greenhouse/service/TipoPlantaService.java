/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.TipoPlanta;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.TipoPlantaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

/** Servicio para la gestión de tipos de planta. */
@Service
@RequiredArgsConstructor
@Transactional
public class TipoPlantaService {

    private final TipoPlantaRepository tipoPlantaRepository;

    public List<TipoPlanta> findAll() { return tipoPlantaRepository.findAll(); }

    public TipoPlanta findById(Long id) {
        return tipoPlantaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("TipoPlanta no encontrado con id: " + id));
    }

    public TipoPlanta save(TipoPlanta tp) {
        if (tipoPlantaRepository.existsByNombre(tp.getNombre()))
            throw new IllegalArgumentException("Ya existe un tipo de planta con el nombre: " + tp.getNombre());
        return tipoPlantaRepository.save(tp);
    }

    public TipoPlanta update(Long id, TipoPlanta updated) {
        TipoPlanta existing = findById(id);
        existing.setNombre(updated.getNombre());
        existing.setDescripcion(updated.getDescripcion());
        existing.setTemperaturaMin(updated.getTemperaturaMin());
        existing.setTemperaturaMax(updated.getTemperaturaMax());
        existing.setHumedadMin(updated.getHumedadMin());
        existing.setHumedadMax(updated.getHumedadMax());
        existing.setCicloDias(updated.getCicloDias());
        existing.setCuidadosEspeciales(updated.getCuidadosEspeciales());
        return tipoPlantaRepository.save(existing);
    }

    public void delete(Long id) { findById(id); tipoPlantaRepository.deleteById(id); }
}
