/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.repository;

import com.greenhouse.entity.Cosecha;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDate;
import java.util.List;

/** Repositorio JPA para la entidad Cosecha. */
@Repository
public interface CosechaRepository extends JpaRepository<Cosecha, Long> {
    List<Cosecha> findByPlantaId(Long plantaId);
    List<Cosecha> findByEmpleadoId(Long empleadoId);
    List<Cosecha> findByFechaCosechaBetween(LocalDate inicio, LocalDate fin);

    @Query("SELECT SUM(c.pesoKg) FROM Cosecha c WHERE c.fechaCosecha BETWEEN :inicio AND :fin")
    Double sumPesoKgByFechaCosechaBetween(@Param("inicio") LocalDate inicio, @Param("fin") LocalDate fin);
}
