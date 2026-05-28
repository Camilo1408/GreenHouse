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

    /**
     * Retorna todos los empleados registrados en el sistema.
     *
     * @return lista completa de empleados (puede estar vacía)
     */
    public List<Empleado> findAll() {
        return empleadoRepository.findAll();
    }

    /**
     * Busca un empleado por su identificador.
     *
     * @param id ID del empleado
     * @return el empleado encontrado
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe un empleado con ese ID
     */
    public Empleado findById(Long id) {
        return empleadoRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Empleado no encontrado con id: " + id));
    }

    /**
     * Busca un empleado por su dirección de correo electrónico.
     *
     * @param email dirección de correo electrónico del empleado
     * @return el empleado encontrado
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe un empleado con ese email
     */
    public Empleado findByEmail(String email) {
        return empleadoRepository.findByEmail(email)
                .orElseThrow(() -> new ResourceNotFoundException("Empleado no encontrado con email: " + email));
    }

    /**
     * Registra un nuevo empleado en el sistema.
     * Codifica la contraseña, activa la verificación de email y asigna proveedor LOCAL por defecto.
     *
     * @param empleado datos del nuevo empleado
     * @return el empleado persistido con su ID asignado
     * @throws IllegalArgumentException si ya existe un empleado con el mismo email
     */
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

    /**
     * Actualiza los datos editables de un empleado existente (nombre, rol, teléfono, estado).
     * El email no se puede cambiar desde este método.
     *
     * @param id      ID del empleado a actualizar
     * @param updated objeto con los nuevos valores
     * @return el empleado actualizado
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe el empleado
     */
    public Empleado update(Long id, Empleado updated) {
        Empleado existing = findById(id);
        existing.setNombreCompleto(updated.getNombreCompleto());
        existing.setRol(updated.getRol());
        existing.setTelefono(updated.getTelefono());
        existing.setEstado(updated.getEstado());
        return empleadoRepository.save(existing);
    }

    /**
     * Elimina un empleado del sistema.
     *
     * @param id ID del empleado a eliminar
     * @throws com.greenhouse.exception.ResourceNotFoundException si no existe el empleado
     */
    public void delete(Long id) {
        findById(id);
        empleadoRepository.deleteById(id);
    }

    /**
     * Verifica si existe un empleado registrado con el email dado.
     *
     * @param email dirección de correo a verificar
     * @return {@code true} si existe; {@code false} en caso contrario
     */
    public boolean existsByEmail(String email) {
        return empleadoRepository.existsByEmail(email);
    }
}
