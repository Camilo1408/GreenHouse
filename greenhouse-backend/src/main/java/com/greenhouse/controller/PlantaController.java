/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Planta;
import com.greenhouse.service.PlantaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
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
    public ResponseEntity<List<Planta>> findAll() {
        return ResponseEntity.ok(plantaService.findAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener planta por ID")
    public ResponseEntity<Planta> findById(@PathVariable Long id) {
        return ResponseEntity.ok(plantaService.findById(id));
    }

    @GetMapping("/zona/{zonaId}")
    @Operation(summary = "Listar plantas por zona")
    public ResponseEntity<List<Planta>> findByZona(@PathVariable Long zonaId) {
        return ResponseEntity.ok(plantaService.findByZona(zonaId));
    }

    @GetMapping("/estado/{estado}")
    @Operation(summary = "Listar plantas por estado")
    public ResponseEntity<List<Planta>> findByEstado(@PathVariable Planta.EstadoPlanta estado) {
        return ResponseEntity.ok(plantaService.findByEstado(estado));
    }

    @PostMapping
    @Operation(summary = "Registrar nueva planta")
    public ResponseEntity<Planta> create(@Valid @RequestBody Planta planta) {
        return ResponseEntity.status(HttpStatus.CREATED).body(plantaService.save(planta));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Actualizar planta")
    public ResponseEntity<Planta> update(@PathVariable Long id, @Valid @RequestBody Planta planta) {
        return ResponseEntity.ok(plantaService.update(id, planta));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Eliminar planta")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        plantaService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
