/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.dto.*;
import com.greenhouse.entity.*;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Servicio principal de autenticación.
 * Gestiona el registro local (email + contraseña), verificación de correo y login.
 */
@Service
@RequiredArgsConstructor
@Transactional
public class AuthService {

    private final EmpleadoRepository empleadoRepository;
    private final VerificationTokenRepository tokenRepository;
    private final EmailService emailService;
    private final PasswordEncoder passwordEncoder;

    /**
     * Registra un nuevo usuario local.
     * Genera un token de verificación y envía el correo de confirmación.
     */
    public AuthResponse registrar(RegisterRequest request) {
        if (empleadoRepository.existsByEmail(request.getEmail())) {
            return AuthResponse.builder()
                    .exito(false)
                    .mensaje("Ya existe una cuenta con ese correo electrónico.")
                    .build();
        }

        Empleado empleado = Empleado.builder()
                .nombreCompleto(request.getNombreCompleto())
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .rol(Empleado.RolEmpleado.EMPLEADO)
                .estado(Empleado.EstadoEmpleado.ACTIVO)
                .emailVerificado(false)
                .authProvider(Empleado.AuthProvider.LOCAL)
                .fechaIngreso(LocalDate.now())
                .build();

        empleadoRepository.save(empleado);

        String token = UUID.randomUUID().toString();
        VerificationToken vToken = VerificationToken.builder()
                .token(token)
                .empleado(empleado)
                .fechaExpiracion(LocalDateTime.now().plusHours(24))
                .usado(false)
                .build();
        tokenRepository.save(vToken);

        emailService.enviarVerificacion(empleado.getEmail(), empleado.getNombreCompleto(), token);

        return AuthResponse.builder()
                .exito(true)
                .mensaje("Registro exitoso. Revisa tu correo para verificar tu cuenta.")
                .email(empleado.getEmail())
                .build();
    }

    /**
     * Verifica el token de correo y activa la cuenta del usuario.
     */
    public AuthResponse verificarEmail(String token) {
        VerificationToken vToken = tokenRepository.findByToken(token)
                .orElseThrow(() -> new ResourceNotFoundException("Token de verificación inválido."));

        if (vToken.isUsado()) {
            return AuthResponse.builder().exito(false).mensaje("Este enlace ya fue utilizado.").build();
        }
        if (vToken.isExpirado()) {
            return AuthResponse.builder().exito(false).mensaje("El enlace de verificación expiró. Solicita uno nuevo.").build();
        }

        Empleado empleado = vToken.getEmpleado();
        empleado.setEmailVerificado(true);
        empleadoRepository.save(empleado);

        vToken.setUsado(true);
        tokenRepository.save(vToken);

        return AuthResponse.builder()
                .exito(true)
                .mensaje("¡Correo verificado exitosamente! Ya puedes iniciar sesión.")
                .redirectUrl("http://localhost:5173/login?verified=true")
                .build();
    }

    /**
     * Reenvía el correo de verificación si el usuario aún no ha verificado su cuenta.
     */
    public AuthResponse reenviarVerificacion(String email) {
        Empleado empleado = empleadoRepository.findByEmail(email)
                .orElseThrow(() -> new ResourceNotFoundException("No existe cuenta con ese correo."));

        if (empleado.isEmailVerificado()) {
            return AuthResponse.builder().exito(false).mensaje("Este correo ya fue verificado.").build();
        }

        tokenRepository.deleteByEmpleadoId(empleado.getId());

        String token = UUID.randomUUID().toString();
        VerificationToken vToken = VerificationToken.builder()
                .token(token)
                .empleado(empleado)
                .fechaExpiracion(LocalDateTime.now().plusHours(24))
                .usado(false)
                .build();
        tokenRepository.save(vToken);
        emailService.enviarVerificacion(empleado.getEmail(), empleado.getNombreCompleto(), token);

        return AuthResponse.builder()
                .exito(true)
                .mensaje("Correo de verificación reenviado. Revisa tu bandeja de entrada.")
                .build();
    }
}
