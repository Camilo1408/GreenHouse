/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
package com.greenhouse.config;

import com.greenhouse.entity.Empleado;
import com.greenhouse.repository.EmpleadoRepository;
import com.greenhouse.service.UserDetailsServiceImpl;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.*;
import org.springframework.security.authentication.*;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.client.userinfo.*;
import org.springframework.security.oauth2.core.user.*;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.*;

import java.time.LocalDate;
import java.util.List;

/**
 * Configuración de Spring Security.
 * Soporta login local (email + contraseña) y OAuth2 con Google.
 * Las rutas /api/** retornan 401 JSON en lugar de redirect al login.
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final EmpleadoRepository empleadoRepository;
    private final UserDetailsServiceImpl userDetailsService;

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("http://localhost:5173", "http://localhost:8080"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/swagger-ui/**", "/v3/api-docs/**", "/swagger-ui.html").permitAll()
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/oauth2/**", "/login/oauth2/**").permitAll()
                .anyRequest().authenticated()
            )
            // Retorna 401 JSON en lugar de redirect para clientes REST
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint((req, res, e) -> {
                    res.setContentType("application/json;charset=UTF-8");
                    res.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                    res.getWriter().write("{\"error\":\"No autenticado\",\"mensaje\":\"Inicia sesión para continuar\"}");
                })
                .accessDeniedHandler((req, res, e) -> {
                    res.setContentType("application/json;charset=UTF-8");
                    res.setStatus(HttpServletResponse.SC_FORBIDDEN);
                    res.getWriter().write("{\"error\":\"Acceso denegado\"}");
                })
            )
            // ── Login local email/contraseña ──
            .formLogin(form -> form
                .loginProcessingUrl("/api/auth/login")
                .usernameParameter("email")
                .passwordParameter("password")
                .successHandler((req, res, auth) -> {
                    res.setContentType("application/json;charset=UTF-8");
                    res.setStatus(HttpServletResponse.SC_OK);
                    String rol = auth.getAuthorities().stream().findFirst()
                            .map(a -> a.getAuthority().replace("ROLE_", "")).orElse("EMPLEADO");
                    res.getWriter().write(
                        "{\"exito\":true,\"mensaje\":\"Login exitoso\",\"email\":\"%s\",\"rol\":\"%s\"}"
                        .formatted(auth.getName(), rol)
                    );
                })
                .failureHandler((req, res, ex) -> {
                    res.setContentType("application/json;charset=UTF-8");
                    res.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                    res.getWriter().write(
                        "{\"exito\":false,\"mensaje\":\"%s\"}".formatted(ex.getMessage())
                    );
                })
                .permitAll()
            )
            // ── OAuth2 con Google ──
            .oauth2Login(oauth2 -> oauth2
                .userInfoEndpoint(userInfo -> userInfo.userService(customOAuth2UserService()))
                .successHandler((req, res, auth) ->
                    res.sendRedirect("http://localhost:5173/dashboard")
                )
                .failureHandler((req, res, ex) ->
                    res.sendRedirect("http://localhost:5173/login?error=oauth")
                )
            )
            .logout(logout -> logout
                .logoutUrl("/api/auth/logout")
                .logoutSuccessHandler((req, res, auth) -> {
                    res.setContentType("application/json;charset=UTF-8");
                    res.setStatus(HttpServletResponse.SC_OK);
                    res.getWriter().write("{\"exito\":true,\"mensaje\":\"Sesión cerrada\"}");
                })
                .invalidateHttpSession(true)
                .deleteCookies("JSESSIONID")
                .permitAll()
            )
            .userDetailsService(userDetailsService);

        return http.build();
    }

    /**
     * Registra automáticamente usuarios de Google si no existen,
     * y asigna su rol como autoridad de Spring Security.
     */
    @Bean
    public OAuth2UserService<OAuth2UserRequest, OAuth2User> customOAuth2UserService() {
        DefaultOAuth2UserService delegate = new DefaultOAuth2UserService();
        return request -> {
            OAuth2User oauthUser = delegate.loadUser(request);
            String email = oauthUser.getAttribute("email");
            String nombre = oauthUser.getAttribute("name");

            Empleado empleado = empleadoRepository.findByEmail(email).orElseGet(() ->
                empleadoRepository.save(Empleado.builder()
                    .email(email)
                    .nombreCompleto(nombre != null ? nombre : email)
                    .rol(Empleado.RolEmpleado.EMPLEADO)
                    .estado(Empleado.EstadoEmpleado.ACTIVO)
                    .emailVerificado(true)
                    .authProvider(Empleado.AuthProvider.GOOGLE)
                    .fechaIngreso(LocalDate.now())
                    .build())
            );

            String role = "ROLE_" + empleado.getRol().name();
            return new DefaultOAuth2User(
                List.of(new SimpleGrantedAuthority(role)),
                oauthUser.getAttributes(),
                "email"
            );
        };
    }
}
