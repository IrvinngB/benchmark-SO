<#
.SYNOPSIS
    Script de control para sistema automatizado de benchmarks con Docker

.DESCRIPTION
    Controla los contenedores de FastAPI, benchmark scheduler y log manager

.PARAMETER Action
    Acción a realizar: start, stop, restart, status, logs, benchmark-manual, analyze-logs

.EXAMPLE
    .\control_automatico.ps1 -Action start
    .\control_automatico.ps1 -Action benchmark-manual
    .\control_automatico.ps1 -Action logs
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "benchmark-manual", "analyze-logs", "build")]
    [string]$Action
)

$ErrorActionPreference = "Stop"
$ComposeFile = "docker-compose.automatico.yml"

function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "========================================================================`n" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

switch ($Action) {
    "start" {
        Write-Header "INICIANDO SISTEMA AUTOMATIZADO"
        Write-Info "Construyendo imágenes si es necesario..."
        docker compose -f $ComposeFile build
        
        Write-Info "Iniciando servicios..."
        docker compose -f $ComposeFile up -d
        
        Write-Success "Sistema iniciado correctamente"
        Write-Info "FastAPI disponible en: http://localhost:8000"
        Write-Info "Benchmarks programados: 9:00 AM y 9:00 PM"
        Write-Info ""
        Write-Info "Ver logs con: .\control_automatico.ps1 -Action logs"
    }
    
    "stop" {
        Write-Header "DETENIENDO SISTEMA"
        docker compose -f $ComposeFile down
        Write-Success "Sistema detenido"
    }
    
    "restart" {
        Write-Header "REINICIANDO SISTEMA"
        docker compose -f $ComposeFile restart
        Write-Success "Sistema reiniciado"
    }
    
    "status" {
        Write-Header "ESTADO DEL SISTEMA"
        docker compose -f $ComposeFile ps
        Write-Host ""
        Write-Info "Uso de recursos:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    }
    
    "logs" {
        Write-Header "LOGS DEL SISTEMA"
        Write-Info "Mostrando logs en tiempo real (Ctrl+C para salir)..."
        docker compose -f $ComposeFile logs -f
    }
    
    "benchmark-manual" {
        Write-Header "EJECUTANDO BENCHMARK MANUAL"
        Write-Info "Ejecutando benchmark fuera del horario programado..."
        
        docker compose -f $ComposeFile run --rm benchmark-scheduler python benchmark_python.py
        
        Write-Success "Benchmark completado"
        Write-Info "Resultados disponibles en: ./benchmark_results/"
        Write-Info "Logs disponibles en: ./.logs/"
    }
    
    "analyze-logs" {
        Write-Header "ANALIZANDO LOGS"
        Write-Info "Ejecutando análisis de logs..."
        
        docker compose -f $ComposeFile --profile tools run --rm log-manager
        
        Write-Success "Análisis completado"
        Write-Info "Reportes disponibles en: ./benchmark_results/"
    }
    
    "build" {
        Write-Header "CONSTRUYENDO IMAGENES"
        Write-Info "Reconstruyendo todas las imágenes..."
        docker compose -f $ComposeFile build --no-cache
        Write-Success "Imágenes construidas"
    }
}

Write-Host ""
