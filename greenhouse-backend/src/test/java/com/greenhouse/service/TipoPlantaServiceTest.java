/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.TipoPlanta;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.TipoPlantaRepository;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Pruebas unitarias para TipoPlantaService.
 * Valida el catálogo de especies cultivables y sus parámetros ambientales.
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("Pruebas unitarias - TipoPlantaService")
class TipoPlantaServiceTest {

    @Mock private TipoPlantaRepository tipoPlantaRepository;
    @InjectMocks private TipoPlantaService tipoPlantaService;

    private TipoPlanta tomate;
    private TipoPlanta lechuga;

    @BeforeEach
    void setUp() {
        tomate = TipoPlanta.builder()
                .id(1L)
                .nombre("Tomate Cherry")
                .descripcion("Tomate de fruto pequeño")
                .temperaturaMin(18.0).temperaturaMax(28.0)
                .humedadMin(60.0).humedadMax(80.0)
                .cicloDias(75)
                .cuidadosEspeciales("Tutorear cuando alcance 30cm")
                .build();

        lechuga = TipoPlanta.builder()
                .id(2L)
                .nombre("Lechuga Romana")
                .temperaturaMin(12.0).temperaturaMax(22.0)
                .humedadMin(50.0).humedadMax(70.0)
                .cicloDias(45)
                .build();
    }

    @Test
    @DisplayName("findAll debe retornar todos los tipos de planta")
    void findAll_debeRetornarTodosLosTipos() {
        when(tipoPlantaRepository.findAll()).thenReturn(List.of(tomate, lechuga));

        List<TipoPlanta> resultado = tipoPlantaService.findAll();

        assertThat(resultado).hasSize(2);
        assertThat(resultado).extracting(TipoPlanta::getNombre)
                .containsExactlyInAnyOrder("Tomate Cherry", "Lechuga Romana");
    }

    @Test
    @DisplayName("findById debe retornar el tipo correcto")
    void findById_tipoExistente_debeRetornar() {
        when(tipoPlantaRepository.findById(1L)).thenReturn(Optional.of(tomate));

        TipoPlanta resultado = tipoPlantaService.findById(1L);

        assertThat(resultado.getNombre()).isEqualTo("Tomate Cherry");
        assertThat(resultado.getCicloDias()).isEqualTo(75);
    }

    @Test
    @DisplayName("findById inexistente debe lanzar ResourceNotFoundException")
    void findById_tipoNoExistente_debeLanzarExcepcion() {
        when(tipoPlantaRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> tipoPlantaService.findById(99L))
                .isInstanceOf(ResourceNotFoundException.class);
    }

    @Test
    @DisplayName("save con nombre nuevo debe persistir el tipo de planta")
    void save_nombreNuevo_debePersistir() {
        when(tipoPlantaRepository.existsByNombre("Tomate Cherry")).thenReturn(false);
        when(tipoPlantaRepository.save(tomate)).thenReturn(tomate);

        TipoPlanta resultado = tipoPlantaService.save(tomate);

        assertThat(resultado.getNombre()).isEqualTo("Tomate Cherry");
        verify(tipoPlantaRepository).save(tomate);
    }

    @Test
    @DisplayName("save con nombre duplicado debe lanzar IllegalArgumentException")
    void save_nombreDuplicado_debeLanzarExcepcion() {
        when(tipoPlantaRepository.existsByNombre("Tomate Cherry")).thenReturn(true);

        assertThatThrownBy(() -> tipoPlantaService.save(tomate))
                .isInstanceOf(IllegalArgumentException.class);
        verify(tipoPlantaRepository, never()).save(any());
    }

    @Test
    @DisplayName("Los rangos de temperatura del Tomate Cherry son válidos")
    void tomate_rangosTemperatura_sonValidos() {
        assertThat(tomate.getTemperaturaMin()).isLessThan(tomate.getTemperaturaMax());
        assertThat(tomate.getTemperaturaMin()).isBetween(0.0, 60.0);
        assertThat(tomate.getTemperaturaMax()).isBetween(0.0, 60.0);
    }

    @Test
    @DisplayName("Los rangos de humedad de la Lechuga Romana son válidos")
    void lechuga_rangosHumedad_sonValidos() {
        assertThat(lechuga.getHumedadMin()).isLessThan(lechuga.getHumedadMax());
        assertThat(lechuga.getHumedadMin()).isBetween(0.0, 100.0);
        assertThat(lechuga.getHumedadMax()).isBetween(0.0, 100.0);
    }

    @Test
    @DisplayName("update debe modificar los campos del tipo de planta")
    void update_debeActualizarCampos() {
        TipoPlanta cambios = TipoPlanta.builder()
                .nombre("Tomate Cherry")
                .temperaturaMin(20.0).temperaturaMax(30.0)
                .humedadMin(65.0).humedadMax(85.0)
                .cicloDias(80)
                .build();

        when(tipoPlantaRepository.findById(1L)).thenReturn(Optional.of(tomate));
        when(tipoPlantaRepository.save(any(TipoPlanta.class))).thenAnswer(i -> i.getArgument(0));

        TipoPlanta resultado = tipoPlantaService.update(1L, cambios);

        assertThat(resultado.getTemperaturaMin()).isEqualTo(20.0);
        assertThat(resultado.getCicloDias()).isEqualTo(80);
    }
}
