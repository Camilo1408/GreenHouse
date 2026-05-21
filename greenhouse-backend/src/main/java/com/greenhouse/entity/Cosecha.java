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
 * Entidad que registra la cosecha realizada sobre una planta.
 */
@Entity
@Table(name = "cosecha")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class Cosecha {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "planta_id", nullable = false)
    private Planta planta;

    @NotNull
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "empleado_id", nullable = false)
    private Empleado empleado;

    @NotNull
    @Column(name = "fecha_cosecha", nullable = false)
    private LocalDate fechaCosecha;

    @NotNull
    @DecimalMin("0.01")
    @Column(name = "peso_kg", nullable = false)
    private Double pesoKg;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private CalidadCosecha calidad;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private DestinoCosecha destino;

    @Size(max = 500)
    private String observaciones;

    public enum CalidadCosecha {
        A, B, C
    }

    public enum DestinoCosecha {
        VENTA, CONSUMO_INTERNO, DESCARTE
    }
}
