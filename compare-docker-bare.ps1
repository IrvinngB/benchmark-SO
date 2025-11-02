# Script de Comparación Docker vs Bare Metal
# Ejecutar desde tu máquina local hacia los droplets

param(
    [string]$BareMetalIP,
    [string]$DockerIP,
    [int]$Runs = 3,
    [int]$Duration = 10
)

if (-not $BareMetalIP -or -not $DockerIP) {
    Write-Host "Uso: .\compare-docker-bare.ps1 -BareMetalIP 'IP_DEL_DROPLET_BARE' -DockerIP 'IP_DEL_DROPLET_DOCKER'" -ForegroundColor Red
    exit 1
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ResultFile = "comparacion_docker_bare_${Timestamp}.txt"

Write-Host "🚀 Comparación Docker vs Bare Metal" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""
Write-Host "Bare Metal IP: $BareMetalIP" -ForegroundColor Yellow
Write-Host "Docker IP: $DockerIP" -ForegroundColor Yellow
Write-Host "Runs: $Runs" -ForegroundColor Yellow
Write-Host "Duration per test: ${Duration}s" -ForegroundColor Yellow
Write-Host ""

# Crear archivo de resultados
"COMPARACIÓN DOCKER VS BARE METAL" | Out-File -FilePath $ResultFile
"Fecha: $(Get-Date)" | Out-File -FilePath $ResultFile -Append
"Bare Metal IP: $BareMetalIP" | Out-File -FilePath $ResultFile -Append
"Docker IP: $DockerIP" | Out-File -FilePath $ResultFile -Append
"Runs: $Runs" | Out-File -FilePath $ResultFile -Append
"Duration: ${Duration}s" | Out-File -FilePath $ResultFile -Append
"".PadRight(50, "=") | Out-File -FilePath $ResultFile -Append
"" | Out-File -FilePath $ResultFile -Append

# Función para ejecutar test
function Run-Test {
    param(
        [string]$Name,
        [string]$IP,
        [string]$Endpoint,
        [int]$Connections = 100
    )

    Write-Host "Testing $Name - $Endpoint..." -ForegroundColor Cyan

    if (Test-Path ".\bombardier.exe") {
        $output = & .\bombardier.exe -c $Connections -n ($Connections * 10) "http://${IP}${Endpoint}" 2>&1
        $output | Out-File -FilePath $ResultFile -Append
    } else {
        Write-Host "  bombardier.exe no encontrado. Instálalo desde https://github.com/codesenberg/bombardier/releases" -ForegroundColor Red
        return
    }

    "" | Out-File -FilePath $ResultFile -Append
}

# Test de conectividad
Write-Host "Verificando conectividad..." -ForegroundColor Yellow

try {
    Invoke-WebRequest -Uri "http://$BareMetalIP/health" -TimeoutSec 5 | Out-Null
    Write-Host "✅ Bare Metal droplet responding" -ForegroundColor Green
} catch {
    Write-Host "❌ Bare Metal droplet not responding" -ForegroundColor Red
    exit 1
}

try {
    Invoke-WebRequest -Uri "http://$DockerIP/health" -TimeoutSec 5 | Out-Null
    Write-Host "✅ Docker droplet responding" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker droplet not responding" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Ejecutando benchmarks..." -ForegroundColor Green
Write-Host ""

# Ejecutar múltiples runs
for ($run = 1; $run -le $Runs; $run++) {
    Write-Host "=== RUN $run de $Runs ===" -ForegroundColor Magenta

    "=== RUN $run de $Runs ===" | Out-File -FilePath $ResultFile -Append
    "Fecha: $(Get-Date)" | Out-File -FilePath $ResultFile -Append
    "" | Out-File -FilePath $ResultFile -Append

    # Baseline
    "BARE METAL - Baseline (/)" | Out-File -FilePath $ResultFile -Append
    Run-Test -Name "Bare Metal Baseline" -IP $BareMetalIP -Endpoint "/"

    "DOCKER - Baseline (/)" | Out-File -FilePath $ResultFile -Append
    Run-Test -Name "Docker Baseline" -IP $DockerIP -Endpoint "/"

    # Heavy endpoint
    "BARE METAL - Heavy (/heavy)" | Out-File -FilePath $ResultFile -Append
    Run-Test -Name "Bare Metal Heavy" -IP $BareMetalIP -Endpoint "/heavy" -Connections 50

    "DOCKER - Heavy (/heavy)" | Out-File -FilePath $ResultFile -Append
    Run-Test -Name "Docker Heavy" -IP $DockerIP -Endpoint "/heavy" -Connections 50

    # JSON Large (con menos conexiones por ser problemático)
    "BARE METAL - JSON Large (/json-large)" | Out-File -FilePath $ResultFile -Append
    Run-Test -Name "Bare Metal JSON Large" -IP $BareMetalIP -Endpoint "/json-large" -Connections 20

    "DOCKER - JSON Large (/json-large)" | Out-File -FilePath $ResultFile -Append
    Run-Test -Name "Docker JSON Large" -IP $DockerIP -Endpoint "/json-large" -Connections 20

    "=== FIN RUN $run ===" | Out-File -FilePath $ResultFile -Append
    "".PadRight(30, "-") | Out-File -FilePath $ResultFile -Append
    "" | Out-File -FilePath $ResultFile -Append

    if ($run -lt $Runs) {
        Write-Host "Esperando 5 segundos antes del siguiente run..." -ForegroundColor Gray
        Start-Sleep -Seconds 5
    }
}

Write-Host ""
Write-Host "✅ Comparación completada!" -ForegroundColor Green
Write-Host "Resultados guardados en: $ResultFile" -ForegroundColor Yellow
Write-Host ""

# Resumen rápido
Write-Host "Resumen rápido de Requests/sec:" -ForegroundColor Green
$content = Get-Content $ResultFile
$rpsLines = $content | Select-String "Reqs/sec" | Select-Object -Last 12  # Últimos 12 resultados
if ($rpsLines) {
    $rpsLines | ForEach-Object {
        Write-Host "  $_" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "  - Revisa el archivo $ResultFile para análisis detallado" -ForegroundColor White
Write-Host "  - Compara especialmente los valores de Req/sec y Latencia" -ForegroundColor White
Write-Host "  - El overhead de Docker suele ser 5-15% en VPS" -ForegroundColor White