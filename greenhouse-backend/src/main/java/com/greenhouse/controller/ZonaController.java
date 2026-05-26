/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Zona;
import com.greenhouse.service.ZonaService;
import io.swagger.v3.oas.annotations.Operation;
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
    public ResponseEntity<List<Zona>> findAll() {
        return ResponseEntity.ok(zonaService.findAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener zona por ID")
    public ResponseEntity<Zona> findById(@PathVariable Long id) {
        return ResponseEntity.ok(zonaService.findById(id));
    }

    @PostMapping
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Crear nueva zona")
    public ResponseEntity<Zona> create(@Valid @RequestBody Zona zona) {
        return ResponseEntity.status(HttpStatus.CREATED).body(zonaService.save(zona));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Actualizar zona existente")
    public ResponseEntity<Zona> update(@PathVariable Long id, @Valid @RequestBody Zona zona) {
        return ResponseEntity.ok(zonaService.update(id, zona));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Eliminar zona")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        zonaService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
