/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Alerta;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.AlertaRepository;
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
        Alerta alerta = alertaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Alerta no encontrada con id: " + id));
        alerta.setEstado(Alerta.EstadoAlerta.ATENDIDA);
        return alertaRepository.save(alerta);
    }

    public Alerta descartar(Long id) {
        Alerta alerta = alertaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Alerta no encontrada con id: " + id));
        alerta.setEstado(Alerta.EstadoAlerta.DESCARTADA);
        return alertaRepository.save(alerta);
    }

    public long countPendientes() {
        return alertaRepository.countByEstado(Alerta.EstadoAlerta.PENDIENTE);
    }
}
