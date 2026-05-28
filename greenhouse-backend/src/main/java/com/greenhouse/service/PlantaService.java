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

    /**
     * Retorna todas las plantas registradas en el invernadero.
     *
     * @return lista completa de plantas (puede estar vacía)
     */
    public List<Planta> findAll() {
        return plantaRepository.findAll();
    }

    /**
     * Busca una planta por su identificador.
     *
     * @param id ID de la planta
     * @return la planta encontrada
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe una planta con ese ID
     */
    public Planta findById(Long id) {
        return plantaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Planta no encontrada con id: " + id));
    }

    /**
     * Registra una nueva planta en el sistema.
     * Valida que el código sea único y que la zona/tipo existan.
     *
     * @param planta datos de la nueva planta
     * @return la planta persistida con su ID asignado
     * @throws IllegalArgumentException si ya existe una planta con el mismo código
     * @throws com.greenhouse.exception.ResourceNotFoundException si la zona o el tipo de planta no existen
     */
    public Planta save(Planta planta) {
        if (plantaRepository.existsByCodigo(planta.getCodigo())) {
            throw new IllegalArgumentException("Ya existe una planta con el código: " + planta.getCodigo());
        }
        validarRelaciones(planta);
        return plantaRepository.save(planta);
    }

    /**
     * Actualiza los datos de una planta existente.
     *
     * @param id      ID de la planta a actualizar
     * @param updated objeto con los nuevos valores
     * @return la planta actualizada
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe la planta, la zona o el tipo de planta
     */
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

    /**
     * Retorna las plantas ubicadas en una zona específica.
     *
     * @param zonaId ID de la zona
     * @return lista de plantas en la zona; vacía si no hay plantas
     */
    public List<Planta> findByZona(Long zonaId) {
        return plantaRepository.findByZonaId(zonaId);
    }

    /**
     * Retorna las plantas que se encuentran en un estado determinado.
     *
     * @param estado estado de la planta (SEMBRADA, EN_CRECIMIENTO, LISTA_PARA_COSECHAR, COSECHADA, BAJA)
     * @return lista de plantas con ese estado; vacía si no hay ninguna
     */
    public List<Planta> findByEstado(Planta.EstadoPlanta estado) {
        return plantaRepository.findByEstado(estado);
    }

    /**
     * Valida que la zona y el tipo de planta referenciados existen en la base de datos.
     *
     * @param planta planta cuyos datos de relación se validarán
     * @throws com.greenhouse.exception.ResourceNotFoundException si la zona o el tipo de planta no existen
     */
    private void validarRelaciones(Planta planta) {
        if (planta.getZona() != null && !zonaRepository.existsById(planta.getZona().getId())) {
            throw new ResourceNotFoundException("Zona no encontrada con id: " + planta.getZona().getId());
        }
        if (planta.getTipoPlanta() != null && !tipoPlantaRepository.existsById(planta.getTipoPlanta().getId())) {
            throw new ResourceNotFoundException("TipoPlanta no encontrado con id: " + planta.getTipoPlanta().getId());
        }
    }
}
