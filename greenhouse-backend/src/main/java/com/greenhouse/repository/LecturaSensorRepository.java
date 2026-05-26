/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.repository;

import com.greenhouse.entity.LecturaSensor;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

/** Repositorio JPA para la entidad LecturaSensor. */
@Repository
public interface LecturaSensorRepository extends JpaRepository<LecturaSensor, Long> {
    List<LecturaSensor> findBySensorId(Long sensorId);
    List<LecturaSensor> findBySensorIdAndFechaHoraBetween(Long sensorId, LocalDateTime inicio, LocalDateTime fin);
    List<LecturaSensor> findBySensorIdInOrderByFechaHoraDesc(List<Long> sensorIds);
    List<LecturaSensor> findBySensorIdOrderByFechaHoraDesc(Long sensorId);
}
