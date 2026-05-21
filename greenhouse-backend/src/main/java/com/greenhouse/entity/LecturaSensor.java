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
import java.time.LocalDateTime;

/**
 * Entidad que registra cada lectura tomada por un sensor del invernadero.
 * Al persistirse, el servicio evalúa si el valor está fuera de umbral para generar alertas.
 */
@Entity
@Table(name = "lectura_sensor")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class LecturaSensor {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "sensor_id", nullable = false)
    private Sensor sensor;

    @NotNull
    @Column(nullable = false)
    private Double valor;

    @NotBlank
    @Size(max = 20)
    @Column(nullable = false)
    private String unidad;

    @NotNull
    @Column(name = "fecha_hora", nullable = false)
    private LocalDateTime fechaHora;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private FuenteLectura fuente;

    public enum FuenteLectura {
        AUTOMATICA, MANUAL
    }
}
