/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Alerta;
import com.greenhouse.service.AlertaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

/**
 * Controlador REST para la consulta y gestión de alertas del invernadero.
 */
@RestController
@RequestMapping("/api/alertas")
@RequiredArgsConstructor
@Tag(name = "Alertas", description = "Gestión de alertas generadas por sensores")
public class AlertaController {

    private final AlertaService alertaService;

    @GetMapping
    @Operation(summary = "Listar todas las alertas")
    public ResponseEntity<List<Alerta>> findAll() {
        return ResponseEntity.ok(alertaService.findAll());
    }

    @GetMapping("/pendientes")
    @Operation(summary = "Listar alertas pendientes")
    public ResponseEntity<List<Alerta>> findPendientes() {
        return ResponseEntity.ok(alertaService.findPendientes());
    }

    @GetMapping("/count/pendientes")
    @Operation(summary = "Contar alertas pendientes")
    public ResponseEntity<Map<String, Long>> countPendientes() {
        return ResponseEntity.ok(Map.of("total", alertaService.countPendientes()));
    }

    @PatchMapping("/{id}/atender")
    @Operation(summary = "Marcar alerta como atendida")
    public ResponseEntity<Alerta> atender(@PathVariable Long id) {
        return ResponseEntity.ok(alertaService.atender(id));
    }

    @PatchMapping("/{id}/descartar")
    @Operation(summary = "Descartar una alerta")
    public ResponseEntity<Alerta> descartar(@PathVariable Long id) {
        return ResponseEntity.ok(alertaService.descartar(id));
    }
}
