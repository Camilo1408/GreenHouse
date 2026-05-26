/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Empleado;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.EmpleadoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

/**
 * Servicio para la gestión de empleados del invernadero.
 */
@Service
@RequiredArgsConstructor
@Transactional
public class EmpleadoService {

    private final EmpleadoRepository empleadoRepository;
    private final PasswordEncoder passwordEncoder;

    public List<Empleado> findAll() {
        return empleadoRepository.findAll();
    }

    public Empleado findById(Long id) {
        return empleadoRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Empleado no encontrado con id: " + id));
    }

    public Empleado findByEmail(String email) {
        return empleadoRepository.findByEmail(email)
                .orElseThrow(() -> new ResourceNotFoundException("Empleado no encontrado con email: " + email));
    }

    public Empleado save(Empleado empleado) {
        if (empleadoRepository.existsByEmail(empleado.getEmail())) {
            throw new IllegalArgumentException("Ya existe un empleado con el email: " + empleado.getEmail());
        }
        // Encode password if provided as plain text
        if (empleado.getPasswordHash() != null && !empleado.getPasswordHash().isBlank()) {
            empleado.setPasswordHash(passwordEncoder.encode(empleado.getPasswordHash()));
        }
        // Set defaults for admin-created employees
        empleado.setEmailVerificado(true);
        if (empleado.getAuthProvider() == null) {
            empleado.setAuthProvider(Empleado.AuthProvider.LOCAL);
        }
        return empleadoRepository.save(empleado);
    }

    public Empleado update(Long id, Empleado updated) {
        Empleado existing = findById(id);
        existing.setNombreCompleto(updated.getNombreCompleto());
        existing.setRol(updated.getRol());
        existing.setTelefono(updated.getTelefono());
        existing.setEstado(updated.getEstado());
        return empleadoRepository.save(existing);
    }

    public void delete(Long id) {
        findById(id);
        empleadoRepository.deleteById(id);
    }

    public boolean existsByEmail(String email) {
        return empleadoRepository.existsByEmail(email);
    }
}
