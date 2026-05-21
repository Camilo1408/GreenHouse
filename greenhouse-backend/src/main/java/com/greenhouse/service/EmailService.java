/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;

/**
 * Servicio para el envío de correos electrónicos.
 * Usado para verificación de cuenta al registrar usuarios locales.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class EmailService {

    private final JavaMailSender mailSender;

    @Value("${spring.mail.username}")
    private String fromEmail;

    @Value("${app.base-url:http://localhost:8080}")
    private String baseUrl;

    /**
     * Envía el correo de verificación al usuario recién registrado.
     * El enlace expira en 24 horas.
     */
    public void enviarVerificacion(String destinatario, String nombreCompleto, String token) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(destinatario);
            helper.setSubject("GreenHouse Manager — Verifica tu correo electrónico");

            String enlace = baseUrl + "/api/auth/verify?token=" + token;
            String html = buildVerificationEmail(nombreCompleto, enlace);

            helper.setText(html, true);
            mailSender.send(message);
            log.info("Correo de verificación enviado a {}", destinatario);

        } catch (MessagingException e) {
            log.error("Error al enviar correo de verificación a {}: {}", destinatario, e.getMessage());
            throw new RuntimeException("No se pudo enviar el correo de verificación");
        }
    }

    private String buildVerificationEmail(String nombre, String enlace) {
        return """
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; background: #f9f9f9; border-radius: 8px;">
              <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="color: #166534;">🌿 GreenHouse Manager</h1>
              </div>
              <h2 style="color: #333;">Hola, %s</h2>
              <p style="color: #555; font-size: 16px;">
                Gracias por registrarte en GreenHouse Manager. Para activar tu cuenta y comenzar a usar el sistema,
                por favor verifica tu correo electrónico haciendo clic en el siguiente enlace:
              </p>
              <div style="text-align: center; margin: 32px 0;">
                <a href="%s"
                   style="background-color: #166534; color: white; padding: 14px 28px;
                          text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: bold;">
                  Verificar mi correo
                </a>
              </div>
              <p style="color: #888; font-size: 13px;">
                Este enlace expira en <strong>24 horas</strong>. Si no creaste una cuenta, puedes ignorar este mensaje.
              </p>
              <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">
              <p style="color: #aaa; font-size: 12px; text-align: center;">
                GreenHouse Manager &mdash; Sistema de gestión integral de invernaderos
              </p>
            </div>
            """.formatted(nombre, enlace);
    }
}
