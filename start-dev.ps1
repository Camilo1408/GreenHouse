# ============================================================
#  GreenHouse Manager — Arranque del entorno de desarrollo
#  Uso: .\start-dev.ps1
#  Requiere: .env en la raíz del proyecto (copia de .env.example)
# ============================================================

$ROOT = $PSScriptRoot

# ── Colores ──────────────────────────────────────────────────
function Info  ($msg) { Write-Host "  $msg" -ForegroundColor Cyan }
function Ok    ($msg) { Write-Host "  ✅ $msg" -ForegroundColor Green }
function Warn  ($msg) { Write-Host "  ⚠️  $msg" -ForegroundColor Yellow }
function Err   ($msg) { Write-Host "  ❌ $msg" -ForegroundColor Red }
function Title ($msg) { Write-Host "`n$msg" -ForegroundColor Magenta }

Clear-Host
Write-Host ""
Write-Host "  🌿  GreenHouse Manager — Dev Environment" -ForegroundColor Green
Write-Host "  ──────────────────────────────────────────" -ForegroundColor DarkGreen
Write-Host ""

# ── 1. Verificar que existe el archivo .env ──────────────────
$envFile = Join-Path $ROOT ".env"
if (-not (Test-Path $envFile)) {
    Err  "No se encontró el archivo .env"
    Warn "Crea el archivo copiando el ejemplo:"
    Write-Host ""
    Write-Host "    Copy-Item .env.example .env" -ForegroundColor White
    Write-Host "    notepad .env   (completa tus credenciales)" -ForegroundColor White
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

# ── 2. Leer y exportar variables del .env ────────────────────
Title "📄 Cargando variables desde .env..."
$envVars = @{}
Get-Content $envFile | Where-Object { $_ -match "^\s*[^#]\S+=.+" } | ForEach-Object {
    $parts = $_ -split "=", 2
    $key   = $parts[0].Trim()
    $val   = $parts[1].Trim()
    [System.Environment]::SetEnvironmentVariable($key, $val, "Process")
    $envVars[$key] = $val
    if ($key -like "*PASSWORD*" -or $key -like "*SECRET*") {
        Info "$key = ****"
    } else {
        Info "$key = $val"
    }
}
Ok "Variables cargadas"

# ── 3. Verificar herramientas necesarias ─────────────────────
Title "🔍 Verificando herramientas..."

$mvnOk  = $null -ne (Get-Command mvn  -ErrorAction SilentlyContinue)
$nodeOk = $null -ne (Get-Command node -ErrorAction SilentlyContinue)
$npmOk  = $null -ne (Get-Command npm  -ErrorAction SilentlyContinue)

if ($mvnOk)  { Ok  "Maven encontrado:  $(mvn -version 2>&1 | Select-Object -First 1)" }
else         { Err "Maven no encontrado. Instala JDK 17 + Maven: https://maven.apache.org/download.cgi" }

if ($nodeOk) { Ok  "Node.js encontrado: $(node -v)" }
else         { Err "Node.js no encontrado. Instala Node.js 20: https://nodejs.org" }

if (-not $mvnOk -or -not $nodeOk) {
    Write-Host ""
    Read-Host "Faltan herramientas. Presiona Enter para salir"
    exit 1
}

# ── 4. Instalar dependencias npm si faltan ───────────────────
$nmPath = Join-Path $ROOT "greenhouse-frontend\node_modules"
if (-not (Test-Path $nmPath)) {
    Title "📦 Instalando dependencias npm (primera vez)..."
    Set-Location (Join-Path $ROOT "greenhouse-frontend")
    npm install --silent
    if ($LASTEXITCODE -ne 0) { Err "npm install falló"; Read-Host "Enter para salir"; exit 1 }
    Ok "Dependencias npm instaladas"
    Set-Location $ROOT
}

# ── 5. Arrancar Backend en nueva ventana ─────────────────────
Title "🚀 Arrancando Backend (Spring Boot)..."

$backendScript = @"
`$Host.UI.RawUI.WindowTitle = 'GreenHouse BACKEND :8080'
`$env:GOOGLE_CLIENT_ID     = '$($envVars['GOOGLE_CLIENT_ID'])'
`$env:GOOGLE_CLIENT_SECRET = '$($envVars['GOOGLE_CLIENT_SECRET'])'
`$env:MAIL_USERNAME        = '$($envVars['MAIL_USERNAME'])'
`$env:MAIL_PASSWORD        = '$($envVars['MAIL_PASSWORD'])'
`$env:DB_URL               = '$($envVars['DB_URL'])'
`$env:DB_USERNAME          = '$($envVars['DB_USERNAME'])'
`$env:DB_PASSWORD          = '$($envVars['DB_PASSWORD'])'
`$env:FRONTEND_URL         = '$($envVars['FRONTEND_URL'])'
`$env:BACKEND_URL          = '$($envVars['BACKEND_URL'])'
Write-Host '🌿 GreenHouse Backend — Spring Boot' -ForegroundColor Green
Write-Host '   Iniciando en http://localhost:8080' -ForegroundColor Cyan
Write-Host '   Swagger UI: http://localhost:8080/swagger-ui.html' -ForegroundColor Cyan
Write-Host ''
Set-Location '$ROOT\greenhouse-backend'
mvn spring-boot:run
"@

$backendScript | Out-File -FilePath "$env:TEMP\gh-backend.ps1" -Encoding UTF8
Start-Process powershell -ArgumentList "-NoExit", "-File", "$env:TEMP\gh-backend.ps1"
Ok "Ventana de Backend abierta"

# ── 6. Esperar que el backend esté listo ─────────────────────
Title "⏳ Esperando que el backend inicie..."
$maxWait = 60
$started = $false
for ($i = 1; $i -le $maxWait; $i++) {
    Start-Sleep -Seconds 2
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8080/api/zonas" `
                                -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -in @(200, 401)) { $started = $true; break }
    } catch { }
    Write-Host "   [$i/$maxWait] Esperando backend..." -ForegroundColor DarkGray
}

if ($started) { Ok "Backend listo en http://localhost:8080" }
else          { Warn "Backend tardando más de lo normal — continúa de todas formas" }

# ── 7. Arrancar Frontend en nueva ventana ───────────────────
Title "🚀 Arrancando Frontend (Vite)..."

$frontendScript = @"
`$Host.UI.RawUI.WindowTitle = 'GreenHouse FRONTEND :5173'
Write-Host '🌿 GreenHouse Frontend — React + Vite' -ForegroundColor Green
Write-Host '   Iniciando en http://localhost:5173' -ForegroundColor Cyan
Write-Host ''
Set-Location '$ROOT\greenhouse-frontend'
npm run dev
"@

$frontendScript | Out-File -FilePath "$env:TEMP\gh-frontend.ps1" -Encoding UTF8
Start-Process powershell -ArgumentList "-NoExit", "-File", "$env:TEMP\gh-frontend.ps1"
Ok "Ventana de Frontend abierta"

# ── 8. Abrir navegador ───────────────────────────────────────
Start-Sleep -Seconds 5
Title "🌐 Abriendo el sistema en el navegador..."
Start-Process "http://localhost:5173"

# ── 9. Resumen ───────────────────────────────────────────────
Write-Host ""
Write-Host "  ═══════════════════════════════════════════" -ForegroundColor Green
Write-Host "  🌿  GreenHouse Manager — Sistema iniciado" -ForegroundColor Green
Write-Host "  ═══════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "  🖥️  Frontend  →  http://localhost:5173" -ForegroundColor Cyan
Write-Host "  🔧  Backend   →  http://localhost:8080" -ForegroundColor Cyan
Write-Host "  📚  Swagger   →  http://localhost:8080/swagger-ui.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Credenciales de prueba:" -ForegroundColor Yellow
Write-Host "    Admin      → admin@greenhouse.com     / Admin1234" -ForegroundColor White
Write-Host "    Supervisor → supervisor@greenhouse.com / Super1234" -ForegroundColor White
Write-Host "    Empleado   → empleado@greenhouse.com   / Empleado1234" -ForegroundColor White
Write-Host ""
Write-Host "  Para detener: cierra las ventanas de Backend y Frontend" -ForegroundColor DarkGray
Write-Host ""
Read-Host "Presiona Enter para cerrar esta ventana"
