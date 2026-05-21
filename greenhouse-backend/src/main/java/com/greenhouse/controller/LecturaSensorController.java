/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.LecturaSensor;
import com.greenhouse.service.LecturaSensorService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import java.util.List;

/**
 * Controlador REST para el registro y consulta de lecturas de sensores.
 */
@RestController
@RequestMapping("/api/lecturas")
@RequiredArgsConstructor
@Tag(name = "Lecturas de Sensores", description = "Registro y consulta de lecturas de sensores")
public class LecturaSensorController {

    private final LecturaSensorService lecturaService;

    @GetMapping("/sensor/{sensorId}")
    @Operation(summary = "Obtener lecturas de un sensor")
    public ResponseEntity<List<LecturaSensor>> findBySensor(@PathVariable Long sensorId) {
        return ResponseEntity.ok(lecturaService.findBySensor(sensorId));
    }

    @PostMapping
    @Operation(summary = "Registrar nueva lectura (genera alerta si está fuera de umbral)")
    public ResponseEntity<LecturaSensor> registrar(@Valid @RequestBody LecturaSensor lectura) {
        return ResponseEntity.status(HttpStatus.CREATED).body(lecturaService.registrar(lectura));
    }
}
