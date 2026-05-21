/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;
import java.time.LocalDate;

/**
 * Entidad que representa una planta individual dentro del invernadero.
 */
@Entity
@Table(name = "planta")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class Planta {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 50)
    @Column(nullable = false, unique = true)
    private String codigo;

    @NotNull
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "tipo_planta_id", nullable = false)
    private TipoPlanta tipoPlanta;

    @NotNull
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "zona_id", nullable = false)
    private Zona zona;

    @NotNull
    @Column(name = "fecha_siembra", nullable = false)
    private LocalDate fechaSiembra;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private EstadoPlanta estado;

    @Size(max = 500)
    private String observaciones;

    public enum EstadoPlanta {
        SEMBRADA, EN_CRECIMIENTO, LISTA_PARA_COSECHAR, COSECHADA, MUERTA
    }
}
