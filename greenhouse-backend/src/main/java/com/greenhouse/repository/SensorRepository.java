/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.repository;

import com.greenhouse.entity.Sensor;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

/** Repositorio JPA para la entidad Sensor. */
@Repository
public interface SensorRepository extends JpaRepository<Sensor, Long> {
    List<Sensor> findByZonaId(Long zonaId);
    List<Sensor> findByEstado(Sensor.EstadoSensor estado);
    List<Sensor> findByTipoSensor(Sensor.TipoSensor tipoSensor);
    boolean existsByCodigo(String codigo);
}
