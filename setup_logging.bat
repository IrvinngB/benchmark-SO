@echo off
REM ========================================================================
REM Script de Configuración Automática - FastAPI Performance Benchmark
REM ========================================================================
REM Este script configura el entorno para ejecutar benchmarks diarios
REM durante 4 semanas con logging completo.

echo ===================================================================
echo 🛠️  CONFIGURACION AUTOMATICA - FASTAPI PERFORMANCE BENCHMARK
echo ===================================================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "benchmark_python.py" (
    echo ❌ Error: No se encuentra benchmark_python.py
    echo    Ejecuta este script desde el directorio del proyecto
    pause
    exit /b 1
)

echo ✅ Directorio del proyecto detectado
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en PATH
    echo    Instala Python 3.10+ y agregalo al PATH
    pause
    exit /b 1
)

echo ✅ Python detectado:
python --version
echo.

REM Crear directorio de logs si no existe
if not exist ".logs" (
    mkdir ".logs"
    mkdir ".logs\daily"
    mkdir ".logs\errors"
    mkdir ".logs\performance" 
    mkdir ".logs\archive"
    echo ✅ Estructura de directorios .logs creada
) else (
    echo ✅ Directorio .logs ya existe
)
echo.

REM Crear directorio de resultados diarios
if not exist "resultados_diarios" (
    mkdir "resultados_diarios"
    echo ✅ Directorio resultados_diarios creado
) else (
    echo ✅ Directorio resultados_diarios ya existe
)
echo.

REM Instalar dependencias si no están instaladas
echo 📦 Verificando dependencias de Python...
python -c "import aiohttp, pandas, matplotlib, seaborn, rich, psutil" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando dependencias...
    pip install aiohttp pandas matplotlib seaborn rich psutil numpy asyncio openpyxl
    if errorlevel 1 (
        echo ❌ Error instalando dependencias
        pause
        exit /b 1
    )
    echo ✅ Dependencias instaladas
) else (
    echo ✅ Dependencias ya instaladas
)
echo.

REM Crear configuración por defecto
echo 📝 Creando configuración por defecto...
python daily_benchmark.py --create-config
if errorlevel 1 (
    echo ❌ Error creando configuración
    pause
    exit /b 1
)
echo.

REM Probar el sistema de logging
echo 🧪 Probando sistema de logging...
python test_logging.py
if errorlevel 1 (
    echo ❌ Error en prueba de logging
    pause
    exit /b 1
)
echo.

REM Crear script de ejecución diaria
echo 📝 Creando script de ejecución diaria...
(
echo @echo off
echo REM Script de ejecución diaria automatica
echo cd /d "%~dp0"
echo echo Ejecutando benchmark diario - %%date%% %%time%%
echo python daily_benchmark.py --config-file daily_config_default.json
echo if errorlevel 1 ^(
echo     echo ❌ Error en ejecucion diaria
echo     pause
echo     exit /b 1
echo ^)
echo echo ✅ Benchmark diario completado exitosamente
echo echo Logs disponibles en: .logs/
echo echo Resultados disponibles en: resultados_diarios/
) > "ejecutar_benchmark_diario.bat"

echo ✅ Script de ejecución creado: ejecutar_benchmark_diario.bat
echo.

REM Crear script de análisis semanal
echo 📝 Creando script de análisis semanal...
(
echo @echo off
echo REM Script de análisis semanal
echo cd /d "%~dp0"
echo set FECHA=%%date:~6,4%%%%date:~3,2%%%%date:~0,2%%_%%time:~0,2%%%%time:~3,2%%%%time:~6,2%%
echo set FECHA=%%FECHA: =0%%
echo echo Generando análisis semanal - %%FECHA%%
echo python analyze_logs.py --days 7 --format markdown --output "reporte_semanal_%%FECHA%%.md"
echo python analyze_logs.py --days 7 --format json --output "reporte_semanal_%%FECHA%%.json"
echo echo ✅ Análisis semanal completado
echo echo Reportes generados: reporte_semanal_%%FECHA%%.*
) > "analisis_semanal.bat"

echo ✅ Script de análisis creado: analisis_semanal.bat
echo.

REM Crear script de limpieza de logs
echo 📝 Creando script de limpieza de logs...
(
echo @echo off
echo REM Script de limpieza de logs antiguos
echo cd /d "%~dp0"
echo echo Limpiando logs antiguos...
echo python analyze_logs.py --clean --days 7
echo echo ✅ Limpieza de logs completada
) > "limpiar_logs.bat"

echo ✅ Script de limpieza creado: limpiar_logs.bat
echo.

REM Mostrar resumen
echo ===================================================================
echo 🎉 CONFIGURACION COMPLETADA EXITOSAMENTE
echo ===================================================================
echo.
echo 📁 Archivos creados:
echo    - ejecutar_benchmark_diario.bat  (Ejecución diaria)
echo    - analisis_semanal.bat          (Análisis semanal)
echo    - limpiar_logs.bat              (Limpieza de logs)
echo    - daily_config_default.json     (Configuración por defecto)
echo.
echo 📂 Directorios creados:
echo    - .logs/                        (Sistema de logging)
echo    - resultados_diarios/          (Resultados diarios)
echo.
echo 🚀 PROXIMOS PASOS:
echo.
echo 1. Para ejecutar UN benchmark manual:
echo    python daily_benchmark.py
echo.
echo 2. Para ejecutar benchmark diario programado:
echo    ejecutar_benchmark_diario.bat
echo.
echo 3. Para generar análisis semanal:
echo    analisis_semanal.bat
echo.
echo 4. Para limpiar logs antiguos:
echo    limpiar_logs.bat
echo.
echo 5. Para programar ejecución automática diaria:
echo    - Abrir "Programador de tareas" de Windows
echo    - Crear tarea básica
echo    - Ejecutar: ejecutar_benchmark_diario.bat
echo    - Programar: Diariamente a las 02:00 AM
echo.
echo 📊 MONITOREO:
echo    - Logs generales:     .logs/daily/
echo    - Logs de errores:    .logs/errors/
echo    - Logs de rendimiento: .logs/performance/
echo    - Resultados:         resultados_diarios/
echo.
echo ===================================================================
echo.
pause