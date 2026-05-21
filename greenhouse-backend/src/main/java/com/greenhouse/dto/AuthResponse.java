/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.dto;

import lombok.*;

/** DTO de respuesta para operaciones de autenticación. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AuthResponse {
    private String mensaje;
    private boolean exito;
    private String email;
    private String rol;
    private String redirectUrl;
}
