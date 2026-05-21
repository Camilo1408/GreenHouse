/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.repository;

import com.greenhouse.entity.TipoPlanta;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

/** Repositorio JPA para la entidad TipoPlanta. */
@Repository
public interface TipoPlantaRepository extends JpaRepository<TipoPlanta, Long> {
    Optional<TipoPlanta> findByNombre(String nombre);
    boolean existsByNombre(String nombre);
}
