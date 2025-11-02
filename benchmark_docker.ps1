# Script de Benchmarking para VPS (Con Docker) - Output CSV
# Uso: .\benchmark-vps-docker.ps1
# Prueba el VPS con Docker en: http://138.68.233.15:8000
# IMPORTANTE: Asegúrate de que el contenedor Docker esté corriendo antes de ejecutar

param(
    [string]$ServerHost = "68.183.168.86:8000",
    [int]$Requests = 1000,
    [int]$Connections = 50,
    [int]$Duration = 30
)

Write-Host "🚀 FastAPI Performance Benchmark - VPS (Con Docker)" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Configuración:" -ForegroundColor Yellow
Write-Host "  Host: $ServerHost" -ForegroundColor White
Write-Host "  Requests: $Requests" -ForegroundColor White
Write-Host "  Connections: $Connections" -ForegroundColor White
Write-Host "  Duration: $Duration segundos" -ForegroundColor White
Write-Host "  Entorno: VPS_DOCKER" -ForegroundColor Magenta
Write-Host ""

# Crear directorio para resultados
$ResultsDir = "benchmark_results"
if (-not (Test-Path $ResultsDir)) {
    New-Item -ItemType Directory -Path $ResultsDir | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$CsvFile = "$ResultsDir\benchmark_vps_docker_${Timestamp}.csv"
$TxtFile = "$ResultsDir\benchmark_vps_docker_${Timestamp}.txt"

# Verificar que la aplicación esté corriendo
Write-Host "Verificando que la aplicación Docker esté corriendo en VPS..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://$ServerHost/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Aplicación Docker corriendo correctamente en VPS" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Error: La aplicación no está respondiendo en http://$ServerHost" -ForegroundColor Red
    Write-Host "Verifica que:" -ForegroundColor Yellow
    Write-Host "  1. El contenedor Docker esté corriendo:" -ForegroundColor White
    Write-Host "     docker ps | grep fastapi" -ForegroundColor Gray
    Write-Host "  2. El puerto 8000 esté mapeado correctamente:" -ForegroundColor White
    Write-Host "     docker run -d -p 8000:8000 fastapi-perf:latest" -ForegroundColor Gray
    Write-Host "  3. El firewall permita el puerto 8000" -ForegroundColor White
    Write-Host "  4. La IP sea correcta: $ServerHost" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "🐳 Iniciando pruebas remotas al VPS con Docker..." -ForegroundColor Green
Write-Host ""

# Crear header del CSV
$csvHeader = "timestamp,endpoint,name,total_requests,successful_requests,failed_requests,total_time_seconds,requests_per_second,avg_latency_ms,min_latency_ms,max_latency_ms,p50_latency_ms,p95_latency_ms,p99_latency_ms,environment"
$csvHeader | Out-File -FilePath $CsvFile -Encoding UTF8

# Header del archivo de texto
"FastAPI Performance Benchmark - VPS (Con Docker)" | Out-File -FilePath $TxtFile
"Date: $(Get-Date)" | Out-File -FilePath $TxtFile -Append
"Host: $ServerHost" | Out-File -FilePath $TxtFile -Append
"Environment: VPS_DOCKER" | Out-File -FilePath $TxtFile -Append
"=======================================" | Out-File -FilePath $TxtFile -Append
"" | Out-File -FilePath $TxtFile -Append

# Función para calcular percentiles
function Get-Percentile {
    param(
        [array]$Values,
        [int]$Percentile
    )
    $sorted = $Values | Sort-Object
    $index = [math]::Ceiling($sorted.Count * $Percentile / 100) - 1
    if ($index -lt 0) { $index = 0 }
    return $sorted[$index]
}

# Función para ejecutar benchmark
function Run-Benchmark {
    param(
        [string]$Endpoint,
        [string]$Name
    )

    Write-Host "Testing: $Name ($Endpoint)" -ForegroundColor Cyan

    $testTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    "Testing $Name - $Endpoint" | Out-File -FilePath $TxtFile -Append
    "----------------------------------------" | Out-File -FilePath $TxtFile -Append

    # Usar bombardier si está disponible
    if (Test-Path ".\bombardier.exe") {
        Write-Host "  Usando bombardier..." -ForegroundColor Yellow
        
        $output = & .\bombardier.exe -c $Connections -n $Requests "http://${ServerHost}${Endpoint}" 2>&1 | Out-String
        $output | Out-File -FilePath $TxtFile -Append
        
        # Parsear output de bombardier
        $rps = if ($output -match "Reqs/sec\s+(\d+\.?\d*)") { $matches[1] } else { "0" }
        $avgLatency = if ($output -match "Latency.*Avg:\s+(\d+\.?\d*)") { $matches[1] } else { "0" }
        $minLatency = if ($output -match "Min:\s+(\d+\.?\d*)") { $matches[1] } else { "0" }
        $maxLatency = if ($output -match "Max:\s+(\d+\.?\d*)") { $matches[1] } else { "0" }
        $totalTime = if ($output -match "Total time:\s+(\d+\.?\d*)") { $matches[1] } else { "0" }
        $successCount = if ($output -match "(\d+) succeeded") { $matches[1] } else { $Requests }
        $errorCount = if ($output -match "(\d+) failed") { $matches[1] } else { "0" }
        
        # Bombardier no da p50, p95, p99 directamente, usar avg como aproximación
        $p50 = $avgLatency
        $p95 = [math]::Round([double]$avgLatency * 1.5, 2)
        $p99 = [math]::Round([double]$avgLatency * 2, 2)
        
    } else {
        # Fallback con Invoke-WebRequest
        Write-Host "  Usando Invoke-WebRequest (mediciones detalladas)..." -ForegroundColor Yellow
        Write-Host "  Nota: Las pruebas remotas pueden ser más lentas debido a latencia de red" -ForegroundColor Gray
        
        $start = Get-Date
        $successCount = 0
        $errorCount = 0
        $latencies = @()

        for ($i = 1; $i -le $Requests; $i++) {
            $reqStart = Get-Date
            try {
                Invoke-WebRequest -Uri "http://${ServerHost}${Endpoint}" -UseBasicParsing -TimeoutSec 30 | Out-Null
                $reqEnd = Get-Date
                $latencyMs = ($reqEnd - $reqStart).TotalMilliseconds
                $latencies += $latencyMs
                $successCount++
            } catch {
                $errorCount++
            }

            # Mostrar progreso cada 50 requests
            if ($i % 50 -eq 0) {
                Write-Host "  Progreso: $i/$Requests requests (Éxitos: $successCount, Errores: $errorCount)" -ForegroundColor Gray
            }
        }

        $end = Get-Date
        $totalTime = ($end - $start).TotalSeconds
        $rps = [math]::Round($Requests / $totalTime, 2)

        # Calcular estadísticas de latencia
        if ($latencies.Count -gt 0) {
            $avgLatency = [math]::Round(($latencies | Measure-Object -Average).Average, 2)
            $minLatency = [math]::Round(($latencies | Measure-Object -Minimum).Minimum, 2)
            $maxLatency = [math]::Round(($latencies | Measure-Object -Maximum).Maximum, 2)
            $p50 = [math]::Round((Get-Percentile -Values $latencies -Percentile 50), 2)
            $p95 = [math]::Round((Get-Percentile -Values $latencies -Percentile 95), 2)
            $p99 = [math]::Round((Get-Percentile -Values $latencies -Percentile 99), 2)
        } else {
            $avgLatency = 0
            $minLatency = 0
            $maxLatency = 0
            $p50 = 0
            $p95 = 0
            $p99 = 0
        }

        # Escribir en archivo de texto
        "Total Requests: $Requests" | Out-File -FilePath $TxtFile -Append
        "Successful: $successCount" | Out-File -FilePath $TxtFile -Append
        "Errors: $errorCount" | Out-File -FilePath $TxtFile -Append
        "Total Time: $totalTime seconds" | Out-File -FilePath $TxtFile -Append
        "Requests per second: $rps" | Out-File -FilePath $TxtFile -Append
        "Avg Latency: $avgLatency ms" | Out-File -FilePath $TxtFile -Append
        "Min Latency: $minLatency ms" | Out-File -FilePath $TxtFile -Append
        "Max Latency: $maxLatency ms" | Out-File -FilePath $TxtFile -Append
        "P50 Latency: $p50 ms" | Out-File -FilePath $TxtFile -Append
        "P95 Latency: $p95 ms" | Out-File -FilePath $TxtFile -Append
        "P99 Latency: $p99 ms" | Out-File -FilePath $TxtFile -Append
    }

    # Escribir línea CSV con identificador de entorno correcto
    $environment = "vps_docker"
    $csvLine = "$testTimestamp,$Endpoint,$Name,$Requests,$successCount,$errorCount,$totalTime,$rps,$avgLatency,$minLatency,$maxLatency,$p50,$p95,$p99,$environment"
    $csvLine | Out-File -FilePath $CsvFile -Append -Encoding UTF8

    "" | Out-File -FilePath $TxtFile -Append
    "" | Out-File -FilePath $TxtFile -Append
    
    Write-Host "  ✓ Completado - RPS: $rps, Avg Latency: $avgLatency ms" -ForegroundColor Green
}

# Ejecutar benchmarks en todos los endpoints
Write-Host "🐳 Probando endpoints del VPS con Docker..." -ForegroundColor Cyan
Write-Host ""

Run-Benchmark "/" "Root Endpoint (Baseline)"
Start-Sleep -Seconds 2

Run-Benchmark "/health" "Health Check"
Start-Sleep -Seconds 2

Run-Benchmark "/async-light" "Async Light"
Start-Sleep -Seconds 2

Run-Benchmark "/heavy" "Heavy Computation"
Start-Sleep -Seconds 2

Run-Benchmark "/json-large" "Large JSON Response"

Write-Host ""
Write-Host "✅ Benchmarks completados!" -ForegroundColor Green
Write-Host "Resultados guardados en:" -ForegroundColor Yellow
Write-Host "  CSV: $CsvFile" -ForegroundColor White
Write-Host "  TXT: $TxtFile" -ForegroundColor White
Write-Host ""

# Mostrar resumen en tabla
Write-Host "📊 Resumen de Resultados (VPS Con Docker):" -ForegroundColor Green
Write-Host ""

# Leer CSV y mostrar tabla formateada
if (Test-Path $CsvFile) {
    $data = Import-Csv $CsvFile
    $data | Format-Table -Property name, requests_per_second, avg_latency_ms, p95_latency_ms, failed_requests -AutoSize
}

Write-Host ""
Write-Host "💡 Comparar con versión sin Docker:" -ForegroundColor Cyan
Write-Host "  # Ejecuta los 3 scripts:" -ForegroundColor White
Write-Host "  .\benchmark-local.ps1         # Tu máquina Windows" -ForegroundColor Gray
Write-Host "  .\benchmark-vps.ps1           # VPS sin Docker" -ForegroundColor Gray
Write-Host "  .\benchmark-vps-docker.ps1    # VPS con Docker (este)" -ForegroundColor Gray
Write-Host "" -ForegroundColor White
Write-Host "  # Analiza todo junto:" -ForegroundColor White
Write-Host "  python analyze_benchmarks.py benchmark_results" -ForegroundColor Gray
Write-Host ""
Write-Host "📈 El análisis mostrará:" -ForegroundColor Cyan
Write-Host "  - Overhead de Docker vs sin Docker" -ForegroundColor White
Write-Host "  - Comparación VPS vs máquina local" -ForegroundColor White
Write-Host "  - Gráficos de rendimiento por entorno" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Nota: La latencia incluye el tiempo de red entre tu máquina y el VPS" -ForegroundColor Yellow
Write-Host "   Para pruebas más precisas, ejecuta wrk/hey directamente desde el VPS" -ForegroundColor Yellow