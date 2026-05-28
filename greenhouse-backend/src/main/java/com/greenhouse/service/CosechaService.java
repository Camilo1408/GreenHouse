/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Cosecha;
import com.greenhouse.entity.Planta;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.CosechaRepository;
import com.greenhouse.repository.PlantaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDate;
import java.util.List;

/**
 * Servicio para el registro y consulta de cosechas del invernadero.
 * Al cosechar, actualiza el estado de la planta a COSECHADA.
 */
@Service
@RequiredArgsConstructor
@Transactional
public class CosechaService {

    private final CosechaRepository cosechaRepository;
    private final PlantaRepository plantaRepository;

    /**
     * Retorna todas las cosechas registradas en el sistema.
     *
     * @return lista completa de cosechas (puede estar vacía)
     */
    public List<Cosecha> findAll() {
        return cosechaRepository.findAll();
    }

    /**
     * Busca una cosecha por su identificador.
     *
     * @param id ID de la cosecha
     * @return la cosecha encontrada
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe una cosecha con ese ID
     */
    public Cosecha findById(Long id) {
        return cosechaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Cosecha no encontrada con id: " + id));
    }

    /**
     * Registra una nueva cosecha y actualiza el estado de la planta a {@code COSECHADA}.
     *
     * @param cosecha datos de la cosecha (debe incluir la referencia a la planta)
     * @return la cosecha persistida con su ID asignado
     * @throws com.greenhouse.exception.ResourceNotFoundException si la planta referenciada no existe
     */
    public Cosecha registrar(Cosecha cosecha) {
        Planta planta = plantaRepository.findById(cosecha.getPlanta().getId())
                .orElseThrow(() -> new ResourceNotFoundException("Planta no encontrada"));

        cosecha.setPlanta(planta);
        Cosecha saved = cosechaRepository.save(cosecha);

        planta.setEstado(Planta.EstadoPlanta.COSECHADA);
        plantaRepository.save(planta);

        return saved;
    }

    /**
     * Retorna las cosechas cuya fecha se encuentra dentro del rango especificado (inclusive).
     *
     * @param inicio fecha de inicio del período (inclusive)
     * @param fin    fecha de fin del período (inclusive)
     * @return lista de cosechas en el período; vacía si no hay ninguna
     */
    public List<Cosecha> findByPeriodo(LocalDate inicio, LocalDate fin) {
        return cosechaRepository.findByFechaCosechaBetween(inicio, fin);
    }

    /**
     * Calcula el total de kilogramos cosechados en un mes específico.
     *
     * @param year  año del período (p.ej. 2026)
     * @param month mes del período (1–12)
     * @return suma de kg cosechados; {@code 0.0} si no hubo cosechas ese mes
     */
    public Double totalKgMes(int year, int month) {
        LocalDate inicio = LocalDate.of(year, month, 1);
        LocalDate fin = inicio.withDayOfMonth(inicio.lengthOfMonth());
        Double total = cosechaRepository.sumPesoKgByFechaCosechaBetween(inicio, fin);
        return total != null ? total : 0.0;
    }
}
