/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.entity.Empleado;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.service.EmpleadoService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

/**
 * Controlador REST para la gestión de empleados del invernadero.
 */
@RestController
@RequestMapping("/api/empleados")
@RequiredArgsConstructor
@Tag(name = "Empleados", description = "Gestión de empleados y sus roles")
public class EmpleadoController {

    private final EmpleadoService empleadoService;

    /**
     * Returns the employee profile of the currently authenticated user (by email).
     * Accessible to all authenticated roles so that SUPERVISOR/EMPLEADO can auto-fill forms.
     * Returns 404 if the authenticated user has no employee record yet.
     */
    @GetMapping("/me")
    @Operation(summary = "Obtener el perfil del empleado autenticado")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Perfil del empleado o indicador sin_perfil"),
        @ApiResponse(responseCode = "401", description = "No autenticado")
    })
    public ResponseEntity<?> getMe(Authentication auth) {
        if (auth == null) return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        try {
            return ResponseEntity.ok(empleadoService.findByEmail(auth.getName()));
        } catch (ResourceNotFoundException e) {
            return ResponseEntity.ok(Map.of("sin_perfil", true));
        }
    }

    @GetMapping
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Listar todos los empleados")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Lista de empleados retornada correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado (requiere ADMINISTRADOR)")
    })
    public ResponseEntity<List<Empleado>> findAll() {
        return ResponseEntity.ok(empleadoService.findAll());
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Obtener empleado por ID")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Empleado encontrado"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado (requiere ADMINISTRADOR)"),
        @ApiResponse(responseCode = "404", description = "Empleado no encontrado")
    })
    public ResponseEntity<Empleado> findById(
            @Parameter(description = "ID del empleado", required = true) @PathVariable Long id) {
        return ResponseEntity.ok(empleadoService.findById(id));
    }

    @PostMapping
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Registrar nuevo empleado")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Empleado registrado exitosamente"),
        @ApiResponse(responseCode = "400", description = "Email duplicado o datos inválidos"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado (requiere ADMINISTRADOR)")
    })
    public ResponseEntity<Empleado> create(@Valid @RequestBody Empleado empleado) {
        return ResponseEntity.status(HttpStatus.CREATED).body(empleadoService.save(empleado));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Actualizar empleado")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Empleado actualizado correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado (requiere ADMINISTRADOR)"),
        @ApiResponse(responseCode = "404", description = "Empleado no encontrado")
    })
    public ResponseEntity<Empleado> update(
            @Parameter(description = "ID del empleado", required = true) @PathVariable Long id,
            @Valid @RequestBody Empleado empleado) {
        return ResponseEntity.ok(empleadoService.update(id, empleado));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Eliminar empleado")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Empleado eliminado correctamente"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado (requiere ADMINISTRADOR)"),
        @ApiResponse(responseCode = "404", description = "Empleado no encontrado")
    })
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID del empleado", required = true) @PathVariable Long id) {
        empleadoService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
