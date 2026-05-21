/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import com.greenhouse.entity.Zona;
import com.greenhouse.exception.ResourceNotFoundException;
import com.greenhouse.repository.ZonaRepository;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("Pruebas unitarias - ZonaService")
class ZonaServiceTest {

    @Mock private ZonaRepository zonaRepository;
    @InjectMocks private ZonaService zonaService;

    private Zona zona;

    @BeforeEach
    void setUp() {
        zona = Zona.builder()
                .id(1L)
                .nombre("Zona A")
                .dimensionM2(50.0)
                .capacidadMaxPlantas(100)
                .estado(Zona.EstadoZona.ACTIVA)
                .ubicacion("Sector Norte")
                .build();
    }

    @Test
    @DisplayName("findAll debe retornar todas las zonas")
    void findAll_debeRetornarLista() {
        when(zonaRepository.findAll()).thenReturn(List.of(zona));
        assertThat(zonaService.findAll()).hasSize(1);
    }

    @Test
    @DisplayName("findById debe retornar la zona correcta")
    void findById_zonaExistente_debeRetornarZona() {
        when(zonaRepository.findById(1L)).thenReturn(Optional.of(zona));
        Zona result = zonaService.findById(1L);
        assertThat(result.getNombre()).isEqualTo("Zona A");
    }

    @Test
    @DisplayName("findById con ID inexistente debe lanzar ResourceNotFoundException")
    void findById_zonaNoExistente_debeLanzarExcepcion() {
        when(zonaRepository.findById(99L)).thenReturn(Optional.empty());
        assertThatThrownBy(() -> zonaService.findById(99L))
                .isInstanceOf(ResourceNotFoundException.class);
    }

    @Test
    @DisplayName("save debe persistir la zona si el nombre no existe")
    void save_nombreNuevo_debePersistir() {
        when(zonaRepository.existsByNombre("Zona A")).thenReturn(false);
        when(zonaRepository.save(zona)).thenReturn(zona);

        Zona result = zonaService.save(zona);
        assertThat(result.getNombre()).isEqualTo("Zona A");
        verify(zonaRepository).save(zona);
    }

    @Test
    @DisplayName("save con nombre duplicado debe lanzar IllegalArgumentException")
    void save_nombreDuplicado_debeLanzarExcepcion() {
        when(zonaRepository.existsByNombre("Zona A")).thenReturn(true);
        assertThatThrownBy(() -> zonaService.save(zona))
                .isInstanceOf(IllegalArgumentException.class);
        verify(zonaRepository, never()).save(any());
    }

    @Test
    @DisplayName("delete debe eliminar la zona si existe")
    void delete_zonaExistente_debeEliminar() {
        when(zonaRepository.findById(1L)).thenReturn(Optional.of(zona));
        zonaService.delete(1L);
        verify(zonaRepository).deleteById(1L);
    }
}
