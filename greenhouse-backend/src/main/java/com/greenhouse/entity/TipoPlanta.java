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
 * Entidad que representa un tipo o especie de planta cultivable en el invernadero.
 */
@Entity
@Table(name = "tipo_planta")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class TipoPlanta {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 100)
    @Column(nullable = false, unique = true)
    private String nombre;

    @Size(max = 500)
    private String descripcion;

    @NotNull
    @DecimalMin("0.0") @DecimalMax("60.0")
    @Column(name = "temp_min", nullable = false)
    private Double temperaturaMin;

    @NotNull
    @DecimalMin("0.0") @DecimalMax("60.0")
    @Column(name = "temp_max", nullable = false)
    private Double temperaturaMax;

    @NotNull
    @DecimalMin("0.0") @DecimalMax("100.0")
    @Column(name = "humedad_min", nullable = false)
    private Double humedadMin;

    @NotNull
    @DecimalMin("0.0") @DecimalMax("100.0")
    @Column(name = "humedad_max", nullable = false)
    private Double humedadMax;

    /** Duración del ciclo de cultivo en días desde siembra hasta cosecha. */
    @NotNull
    @Min(1)
    @Column(name = "ciclo_dias", nullable = false)
    private Integer cicloDias;

    @Size(max = 500)
    @Column(name = "cuidados_especiales")
    private String cuidadosEspeciales;
}
