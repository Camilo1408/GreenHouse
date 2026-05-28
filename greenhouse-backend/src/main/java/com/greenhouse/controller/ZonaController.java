/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Zona;
import com.greenhouse.service.ZonaService;
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
 * Controlador REST para la gestión de zonas del invernadero.
 */
@RestController
@RequestMapping("/api/zonas")
@RequiredArgsConstructor
@Tag(name = "Zonas", description = "Gestión de zonas del invernadero")
public class ZonaController {

    private final ZonaService zonaService;

    @GetMapping
    @Operation(summary = "Listar todas las zonas")
    @ApiResponse(responseCode = "200", description = "Lista de zonas retornada correctamente")
    public ResponseEntity<List<Zona>> findAll() {
        return ResponseEntity.ok(zonaService.findAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener zona por ID")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Zona encontrada"),
        @ApiResponse(responseCode = "404", description = "Zona no encontrada")
    })
    public ResponseEntity<Zona> findById(
            @Parameter(description = "ID de la zona", required = true) @PathVariable Long id) {
        return ResponseEntity.ok(zonaService.findById(id));
    }

    @PostMapping
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Crear nueva zona")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Zona creada exitosamente"),
        @ApiResponse(responseCode = "400", description = "Nombre de zona duplicado o datos inválidos"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado")
    })
    public ResponseEntity<Zona> create(@Valid @RequestBody Zona zona) {
        return ResponseEntity.status(HttpStatus.CREATED).body(zonaService.save(zona));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Actualizar zona existente")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Zona actualizada correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado"),
        @ApiResponse(responseCode = "404", description = "Zona no encontrada")
    })
    public ResponseEntity<Zona> update(
            @Parameter(description = "ID de la zona", required = true) @PathVariable Long id,
            @Valid @RequestBody Zona zona) {
        return ResponseEntity.ok(zonaService.update(id, zona));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Eliminar zona")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Zona eliminada correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado (requiere ADMINISTRADOR)"),
        @ApiResponse(responseCode = "404", description = "Zona no encontrada")
    })
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID de la zona", required = true) @PathVariable Long id) {
        zonaService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
