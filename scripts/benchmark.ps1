# Script de benchmarking para Windows PowerShell
# Uso: .\benchmark.ps1 -Mode "docker" -Host "localhost:8000"

param(
    [string]$Mode = "bare",  # docker o bare
    [string]$Host = "localhost:8000",
    [int]$Duration = 30,
    [int]$Connections = 100,
    [int]$Requests = 10000
)

Write-Host "================================" -ForegroundColor Green
Write-Host "FastAPI Performance Benchmark" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Mode: $Mode" -ForegroundColor Yellow
Write-Host "Host: $Host" -ForegroundColor Yellow
Write-Host "Requests: $Requests" -ForegroundColor Yellow
Write-Host "Connections: $Connections" -ForegroundColor Yellow
Write-Host ""

# Crear directorio para resultados
$ResultsDir = "benchmark_results"
if (-not (Test-Path $ResultsDir)) {
    New-Item -ItemType Directory -Path $ResultsDir | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ResultFile = "$ResultsDir\benchmark_${Mode}_${Timestamp}.txt"

# Verificar que el servidor esté corriendo
Write-Host "Checking if server is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://$Host/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Server is running" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Server is not responding" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting benchmarks..." -ForegroundColor Green
Write-Host ""

# Header del archivo de resultados
"FastAPI Performance Benchmark Results" | Out-File -FilePath $ResultFile
"Mode: $Mode" | Out-File -FilePath $ResultFile -Append
"Date: $(Get-Date)" | Out-File -FilePath $ResultFile -Append
"Host: $Host" | Out-File -FilePath $ResultFile -Append
"=======================================" | Out-File -FilePath $ResultFile -Append
"" | Out-File -FilePath $ResultFile -Append

# Función para ejecutar benchmark (requiere bombardier o similar)
function Run-Benchmark {
    param(
        [string]$Endpoint,
        [string]$Name
    )
    
    Write-Host "Testing endpoint: $Endpoint" -ForegroundColor Yellow
    "Testing $Name - $Endpoint" | Out-File -FilePath $ResultFile -Append
    "----------------------------------------" | Out-File -FilePath $ResultFile -Append
    
    # Nota: En Windows, puedes instalar bombardier desde https://github.com/codesenberg/bombardier
    # O usar hey desde https://github.com/rakyll/hey
    
    if (Get-Command bombardier -ErrorAction SilentlyContinue) {
        bombardier -c $Connections -n $Requests "http://${Host}${Endpoint}" | Out-File -FilePath $ResultFile -Append
    } elseif (Get-Command hey -ErrorAction SilentlyContinue) {
        hey -n $Requests -c $Connections "http://${Host}${Endpoint}" | Out-File -FilePath $ResultFile -Append
    } else {
        Write-Host "Neither bombardier nor hey found. Please install one of them." -ForegroundColor Red
        Write-Host "bombardier: https://github.com/codesenberg/bombardier/releases" -ForegroundColor Yellow
        Write-Host "hey: https://github.com/rakyll/hey/releases" -ForegroundColor Yellow
        
        # Fallback: simple test con Invoke-WebRequest
        Write-Host "Using simple Invoke-WebRequest test (not accurate for benchmarking)" -ForegroundColor Yellow
        $start = Get-Date
        1..$Requests | ForEach-Object {
            try {
                Invoke-WebRequest -Uri "http://${Host}${Endpoint}" -UseBasicParsing -TimeoutSec 5 | Out-Null
            } catch {
                Write-Host "Request failed: $_" -ForegroundColor Red
            }
        }
        $end = Get-Date
        $elapsed = ($end - $start).TotalSeconds
        "Total time: $elapsed seconds" | Out-File -FilePath $ResultFile -Append
        "Requests per second: $($Requests / $elapsed)" | Out-File -FilePath $ResultFile -Append
    }
    
    "" | Out-File -FilePath $ResultFile -Append
    "" | Out-File -FilePath $ResultFile -Append
}

# Ejecutar benchmarks
Run-Benchmark -Endpoint "/" -Name "Root Endpoint (Baseline)"
Start-Sleep -Seconds 2

Run-Benchmark -Endpoint "/health" -Name "Health Check"
Start-Sleep -Seconds 2

Run-Benchmark -Endpoint "/async-light" -Name "Async Light"
Start-Sleep -Seconds 2

Run-Benchmark -Endpoint "/heavy" -Name "Heavy Computation"
Start-Sleep -Seconds 2

Run-Benchmark -Endpoint "/json-large" -Name "Large JSON Response"

Write-Host ""
Write-Host "✓ Benchmarks completed!" -ForegroundColor Green
Write-Host "Results saved to: $ResultFile" -ForegroundColor Yellow
Write-Host ""
