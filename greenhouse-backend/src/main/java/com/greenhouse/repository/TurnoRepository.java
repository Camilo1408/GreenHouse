/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.repository;

import com.greenhouse.entity.Turno;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

/** Repositorio JPA para la entidad Turno. */
@Repository
public interface TurnoRepository extends JpaRepository<Turno, Long> {
    List<Turno> findByEmpleadoId(Long empleadoId);
    List<Turno> findByZonaId(Long zonaId);
}
