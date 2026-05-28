/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Alerta;
import com.greenhouse.entity.Empleado;
import com.greenhouse.entity.Zona;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.AlertaRepository;
import com.greenhouse.repository.EmpleadoRepository;
import com.greenhouse.repository.ZonaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
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
    private final ZonaRepository zonaRepository;

    /**
     * Retorna todas las alertas registradas en el sistema.
     *
     * @return lista completa de alertas (puede estar vacía)
     */
    public List<Alerta> findAll() {
        return alertaRepository.findAll();
    }

    /**
     * Retorna las alertas cuyo estado es {@code PENDIENTE}.
     *
     * @return lista de alertas pendientes de atención
     */
    public List<Alerta> findPendientes() {
        return alertaRepository.findByEstado(Alerta.EstadoAlerta.PENDIENTE);
    }

    /**
     * Retorna todas las alertas asociadas a una zona específica.
     *
     * @param zonaId ID de la zona
     * @return lista de alertas de la zona; vacía si la zona no tiene alertas
     */
    public List<Alerta> findByZona(Long zonaId) {
        return alertaRepository.findByZonaId(zonaId);
    }

    /**
     * Marca una alerta como atendida sin notas ni empleado responsable.
     *
     * @param id ID de la alerta a atender
     * @return la alerta actualizada con estado {@code ATENDIDA}
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe la alerta
     */
    public Alerta atender(Long id) {
        return atender(id, null, null);
    }

    /**
     * Marca una alerta como atendida, opcionalmente registrando notas y el empleado responsable.
     *
     * @param id         ID de la alerta a atender
     * @param notas      notas de resolución (puede ser {@code null})
     * @param empleadoId ID del empleado que atiende la alerta (puede ser {@code null})
     * @return la alerta actualizada con estado {@code ATENDIDA}
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe la alerta o el empleado
     */
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

    /**
     * Descarta una alerta sin notas ni empleado responsable.
     *
     * @param id ID de la alerta a descartar
     * @return la alerta actualizada con estado {@code DESCARTADA}
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe la alerta
     */
    public Alerta descartar(Long id) {
        return descartar(id, null, null);
    }

    /**
     * Descarta una alerta, opcionalmente registrando notas y el empleado responsable.
     *
     * @param id         ID de la alerta a descartar
     * @param notas      notas de descarte (puede ser {@code null})
     * @param empleadoId ID del empleado que descarta la alerta (puede ser {@code null})
     * @return la alerta actualizada con estado {@code DESCARTADA}
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe la alerta o el empleado
     */
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

    /**
     * Agrega o actualiza las notas de resolución de una alerta en cualquier estado.
     *
     * @param id         ID de la alerta
     * @param notas      texto de las notas a agregar
     * @param empleadoId ID del empleado que agrega las notas (puede ser {@code null})
     * @return la alerta actualizada
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe la alerta o el empleado
     */
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

    /**
     * Cuenta el número de alertas en estado {@code PENDIENTE}.
     *
     * @return cantidad de alertas pendientes
     */
    public long countPendientes() {
        return alertaRepository.countByEstado(Alerta.EstadoAlerta.PENDIENTE);
    }

    /**
     * Crea una alerta manual (novedad reportada por un empleado o supervisor).
     * Ejemplos: enfermedad en planta, falla de sistema en zona.
     *
     * @param zonaId      ID de la zona afectada
     * @param tipo        tipo de alerta (p.ej. "ENFERMEDAD", "FALLA_SISTEMA")
     * @param severidad   nivel de severidad de la alerta
     * @param descripcion descripción detallada de la novedad
     * @param empleadoId  ID del empleado que reporta (puede ser {@code null})
     * @return la alerta creada con estado {@code PENDIENTE}
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe la zona o el empleado
     */
    public Alerta crearManual(Long zonaId, String tipo, Alerta.Severidad severidad,
                              String descripcion, Long empleadoId) {
        Zona zona = zonaRepository.findById(zonaId)
                .orElseThrow(() -> new ResourceNotFoundException("Zona no encontrada con id: " + zonaId));

        Alerta alerta = Alerta.builder()
                .tipo(tipo)
                .severidad(severidad)
                .zona(zona)
                .fechaGeneracion(LocalDateTime.now())
                .estado(Alerta.EstadoAlerta.PENDIENTE)
                .descripcion(descripcion)
                .build();

        if (empleadoId != null) {
            Empleado empleado = empleadoRepository.findById(empleadoId)
                    .orElseThrow(() -> new ResourceNotFoundException("Empleado no encontrado con id: " + empleadoId));
            alerta.setAtendidoPor(empleado);
        }

        return alertaRepository.save(alerta);
    }
}
