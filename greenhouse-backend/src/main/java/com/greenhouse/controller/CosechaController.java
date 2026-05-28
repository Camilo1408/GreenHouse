/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Cosecha;
import com.greenhouse.service.CosechaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * Controlador REST para el registro y consulta de cosechas del invernadero.
 */
@RestController
@RequestMapping("/api/cosechas")
@RequiredArgsConstructor
@Tag(name = "Cosechas", description = "Registro y estadísticas de cosechas")
public class CosechaController {

    private final CosechaService cosechaService;

    @GetMapping
    @Operation(summary = "Listar todas las cosechas")
    @ApiResponse(responseCode = "200", description = "Lista de cosechas retornada correctamente")
    public ResponseEntity<List<Cosecha>> findAll() {
        return ResponseEntity.ok(cosechaService.findAll());
    }

    @GetMapping("/periodo")
    @Operation(summary = "Listar cosechas por periodo")
    @ApiResponse(responseCode = "200", description = "Lista de cosechas en el período indicado")
    public ResponseEntity<List<Cosecha>> findByPeriodo(
            @Parameter(description = "Fecha de inicio del período (yyyy-MM-dd)", required = true)
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate inicio,
            @Parameter(description = "Fecha de fin del período (yyyy-MM-dd)", required = true)
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate fin) {
        return ResponseEntity.ok(cosechaService.findByPeriodo(inicio, fin));
    }

    @GetMapping("/estadisticas/mes")
    @Operation(summary = "Total de kg cosechados en un mes")
    @ApiResponse(responseCode = "200", description = "Total de kg cosechados en el mes indicado")
    public ResponseEntity<Map<String, Double>> totalKgMes(
            @Parameter(description = "Año del período (ej. 2026)", required = true) @RequestParam int year,
            @Parameter(description = "Mes del período (1–12)", required = true) @RequestParam int month) {
        return ResponseEntity.ok(Map.of("totalKg", cosechaService.totalKgMes(year, month)));
    }

    @PostMapping
    @Operation(summary = "Registrar nueva cosecha")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Cosecha registrada. El estado de la planta cambia a COSECHADA"),
        @ApiResponse(responseCode = "400", description = "Datos inválidos"),
        @ApiResponse(responseCode = "404", description = "Planta no encontrada")
    })
    public ResponseEntity<Cosecha> registrar(@Valid @RequestBody Cosecha cosecha) {
        return ResponseEntity.status(HttpStatus.CREATED).body(cosechaService.registrar(cosecha));
    }
}
