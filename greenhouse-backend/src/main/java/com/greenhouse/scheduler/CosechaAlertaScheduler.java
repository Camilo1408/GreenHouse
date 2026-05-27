/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.scheduler;

import com.greenhouse.entity.Alerta;
import com.greenhouse.entity.Planta;
import com.greenhouse.repository.AlertaRepository;
import com.greenhouse.repository.PlantaRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;

/**
 * Scheduler que evalúa el estado de cosecha de todas las plantas activas
 * y genera alertas automáticas según su proximidad o vencimiento.
 *
 * Categorías de alerta:
 *  COSECHA_PROXIMA     — faltan ≤ 7 días para la cosecha estimada  → BAJA
 *  COSECHA_LISTA       — la cosecha ya debería haber ocurrido (0–3 días tarde) → MEDIA
 *  COSECHA_VENCIDA     — 3–7 días tarde                             → ALTA
 *  COSECHA_MUY_VENCIDA — más de 7 días tarde                        → CRITICA
 *
 * Deduplicación: antes de crear una alerta se verifica que no exista ya
 * una alerta PENDIENTE del mismo tipo para la misma planta (usando el
 * marcador "[PLT-{id}]" al inicio de la descripción).
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class CosechaAlertaScheduler {

    private final PlantaRepository plantaRepository;
    private final AlertaRepository alertaRepository;

    /**
     * Se ejecuta cada 6 horas (también al arrancar la aplicación con
     * initialDelay=0 para que aparezca de inmediato en la primera carga).
     * Cron: "0 0 0/6 * * ?" — a las 00:00, 06:00, 12:00 y 18:00.
     */
    @Scheduled(cron = "0 0 0/6 * * ?")
    @Transactional
    public void evaluarCosechasPendientes() {
        log.info("[Scheduler] Evaluando alertas de cosecha...");

        List<Planta.EstadoPlanta> estadosActivos = List.of(
                Planta.EstadoPlanta.SEMBRADA,
                Planta.EstadoPlanta.EN_CRECIMIENTO,
                Planta.EstadoPlanta.LISTA_PARA_COSECHAR
        );

        List<Planta> plantas = plantaRepository.findByEstadoIn(estadosActivos);
        int creadas = 0;

        for (Planta planta : plantas) {
            if (planta.getTipoPlanta() == null || planta.getTipoPlanta().getCicloDias() == null) {
                continue; // sin ciclo definido, no se puede calcular
            }

            LocalDate hoy = LocalDate.now();
            LocalDate fechaCosechaEst = planta.getFechaSiembra()
                    .plusDays(planta.getTipoPlanta().getCicloDias());
            long diasRestantes = ChronoUnit.DAYS.between(hoy, fechaCosechaEst);
            // diasRestantes > 0 → falta tiempo  |  < 0 → está vencida

            String tipo;
            Alerta.Severidad severidad;
            String mensajeEstado;

            if (diasRestantes > 7) {
                continue; // aún falta más de 7 días, no se necesita alerta
            } else if (diasRestantes > 0) {
                // Faltan entre 1 y 7 días
                tipo = "COSECHA_PROXIMA";
                severidad = Alerta.Severidad.BAJA;
                mensajeEstado = "Faltan " + diasRestantes + " día(s) para la cosecha estimada";
            } else if (diasRestantes >= -3) {
                // Puntual o hasta 3 días tarde
                tipo = "COSECHA_LISTA";
                severidad = Alerta.Severidad.MEDIA;
                mensajeEstado = diasRestantes == 0
                        ? "Hoy es el día estimado de cosecha"
                        : "Cosecha con " + Math.abs(diasRestantes) + " día(s) de retraso";
                // Actualizar estado de la planta si aún está en crecimiento
                actualizarEstadoListaParaCosechar(planta);
            } else if (diasRestantes >= -7) {
                // 4–7 días tarde
                tipo = "COSECHA_VENCIDA";
                severidad = Alerta.Severidad.ALTA;
                mensajeEstado = "Cosecha vencida con " + Math.abs(diasRestantes) + " días de retraso";
                actualizarEstadoListaParaCosechar(planta);
            } else {
                // Más de 7 días tarde
                tipo = "COSECHA_MUY_VENCIDA";
                severidad = Alerta.Severidad.CRITICA;
                mensajeEstado = "VENCIDA — " + Math.abs(diasRestantes) + " días sin cosechar";
                actualizarEstadoListaParaCosechar(planta);
            }

            // Deduplicación: no crear si ya existe una alerta PENDIENTE de ese tipo para esta planta
            String plantaRef = "[PLT-" + planta.getId() + "]";
            boolean yaExiste = alertaRepository.existsByTipoAndDescripcionContainingAndEstado(
                    tipo, plantaRef, Alerta.EstadoAlerta.PENDIENTE);

            if (yaExiste) {
                continue;
            }

            String descripcion = String.format(
                    "%s Planta %s (%s) en zona '%s'. %s. Fecha estimada: %s.",
                    plantaRef,
                    planta.getCodigo(),
                    planta.getTipoPlanta().getNombre(),
                    planta.getZona().getNombre(),
                    mensajeEstado,
                    fechaCosechaEst
            );

            Alerta alerta = Alerta.builder()
                    .tipo(tipo)
                    .severidad(severidad)
                    .zona(planta.getZona())
                    .sensor(null)
                    .fechaGeneracion(LocalDateTime.now())
                    .estado(Alerta.EstadoAlerta.PENDIENTE)
                    .descripcion(descripcion)
                    .build();

            alertaRepository.save(alerta);
            creadas++;

            log.info("[Scheduler] Alerta {} creada para planta {} ({})",
                    tipo, planta.getCodigo(), mensajeEstado);
        }

        log.info("[Scheduler] Evaluación completada — {} alerta(s) generada(s)", creadas);
    }

    /**
     * Si la planta ya debería cosecharse pero aún está en estado SEMBRADA o
     * EN_CRECIMIENTO, la actualiza automáticamente a LISTA_PARA_COSECHAR.
     */
    private void actualizarEstadoListaParaCosechar(Planta planta) {
        if (planta.getEstado() == Planta.EstadoPlanta.SEMBRADA
                || planta.getEstado() == Planta.EstadoPlanta.EN_CRECIMIENTO) {
            planta.setEstado(Planta.EstadoPlanta.LISTA_PARA_COSECHAR);
            plantaRepository.save(planta);
            log.info("[Scheduler] Planta {} actualizada a LISTA_PARA_COSECHAR", planta.getCodigo());
        }
    }
}
