/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.LecturaSensor;
import com.greenhouse.service.LecturaSensorService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
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
    @ApiResponse(responseCode = "200", description = "Lista de lecturas del sensor")
    public ResponseEntity<List<LecturaSensor>> findBySensor(
            @Parameter(description = "ID del sensor", required = true) @PathVariable Long sensorId) {
        return ResponseEntity.ok(lecturaService.findBySensor(sensorId));
    }

    @GetMapping("/zona/{zonaId}")
    @Operation(summary = "Obtener todas las lecturas de los sensores de una zona")
    @ApiResponse(responseCode = "200", description = "Lista de lecturas de todos los sensores de la zona, ordenadas por fecha desc")
    public ResponseEntity<List<LecturaSensor>> findByZona(
            @Parameter(description = "ID de la zona", required = true) @PathVariable Long zonaId) {
        return ResponseEntity.ok(lecturaService.findByZona(zonaId));
    }

    @PostMapping
    @Operation(summary = "Registrar nueva lectura (genera alerta si está fuera de umbral)")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Lectura registrada. Se genera alerta automáticamente si el valor supera los umbrales"),
        @ApiResponse(responseCode = "400", description = "Datos inválidos"),
        @ApiResponse(responseCode = "404", description = "Sensor no encontrado")
    })
    public ResponseEntity<LecturaSensor> registrar(@Valid @RequestBody LecturaSensor lectura) {
        return ResponseEntity.status(HttpStatus.CREATED).body(lecturaService.registrar(lectura));
    }
}
