/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.service.TaigaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * Controlador REST proxy para la API de Taiga.
 * Expone las historias de usuario del proyecto GreenHouse Manager
 * únicamente para usuarios con rol ADMINISTRADOR.
 */
@RestController
@RequestMapping("/api/taiga")
@RequiredArgsConstructor
@Tag(name = "Taiga", description = "Proxy para historias de usuario del proyecto en Taiga")
public class TaigaController {

    private final TaigaService taigaService;

    /**
     * Retorna todas las historias de usuario del proyecto Taiga,
     * agrupables por sprint en el frontend.
     * Solo accesible para ADMINISTRADOR.
     */
    @GetMapping("/historias")
    @PreAuthorize("hasRole('ADMINISTRADOR')")
    @Operation(summary = "Obtener historias de usuario del proyecto Taiga (solo ADMINISTRADOR)")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Lista de historias de usuario del proyecto"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado (requiere ADMINISTRADOR)"),
        @ApiResponse(responseCode = "503", description = "API de Taiga no disponible o credenciales no configuradas")
    })
    public ResponseEntity<?> getHistorias() {
        try {
            List<Map<String, Object>> historias = taigaService.getHistorias();
            return ResponseEntity.ok(historias);
        } catch (IllegalStateException e) {
            // Credenciales no configuradas
            return ResponseEntity.status(503).body(
                Map.of("error", "no_credentials", "mensaje", e.getMessage())
            );
        } catch (Exception e) {
            // API no accesible (timeout, 403 WAF, etc.)
            return ResponseEntity.status(503).body(
                Map.of("error", "taiga_unavailable", "mensaje",
                       "La API de Taiga no está disponible: " + e.getMessage())
            );
        }
    }
}
