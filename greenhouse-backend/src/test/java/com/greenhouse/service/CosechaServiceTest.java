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

import java.time.LocalDate;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("Pruebas unitarias - CosechaService")
class CosechaServiceTest {

    @Mock private CosechaRepository cosechaRepository;
    @Mock private PlantaRepository plantaRepository;
    @InjectMocks private CosechaService cosechaService;

    private Planta planta;
    private Empleado empleado;

    @BeforeEach
    void setUp() {
        planta = Planta.builder()
                .id(1L).codigo("PLT-001")
                .estado(Planta.EstadoPlanta.LISTA_PARA_COSECHAR)
                .build();
        empleado = Empleado.builder()
                .id(1L).email("empleado@test.com")
                .rol(Empleado.RolEmpleado.EMPLEADO)
                .build();
    }

    @Test
    @DisplayName("registrar cosecha debe actualizar estado de la planta a COSECHADA")
    void registrar_debeActualizarEstadoPlanta() {
        Cosecha cosecha = Cosecha.builder()
                .planta(planta).empleado(empleado)
                .fechaCosecha(LocalDate.now())
                .pesoKg(5.0)
                .calidad(Cosecha.CalidadCosecha.A)
                .destino(Cosecha.DestinoCosecha.VENTA)
                .build();

        when(plantaRepository.findById(1L)).thenReturn(Optional.of(planta));
        when(cosechaRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        cosechaService.registrar(cosecha);

        assertThat(planta.getEstado()).isEqualTo(Planta.EstadoPlanta.COSECHADA);
        verify(plantaRepository).save(planta);
    }

    @Test
    @DisplayName("registrar cosecha con planta inexistente debe lanzar excepción")
    void registrar_plantaNoExistente_debeLanzarExcepcion() {
        Cosecha cosecha = Cosecha.builder().planta(planta).build();
        when(plantaRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> cosechaService.registrar(cosecha))
                .isInstanceOf(ResourceNotFoundException.class);
    }

    @Test
    @DisplayName("totalKgMes debe retornar 0 si no hay cosechas")
    void totalKgMes_sinCosechas_debeRetornarCero() {
        when(cosechaRepository.sumPesoKgByFechaCosechaBetween(any(), any())).thenReturn(null);
        assertThat(cosechaService.totalKgMes(2026, 5)).isEqualTo(0.0);
    }
}
