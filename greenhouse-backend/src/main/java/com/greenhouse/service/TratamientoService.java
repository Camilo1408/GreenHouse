/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Tratamiento;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.EmpleadoRepository;
import com.greenhouse.repository.PlantaRepository;
import com.greenhouse.repository.TratamientoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

/**
 * Servicio para la gestión de tratamientos aplicados a las plantas.
 */
@Service
@RequiredArgsConstructor
@Transactional
public class TratamientoService {

    private final TratamientoRepository tratamientoRepository;
    private final PlantaRepository plantaRepository;
    private final EmpleadoRepository empleadoRepository;

    /**
     * Retorna todos los tratamientos registrados en el sistema.
     *
     * @return lista completa de tratamientos (puede estar vacía)
     */
    public List<Tratamiento> findAll() {
        return tratamientoRepository.findAll();
    }

    /**
     * Retorna los tratamientos aplicados a una planta específica.
     *
     * @param plantaId ID de la planta
     * @return lista de tratamientos de la planta; vacía si no tiene ninguno
     */
    public List<Tratamiento> findByPlanta(Long plantaId) {
        return tratamientoRepository.findByPlantaId(plantaId);
    }

    /**
     * Retorna los tratamientos realizados por un empleado específico.
     *
     * @param empleadoId ID del empleado
     * @return lista de tratamientos del empleado; vacía si no tiene ninguno
     */
    public List<Tratamiento> findByEmpleado(Long empleadoId) {
        return tratamientoRepository.findByEmpleadoId(empleadoId);
    }

    /**
     * Busca un tratamiento por su identificador.
     *
     * @param id ID del tratamiento
     * @return el tratamiento encontrado
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe un tratamiento con ese ID
     */
    public Tratamiento findById(Long id) {
        return tratamientoRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Tratamiento no encontrado con id: " + id));
    }

    /**
     * Registra un nuevo tratamiento.
     * Valida que la planta y el empleado referenciados existan.
     *
     * @param tratamiento datos del nuevo tratamiento
     * @return el tratamiento persistido con su ID asignado
     * @throws com.greenhouse.exception.ResourceNotFoundException si la planta o el empleado no existen
     */
    public Tratamiento save(Tratamiento tratamiento) {
        if (!plantaRepository.existsById(tratamiento.getPlanta().getId())) {
            throw new ResourceNotFoundException("Planta no encontrada con id: " + tratamiento.getPlanta().getId());
        }
        if (!empleadoRepository.existsById(tratamiento.getEmpleado().getId())) {
            throw new ResourceNotFoundException("Empleado no encontrado con id: " + tratamiento.getEmpleado().getId());
        }
        return tratamientoRepository.save(tratamiento);
    }

    /**
     * Actualiza los datos de un tratamiento existente.
     *
     * @param id      ID del tratamiento a actualizar
     * @param updated objeto con los nuevos valores
     * @return el tratamiento actualizado
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe el tratamiento
     */
    public Tratamiento update(Long id, Tratamiento updated) {
        Tratamiento existing = findById(id);
        existing.setTipoTratamiento(updated.getTipoTratamiento());
        existing.setProductoUtilizado(updated.getProductoUtilizado());
        existing.setDosis(updated.getDosis());
        existing.setFechaHora(updated.getFechaHora());
        existing.setResultadoObservado(updated.getResultadoObservado());
        return tratamientoRepository.save(existing);
    }

    /**
     * Elimina un tratamiento del sistema.
     *
     * @param id ID del tratamiento a eliminar
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe el tratamiento
     */
    public void delete(Long id) {
        findById(id);
        tratamientoRepository.deleteById(id);
    }
}
