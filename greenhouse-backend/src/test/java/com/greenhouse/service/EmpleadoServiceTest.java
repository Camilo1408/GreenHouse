/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Empleado;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.EmpleadoRepository;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Pruebas unitarias para EmpleadoService.
 * Valida la gestión de usuarios del sistema y sus roles.
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("Pruebas unitarias - EmpleadoService")
class EmpleadoServiceTest {

    @Mock private EmpleadoRepository empleadoRepository;
    @Mock private PasswordEncoder passwordEncoder;
    @InjectMocks private EmpleadoService empleadoService;

    private Empleado admin;
    private Empleado empleadoBasico;

    @BeforeEach
    void setUp() {
        admin = Empleado.builder()
                .id(1L)
                .nombreCompleto("Carlos Administrador")
                .email("admin@greenhouse.com")
                .passwordHash("$2a$10$hashedpassword")
                .rol(Empleado.RolEmpleado.ADMINISTRADOR)
                .estado(Empleado.EstadoEmpleado.ACTIVO)
                .emailVerificado(true)
                .authProvider(Empleado.AuthProvider.LOCAL)
                .fechaIngreso(LocalDate.of(2024, 1, 15))
                .build();

        empleadoBasico = Empleado.builder()
                .id(2L)
                .nombreCompleto("Juan Pérez")
                .email("juan@greenhouse.com")
                .passwordHash("$2a$10$hashedpassword2")
                .rol(Empleado.RolEmpleado.EMPLEADO)
                .estado(Empleado.EstadoEmpleado.ACTIVO)
                .emailVerificado(true)
                .authProvider(Empleado.AuthProvider.LOCAL)
                .fechaIngreso(LocalDate.of(2024, 6, 10))
                .build();
    }

    @Test
    @DisplayName("findAll debe retornar todos los empleados registrados")
    void findAll_debeRetornarTodosLosEmpleados() {
        when(empleadoRepository.findAll()).thenReturn(List.of(admin, empleadoBasico));

        List<Empleado> resultado = empleadoService.findAll();

        assertThat(resultado).hasSize(2);
        assertThat(resultado).extracting(Empleado::getRol)
                .containsExactlyInAnyOrder(
                        Empleado.RolEmpleado.ADMINISTRADOR,
                        Empleado.RolEmpleado.EMPLEADO);
    }

    @Test
    @DisplayName("findById debe retornar el empleado correcto")
    void findById_empleadoExistente_debeRetornar() {
        when(empleadoRepository.findById(1L)).thenReturn(Optional.of(admin));

        Empleado resultado = empleadoService.findById(1L);

        assertThat(resultado.getEmail()).isEqualTo("admin@greenhouse.com");
        assertThat(resultado.getRol()).isEqualTo(Empleado.RolEmpleado.ADMINISTRADOR);
    }

    @Test
    @DisplayName("findById con ID inexistente debe lanzar ResourceNotFoundException")
    void findById_empleadoNoExistente_debeLanzarExcepcion() {
        when(empleadoRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> empleadoService.findById(99L))
                .isInstanceOf(ResourceNotFoundException.class);
    }

    @Test
    @DisplayName("save con email nuevo debe persistir el empleado")
    void save_emailNuevo_debePersistir() {
        when(empleadoRepository.existsByEmail("juan@greenhouse.com")).thenReturn(false);
        when(passwordEncoder.encode(any())).thenReturn("$2a$10$encoded_in_test");
        when(empleadoRepository.save(any(Empleado.class))).thenReturn(empleadoBasico);

        Empleado resultado = empleadoService.save(empleadoBasico);

        assertThat(resultado.getNombreCompleto()).isEqualTo("Juan Pérez");
        verify(empleadoRepository).save(any(Empleado.class));
    }

    @Test
    @DisplayName("save con email duplicado debe lanzar IllegalArgumentException")
    void save_emailDuplicado_debeLanzarExcepcion() {
        when(empleadoRepository.existsByEmail("juan@greenhouse.com")).thenReturn(true);

        assertThatThrownBy(() -> empleadoService.save(empleadoBasico))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("email");
        verify(empleadoRepository, never()).save(any());
    }

    @Test
    @DisplayName("update debe actualizar los datos del empleado correctamente")
    void update_debeActualizarDatos() {
        Empleado datosActualizados = Empleado.builder()
                .nombreCompleto("Juan Carlos Pérez")
                .email("juan@greenhouse.com")
                .rol(Empleado.RolEmpleado.SUPERVISOR)
                .estado(Empleado.EstadoEmpleado.ACTIVO)
                .build();

        when(empleadoRepository.findById(2L)).thenReturn(Optional.of(empleadoBasico));
        when(empleadoRepository.save(any(Empleado.class))).thenAnswer(i -> i.getArgument(0));

        Empleado resultado = empleadoService.update(2L, datosActualizados);

        assertThat(resultado.getNombreCompleto()).isEqualTo("Juan Carlos Pérez");
        assertThat(resultado.getRol()).isEqualTo(Empleado.RolEmpleado.SUPERVISOR);
    }

    @Test
    @DisplayName("delete debe eliminar el empleado si existe")
    void delete_empleadoExistente_debeEliminar() {
        when(empleadoRepository.findById(2L)).thenReturn(Optional.of(empleadoBasico));

        empleadoService.delete(2L);

        verify(empleadoRepository).deleteById(2L);
    }

    @Test
    @DisplayName("El empleado ADMINISTRADOR tiene rol correcto")
    void admin_debeSerRolAdministrador() {
        assertThat(admin.getRol()).isEqualTo(Empleado.RolEmpleado.ADMINISTRADOR);
    }

    @Test
    @DisplayName("Empleado con emailVerificado=false no debe poder autenticarse con login local")
    void empleadoSinVerificar_noDebeEstarVerificado() {
        Empleado sinVerificar = Empleado.builder()
                .email("nuevo@test.com")
                .emailVerificado(false)
                .authProvider(Empleado.AuthProvider.LOCAL)
                .build();

        assertThat(sinVerificar.isEmailVerificado()).isFalse();
    }
}
