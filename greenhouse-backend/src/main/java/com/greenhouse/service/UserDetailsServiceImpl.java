/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Empleado;
import com.greenhouse.repository.EmpleadoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.*;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * Implementación de UserDetailsService para autenticación local con email y contraseña.
 * Spring Security lo usa internamente al procesar el formulario de login.
 */
@Service
@RequiredArgsConstructor
public class UserDetailsServiceImpl implements UserDetailsService {

    private final EmpleadoRepository empleadoRepository;

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        Empleado empleado = empleadoRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("No existe cuenta con el email: " + email));

        if (!empleado.isEmailVerificado()) {
            throw new UsernameNotFoundException("Debes verificar tu correo antes de iniciar sesión.");
        }

        if (empleado.getEstado() == Empleado.EstadoEmpleado.INACTIVO) {
            throw new UsernameNotFoundException("Tu cuenta está inactiva.");
        }

        return User.builder()
                .username(empleado.getEmail())
                .password(empleado.getPasswordHash() != null ? empleado.getPasswordHash() : "")
                .authorities(List.of(new SimpleGrantedAuthority("ROLE_" + empleado.getRol().name())))
                .build();
    }
}
