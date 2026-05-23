# ============================================================
# GreenHouse Manager — Script de arranque del backend
# Copia este archivo como run-backend.local.ps1,
# completa tus credenciales reales y ejecuta ESE archivo.
# Este archivo es solo la plantilla (sin secretos).
# ============================================================
Write-Host "`n🌿 Iniciando GreenHouse Manager Backend..." -ForegroundColor Green

# ── Completa estos valores con tus credenciales reales ──────
$env:GOOGLE_CLIENT_ID     = "REEMPLAZA-CON-TU-CLIENT-ID"
$env:GOOGLE_CLIENT_SECRET = "REEMPLAZA-CON-TU-CLIENT-SECRET"
$env:MAIL_USERNAME        = "REEMPLAZA-CON-TU-EMAIL@gmail.com"
$env:MAIL_PASSWORD        = "REEMPLAZA-CON-TU-APP-PASSWORD"
$env:DB_URL               = "jdbc:postgresql://localhost:5432/greenhouse_db"
$env:DB_USERNAME          = "postgres"
$env:DB_PASSWORD          = "postgres"
$env:FRONTEND_URL         = "http://localhost:5173"
$env:BACKEND_URL          = "http://localhost:8080"
# ────────────────────────────────────────────────────────────

Write-Host "✅ Variables de entorno configuradas" -ForegroundColor Cyan
Write-Host "   GOOGLE_CLIENT_ID  = $($env:GOOGLE_CLIENT_ID.Substring(0, [Math]::Min(20,$env:GOOGLE_CLIENT_ID.Length)))..." -ForegroundColor Gray
Write-Host "   MAIL_USERNAME     = $env:MAIL_USERNAME" -ForegroundColor Gray
Write-Host "   DB_URL            = $env:DB_URL" -ForegroundColor Gray

Set-Location "$PSScriptRoot\greenhouse-backend"
Write-Host "`n▶  Ejecutando: mvn spring-boot:run`n" -ForegroundColor Yellow
mvn spring-boot:run
