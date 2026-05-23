/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;
import java.time.LocalDate;

/**
 * Entidad que representa un empleado del invernadero con acceso al sistema.
 * Soporta autenticación local (email + contraseña) y OAuth2 (Google).
 */
@Entity
@Table(name = "empleado")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler", "passwordHash"})
public class Empleado {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 150)
    @Column(name = "nombre_completo", nullable = false)
    private String nombreCompleto;

    @NotBlank
    @Email
    @Column(nullable = false, unique = true)
    private String email;

    /** Contraseña hasheada con BCrypt. Null si el usuario se registró con Google. */
    @JsonIgnore
    @Column(name = "password_hash")
    private String passwordHash;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RolEmpleado rol;

    @Size(max = 20)
    private String telefono;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private EstadoEmpleado estado = EstadoEmpleado.ACTIVO;

    @Column(name = "fecha_ingreso")
    private LocalDate fechaIngreso;

    /** Indica si el correo fue verificado (requerido para login local). */
    @Column(name = "email_verificado")
    @Builder.Default
    private boolean emailVerificado = false;

    /** Origen del registro del usuario. */
    @Enumerated(EnumType.STRING)
    @Column(name = "auth_provider")
    @Builder.Default
    private AuthProvider authProvider = AuthProvider.LOCAL;

    public enum RolEmpleado {
        ADMINISTRADOR, EMPLEADO, SUPERVISOR
    }

    public enum EstadoEmpleado {
        ACTIVO, INACTIVO
    }

    public enum AuthProvider {
        LOCAL, GOOGLE
    }
}
