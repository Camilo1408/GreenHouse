/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Cosecha;
import com.greenhouse.service.CosechaService;
import io.swagger.v3.oas.annotations.Operation;
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
    public ResponseEntity<List<Cosecha>> findAll() {
        return ResponseEntity.ok(cosechaService.findAll());
    }

    @GetMapping("/periodo")
    @Operation(summary = "Listar cosechas por periodo")
    public ResponseEntity<List<Cosecha>> findByPeriodo(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate inicio,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate fin) {
        return ResponseEntity.ok(cosechaService.findByPeriodo(inicio, fin));
    }

    @GetMapping("/estadisticas/mes")
    @Operation(summary = "Total de kg cosechados en un mes")
    public ResponseEntity<Map<String, Double>> totalKgMes(
            @RequestParam int year, @RequestParam int month) {
        return ResponseEntity.ok(Map.of("totalKg", cosechaService.totalKgMes(year, month)));
    }

    @PostMapping
    @Operation(summary = "Registrar nueva cosecha")
    public ResponseEntity<Cosecha> registrar(@Valid @RequestBody Cosecha cosecha) {
        return ResponseEntity.status(HttpStatus.CREATED).body(cosechaService.registrar(cosecha));
    }
}
