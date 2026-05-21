/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.dto;

import jakarta.validation.constraints.*;
import lombok.Data;

/** DTO para el inicio de sesión con email y contraseña. */
@Data
public class LoginRequest {

    @NotBlank(message = "El email es obligatorio")
    @Email
    private String email;

    @NotBlank(message = "La contraseña es obligatoria")
    private String password;
}
