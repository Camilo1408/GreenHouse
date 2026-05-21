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
 * Entidad que registra un tratamiento aplicado a una planta (fertilización, poda, pesticida, etc.).
 */
@Entity
@Table(name = "tratamiento")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class Tratamiento {

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
    @Enumerated(EnumType.STRING)
    @Column(name = "tipo_tratamiento", nullable = false)
    private TipoTratamiento tipoTratamiento;

    @Size(max = 150)
    @Column(name = "producto_utilizado")
    private String productoUtilizado;

    @Size(max = 100)
    private String dosis;

    @NotNull
    @Column(name = "fecha_hora", nullable = false)
    private LocalDateTime fechaHora;

    @Size(max = 500)
    @Column(name = "resultado_observado")
    private String resultadoObservado;

    public enum TipoTratamiento {
        FERTILIZACION, PESTICIDA, PODA, RIEGO_MANUAL, REVISION
    }
}
