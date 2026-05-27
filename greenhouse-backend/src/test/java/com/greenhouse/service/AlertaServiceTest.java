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
    @Mock private EmpleadoRepository empleadoRepository;
    @Mock private ZonaRepository zonaRepository;
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

    @Test
    @DisplayName("crearManual debe crear alerta con tipo y zona correctos")
    void crearManual_debePersistirAlerta() {
        when(zonaRepository.findById(1L)).thenReturn(Optional.of(zona));
        when(alertaRepository.save(any())).thenAnswer(inv -> {
            Alerta a = inv.getArgument(0);
            a.setId(99L);
            return a;
        });

        Alerta result = alertaService.crearManual(
                1L, "FALLA_SISTEMA", Alerta.Severidad.MEDIA,
                "Falla detectada en zona A", null);

        assertThat(result.getTipo()).isEqualTo("FALLA_SISTEMA");
        assertThat(result.getSeveridad()).isEqualTo(Alerta.Severidad.MEDIA);
        assertThat(result.getEstado()).isEqualTo(Alerta.EstadoAlerta.PENDIENTE);
        assertThat(result.getZona()).isEqualTo(zona);
        verify(alertaRepository).save(any(Alerta.class));
    }

    @Test
    @DisplayName("crearManual con zona inexistente debe lanzar ResourceNotFoundException")
    void crearManual_zonaNoExistente_debeLanzarExcepcion() {
        when(zonaRepository.findById(99L)).thenReturn(Optional.empty());
        assertThatThrownBy(() -> alertaService.crearManual(
                99L, "FALLA_SISTEMA", Alerta.Severidad.ALTA, "Test", null))
                .isInstanceOf(ResourceNotFoundException.class);
        verify(alertaRepository, never()).save(any());
    }

    @Test
    @DisplayName("agregarNotas debe actualizar las notas de resolución de la alerta")
    void agregarNotas_debeActualizarNotas() {
        when(alertaRepository.findById(1L)).thenReturn(Optional.of(alertaPendiente));
        when(alertaRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        Alerta result = alertaService.agregarNotas(1L, "Se revisó el sensor", null);

        assertThat(result.getNotasResolucion()).isEqualTo("Se revisó el sensor");
        verify(alertaRepository).save(alertaPendiente);
    }
}
