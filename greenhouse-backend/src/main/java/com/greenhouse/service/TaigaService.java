/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.*;

/**
 * Servicio proxy para la API de Taiga.
 * Autentica con Taiga usando las credenciales configuradas y obtiene las
 * historias de usuario del proyecto GreenHouse Manager.
 * El token de autenticación se cachea en memoria durante 23 horas.
 */
@Service
public class TaigaService {

    private static final Logger log = LoggerFactory.getLogger(TaigaService.class);

    @Value("${taiga.url:https://api.taiga.io/api/v1}")
    private String taigaUrl;

    @Value("${taiga.username:}")
    private String username;

    @Value("${taiga.password:}")
    private String password;

    @Value("${taiga.project-slug:cesar_camilo-greenhouse-manager}")
    private String projectSlug;

    private final RestTemplate restTemplate = new RestTemplate();

    /** Token cacheado en memoria (se renueva cada 23h). */
    private String cachedToken = null;
    private long   tokenExpiry = 0L;

    // ── Autenticación ──────────────────────────────────────────────────────────

    /**
     * Obtiene o renueva el token de autenticación de Taiga.
     * El token se cachea en memoria hasta 23 horas.
     *
     * @return token de autenticación Bearer
     * @throws IllegalStateException si las credenciales no están configuradas
     * @throws RestClientException   si la API de Taiga no es accesible
     */
    public String getToken() {
        if (cachedToken != null && System.currentTimeMillis() < tokenExpiry) {
            return cachedToken;
        }

        if (username == null || username.isBlank() || password == null || password.isBlank()) {
            throw new IllegalStateException("Credenciales de Taiga no configuradas (TAIGA_USERNAME / TAIGA_PASSWORD)");
        }

        Map<String, String> body = new HashMap<>();
        body.put("type",     "normal");
        body.put("username", username);
        body.put("password", password);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> request = new HttpEntity<>(body, headers);

        ResponseEntity<Map<String, Object>> resp = restTemplate.exchange(
                taigaUrl + "/auth",
                HttpMethod.POST,
                request,
                new ParameterizedTypeReference<>() {}
        );

        if (resp.getStatusCode() != HttpStatus.OK || resp.getBody() == null) {
            throw new RestClientException("Taiga devolvió respuesta inesperada: " + resp.getStatusCode());
        }

        cachedToken = (String) resp.getBody().get("auth_token");
        tokenExpiry = System.currentTimeMillis() + 23L * 60 * 60 * 1000;
        log.info("Token de Taiga renovado (expira en 23h)");
        return cachedToken;
    }

    /**
     * Construye los headers HTTP con el token Bearer de Taiga.
     *
     * @return HttpEntity con Authorization y Content-Type
     */
    private HttpEntity<Void> authHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + getToken());
        headers.setContentType(MediaType.APPLICATION_JSON);
        return new HttpEntity<>(headers);
    }

    // ── Historias de usuario ────────────────────────────────────────────────────

    /**
     * Retorna el ID del proyecto GreenHouse Manager en Taiga.
     *
     * @return ID del proyecto
     * @throws RestClientException si el proyecto no se encuentra
     */
    @SuppressWarnings("unchecked")
    public Integer getProjectId() {
        ResponseEntity<Map<String, Object>> resp = restTemplate.exchange(
                taigaUrl + "/projects/by_slug?slug=" + projectSlug,
                HttpMethod.GET,
                authHeaders(),
                new ParameterizedTypeReference<>() {}
        );
        if (resp.getBody() == null) {
            throw new RestClientException("Proyecto '" + projectSlug + "' no encontrado en Taiga");
        }
        return (Integer) resp.getBody().get("id");
    }

    /**
     * Retorna todas las historias de usuario del proyecto, enriquecidas con
     * el nombre del sprint y campos esenciales para la UI.
     *
     * @return lista de mapas con los campos: id, ref, subject, status, statusColor,
     *         isClosed, sprint, points, tags
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getHistorias() {
        Integer projectId = getProjectId();

        ResponseEntity<List<Map<String, Object>>> resp = restTemplate.exchange(
                taigaUrl + "/userstories?project=" + projectId + "&order_by=sprint_order",
                HttpMethod.GET,
                authHeaders(),
                new ParameterizedTypeReference<>() {}
        );

        List<Map<String, Object>> raw = resp.getBody() != null ? resp.getBody() : List.of();

        List<Map<String, Object>> result = new ArrayList<>();
        for (Map<String, Object> story : raw) {
            Map<String, Object> dto = new LinkedHashMap<>();
            dto.put("id",  story.get("id"));
            dto.put("ref", story.get("ref"));
            dto.put("subject", story.get("subject"));

            // Estado
            Map<String, Object> statusInfo = (Map<String, Object>) story.get("status_extra_info");
            dto.put("status",      statusInfo != null ? statusInfo.get("name")     : "Unknown");
            dto.put("statusColor", statusInfo != null ? statusInfo.get("color")    : "#999999");
            dto.put("isClosed",    statusInfo != null && Boolean.TRUE.equals(statusInfo.get("is_closed")));

            // Sprint / Milestone
            Map<String, Object> milestone = (Map<String, Object>) story.get("milestone_extra_info");
            dto.put("sprint", milestone != null ? milestone.get("name") : null);

            // Puntos
            dto.put("points", story.get("total_points"));

            // Etiquetas: [[nombre, color], ...] → [nombre, ...]
            List<Object> rawTags = (List<Object>) story.get("tags");
            List<String> tags = new ArrayList<>();
            if (rawTags != null) {
                for (Object tag : rawTags) {
                    if (tag instanceof List<?> tagPair && !((List<?>) tag).isEmpty()) {
                        tags.add(String.valueOf(((List<?>) tagPair).get(0)));
                    }
                }
            }
            dto.put("tags", tags);

            result.add(dto);
        }

        return result;
    }
}
