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

    /**
     * Retorna todos los tipos de planta registrados en el catálogo.
     *
     * @return lista completa de tipos de planta (puede estar vacía)
     */
    public List<TipoPlanta> findAll() { return tipoPlantaRepository.findAll(); }

    /**
     * Busca un tipo de planta por su identificador.
     *
     * @param id ID del tipo de planta
     * @return el tipo de planta encontrado
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe un tipo con ese ID
     */
    public TipoPlanta findById(Long id) {
        return tipoPlantaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("TipoPlanta no encontrado con id: " + id));
    }

    /**
     * Crea un nuevo tipo de planta en el catálogo.
     * El nombre debe ser único entre todos los tipos existentes.
     *
     * @param tp datos del nuevo tipo de planta
     * @return el tipo de planta persistido con su ID asignado
     * @throws IllegalArgumentException si ya existe un tipo con el mismo nombre
     */
    public TipoPlanta save(TipoPlanta tp) {
        if (tipoPlantaRepository.existsByNombre(tp.getNombre()))
            throw new IllegalArgumentException("Ya existe un tipo de planta con el nombre: " + tp.getNombre());
        return tipoPlantaRepository.save(tp);
    }

    /**
     * Actualiza todos los campos de un tipo de planta existente.
     *
     * @param id      ID del tipo de planta a actualizar
     * @param updated objeto con los nuevos valores
     * @return el tipo de planta actualizado
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe el tipo de planta
     */
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

    /**
     * Elimina un tipo de planta del catálogo.
     *
     * @param id ID del tipo de planta a eliminar
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe el tipo de planta
     */
    public void delete(Long id) { findById(id); tipoPlantaRepository.deleteById(id); }
}
