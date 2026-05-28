/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.dto.*;
import com.greenhouse.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;

/**
 * Controlador REST para registro, verificación de correo y autenticación de usuarios.
 */
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Tag(name = "Autenticación", description = "Registro, login y verificación de correo")
public class AuthController {

    private final AuthService authService;

    @Value("${app.frontend-url:http://localhost:5173}")
    private String frontendUrl;

    @PostMapping("/register")
    @Operation(summary = "Registrar nuevo usuario con email y contraseña")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Usuario registrado. Se envía correo de verificación"),
        @ApiResponse(responseCode = "409", description = "El email ya está registrado")
    })
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        AuthResponse response = authService.registrar(request);
        HttpStatus status = response.isExito() ? HttpStatus.CREATED : HttpStatus.CONFLICT;
        return ResponseEntity.status(status).body(response);
    }

    @GetMapping("/verify")
    @Operation(summary = "Verificar correo electrónico mediante token")
    @ApiResponses({
        @ApiResponse(responseCode = "302", description = "Redirige al frontend con resultado de la verificación")
    })
    public void verify(
            @Parameter(description = "Token UUID de verificación enviado al correo", required = true)
            @RequestParam String token,
            HttpServletResponse response) throws IOException {
        AuthResponse result = authService.verificarEmail(token);
        if (result.isExito()) {
            response.sendRedirect(frontendUrl + "/login?verified=true");
        } else {
            response.sendRedirect(frontendUrl + "/verify-error?msg=" + result.getMensaje());
        }
    }

    @PostMapping("/resend-verification")
    @Operation(summary = "Reenviar correo de verificación")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Correo de verificación reenviado correctamente"),
        @ApiResponse(responseCode = "404", description = "No existe cuenta con ese correo")
    })
    public ResponseEntity<AuthResponse> resendVerification(
            @Parameter(description = "Email del usuario que necesita reenvío", required = true)
            @RequestParam String email) {
        return ResponseEntity.ok(authService.reenviarVerificacion(email));
    }

    @GetMapping("/me")
    @Operation(summary = "Obtener información del usuario autenticado")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Información del usuario autenticado (email y rol)"),
        @ApiResponse(responseCode = "401", description = "No autenticado")
    })
    public ResponseEntity<AuthResponse> me(org.springframework.security.core.Authentication auth) {
        if (auth == null || !auth.isAuthenticated()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        return ResponseEntity.ok(AuthResponse.builder()
                .exito(true)
                .email(auth.getName())
                .rol(auth.getAuthorities().stream().findFirst()
                        .map(a -> a.getAuthority().replace("ROLE_", ""))
                        .orElse("EMPLEADO"))
                .build());
    }
}
