/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.repository;

import com.greenhouse.entity.Zona;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

/** Repositorio JPA para la entidad Zona. */
@Repository
public interface ZonaRepository extends JpaRepository<Zona, Long> {
    List<Zona> findByEstado(Zona.EstadoZona estado);
    boolean existsByNombre(String nombre);
}
