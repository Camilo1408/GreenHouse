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
    public ResponseEntity<List<Empleado>> findAll() {
        return ResponseEntity.ok(empleadoService.findAll());
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Obtener empleado por ID")
    public ResponseEntity<Empleado> findById(@PathVariable Long id) {
        return ResponseEntity.ok(empleadoService.findById(id));
    }

    @PostMapping
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Registrar nuevo empleado")
    public ResponseEntity<Empleado> create(@Valid @RequestBody Empleado empleado) {
        return ResponseEntity.status(HttpStatus.CREATED).body(empleadoService.save(empleado));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Actualizar empleado")
    public ResponseEntity<Empleado> update(@PathVariable Long id, @Valid @RequestBody Empleado empleado) {
        return ResponseEntity.ok(empleadoService.update(id, empleado));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Eliminar empleado")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        empleadoService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
