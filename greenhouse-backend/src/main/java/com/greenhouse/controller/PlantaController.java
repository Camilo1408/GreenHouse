/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Planta;
import com.greenhouse.service.PlantaService;
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
 * Controlador REST para la gestión de plantas del invernadero.
 */
@RestController
@RequestMapping("/api/plantas")
@RequiredArgsConstructor
@Tag(name = "Plantas", description = "Gestión del ciclo de vida de las plantas")
public class PlantaController {

    private final PlantaService plantaService;

    @GetMapping
    @Operation(summary = "Listar todas las plantas")
    @ApiResponse(responseCode = "200", description = "Lista de plantas retornada correctamente")
    public ResponseEntity<List<Planta>> findAll() {
        return ResponseEntity.ok(plantaService.findAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener planta por ID")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Planta encontrada"),
        @ApiResponse(responseCode = "404", description = "Planta no encontrada")
    })
    public ResponseEntity<Planta> findById(
            @Parameter(description = "ID de la planta", required = true) @PathVariable Long id) {
        return ResponseEntity.ok(plantaService.findById(id));
    }

    @GetMapping("/zona/{zonaId}")
    @Operation(summary = "Listar plantas por zona")
    @ApiResponse(responseCode = "200", description = "Lista de plantas en la zona")
    public ResponseEntity<List<Planta>> findByZona(
            @Parameter(description = "ID de la zona", required = true) @PathVariable Long zonaId) {
        return ResponseEntity.ok(plantaService.findByZona(zonaId));
    }

    @GetMapping("/estado/{estado}")
    @Operation(summary = "Listar plantas por estado")
    @ApiResponse(responseCode = "200", description = "Lista de plantas con el estado indicado")
    public ResponseEntity<List<Planta>> findByEstado(
            @Parameter(description = "Estado de la planta (SEMBRADA, EN_CRECIMIENTO, LISTA_PARA_COSECHAR, COSECHADA, BAJA)", required = true)
            @PathVariable Planta.EstadoPlanta estado) {
        return ResponseEntity.ok(plantaService.findByEstado(estado));
    }

    @PostMapping
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Registrar nueva planta")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Planta registrada exitosamente"),
        @ApiResponse(responseCode = "400", description = "Datos inválidos o código duplicado"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado")
    })
    public ResponseEntity<Planta> create(@Valid @RequestBody Planta planta) {
        return ResponseEntity.status(HttpStatus.CREATED).body(plantaService.save(planta));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Actualizar planta")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Planta actualizada correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado"),
        @ApiResponse(responseCode = "404", description = "Planta no encontrada")
    })
    public ResponseEntity<Planta> update(
            @Parameter(description = "ID de la planta", required = true) @PathVariable Long id,
            @Valid @RequestBody Planta planta) {
        return ResponseEntity.ok(plantaService.update(id, planta));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Eliminar planta")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Planta eliminada correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado (requiere ADMINISTRADOR)"),
        @ApiResponse(responseCode = "404", description = "Planta no encontrada")
    })
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID de la planta", required = true) @PathVariable Long id) {
        plantaService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
