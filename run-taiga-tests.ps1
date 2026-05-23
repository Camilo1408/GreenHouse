# ===========================================================
# GreenHouse Manager — Script para ejecutar pruebas de Taiga
# ===========================================================
# Uso:
#   .\run-taiga-tests.ps1 -TaigaUser "tu-usuario" -TaigaPass "tu-contrasena" -Slug "SLUG-del-proyecto"
#
# El SLUG lo encuentras en Taiga:
#   1. Abre tu proyecto en taiga.io
#   2. Mira la URL: https://taiga.io/project/ESTE-ES-EL-SLUG/backlog
#   3. Copia todo lo que está entre /project/ y /backlog (o /timeline, etc.)

param(
    [Parameter(Mandatory=$true)]
    [string]$TaigaUser,

    [Parameter(Mandatory=$true)]
    [string]$TaigaPass,

    [Parameter(Mandatory=$false)]
    [string]$Slug = "cesar_camilo-greenhouse-manager",

    [Parameter(Mandatory=$false)]
    [string]$ApiBase = "http://localhost:8080"
)

# ── Si no se pasa slug, intentamos descubrirlo automáticamente ─────────────────
if (-not $Slug) {
    Write-Host "`n[INFO] Buscando slug del proyecto en Taiga..." -ForegroundColor Cyan

    # 1. Autenticar
    $authBody = @{ type = "normal"; username = $TaigaUser; password = $TaigaPass } | ConvertTo-Json
    $authResp  = Invoke-RestMethod -Uri "https://api.taiga.io/api/v1/auth" `
                                   -Method POST -Body $authBody `
                                   -ContentType "application/json" -ErrorAction Stop
    $token = $authResp.auth_token
    $headers = @{ Authorization = "Bearer $token" }

    # 2. Listar proyectos del usuario
    $projectsResp = Invoke-RestMethod -Uri "https://api.taiga.io/api/v1/projects?member=$($authResp.id)&order_by=user_order" `
                                      -Headers $headers -ErrorAction Stop

    # 3. Buscar el que tenga "greenhouse" en el nombre o slug
    $ghProject = $projectsResp | Where-Object { $_.slug -match "greenhouse" -or $_.name -match "greenhouse" }

    if ($ghProject) {
        $Slug = $ghProject.slug
        Write-Host "[OK] Slug encontrado automáticamente: $Slug" -ForegroundColor Green
    } else {
        Write-Host "[WARN] No se encontró un proyecto 'greenhouse' automáticamente." -ForegroundColor Yellow
        Write-Host "       Proyectos disponibles:" -ForegroundColor Yellow
        $projectsResp | ForEach-Object { Write-Host "       - $($_.slug)  ($($_.name))" }
        Write-Host "`n       Ejecuta de nuevo pasando -Slug 'el-slug-correcto'" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`n[INFO] Configurando variables de entorno..." -ForegroundColor Cyan
$env:TAIGA_URL            = "https://api.taiga.io/api/v1"
$env:TAIGA_USERNAME       = $TaigaUser
$env:TAIGA_PASSWORD       = $TaigaPass
$env:TAIGA_PROJECT_SLUG   = $Slug
$env:API_BASE_URL         = $ApiBase

Write-Host "  TAIGA_URL          = $env:TAIGA_URL"
Write-Host "  TAIGA_USERNAME     = $env:TAIGA_USERNAME"
Write-Host "  TAIGA_PROJECT_SLUG = $env:TAIGA_PROJECT_SLUG"
Write-Host "  API_BASE_URL       = $env:API_BASE_URL"

# ── Ir al directorio de tests ───────────────────────────────────────────────────
Set-Location "$PSScriptRoot\tests-python"

# ── Instalar dependencias si hace falta ────────────────────────────────────────
if (-not (Get-Command pytest -ErrorAction SilentlyContinue)) {
    Write-Host "`n[INFO] Instalando dependencias Python..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

# ── Ejecutar los tests de Taiga ────────────────────────────────────────────────
Write-Host "`n[INFO] Ejecutando pruebas de integración con Taiga..." -ForegroundColor Cyan
pytest test_taiga_integration.py -v --html=reporte-taiga.html --self-contained-html

Write-Host "`n[INFO] Reporte generado en: tests-python\reporte-taiga.html" -ForegroundColor Green
