/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Sensor;
import com.greenhouse.service.SensorService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import java.util.List;

/**
 * Controlador REST para la gestión de sensores del invernadero.
 */
@RestController
@RequestMapping("/api/sensores")
@RequiredArgsConstructor
@Tag(name = "Sensores", description = "Gestión de sensores del invernadero")
public class SensorController {

    private final SensorService sensorService;

    @GetMapping
    @Operation(summary = "Listar todos los sensores")
    public ResponseEntity<List<Sensor>> findAll() {
        return ResponseEntity.ok(sensorService.findAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener sensor por ID")
    public ResponseEntity<Sensor> findById(@PathVariable Long id) {
        return ResponseEntity.ok(sensorService.findById(id));
    }

    @GetMapping("/zona/{zonaId}")
    @Operation(summary = "Listar sensores por zona")
    public ResponseEntity<List<Sensor>> findByZona(@PathVariable Long zonaId) {
        return ResponseEntity.ok(sensorService.findByZona(zonaId));
    }

    @PostMapping
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Crear nuevo sensor")
    public ResponseEntity<Sensor> create(@Valid @RequestBody Sensor sensor) {
        return ResponseEntity.status(HttpStatus.CREATED).body(sensorService.save(sensor));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Actualizar sensor")
    public ResponseEntity<Sensor> update(@PathVariable Long id, @Valid @RequestBody Sensor sensor) {
        return ResponseEntity.ok(sensorService.update(id, sensor));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Eliminar sensor")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        sensorService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
