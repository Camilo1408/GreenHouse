/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.controller;

import com.greenhouse.dto.*;
import com.greenhouse.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
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

    @PostMapping("/register")
    @Operation(summary = "Registrar nuevo usuario con email y contraseña")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        AuthResponse response = authService.registrar(request);
        HttpStatus status = response.isExito() ? HttpStatus.CREATED : HttpStatus.CONFLICT;
        return ResponseEntity.status(status).body(response);
    }

    @GetMapping("/verify")
    @Operation(summary = "Verificar correo electrónico mediante token")
    public void verify(@RequestParam String token, HttpServletResponse response) throws IOException {
        AuthResponse result = authService.verificarEmail(token);
        if (result.isExito()) {
            response.sendRedirect("http://localhost:5173/login?verified=true");
        } else {
            response.sendRedirect("http://localhost:5173/verify-error?msg=" + result.getMensaje());
        }
    }

    @PostMapping("/resend-verification")
    @Operation(summary = "Reenviar correo de verificación")
    public ResponseEntity<AuthResponse> resendVerification(@RequestParam String email) {
        return ResponseEntity.ok(authService.reenviarVerificacion(email));
    }

    @GetMapping("/me")
    @Operation(summary = "Obtener información del usuario autenticado")
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
