# Script de Comparación Docker vs Bare Metal para Windows
# Ejecutar desde PowerShell en máquina externa

param(
    [string]$BareMetalIP = "TU_DROPLET_IP_BARE_METAL",
    [string]$DockerIP = "TU_DROPLET_IP_DOCKER",
    [int]$Duration = 60,
    [int]$Connections = 100,
    [int]$Threads = 4
)

Write-Host "🚀 Iniciando comparación Docker vs Bare Metal" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "Duración: ${Duration}s | Conexiones: ${Connections} | Threads: ${Threads}" -ForegroundColor Cyan
Write-Host ""

# Función para ejecutar pruebas
function Run-Test {
    param(
        [string]$Endpoint,
        [string]$Name
    )

    Write-Host "📊 Probando ${Name} - Endpoint: ${Endpoint}" -ForegroundColor Magenta
    Write-Host "--------------------------------------------" -ForegroundColor Gray

    Write-Host "🔸 Bare Metal (${BareMetalIP}):" -ForegroundColor Red
    wrk -t${Threads} -c${Connections} -d${Duration}s "http://${BareMetalIP}:8000${Endpoint}"

    Write-Host ""
    Write-Host "🐳 Docker (${DockerIP}):" -ForegroundColor Blue
    wrk -t${Threads} -c${Connections} -d${Duration}s "http://${DockerIP}:8000${Endpoint}"

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Gray
}

# Verificar conectividad
Write-Host "🔍 Verificando conectividad..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://${BareMetalIP}:8000/health" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ Bare Metal: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Bare Metal: FAIL" -ForegroundColor Red
}

try {
    Invoke-WebRequest -Uri "http://${DockerIP}:8000/health" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ Docker: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker: FAIL" -ForegroundColor Red
}

Write-Host ""

# Ejecutar pruebas por endpoint
Run-Test "/" "Endpoint Ligero"
Run-Test "/heavy" "Endpoint Pesado"
Run-Test "/async-light" "Endpoint Async"
Run-Test "/json-large" "Endpoint JSON Grande"

Write-Host "✅ Comparación completada" -ForegroundColor Green
Write-Host "📋 Revisa los resultados arriba y documenta en PERFORMANCE_REPORT.md" -ForegroundColor Cyan