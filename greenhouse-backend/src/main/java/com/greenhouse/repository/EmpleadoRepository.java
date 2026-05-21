/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.repository;

import com.greenhouse.entity.Empleado;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

/** Repositorio JPA para la entidad Empleado. */
@Repository
public interface EmpleadoRepository extends JpaRepository<Empleado, Long> {
    Optional<Empleado> findByEmail(String email);
    List<Empleado> findByEstado(Empleado.EstadoEmpleado estado);
    List<Empleado> findByRol(Empleado.RolEmpleado rol);
    boolean existsByEmail(String email);
}
