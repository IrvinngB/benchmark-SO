#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Instalar Bombardier - Herramienta de Benchmarking HTTP
    
.DESCRIPTION
    Descarga e instala bombardier en Windows
    
.EXAMPLE
    .\install-bombardier.ps1
#>

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                                ║" -ForegroundColor Cyan
Write-Host "║              📦 Instalador de Bombardier para Windows                        ║" -ForegroundColor Cyan
Write-Host "║                                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Verificar si bombardier ya está instalado
Write-Host "`n🔍 Verificando si bombardier ya está instalado..." -ForegroundColor Yellow

try {
    $version = bombardier --version 2>&1
    Write-Host "✅ ¡Bombardier ya está instalado!" -ForegroundColor Green
    Write-Host "   Versión: $version" -ForegroundColor Green
    exit 0
}
catch {
    Write-Host "⚠️  Bombardier no está instalado. Procederemos con la instalación." -ForegroundColor Yellow
}

# Opción 1: Usar Chocolatey
Write-Host "`n📋 Opción 1: Intentar instalar con Chocolatey..." -ForegroundColor Cyan

try {
    $chocoVersion = choco --version 2>&1
    Write-Host "✅ Chocolatey detectado: $chocoVersion" -ForegroundColor Green
    
    Write-Host "`n⏳ Instalando bombardier con choco..." -ForegroundColor Yellow
    choco install bombardier -y
    
    Write-Host "`n✅ ¡Instalación completada!" -ForegroundColor Green
    bombardier --version
    exit 0
}
catch {
    Write-Host "❌ Chocolatey no está disponible o la instalación falló." -ForegroundColor Red
}

# Opción 2: Descarga manual desde GitHub
Write-Host "`n📋 Opción 2: Descargar desde GitHub..." -ForegroundColor Cyan

$downloadUrl = "https://github.com/codesenberg/bombardier/releases/download/v1.2.5/bombardier-windows-amd64.exe"
$installPath = "$env:ProgramFiles\Bombardier"
$exePath = "$installPath\bombardier.exe"

# Crear directorio si no existe
if (-not (Test-Path $installPath)) {
    New-Item -ItemType Directory -Path $installPath | Out-Null
    Write-Host "📁 Directorio creado: $installPath" -ForegroundColor Green
}

Write-Host "`n⏳ Descargando bombardier..." -ForegroundColor Yellow
Write-Host "   Desde: $downloadUrl" -ForegroundColor Gray

try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath -ErrorAction Stop
    Write-Host "✅ Descarga completada" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error descargando desde GitHub: $_" -ForegroundColor Red
    Write-Host "`n💡 Alternativas:" -ForegroundColor Yellow
    Write-Host "   1. Instalar Chocolatey: https://chocolatey.org/install" -ForegroundColor Gray
    Write-Host "   2. Descargar manualmente: https://github.com/codesenberg/bombardier/releases" -ForegroundColor Gray
    exit 1
}

# Agregar a PATH
Write-Host "`n⏳ Agregando bombardier al PATH..." -ForegroundColor Yellow

$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if (-not $currentPath.Contains($installPath)) {
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$installPath", "User")
    Write-Host "✅ PATH actualizado" -ForegroundColor Green
}

# Refrescar variables de entorno
$env:PATH = "$env:PATH;$installPath"

# Verificar instalación
Write-Host "`n🔍 Verificando instalación..." -ForegroundColor Yellow

Start-Sleep -Seconds 2

try {
    $version = & $exePath --version
    Write-Host "✅ ¡Bombardier instalado correctamente!" -ForegroundColor Green
    Write-Host "   Versión: $version" -ForegroundColor Green
    Write-Host "   Ubicación: $exePath" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Verificación fallida. Intenta abrir una nueva terminal PowerShell." -ForegroundColor Yellow
}

Write-Host "`n" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Instalación completada. Puedes ejecutar benchmarks ahora." -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "`n📝 Próximo paso: .\benchmark-improved.ps1" -ForegroundColor Cyan
Write-Host ""
