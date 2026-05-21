/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.repository;

import com.greenhouse.entity.Tratamiento;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

/** Repositorio JPA para la entidad Tratamiento. */
@Repository
public interface TratamientoRepository extends JpaRepository<Tratamiento, Long> {
    List<Tratamiento> findByPlantaId(Long plantaId);
    List<Tratamiento> findByEmpleadoId(Long empleadoId);
    List<Tratamiento> findByTipoTratamiento(Tratamiento.TipoTratamiento tipo);
}
