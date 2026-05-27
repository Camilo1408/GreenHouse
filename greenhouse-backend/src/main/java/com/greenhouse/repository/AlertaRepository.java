/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.repository;

import com.greenhouse.entity.Alerta;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

/** Repositorio JPA para la entidad Alerta. */
@Repository
public interface AlertaRepository extends JpaRepository<Alerta, Long> {
    List<Alerta> findByEstado(Alerta.EstadoAlerta estado);
    List<Alerta> findByZonaId(Long zonaId);
    List<Alerta> findBySeveridad(Alerta.Severidad severidad);
    long countByEstado(Alerta.EstadoAlerta estado);

    /**
     * Verifica si ya existe una alerta pendiente del mismo tipo que mencione
     * la referencia de la planta (ej: "[PLT-5]") en la descripción.
     * Usado por el scheduler para evitar duplicar alertas de cosecha.
     */
    boolean existsByTipoAndDescripcionContainingAndEstado(
            String tipo, String descripcionContiene, Alerta.EstadoAlerta estado);
}
