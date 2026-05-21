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
 * Entidad que representa un sensor físico instalado en una zona del invernadero.
 */
@Entity
@Table(name = "sensor")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class Sensor {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 50)
    @Column(nullable = false, unique = true)
    private String codigo;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(name = "tipo_sensor", nullable = false)
    private TipoSensor tipoSensor;

    @NotNull
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "zona_id", nullable = false)
    private Zona zona;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private EstadoSensor estado = EstadoSensor.ACTIVO;

    @Column(name = "fecha_instalacion")
    private LocalDate fechaInstalacion;

    @Column(name = "umbral_min")
    private Double umbralMin;

    @Column(name = "umbral_max")
    private Double umbralMax;

    public enum TipoSensor {
        TEMPERATURA, HUMEDAD, PH, CO2, LUZ
    }

    public enum EstadoSensor {
        ACTIVO, INACTIVO, EN_MANTENIMIENTO
    }
}
