#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Ejecutar Benchmark Python y preparar para Git
    
.DESCRIPTION
    Script que ejecuta el benchmark Python y automáticamente
    prepara todos los resultados en resultados_muestra/ para
    subirlos a Git.
    
.PARAMETER Quick
    Modo prueba rápida (2 tests en lugar de 6)
    
.PARAMETER VerifyOnly
    Solo verificar resultados existentes sin ejecutar
    
.EXAMPLE
    .\run_benchmark_to_git.ps1
    .\run_benchmark_to_git.ps1 -Quick
    .\run_benchmark_to_git.ps1 -VerifyOnly
#>

param(
    [switch]$Quick,
    [switch]$VerifyOnly
)

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Title)
    Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ $Title" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message, [string]$Status = "")
    if ($Status -eq "success") {
        Write-Host "✅ $Message" -ForegroundColor Green
    } elseif ($Status -eq "error") {
        Write-Host "❌ $Message" -ForegroundColor Red
    } elseif ($Status -eq "info") {
        Write-Host "ℹ️ $Message" -ForegroundColor Blue
    } else {
        Write-Host "⏳ $Message" -ForegroundColor Yellow
    }
}

# Header
Write-Header "🚀 FastAPI Benchmark Python → Git"

# Modo verificación
if ($VerifyOnly) {
    Write-Step "Modo: Solo verificar resultados existentes" "info"
    
    if (Test-Path "resultados_muestra") {
        $csvCount = (Get-ChildItem "resultados_muestra" -Filter "benchmark_detailed_*.csv" -ErrorAction SilentlyContinue | Measure-Object).Count
        $jsonCount = (Get-ChildItem "resultados_muestra" -Filter "benchmark_detailed_*.json" -ErrorAction SilentlyContinue | Measure-Object).Count
        $xlsxCount = (Get-ChildItem "resultados_muestra" -Filter "benchmark_analysis_*.xlsx" -ErrorAction SilentlyContinue | Measure-Object).Count
        $mdCount = (Get-ChildItem "resultados_muestra" -Filter "benchmark_report_*.md" -ErrorAction SilentlyContinue | Measure-Object).Count
        
        Write-Step "Archivos encontrados:" "info"
        Write-Host "   📊 CSV: $csvCount archivo(s)"
        Write-Host "   📋 JSON: $jsonCount archivo(s)"
        Write-Host "   📈 XLSX: $xlsxCount archivo(s)"
        Write-Host "   📝 Reportes MD: $mdCount archivo(s)"
        
        if ($csvCount -gt 0) {
            Write-Step "Resultados listos para Git" "success"
        } else {
            Write-Step "Sin resultados de benchmark" "error"
        }
    } else {
        Write-Step "Carpeta resultados_muestra no existe" "error"
    }
    
    exit
}

# Ejecutar benchmark
Write-Header "Ejecutando Benchmark Python"

$benchmarkCmd = if ($Quick) {
    Write-Step "Modo: Prueba rápida (2 tests)" "info"
    "python benchmark_python.py --tests 2 --requests 100 --connections 25"
} else {
    Write-Step "Modo: Benchmark completo (6 tests)" "info"
    "python benchmark_python.py"
}

Write-Host "`n"
Write-Step "Ejecutando: $benchmarkCmd"

try {
    Invoke-Expression $benchmarkCmd
    Write-Step "Benchmark completado" "success"
} catch {
    Write-Step "Error durante el benchmark: $_" "error"
    exit 1
}

# Verificar resultados
Write-Header "Verificando Resultados"

if (-not (Test-Path "resultados_muestra")) {
    Write-Step "Carpeta resultados_muestra no encontrada" "error"
    exit 1
}

$csvFiles = Get-ChildItem "resultados_muestra" -Filter "benchmark_detailed_*.csv" -ErrorAction SilentlyContinue
$jsonFiles = Get-ChildItem "resultados_muestra" -Filter "benchmark_detailed_*.json" -ErrorAction SilentlyContinue
$xlsxFiles = Get-ChildItem "resultados_muestra" -Filter "benchmark_analysis_*.xlsx" -ErrorAction SilentlyContinue
$mdFiles = Get-ChildItem "resultados_muestra" -Filter "benchmark_report_*.md" -ErrorAction SilentlyContinue
$vizDirs = Get-ChildItem "resultados_muestra" -Filter "visualizations_*" -Directory -ErrorAction SilentlyContinue

Write-Step "Archivos generados:" "info"
Write-Host "   📊 CSV: $($csvFiles.Count) archivo(s)"
Write-Host "   📋 JSON: $($jsonFiles.Count) archivo(s)"
Write-Host "   📈 XLSX: $($xlsxFiles.Count) archivo(s)"
Write-Host "   📝 Reportes MD: $($mdFiles.Count) archivo(s)"
Write-Host "   🎨 Carpetas de visualizaciones: $($vizDirs.Count)"

if ($csvFiles -and $jsonFiles) {
    $latestCsv = $csvFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $sizeMB = [Math]::Round($latestCsv.Length / 1MB, 2)
    Write-Host "`n   📈 Último CSV: $($latestCsv.Name) ($sizeMB MB)"
    
    Write-Step "Todos los archivos generados correctamente" "success"
} else {
    Write-Step "Algunos archivos pueden no haberse generado" "error"
    exit 1
}

# Crear resumen
Write-Header "Preparando para Git"

$summary = @{
    timestamp = (Get-Date).ToString("o")
    benchmark_version = "Python Edition 1.0"
    status = "completed"
    output_directory = "resultados_muestra"
    git_ready = $true
}

$summary | ConvertTo-Json | Out-File "resultados_muestra\LAST_RUN_SUMMARY.json" -Encoding UTF8
Write-Step "Resumen generado: LAST_RUN_SUMMARY.json" "success"

# Comandos Git
Write-Header "Próximos Pasos - Subir a Git"

Write-Host "`n📤 Comandos para subir los resultados:`n" -ForegroundColor Cyan

$commands = @(
    @{ Step = "1. Verificar estado"; Cmd = "git status" },
    @{ Step = "2. Agregar resultados"; Cmd = "git add resultados_muestra/" },
    @{ Step = "3. Crear commit"; Cmd = 'git commit -m "Benchmarks Python: resultados del $(Get-Date -Format "dd/MM/yyyy")"' },
    @{ Step = "4. Subir a remote"; Cmd = "git push origin main" }
)

foreach ($cmd in $commands) {
    Write-Host "$($cmd.Step)" -ForegroundColor Yellow
    Write-Host "  `$ $($cmd.Cmd)" -ForegroundColor White
    Write-Host ""
}

Write-Host "💡 O combina en un solo comando:" -ForegroundColor Cyan
Write-Host '  $ git add resultados_muestra/ && git commit -m "Benchmark results" && git push' -ForegroundColor White

Write-Host "`n"
Write-Step "✨ Los resultados están listos para Git!" "success"
Write-Host "   Todos los archivos están en: resultados_muestra/" -ForegroundColor Cyan
Write-Host ""