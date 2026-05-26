/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Alerta;
import com.greenhouse.entity.Empleado;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.AlertaRepository;
import com.greenhouse.repository.EmpleadoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

/**
 * Servicio para la consulta y gestión del estado de las alertas del invernadero.
 */
@Service
@RequiredArgsConstructor
@Transactional
public class AlertaService {

    private final AlertaRepository alertaRepository;
    private final EmpleadoRepository empleadoRepository;

    public List<Alerta> findAll() {
        return alertaRepository.findAll();
    }

    public List<Alerta> findPendientes() {
        return alertaRepository.findByEstado(Alerta.EstadoAlerta.PENDIENTE);
    }

    public List<Alerta> findByZona(Long zonaId) {
        return alertaRepository.findByZonaId(zonaId);
    }

    public Alerta atender(Long id) {
        return atender(id, null, null);
    }

    public Alerta atender(Long id, String notas, Long empleadoId) {
        Alerta alerta = alertaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Alerta no encontrada con id: " + id));
        alerta.setEstado(Alerta.EstadoAlerta.ATENDIDA);
        if (notas != null && !notas.isBlank()) {
            alerta.setNotasResolucion(notas);
        }
        if (empleadoId != null) {
            Empleado empleado = empleadoRepository.findById(empleadoId)
                    .orElseThrow(() -> new ResourceNotFoundException("Empleado no encontrado con id: " + empleadoId));
            alerta.setAtendidoPor(empleado);
        }
        return alertaRepository.save(alerta);
    }

    public Alerta descartar(Long id) {
        return descartar(id, null, null);
    }

    public Alerta descartar(Long id, String notas, Long empleadoId) {
        Alerta alerta = alertaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Alerta no encontrada con id: " + id));
        alerta.setEstado(Alerta.EstadoAlerta.DESCARTADA);
        if (notas != null && !notas.isBlank()) {
            alerta.setNotasResolucion(notas);
        }
        if (empleadoId != null) {
            Empleado empleado = empleadoRepository.findById(empleadoId)
                    .orElseThrow(() -> new ResourceNotFoundException("Empleado no encontrado con id: " + empleadoId));
            alerta.setAtendidoPor(empleado);
        }
        return alertaRepository.save(alerta);
    }

    public Alerta agregarNotas(Long id, String notas, Long empleadoId) {
        Alerta alerta = alertaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Alerta no encontrada con id: " + id));
        if (notas != null && !notas.isBlank()) {
            alerta.setNotasResolucion(notas);
        }
        if (empleadoId != null) {
            Empleado empleado = empleadoRepository.findById(empleadoId)
                    .orElseThrow(() -> new ResourceNotFoundException("Empleado no encontrado con id: " + empleadoId));
            alerta.setAtendidoPor(empleado);
        }
        return alertaRepository.save(alerta);
    }

    public long countPendientes() {
        return alertaRepository.countByEstado(Alerta.EstadoAlerta.PENDIENTE);
    }
}
