/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.repository;

import com.greenhouse.entity.Planta;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

/** Repositorio JPA para la entidad Planta. */
@Repository
public interface PlantaRepository extends JpaRepository<Planta, Long> {
    Optional<Planta> findByCodigo(String codigo);
    List<Planta> findByZonaId(Long zonaId);
    List<Planta> findByEstado(Planta.EstadoPlanta estado);
    List<Planta> findByTipoPlantaId(Long tipoPlantaId);
    boolean existsByCodigo(String codigo);
}
