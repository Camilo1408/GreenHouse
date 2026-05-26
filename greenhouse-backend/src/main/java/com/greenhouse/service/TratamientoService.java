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

    public List<Tratamiento> findAll() {
        return tratamientoRepository.findAll();
    }

    public List<Tratamiento> findByPlanta(Long plantaId) {
        return tratamientoRepository.findByPlantaId(plantaId);
    }

    public List<Tratamiento> findByEmpleado(Long empleadoId) {
        return tratamientoRepository.findByEmpleadoId(empleadoId);
    }

    public Tratamiento findById(Long id) {
        return tratamientoRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Tratamiento no encontrado con id: " + id));
    }

    public Tratamiento save(Tratamiento tratamiento) {
        if (!plantaRepository.existsById(tratamiento.getPlanta().getId())) {
            throw new ResourceNotFoundException("Planta no encontrada con id: " + tratamiento.getPlanta().getId());
        }
        if (!empleadoRepository.existsById(tratamiento.getEmpleado().getId())) {
            throw new ResourceNotFoundException("Empleado no encontrado con id: " + tratamiento.getEmpleado().getId());
        }
        return tratamientoRepository.save(tratamiento);
    }

    public Tratamiento update(Long id, Tratamiento updated) {
        Tratamiento existing = findById(id);
        existing.setTipoTratamiento(updated.getTipoTratamiento());
        existing.setProductoUtilizado(updated.getProductoUtilizado());
        existing.setDosis(updated.getDosis());
        existing.setFechaHora(updated.getFechaHora());
        existing.setResultadoObservado(updated.getResultadoObservado());
        return tratamientoRepository.save(existing);
    }

    public void delete(Long id) {
        findById(id);
        tratamientoRepository.deleteById(id);
    }
}
