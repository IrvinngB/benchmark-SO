# Script de Benchmarking Simple para Windows
# Uso: .\benchmark-local.ps1

param(
    [string]$ServerHost = "localhost:8000",
    [int]$Requests = 1000,
    [int]$Connections = 50,
    [int]$Duration = 30
)

Write-Host "🚀 FastAPI Performance Benchmark - Local" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Configuración:" -ForegroundColor Yellow
Write-Host "  Host: $ServerHost" -ForegroundColor White
Write-Host "  Requests: $Requests" -ForegroundColor White
Write-Host "  Connections: $Connections" -ForegroundColor White
Write-Host "  Duration: $Duration segundos" -ForegroundColor White
Write-Host ""

# Crear directorio para resultados
$ResultsDir = "benchmark_results"
if (-not (Test-Path $ResultsDir)) {
    New-Item -ItemType Directory -Path $ResultsDir | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ResultFile = "$ResultsDir\benchmark_local_${Timestamp}.txt"

# Verificar que la aplicación esté corriendo
Write-Host "Verificando que la aplicación esté corriendo..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://$ServerHost/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Aplicación corriendo correctamente" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Error: La aplicación no está respondiendo en http://$ServerHost" -ForegroundColor Red
    Write-Host "Asegúrate de que uvicorn esté ejecutándose: uvicorn app.main:app --reload" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Ejecutando benchmarks..." -ForegroundColor Green
Write-Host ""

# Header del archivo de resultados
"FastAPI Performance Benchmark - Local" | Out-File -FilePath $ResultFile
"Date: $(Get-Date)" | Out-File -FilePath $ResultFile -Append
"Host: $ServerHost" | Out-File -FilePath $ResultFile -Append
"=======================================" | Out-File -FilePath $ResultFile -Append
"" | Out-File -FilePath $ResultFile -Append

# Función para ejecutar benchmark con bombardier
function Run-Benchmark {
    param(
        [string]$Endpoint,
        [string]$Name
    )

    Write-Host "Testing: $Name ($Endpoint)" -ForegroundColor Cyan

    "Testing $Name - $Endpoint" | Out-File -FilePath $ResultFile -Append
    "----------------------------------------" | Out-File -FilePath $ResultFile -Append

    # Usar bombardier si está disponible
    if (Test-Path ".\bombardier.exe") {
        $output = & .\bombardier.exe -c $Connections -n $Requests "http://${ServerHost}${Endpoint}" 2>&1
        $output | Out-File -FilePath $ResultFile -Append
    } else {
        # Fallback con Invoke-WebRequest (más lento pero funciona)
        Write-Host "  Usando Invoke-WebRequest (más lento)..." -ForegroundColor Yellow
        $start = Get-Date
        $successCount = 0
        $errorCount = 0

        for ($i = 1; $i -le $Requests; $i++) {
            try {
                Invoke-WebRequest -Uri "http://${ServerHost}${Endpoint}" -UseBasicParsing -TimeoutSec 10 | Out-Null
                $successCount++
            } catch {
                $errorCount++
            }

            # Mostrar progreso cada 100 requests
            if ($i % 100 -eq 0) {
                Write-Host "  Progreso: $i/$Requests requests" -ForegroundColor Gray
            }
        }

        $end = Get-Date
        $elapsed = ($end - $start).TotalSeconds
        $rps = [math]::Round($Requests / $elapsed, 2)

        "Total Requests: $Requests" | Out-File -FilePath $ResultFile -Append
        "Successful: $successCount" | Out-File -FilePath $ResultFile -Append
        "Errors: $errorCount" | Out-File -FilePath $ResultFile -Append
        "Total Time: $elapsed seconds" | Out-File -FilePath $ResultFile -Append
        "Requests per second: $rps" | Out-File -FilePath $ResultFile -Append
    }

    "" | Out-File -FilePath $ResultFile -Append
    "" | Out-File -FilePath $ResultFile -Append
}

# Ejecutar benchmarks en todos los endpoints
Run-Benchmark "/" "Root Endpoint (Baseline)"
Start-Sleep -Seconds 1

Run-Benchmark "/health" "Health Check"
Start-Sleep -Seconds 1

Run-Benchmark "/async-light" "Async Light"
Start-Sleep -Seconds 1

Run-Benchmark "/heavy" "Heavy Computation"
Start-Sleep -Seconds 1

Run-Benchmark "/json-large" "Large JSON Response"

Write-Host ""
Write-Host "✅ Benchmarks completados!" -ForegroundColor Green
Write-Host "Resultados guardados en: $ResultFile" -ForegroundColor Yellow
Write-Host ""

# Mostrar resumen rápido
Write-Host "Resumen rápido:" -ForegroundColor Green
if (Test-Path $ResultFile) {
    $content = Get-Content $ResultFile
    $rpsLines = $content | Select-String "reqs/sec|Requests per second"
    if ($rpsLines) {
        $rpsLines | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
    }
}

Write-Host ""
Write-Host "💡 Tips para mejores resultados:" -ForegroundColor Cyan
Write-Host "  - Asegúrate de que no haya otras aplicaciones consumiendo CPU/RAM" -ForegroundColor White
Write-Host "  - Ejecuta múltiples veces para obtener promedios consistentes" -ForegroundColor White
Write-Host "  - Compara resultados con diferentes números de workers en uvicorn" -ForegroundColor White
Write-Host "  - Para pruebas más avanzadas, instala wrk o hey en WSL/Linux" -ForegroundColor White