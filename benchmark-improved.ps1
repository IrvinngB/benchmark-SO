#!/usr/bin/env pwsh
<#
.SYNOPSIS
    FastAPI Performance Benchmark - 10 Runs per Environment
    Ejecuta 10 pruebas completas para cada entorno (Docker y Sin Docker)
    
.DESCRIPTION
    Script mejorado que automatiza 10 pruebas consecutivas por entorno.
    Resultados guardados en benchmark_results_improved/
    
.PARAMETER Requests
    Número de requests por prueba (default: 1000)
    
.PARAMETER Connections
    Conexiones concurrentes (default: 50)
    
.EXAMPLE
    .\benchmark-improved.ps1
#>

param(
    [int]$Requests = 1000,
    [int]$Connections = 50
)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

$NUM_TESTS = 6
$RESULTS_DIR = "benchmark_results_improved"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"

# Configuración de servidores por entorno (NO usar $Host - es variable automática de PowerShell)
$SERVERS = @{
    "local" = "localhost:8000"
    "vps_no_docker" = "138.68.233.15:8000"
    "vps_docker" = "68.183.168.86:8000"
}

$ENDPOINTS = @(
    @{ Name = "Root Endpoint (Baseline)"; Path = "/" },
    @{ Name = "Health Check"; Path = "/health" },
    @{ Name = "Async Light"; Path = "/async-light" },
    @{ Name = "Heavy Computation"; Path = "/heavy" },
    @{ Name = "Large JSON Response"; Path = "/json-large?page=1&limit=50" }
)

$ENVIRONMENTS = @(
    @{ Name = "vps_no_docker"; Label = "VPS Sin Docker"; Color = "Green"; IP = "138.68.233.15" },
    @{ Name = "vps_docker"; Label = "VPS Con Docker"; Color = "Blue"; IP = "68.183.168.86" }
)

# ============================================================================
# FUNCIONES
# ============================================================================

function Initialize-Directories {
    Write-Host "📁 Inicializando directorios..." -ForegroundColor Cyan
    
    if (-not (Test-Path $RESULTS_DIR)) {
        New-Item -ItemType Directory -Path $RESULTS_DIR | Out-Null
        Write-Host "   ✅ Directorio creado: $RESULTS_DIR"
    }
    
    # Crear subdirectorios por entorno
    foreach ($env in $ENVIRONMENTS) {
        $envDir = "$RESULTS_DIR\$($env.Name.ToLower())"
        if (-not (Test-Path $envDir)) {
            New-Item -ItemType Directory -Path $envDir | Out-Null
            Write-Host "   ✅ Directorio creado: $envDir"
        }
    }
}

function Test-Connectivity {
    param([string]$EnvironmentName)
    
    Write-Host "`n🔍 Verificando conectividad..." -ForegroundColor Cyan
    
    $serverAddr = $SERVERS[$EnvironmentName]
    
    try {
        $response = Invoke-WebRequest -Uri "http://$serverAddr/health" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ Servidor accesible: http://$serverAddr" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "   ❌ No se puede conectar a http://$serverAddr" -ForegroundColor Red
        Write-Host "   Error: $_" -ForegroundColor Red
        return $false
    }
}

function Invoke-Benchmark {
    param(
        [int]$TestNumber,
        [string]$Endpoint,
        [string]$EndpointName,
        [string]$EnvironmentName,
        [string]$ServerHost
    )
    
    $url = "http://$ServerHost$Endpoint"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    Write-Host "   Ejecutando... ($url)" -ForegroundColor Gray -NoNewline
    
    try {
        # Ejecutar bombardier
        $output = bombardier -n $Requests -c $Connections -l "$url" 2>&1 | Out-String
        
        Write-Host " ✅" -ForegroundColor Green
        
        # Extraer estadísticas
        $stats = ConvertFrom-BombardierOutput $output
        $stats["environment"] = $EnvironmentName
        $stats["name"] = $EndpointName
        $stats["timestamp"] = $timestamp
        $stats["test_number"] = $TestNumber
        $stats["url"] = $url
        
        return $stats
    }
    catch {
        Write-Host " ❌" -ForegroundColor Red
        Write-Host "      Error: $_" -ForegroundColor Red
        return $null
    }
}

function ConvertFrom-BombardierOutput {
    param([string]$Output)
    
    $stats = @{
        "requests_per_second" = 0
        "avg_latency_ms" = 0
        "p50_latency_ms" = 0
        "p95_latency_ms" = 0
        "p99_latency_ms" = 0
        "max_latency_ms" = 0
        "total_requests" = 0
        "successful_requests" = 0
        "failed_requests" = 0
    }
    
    # Extraer Reqs/sec
    if ($Output -match "Reqs/sec\s+(\d+\.?\d*)") {
        $stats["requests_per_second"] = [double]$matches[1]
    }
    
    # Extraer Latency promedio
    if ($Output -match "Latency\s+(\d+\.?\d*)ms") {
        $stats["avg_latency_ms"] = [double]$matches[1]
    }
    
    # Extraer Max latency
    if ($Output -match "Max\s+(\d+\.?\d*)") {
        $stats["max_latency_ms"] = [double]$matches[1]
    }
    
    # Extraer códigos HTTP
    if ($Output -match "2xx - (\d+)") {
        $stats["successful_requests"] = [int]$matches[1]
    }
    if ($Output -match "5xx - (\d+)") {
        $stats["failed_requests"] = [int]$matches[1]
    }
    
    # Total requests
    $stats["total_requests"] = $Requests
    
    return $stats
}

function Save-Results {
    param(
        [array]$AllResults,
        [string]$Format
    )
    
    if ($Format -eq "CSV") {
        foreach ($env in $ENVIRONMENTS) {
            $envResults = $AllResults | Where-Object { $_.environment -eq $env.Name }
            $envDir = "$RESULTS_DIR\$($env.Name.ToLower())"
            
            if ($envResults) {
                $csvPath = "$envDir\benchmark_$($TIMESTAMP).csv"
                
                # Crear CSV con cabeceras
                $header = "timestamp,test_number,name,environment,url,requests_per_second,avg_latency_ms,max_latency_ms,total_requests,successful_requests,failed_requests"
                $header | Out-File -FilePath $csvPath -Encoding UTF8
                
                foreach ($result in $envResults) {
                    $line = "$($result.timestamp),$($result.test_number),$($result.name),$($result.environment),$($result.url),$($result.requests_per_second),$($result.avg_latency_ms),$($result.max_latency_ms),$($result.total_requests),$($result.successful_requests),$($result.failed_requests)"
                    Add-Content -Path $csvPath -Value $line
                }
                
                Write-Host "   ✅ CSV guardado: $(Split-Path -Leaf $csvPath)"
            }
        }
    }
    elseif ($Format -eq "JSON") {
        $jsonPath = "$RESULTS_DIR\benchmark_$($TIMESTAMP).json"
        $AllResults | ConvertTo-Json | Out-File -FilePath $jsonPath -Encoding UTF8
        Write-Host "   ✅ JSON guardado: $(Split-Path -Leaf $jsonPath)"
    }
    elseif ($Format -eq "TXT") {
        $txtPath = "$RESULTS_DIR\benchmark_$($TIMESTAMP).txt"
        $AllResults | Format-Table -AutoSize | Out-File -FilePath $txtPath -Encoding UTF8
        Write-Host "   ✅ TXT guardado: $(Split-Path -Leaf $txtPath)"
    }
}

function Write-Summary {
    param([array]$AllResults)
    
    Write-Host "`n" -ForegroundColor Cyan
    Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                         RESUMEN DE PRUEBAS (6 Runs)                            ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    foreach ($env in $ENVIRONMENTS) {
        Write-Host "`n🌍 $($env.Label)" -ForegroundColor $env.Color
        Write-Host "─" * 80
        
        $envResults = $AllResults | Where-Object { $_.environment -eq $env.Name }
        
        Write-Host ("{0,-30} {1,15} {2,15} {3,15}" -f "Endpoint", "RPS Avg", "RPS Min", "RPS Max")
        Write-Host "─" * 80
        
        foreach ($endpoint in $ENDPOINTS) {
            $endpointResults = $envResults | Where-Object { $_.name -eq $endpoint.Name }
            
            if ($endpointResults) {
                $avgRPS = ($endpointResults.requests_per_second | Measure-Object -Average).Average
                $minRPS = ($endpointResults.requests_per_second | Measure-Object -Minimum).Minimum
                $maxRPS = ($endpointResults.requests_per_second | Measure-Object -Maximum).Maximum
                
                Write-Host ("{0,-30} {1,15:F2} {2,15:F2} {3,15:F2}" -f $endpoint.Name, $avgRPS, $minRPS, $maxRPS)
            }
        }
    }
    
    Write-Host "`n"
}

# ============================================================================
# MAIN
# ============================================================================

function Main {
    Clear-Host
    
    Write-Host @"
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║           🚀 FastAPI Performance Benchmark - 10 Runs per Environment         ║
║                                                                                ║
║  VPS Sin Docker:  138.68.233.15:8000                                          ║
║  VPS Con Docker:  68.183.168.86:8000                                          ║
║                                                                                ║
║  Ejecución: $NUM_TESTS pruebas por entorno                                    ║
║  Total:     $($NUM_TESTS * 5 * 2) pruebas (6 runs × 5 endpoints × 2 env)   ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan
    
    # Inicializar
    Initialize-Directories
    
    # Array para almacenar todos los resultados
    $allResults = @()
    
    # Ejecutar pruebas por entorno
    $totalTests = $NUM_TESTS * @($ENDPOINTS).Count * @($ENVIRONMENTS).Count
    $currentTest = 0
    
    foreach ($env in $ENVIRONMENTS) {
        $serverAddr = $SERVERS[$env.Name]
        
        # Verificar conectividad
        Write-Host "`n"
        Write-Host "════════════════════════════════════════════════════════════════════════════════" -ForegroundColor $env.Color
        Write-Host "  🔍 AMBIENTE: $($env.Label)" -ForegroundColor $env.Color
        Write-Host "  📍 IP: $serverAddr" -ForegroundColor $env.Color
        Write-Host "════════════════════════════════════════════════════════════════════════════════" -ForegroundColor $env.Color
        
        if (-not (Test-Connectivity -EnvironmentName $env.Name)) {
            Write-Host "`n❌ No se puede conectar a $serverAddr. Saltando este entorno." -ForegroundColor Red
            continue
        }
        
        # Ejecutar $NUM_TESTS pruebas
        for ($run = 1; $run -le $NUM_TESTS; $run++) {
            Write-Host "`n📍 EJECUCIÓN $run/$NUM_TESTS" -ForegroundColor Yellow
            
            foreach ($endpoint in $ENDPOINTS) {
                $currentTest++
                $progress = [Math]::Round(($currentTest / $totalTests) * 100, 1)
                
                Write-Host "   ⏳ [$progress%] $($endpoint.Name)" -ForegroundColor Gray
                
                $result = Invoke-Benchmark `
                    -TestNumber $run `
                    -Endpoint $endpoint.Path `
                    -EndpointName $endpoint.Name `
                    -EnvironmentName $env.Name `
                    -ServerHost $serverAddr
                
                if ($result) {
                    $allResults += $result
                }
            }
        }
    }
    
    # Guardar resultados
    Write-Host "`n" -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  💾 GUARDANDO RESULTADOS" -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    
    Save-Results -AllResults $allResults -Format "CSV"
    Save-Results -AllResults $allResults -Format "TXT"
    Save-Results -AllResults $allResults -Format "JSON"
    
    # Mostrar resumen
    Write-Summary -AllResults $allResults
    
    Write-Host "✅ Benchmark completado exitosamente" -ForegroundColor Green
    Write-Host "📁 Resultados guardados en: $RESULTS_DIR\" -ForegroundColor Green
    Write-Host "`n📝 Próximo paso: python analyze_benchmarks_improved.py benchmark_results_improved" -ForegroundColor Cyan
}

# Ejecutar
Main
