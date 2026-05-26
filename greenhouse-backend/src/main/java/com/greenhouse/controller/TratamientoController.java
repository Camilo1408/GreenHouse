/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Tratamiento;
import com.greenhouse.service.TratamientoService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
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
    public ResponseEntity<List<Tratamiento>> findAll() {
        return ResponseEntity.ok(tratamientoService.findAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener tratamiento por ID")
    public ResponseEntity<Tratamiento> findById(@PathVariable Long id) {
        return ResponseEntity.ok(tratamientoService.findById(id));
    }

    @GetMapping("/planta/{plantaId}")
    @Operation(summary = "Listar tratamientos por planta")
    public ResponseEntity<List<Tratamiento>> findByPlanta(@PathVariable Long plantaId) {
        return ResponseEntity.ok(tratamientoService.findByPlanta(plantaId));
    }

    @PostMapping
    @Operation(summary = "Registrar nuevo tratamiento")
    public ResponseEntity<Tratamiento> create(@Valid @RequestBody Tratamiento tratamiento) {
        return ResponseEntity.status(HttpStatus.CREATED).body(tratamientoService.save(tratamiento));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Actualizar tratamiento")
    public ResponseEntity<Tratamiento> update(@PathVariable Long id, @Valid @RequestBody Tratamiento tratamiento) {
        return ResponseEntity.ok(tratamientoService.update(id, tratamiento));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Eliminar tratamiento")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        tratamientoService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
