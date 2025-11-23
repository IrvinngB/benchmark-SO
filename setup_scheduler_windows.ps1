# ============================================================================
# Script de Configuración de Tareas Programadas - Windows
# ============================================================================
# Este script configura Windows Task Scheduler para ejecutar benchmarks
# automáticamente a las 11:00 AM y 11:00 PM todos los días.
#
# REQUISITOS:
# - Ejecutar PowerShell como Administrador
# - Python 3.8+ instalado y en el PATH
# - Todas las dependencias instaladas (requirements.txt)
#
# USO:
#   .\setup_scheduler_windows.ps1
#   .\setup_scheduler_windows.ps1 -PythonPath "C:\Python39\python.exe"
#   .\setup_scheduler_windows.ps1 -Uninstall
# ============================================================================

param(
    [string]$PythonPath = "python",
    [string]$WorkingDirectory = $PSScriptRoot,
    [switch]$Uninstall = $false
)

# Configuración
$TaskNameAM = "BenchmarkServers_11AM"
$TaskNamePM = "BenchmarkServers_11PM"
$ScriptPath = Join-Path $WorkingDirectory "scheduled_benchmark.py"
$ConfigPath = Join-Path $WorkingDirectory "benchmark_config_servers.json"
$LogDir = Join-Path $WorkingDirectory ".logs_scheduled"

# Verificar que el script existe
if (-not (Test-Path $ScriptPath)) {
    Write-Host "❌ Error: No se encontró el script scheduled_benchmark.py" -ForegroundColor Red
    Write-Host "   Ruta esperada: $ScriptPath" -ForegroundColor Yellow
    exit 1
}

# Verificar que existe la configuración
if (-not (Test-Path $ConfigPath)) {
    Write-Host "❌ Error: No se encontró el archivo de configuración" -ForegroundColor Red
    Write-Host "   Ruta esperada: $ConfigPath" -ForegroundColor Yellow
    exit 1
}

# Función para eliminar tareas
function Remove-BenchmarkTasks {
    Write-Host "`n🗑️  Eliminando tareas programadas..." -ForegroundColor Cyan
    
    try {
        Unregister-ScheduledTask -TaskName $TaskNameAM -Confirm:$false -ErrorAction SilentlyContinue
        Write-Host "✅ Tarea eliminada: $TaskNameAM" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Tarea no encontrada: $TaskNameAM" -ForegroundColor Yellow
    }
    
    try {
        Unregister-ScheduledTask -TaskName $TaskNamePM -Confirm:$false -ErrorAction SilentlyContinue
        Write-Host "✅ Tarea eliminada: $TaskNamePM" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Tarea no encontrada: $TaskNamePM" -ForegroundColor Yellow
    }
    
    Write-Host "`n✅ Proceso de desinstalación completado" -ForegroundColor Green
}

# Si se solicita desinstalación
if ($Uninstall) {
    Remove-BenchmarkTasks
    exit 0
}

# Verificar Python
Write-Host "`n🔍 Verificando instalación de Python..." -ForegroundColor Cyan
try {
    $pythonVersion = & $PythonPath --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: No se pudo ejecutar Python" -ForegroundColor Red
    Write-Host "   Intenta especificar la ruta completa con -PythonPath" -ForegroundColor Yellow
    exit 1
}

# Crear directorio de logs si no existe
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    Write-Host "✅ Directorio de logs creado: $LogDir" -ForegroundColor Green
}

Write-Host "`n📅 Configurando tareas programadas..." -ForegroundColor Cyan
Write-Host "   Directorio de trabajo: $WorkingDirectory" -ForegroundColor Gray
Write-Host "   Script: $ScriptPath" -ForegroundColor Gray
Write-Host "   Python: $PythonPath" -ForegroundColor Gray

# ============================================================================
# TAREA 1: 11:00 AM
# ============================================================================

Write-Host "`n⏰ Configurando tarea para 11:00 AM..." -ForegroundColor Yellow

# Eliminar tarea existente si existe
Unregister-ScheduledTask -TaskName $TaskNameAM -Confirm:$false -ErrorAction SilentlyContinue

# Crear acción
$actionAM = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ScriptPath`" --config `"$ConfigPath`"" `
    -WorkingDirectory $WorkingDirectory

# Crear trigger para 11:00 AM diario
$triggerAM = New-ScheduledTaskTrigger -Daily -At "11:00AM"

# Configuración de la tarea
$settingsAM = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Crear principal (usuario actual)
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

# Registrar tarea
Register-ScheduledTask `
    -TaskName $TaskNameAM `
    -Action $actionAM `
    -Trigger $triggerAM `
    -Settings $settingsAM `
    -Principal $principal `
    -Description "Ejecuta benchmark automático de servidores a las 11:00 AM" | Out-Null

Write-Host "✅ Tarea creada: $TaskNameAM" -ForegroundColor Green

# ============================================================================
# TAREA 2: 11:00 PM
# ============================================================================

Write-Host "`n⏰ Configurando tarea para 11:00 PM..." -ForegroundColor Yellow

# Eliminar tarea existente si existe
Unregister-ScheduledTask -TaskName $TaskNamePM -Confirm:$false -ErrorAction SilentlyContinue

# Crear acción
$actionPM = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ScriptPath`" --config `"$ConfigPath`"" `
    -WorkingDirectory $WorkingDirectory

# Crear trigger para 11:00 PM diario
$triggerPM = New-ScheduledTaskTrigger -Daily -At "11:00PM"

# Configuración de la tarea
$settingsPM = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Registrar tarea
Register-ScheduledTask `
    -TaskName $TaskNamePM `
    -Action $actionPM `
    -Trigger $triggerPM `
    -Settings $settingsPM `
    -Principal $principal `
    -Description "Ejecuta benchmark automático de servidores a las 11:00 PM" | Out-Null

Write-Host "✅ Tarea creada: $TaskNamePM" -ForegroundColor Green

# ============================================================================
# RESUMEN
# ============================================================================

Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Cyan

Write-Host "`n📋 Tareas programadas creadas:" -ForegroundColor White
Write-Host "   1. $TaskNameAM - Ejecuta diariamente a las 11:00 AM" -ForegroundColor Gray
Write-Host "   2. $TaskNamePM - Ejecuta diariamente a las 11:00 PM" -ForegroundColor Gray

Write-Host "`n🎯 Servidores a monitorear:" -ForegroundColor White
Write-Host "   • 143.110.201.94" -ForegroundColor Gray
Write-Host "   • 104.248.217.252" -ForegroundColor Gray
Write-Host "   • 206.189.215.59" -ForegroundColor Gray

Write-Host "`n📝 Logs y resultados:" -ForegroundColor White
Write-Host "   • Logs: $LogDir" -ForegroundColor Gray
Write-Host "   • Resultados: $WorkingDirectory\resultados_automaticos" -ForegroundColor Gray

Write-Host "`n🔧 Comandos útiles:" -ForegroundColor White
Write-Host "   Ver tareas:      Get-ScheduledTask | Where-Object {`$_.TaskName -like 'BenchmarkServers*'}" -ForegroundColor Gray
Write-Host "   Ejecutar ahora:  Start-ScheduledTask -TaskName '$TaskNameAM'" -ForegroundColor Gray
Write-Host "   Desinstalar:     .\setup_scheduler_windows.ps1 -Uninstall" -ForegroundColor Gray

Write-Host "`n💡 Próxima ejecución:" -ForegroundColor White
$nextRunAM = (Get-ScheduledTask -TaskName $TaskNameAM).Triggers[0].StartBoundary
$nextRunPM = (Get-ScheduledTask -TaskName $TaskNamePM).Triggers[0].StartBoundary
Write-Host "   11:00 AM - $nextRunAM" -ForegroundColor Gray
Write-Host "   11:00 PM - $nextRunPM" -ForegroundColor Gray

Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host ""
