/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Tratamiento;
import com.greenhouse.service.TratamientoService;
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
 * Controlador REST para la gestión de tratamientos aplicados a las plantas.
 */
@RestController
@RequestMapping("/api/tratamientos")
@RequiredArgsConstructor
@Tag(name = "Tratamientos", description = "Gestión de tratamientos y notas de cultivo")
public class TratamientoController {

    private final TratamientoService tratamientoService;

    @GetMapping
    @Operation(summary = "Listar todos los tratamientos")
    @ApiResponse(responseCode = "200", description = "Lista de tratamientos retornada correctamente")
    public ResponseEntity<List<Tratamiento>> findAll() {
        return ResponseEntity.ok(tratamientoService.findAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener tratamiento por ID")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Tratamiento encontrado"),
        @ApiResponse(responseCode = "404", description = "Tratamiento no encontrado")
    })
    public ResponseEntity<Tratamiento> findById(
            @Parameter(description = "ID del tratamiento", required = true) @PathVariable Long id) {
        return ResponseEntity.ok(tratamientoService.findById(id));
    }

    @GetMapping("/planta/{plantaId}")
    @Operation(summary = "Listar tratamientos por planta")
    @ApiResponse(responseCode = "200", description = "Lista de tratamientos de la planta")
    public ResponseEntity<List<Tratamiento>> findByPlanta(
            @Parameter(description = "ID de la planta", required = true) @PathVariable Long plantaId) {
        return ResponseEntity.ok(tratamientoService.findByPlanta(plantaId));
    }

    @PostMapping
    @Operation(summary = "Registrar nuevo tratamiento")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Tratamiento registrado exitosamente"),
        @ApiResponse(responseCode = "400", description = "Datos inválidos"),
        @ApiResponse(responseCode = "404", description = "Planta o empleado no encontrado")
    })
    public ResponseEntity<Tratamiento> create(@Valid @RequestBody Tratamiento tratamiento) {
        return ResponseEntity.status(HttpStatus.CREATED).body(tratamientoService.save(tratamiento));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Actualizar tratamiento")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Tratamiento actualizado correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado"),
        @ApiResponse(responseCode = "404", description = "Tratamiento no encontrado")
    })
    public ResponseEntity<Tratamiento> update(
            @Parameter(description = "ID del tratamiento", required = true) @PathVariable Long id,
            @Valid @RequestBody Tratamiento tratamiento) {
        return ResponseEntity.ok(tratamientoService.update(id, tratamiento));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Eliminar tratamiento")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Tratamiento eliminado correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado (requiere ADMINISTRADOR)"),
        @ApiResponse(responseCode = "404", description = "Tratamiento no encontrado")
    })
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID del tratamiento", required = true) @PathVariable Long id) {
        tratamientoService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
