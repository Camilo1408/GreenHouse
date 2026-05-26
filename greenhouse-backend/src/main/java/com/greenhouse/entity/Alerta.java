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
 * Entidad que representa una alerta generada cuando una lectura de sensor supera los umbrales configurados.
 */
@Entity
@Table(name = "alerta")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class Alerta {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 200)
    @Column(nullable = false)
    private String tipo;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Severidad severidad;

    @NotNull
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "zona_id", nullable = false)
    private Zona zona;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "sensor_id")
    private Sensor sensor;

    @NotNull
    @Column(name = "fecha_generacion", nullable = false)
    private LocalDateTime fechaGeneracion;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private EstadoAlerta estado = EstadoAlerta.PENDIENTE;

    @Size(max = 500)
    private String descripcion;

    /** Notas de resolución agregadas por el empleado que atendió la alerta. */
    @Size(max = 1000)
    @Column(name = "notas_resolucion")
    private String notasResolucion;

    /** Empleado que atendió o resolvió la alerta. */
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "atendido_por_id")
    private Empleado atendidoPor;

    public enum Severidad {
        BAJA, MEDIA, ALTA, CRITICA
    }

    public enum EstadoAlerta {
        PENDIENTE, ATENDIDA, DESCARTADA
    }
}
