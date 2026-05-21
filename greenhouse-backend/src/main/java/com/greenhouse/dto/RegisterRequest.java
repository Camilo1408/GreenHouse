/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.dto;

import jakarta.validation.constraints.*;
import lombok.Data;

/** DTO para el registro de un nuevo usuario con email y contraseña. */
@Data
public class RegisterRequest {

    @NotBlank(message = "El nombre completo es obligatorio")
    @Size(max = 150)
    private String nombreCompleto;

    @NotBlank(message = "El email es obligatorio")
    @Email(message = "El email no tiene un formato válido")
    private String email;

    @NotBlank(message = "La contraseña es obligatoria")
    @Size(min = 8, message = "La contraseña debe tener al menos 8 caracteres")
    private String password;
}
