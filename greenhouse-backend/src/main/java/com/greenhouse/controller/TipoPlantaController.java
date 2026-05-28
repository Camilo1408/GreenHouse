/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.TipoPlanta;
import com.greenhouse.service.TipoPlantaService;
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

/** Controlador REST para tipos de planta. */
@RestController
@RequestMapping("/api/tipos-planta")
@RequiredArgsConstructor
@Tag(name = "Tipos de Planta", description = "Catálogo de tipos de planta cultivables")
public class TipoPlantaController {

    private final TipoPlantaService service;

    @GetMapping
    @Operation(summary = "Listar todos los tipos de planta")
    @ApiResponse(responseCode = "200", description = "Catálogo completo de tipos de planta")
    public ResponseEntity<List<TipoPlanta>> findAll() { return ResponseEntity.ok(service.findAll()); }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener tipo de planta por ID")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Tipo de planta encontrado"),
        @ApiResponse(responseCode = "404", description = "Tipo de planta no encontrado")
    })
    public ResponseEntity<TipoPlanta> findById(
            @Parameter(description = "ID del tipo de planta", required = true) @PathVariable Long id) {
        return ResponseEntity.ok(service.findById(id));
    }

    @PostMapping
    @Operation(summary = "Crear tipo de planta")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Tipo de planta creado exitosamente"),
        @ApiResponse(responseCode = "400", description = "Nombre duplicado o datos inválidos")
    })
    public ResponseEntity<TipoPlanta> create(@Valid @RequestBody TipoPlanta tp) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.save(tp));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Actualizar tipo de planta")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Tipo de planta actualizado correctamente"),
        @ApiResponse(responseCode = "404", description = "Tipo de planta no encontrado")
    })
    public ResponseEntity<TipoPlanta> update(
            @Parameter(description = "ID del tipo de planta", required = true) @PathVariable Long id,
            @Valid @RequestBody TipoPlanta tp) {
        return ResponseEntity.ok(service.update(id, tp));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Eliminar tipo de planta")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Tipo de planta eliminado correctamente"),
        @ApiResponse(responseCode = "404", description = "Tipo de planta no encontrado")
    })
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID del tipo de planta", required = true) @PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
