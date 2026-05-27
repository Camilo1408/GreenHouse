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
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Pruebas unitarias para PlantaService.
 * Valida el ciclo de vida completo de una planta en el invernadero.
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("Pruebas unitarias - PlantaService")
class PlantaServiceTest {

    @Mock private PlantaRepository       plantaRepository;
    @Mock private ZonaRepository         zonaRepository;
    @Mock private TipoPlantaRepository   tipoPlantaRepository;
    @Mock private TratamientoRepository  tratamientoRepository;
    @Mock private CosechaRepository      cosechaRepository;
    @InjectMocks private PlantaService plantaService;

    private Planta planta;
    private Zona zona;
    private TipoPlanta tipoPlanta;

    @BeforeEach
    void setUp() {
        zona = Zona.builder()
                .id(1L).nombre("Zona A")
                .estado(Zona.EstadoZona.ACTIVA)
                .build();

        tipoPlanta = TipoPlanta.builder()
                .id(1L).nombre("Tomate Cherry")
                .temperaturaMin(18.0).temperaturaMax(28.0)
                .humedadMin(60.0).humedadMax(80.0)
                .cicloDias(75)
                .build();

        planta = Planta.builder()
                .id(1L)
                .codigo("TOM-001")
                .tipoPlanta(tipoPlanta)
                .zona(zona)
                .fechaSiembra(LocalDate.of(2026, 3, 1))
                .estado(Planta.EstadoPlanta.EN_CRECIMIENTO)
                .build();
    }

    @Test
    @DisplayName("findAll debe retornar la lista completa de plantas")
    void findAll_debeRetornarTodasLasPlantas() {
        when(plantaRepository.findAll()).thenReturn(List.of(planta));

        List<Planta> resultado = plantaService.findAll();

        assertThat(resultado).hasSize(1);
        assertThat(resultado.get(0).getCodigo()).isEqualTo("TOM-001");
    }

    @Test
    @DisplayName("findById debe retornar la planta cuando existe")
    void findById_plantaExistente_debeRetornar() {
        when(plantaRepository.findById(1L)).thenReturn(Optional.of(planta));

        Planta resultado = plantaService.findById(1L);

        assertThat(resultado.getCodigo()).isEqualTo("TOM-001");
        assertThat(resultado.getEstado()).isEqualTo(Planta.EstadoPlanta.EN_CRECIMIENTO);
    }

    @Test
    @DisplayName("findById con ID inexistente debe lanzar ResourceNotFoundException")
    void findById_plantaNoExistente_debeLanzarExcepcion() {
        when(plantaRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> plantaService.findById(99L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("99");
    }

    @Test
    @DisplayName("save debe persistir la planta si el código no existe")
    void save_codigoNuevo_debePersistir() {
        when(plantaRepository.existsByCodigo("TOM-001")).thenReturn(false);
        when(zonaRepository.existsById(1L)).thenReturn(true);
        when(tipoPlantaRepository.existsById(1L)).thenReturn(true);
        when(plantaRepository.save(planta)).thenReturn(planta);

        Planta resultado = plantaService.save(planta);

        assertThat(resultado.getCodigo()).isEqualTo("TOM-001");
        verify(plantaRepository).save(planta);
    }

    @Test
    @DisplayName("save con código duplicado debe lanzar IllegalArgumentException")
    void save_codigoDuplicado_debeLanzarExcepcion() {
        when(plantaRepository.existsByCodigo("TOM-001")).thenReturn(true);

        assertThatThrownBy(() -> plantaService.save(planta))
                .isInstanceOf(IllegalArgumentException.class);
        verify(plantaRepository, never()).save(any());
    }

    @Test
    @DisplayName("findByZona debe retornar solo plantas de esa zona")
    void findByZona_debeRetornarPlantasDeLaZona() {
        when(plantaRepository.findByZonaId(1L)).thenReturn(List.of(planta));

        List<Planta> resultado = plantaService.findByZona(1L);

        assertThat(resultado).hasSize(1);
        assertThat(resultado.get(0).getZona().getNombre()).isEqualTo("Zona A");
    }

    @Test
    @DisplayName("findByEstado debe retornar plantas con el estado indicado")
    void findByEstado_debeRetornarPlantasFiltradas() {
        when(plantaRepository.findByEstado(Planta.EstadoPlanta.EN_CRECIMIENTO))
                .thenReturn(List.of(planta));

        List<Planta> resultado = plantaService.findByEstado(Planta.EstadoPlanta.EN_CRECIMIENTO);

        assertThat(resultado).hasSize(1);
        assertThat(resultado.get(0).getEstado()).isEqualTo(Planta.EstadoPlanta.EN_CRECIMIENTO);
    }

    @Test
    @DisplayName("update debe cambiar el estado de la planta correctamente")
    void update_debeActualizarEstado() {
        Planta actualizada = Planta.builder()
                .codigo("TOM-001")
                .tipoPlanta(tipoPlanta)
                .zona(zona)
                .fechaSiembra(LocalDate.of(2026, 3, 1))
                .estado(Planta.EstadoPlanta.LISTA_PARA_COSECHAR)
                .build();

        when(plantaRepository.findById(1L)).thenReturn(Optional.of(planta));
        when(zonaRepository.existsById(1L)).thenReturn(true);
        when(tipoPlantaRepository.existsById(1L)).thenReturn(true);
        when(plantaRepository.save(any(Planta.class))).thenAnswer(i -> i.getArgument(0));

        Planta resultado = plantaService.update(1L, actualizada);

        assertThat(resultado.getEstado()).isEqualTo(Planta.EstadoPlanta.LISTA_PARA_COSECHAR);
    }

    @Test
    @DisplayName("delete debe eliminar la planta y sus dependencias (tratamientos y cosechas)")
    void delete_plantaExistente_debeEliminar() {
        when(plantaRepository.findById(1L)).thenReturn(Optional.of(planta));
        // Stub de dependencias cascade: la planta de prueba no tiene tratamientos
        // ni cosechas asociadas, por lo que se devuelven listas vacias
        when(tratamientoRepository.findByPlantaId(1L)).thenReturn(Collections.emptyList());
        when(cosechaRepository.findByPlantaId(1L)).thenReturn(Collections.emptyList());

        plantaService.delete(1L);

        verify(tratamientoRepository).deleteAll(Collections.emptyList());
        verify(cosechaRepository).deleteAll(Collections.emptyList());
        verify(plantaRepository).deleteById(1L);
    }
}
