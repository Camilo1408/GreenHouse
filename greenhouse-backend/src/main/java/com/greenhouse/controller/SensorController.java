/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Sensor;
import com.greenhouse.service.SensorService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
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
    @ApiResponse(responseCode = "200", description = "Lista de sensores retornada correctamente")
    public ResponseEntity<List<Sensor>> findAll() {
        return ResponseEntity.ok(sensorService.findAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener sensor por ID")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Sensor encontrado"),
        @ApiResponse(responseCode = "404", description = "Sensor no encontrado")
    })
    public ResponseEntity<Sensor> findById(
            @Parameter(description = "ID del sensor", required = true) @PathVariable Long id) {
        return ResponseEntity.ok(sensorService.findById(id));
    }

    @GetMapping("/zona/{zonaId}")
    @Operation(summary = "Listar sensores por zona")
    @ApiResponse(responseCode = "200", description = "Lista de sensores en la zona")
    public ResponseEntity<List<Sensor>> findByZona(
            @Parameter(description = "ID de la zona", required = true) @PathVariable Long zonaId) {
        return ResponseEntity.ok(sensorService.findByZona(zonaId));
    }

    @PostMapping
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Crear nuevo sensor")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Sensor creado exitosamente"),
        @ApiResponse(responseCode = "400", description = "Código duplicado o datos inválidos"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado")
    })
    public ResponseEntity<Sensor> create(@Valid @RequestBody Sensor sensor) {
        return ResponseEntity.status(HttpStatus.CREATED).body(sensorService.save(sensor));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Actualizar sensor")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Sensor actualizado correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado"),
        @ApiResponse(responseCode = "404", description = "Sensor o zona no encontrado")
    })
    public ResponseEntity<Sensor> update(
            @Parameter(description = "ID del sensor", required = true) @PathVariable Long id,
            @Valid @RequestBody Sensor sensor) {
        return ResponseEntity.ok(sensorService.update(id, sensor));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Eliminar sensor")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Sensor eliminado correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado (requiere ADMINISTRADOR)"),
        @ApiResponse(responseCode = "404", description = "Sensor no encontrado")
    })
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID del sensor", required = true) @PathVariable Long id) {
        sensorService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
