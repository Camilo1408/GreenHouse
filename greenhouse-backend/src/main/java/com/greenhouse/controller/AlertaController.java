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
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
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

    @GetMapping("/zona/{zonaId}")
    @Operation(summary = "Listar alertas por zona")
    public ResponseEntity<List<Alerta>> findByZona(@PathVariable Long zonaId) {
        return ResponseEntity.ok(alertaService.findByZona(zonaId));
    }

    @PostMapping
    @Operation(summary = "Crear alerta manual (novedad reportada por empleado/supervisor)")
    public ResponseEntity<Alerta> crearManual(@RequestBody Map<String, Object> body) {
        Long zonaId = Long.valueOf(body.get("zonaId").toString());
        String tipo = (String) body.get("tipo");
        Alerta.Severidad severidad = Alerta.Severidad.valueOf((String) body.get("severidad"));
        String descripcion = (String) body.get("descripcion");
        Long empleadoId = body.get("empleadoId") != null
                ? Long.valueOf(body.get("empleadoId").toString()) : null;
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(alertaService.crearManual(zonaId, tipo, severidad, descripcion, empleadoId));
    }

    @PatchMapping("/{id}/atender")
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Marcar alerta como atendida, con notas opcionales y empleado responsable")
    public ResponseEntity<Alerta> atender(
            @PathVariable Long id,
            @RequestBody(required = false) Map<String, Object> body) {
        String notas = body != null ? (String) body.get("notas") : null;
        Long empleadoId = body != null && body.get("empleadoId") != null
                ? Long.valueOf(body.get("empleadoId").toString()) : null;
        return ResponseEntity.ok(alertaService.atender(id, notas, empleadoId));
    }

    @PatchMapping("/{id}/descartar")
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Descartar una alerta, con notas opcionales")
    public ResponseEntity<Alerta> descartar(
            @PathVariable Long id,
            @RequestBody(required = false) Map<String, Object> body) {
        String notas = body != null ? (String) body.get("notas") : null;
        Long empleadoId = body != null && body.get("empleadoId") != null
                ? Long.valueOf(body.get("empleadoId").toString()) : null;
        return ResponseEntity.ok(alertaService.descartar(id, notas, empleadoId));
    }

    @PatchMapping("/{id}/notas")
    @PreAuthorize("hasAnyRole('ADMINISTRADOR','SUPERVISOR')")
    @Operation(summary = "Agregar notas a una alerta (cualquier estado)")
    public ResponseEntity<Alerta> agregarNotas(
            @PathVariable Long id,
            @RequestBody Map<String, Object> body) {
        String notas = (String) body.get("notas");
        Long empleadoId = body.get("empleadoId") != null
                ? Long.valueOf(body.get("empleadoId").toString()) : null;
        return ResponseEntity.ok(alertaService.agregarNotas(id, notas, empleadoId));
    }
}
