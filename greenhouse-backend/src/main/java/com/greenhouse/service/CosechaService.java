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

    public List<Cosecha> findAll() {
        return cosechaRepository.findAll();
    }

    public Cosecha findById(Long id) {
        return cosechaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Cosecha no encontrada con id: " + id));
    }

    public Cosecha registrar(Cosecha cosecha) {
        Planta planta = plantaRepository.findById(cosecha.getPlanta().getId())
                .orElseThrow(() -> new ResourceNotFoundException("Planta no encontrada"));

        cosecha.setPlanta(planta);
        Cosecha saved = cosechaRepository.save(cosecha);

        planta.setEstado(Planta.EstadoPlanta.COSECHADA);
        plantaRepository.save(planta);

        return saved;
    }

    public List<Cosecha> findByPeriodo(LocalDate inicio, LocalDate fin) {
        return cosechaRepository.findByFechaCosechaBetween(inicio, fin);
    }

    public Double totalKgMes(int year, int month) {
        LocalDate inicio = LocalDate.of(year, month, 1);
        LocalDate fin = inicio.withDayOfMonth(inicio.lengthOfMonth());
        Double total = cosechaRepository.sumPesoKgByFechaCosechaBetween(inicio, fin);
        return total != null ? total : 0.0;
    }
}
