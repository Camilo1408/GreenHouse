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

/**
 * Entidad que representa una zona física dentro del invernadero.
 */
@Entity
@Table(name = "zona")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class Zona {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 100)
    @Column(nullable = false, unique = true)
    private String nombre;

    @DecimalMin("0.1")
    @Column(name = "dimension_m2")
    private Double dimensionM2;

    @Min(1)
    @Column(name = "capacidad_max_plantas")
    private Integer capacidadMaxPlantas;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private EstadoZona estado;

    @Size(max = 200)
    private String ubicacion;

    public enum EstadoZona {
        ACTIVA, EN_MANTENIMIENTO, INACTIVA
    }
}
