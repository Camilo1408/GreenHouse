/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.*;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("Pruebas unitarias - AlertaService")
class AlertaServiceTest {

    @Mock private AlertaRepository alertaRepository;
    @InjectMocks private AlertaService alertaService;

    private Alerta alertaPendiente;
    private Zona zona;

    @BeforeEach
    void setUp() {
        zona = Zona.builder().id(1L).nombre("Zona A").estado(Zona.EstadoZona.ACTIVA).build();
        alertaPendiente = Alerta.builder()
                .id(1L)
                .tipo("UMBRAL_TEMPERATURA")
                .severidad(Alerta.Severidad.ALTA)
                .zona(zona)
                .fechaGeneracion(LocalDateTime.now())
                .estado(Alerta.EstadoAlerta.PENDIENTE)
                .descripcion("Temperatura fuera de rango")
                .build();
    }

    @Test
    @DisplayName("Debe retornar todas las alertas")
    void findAll_debeRetornarLista() {
        when(alertaRepository.findAll()).thenReturn(List.of(alertaPendiente));
        List<Alerta> result = alertaService.findAll();
        assertThat(result).hasSize(1);
        verify(alertaRepository).findAll();
    }

    @Test
    @DisplayName("Debe retornar solo alertas pendientes")
    void findPendientes_debeRetornarSoloPendientes() {
        when(alertaRepository.findByEstado(Alerta.EstadoAlerta.PENDIENTE))
                .thenReturn(List.of(alertaPendiente));
        List<Alerta> result = alertaService.findPendientes();
        assertThat(result).allMatch(a -> a.getEstado() == Alerta.EstadoAlerta.PENDIENTE);
    }

    @Test
    @DisplayName("Atender alerta debe cambiar estado a ATENDIDA")
    void atender_debeCambiarEstado() {
        when(alertaRepository.findById(1L)).thenReturn(Optional.of(alertaPendiente));
        when(alertaRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        Alerta result = alertaService.atender(1L);

        assertThat(result.getEstado()).isEqualTo(Alerta.EstadoAlerta.ATENDIDA);
    }

    @Test
    @DisplayName("Descartar alerta debe cambiar estado a DESCARTADA")
    void descartar_debeCambiarEstado() {
        when(alertaRepository.findById(1L)).thenReturn(Optional.of(alertaPendiente));
        when(alertaRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        Alerta result = alertaService.descartar(1L);

        assertThat(result.getEstado()).isEqualTo(Alerta.EstadoAlerta.DESCARTADA);
    }

    @Test
    @DisplayName("Atender alerta inexistente debe lanzar ResourceNotFoundException")
    void atender_alertaNoExistente_debeLanzarExcepcion() {
        when(alertaRepository.findById(99L)).thenReturn(Optional.empty());
        assertThatThrownBy(() -> alertaService.atender(99L))
                .isInstanceOf(ResourceNotFoundException.class);
    }

    @Test
    @DisplayName("Contar alertas pendientes debe retornar el total correcto")
    void countPendientes_debeRetornarTotal() {
        when(alertaRepository.countByEstado(Alerta.EstadoAlerta.PENDIENTE)).thenReturn(5L);
        assertThat(alertaService.countPendientes()).isEqualTo(5L);
    }
}
