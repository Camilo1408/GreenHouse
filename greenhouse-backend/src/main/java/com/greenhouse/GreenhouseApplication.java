/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Punto de entrada principal de la aplicación GreenHouse Manager.
 */
@SpringBootApplication
@EnableScheduling
public class GreenhouseApplication {
    public static void main(String[] args) {
        SpringApplication.run(GreenhouseApplication.class, args);
    }
}
