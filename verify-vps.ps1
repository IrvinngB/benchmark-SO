#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Verificación rápida de connectividad con ambos VPS
    
.DESCRIPTION
    Testa health check en ambos servidores FastAPI
    
.EXAMPLE
    .\verify-vps.ps1
#>

$ENVIRONMENTS = @(
    @{ 
        Name = "VPS_NO_DOCKER"
        IP = "138.68.233.15"
        Port = "8000"
        Label = "SIN DOCKER"
        Color = "Green"
    },
    @{ 
        Name = "VPS_DOCKER"
        IP = "68.183.168.86"
        Port = "8000"
        Label = "CON DOCKER"
        Color = "Blue"
    }
)

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                 Verificación de Conectividad - VPS FastAPI                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$allHealthy = $true

foreach ($env in $ENVIRONMENTS) {
    $url = "http://$($env.IP):$($env.Port)/health"
    $displayUrl = "$($env.IP):$($env.Port)"
    
    Write-Host "`n" -ForegroundColor $env.Color
    Write-Host "────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $env.Color
    Write-Host "  🌍 $($env.Label)" -ForegroundColor $env.Color
    Write-Host "  📍 $displayUrl" -ForegroundColor $env.Color
    Write-Host "────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $env.Color
    
    Write-Host "  ⏳ Conectando..." -NoNewline -ForegroundColor Gray
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -ErrorAction Stop
        
        Write-Host " ✅" -ForegroundColor Green
        Write-Host "  Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "  Tiempo de respuesta: $($response.RawContentLength) bytes" -ForegroundColor Green
        
        # Parsear respuesta JSON si existe
        try {
            $content = $response.Content | ConvertFrom-Json
            Write-Host "  Respuesta: $($content | ConvertTo-Json -Compress)" -ForegroundColor Green
        }
        catch {
            Write-Host "  Respuesta: $($response.Content)" -ForegroundColor Green
        }
    }
    catch {
        Write-Host " ❌" -ForegroundColor Red
        $allHealthy = $false
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  " -ForegroundColor Red
        Write-Host "  💡 Soluciones:" -ForegroundColor Yellow
        Write-Host "     1. Verificar que el VPS está en línea" -ForegroundColor Yellow
        Write-Host "     2. Verificar firewall permite puerto 8000" -ForegroundColor Yellow
        Write-Host "     3. Verificar que FastAPI está corriendo" -ForegroundColor Yellow
        Write-Host "        ssh user@$($env.IP)" -ForegroundColor Yellow
        Write-Host "        ps aux | grep uvicorn" -ForegroundColor Yellow
    }
}

Write-Host "`n" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($allHealthy) {
    Write-Host "✅ Ambos VPS están operacionales y listos para benchmarking" -ForegroundColor Green
    Write-Host "`n📝 Próximo paso: Ejecutar .\benchmark-improved.ps1" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "❌ Uno o más VPS no están disponibles" -ForegroundColor Red
    Write-Host "`n🔧 Por favor, verifica la conectividad antes de ejecutar benchmarks" -ForegroundColor Red
    exit 1
}
