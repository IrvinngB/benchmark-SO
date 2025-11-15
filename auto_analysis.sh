#!/bin/bash

# auto_analysis.sh - Script para automatizar análisis de logs
# Este script se puede ejecutar automáticamente o manualmente

# Configuración
ANALYSIS_DIR="analysis_results"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
DAYS_TO_ANALYZE=7
LOG_FILE=".logs/daily/auto_analysis_${DATE}.log"

# Crear directorio de resultados si no existe
mkdir -p "$ANALYSIS_DIR"

# Función para logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Función para análisis con Docker
analyze_with_docker() {
    log "🐳 Iniciando análisis automático con Docker..."
    
    # Análisis básico (últimos 7 días)
    docker compose run --rm benchmark python analyze_logs.py \
        --days $DAYS_TO_ANALYZE \
        --format json \
        --output "${ANALYSIS_DIR}/auto_analysis_${DATE}.json" \
        >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✅ Análisis JSON completado"
    else
        log "❌ Error en análisis JSON"
        return 1
    fi
    
    # Generar reporte markdown
    docker compose run --rm benchmark python analyze_logs.py \
        --days $DAYS_TO_ANALYZE \
        --format markdown \
        --output "${ANALYSIS_DIR}/auto_report_${DATE}.md" \
        >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✅ Reporte Markdown completado"
    else
        log "❌ Error en reporte Markdown"
        return 1
    fi
    
    # Análisis CSV para Excel
    docker compose run --rm benchmark python analyze_logs.py \
        --days $DAYS_TO_ANALYZE \
        --format csv \
        --output "${ANALYSIS_DIR}/auto_data_${DATE}.csv" \
        >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✅ Datos CSV completados"
    else
        log "❌ Error en datos CSV"
        return 1
    fi
    
    log "🎉 Análisis automático completado exitosamente"
    log "📁 Resultados en: $ANALYSIS_DIR/"
    
    return 0
}

# Función para análisis con Python local
analyze_with_python() {
    log "🐍 Iniciando análisis automático con Python local..."
    
    # Verificar si existe entorno virtual
    if [ ! -d "benchmark-env" ]; then
        log "❌ Error: No se encontró entorno virtual 'benchmark-env'"
        log "Ejecuta primero: python3 -m venv benchmark-env && source benchmark-env/bin/activate && pip install -r requirements.txt"
        return 1
    fi
    
    # Activar entorno virtual
    source benchmark-env/bin/activate
    
    # Verificar dependencias
    python -c "import pandas, matplotlib, seaborn" 2>/dev/null
    if [ $? -ne 0 ]; then
        log "❌ Error: Dependencias Python no instaladas"
        log "Ejecuta: pip install -r requirements.txt"
        return 1
    fi
    
    # Análisis básico
    python analyze_logs.py \
        --days $DAYS_TO_ANALYZE \
        --format json \
        --output "${ANALYSIS_DIR}/auto_analysis_${DATE}.json" \
        >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✅ Análisis JSON completado"
    else
        log "❌ Error en análisis JSON"
        deactivate
        return 1
    fi
    
    # Generar reporte markdown  
    python analyze_logs.py \
        --days $DAYS_TO_ANALYZE \
        --format markdown \
        --output "${ANALYSIS_DIR}/auto_report_${DATE}.md" \
        >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✅ Reporte Markdown completado"
    else
        log "❌ Error en reporte Markdown"
        deactivate
        return 1
    fi
    
    # Análisis CSV
    python analyze_logs.py \
        --days $DAYS_TO_ANALYZE \
        --format csv \
        --output "${ANALYSIS_DIR}/auto_data_${DATE}.csv" \
        >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✅ Datos CSV completados"
    else
        log "❌ Error en datos CSV"
        deactivate
        return 1
    fi
    
    # Desactivar entorno virtual
    deactivate
    
    log "🎉 Análisis automático completado exitosamente"
    log "📁 Resultados en: $ANALYSIS_DIR/"
    
    return 0
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
🤖 Script de Análisis Automático de Logs

Uso: $0 [opciones]

Opciones:
    -d, --docker        Usar Docker para análisis (recomendado)
    -p, --python        Usar Python local para análisis
    -m, --manual        Mostrar comandos para análisis manual
    -s, --schedule      Mostrar cómo programar ejecución automática
    -h, --help          Mostrar esta ayuda
    --days N            Analizar últimos N días (default: 7)

Ejemplos:
    $0 --docker                    # Análisis con Docker
    $0 --python                    # Análisis con Python local
    $0 --docker --days 14          # Analizar últimos 14 días
    $0 --manual                    # Ver comandos manuales

Archivos generados:
    analysis_results/auto_analysis_FECHA.json    # Datos en JSON
    analysis_results/auto_report_FECHA.md        # Reporte legible
    analysis_results/auto_data_FECHA.csv         # Datos para Excel
    .logs/daily/auto_analysis_FECHA.log          # Log del proceso

EOF
}

# Función para mostrar comandos manuales
show_manual_commands() {
    cat << EOF
📋 Comandos para Análisis Manual de Logs

🐳 Con Docker (Recomendado):
    # Análisis básico últimos 7 días
    docker compose run --rm benchmark python analyze_logs.py --days 7

    # Generar reporte completo
    docker compose run --rm benchmark python analyze_logs.py --days 7 --format all

    # Solo JSON para procesamiento
    docker compose run --rm benchmark python analyze_logs.py --days 7 --format json --output mi_analisis.json

    # Solo gráficos y markdown
    docker compose run --rm benchmark python analyze_logs.py --days 14 --format markdown --output reporte.md

🐍 Con Python Local:
    # Activar entorno virtual
    source benchmark-env/bin/activate

    # Análisis básico
    python analyze_logs.py --days 7

    # Reporte personalizado
    python analyze_logs.py --days 14 --format all --output mi_reporte

    # Limpiar logs antiguos
    python analyze_logs.py --clean --days 30

    # Desactivar entorno
    deactivate

🔧 Opciones adicionales:
    --clean              Limpiar logs antiguos
    --dry-run            Simular limpieza sin ejecutar
    --format all         Generar todos los formatos
    --format json        Solo datos JSON
    --format csv         Solo datos CSV
    --format markdown    Solo reporte Markdown
    --output NOMBRE      Especificar nombre de archivo

EOF
}

# Función para mostrar programación automática
show_schedule_info() {
    cat << EOF
⏰ Cómo Programar Análisis Automático

📅 Opción 1: Cron (Linux/Mac)
    # Editar crontab
    crontab -e

    # Análisis diario a las 23:30
    30 23 * * * cd /ruta/a/benchmark-SO && ./auto_analysis.sh --docker

    # Análisis cada 3 días a las 02:00
    0 2 */3 * * cd /ruta/a/benchmark-SO && ./auto_analysis.sh --docker --days 3

    # Solo días laborales a las 18:00
    0 18 * * 1-5 cd /ruta/a/benchmark-SO && ./auto_analysis.sh --docker

🔄 Opción 2: Systemd Timer (Linux)
    # Crear servicio
    sudo tee /etc/systemd/system/benchmark-analysis.service > /dev/null << EOF2
[Unit]
Description=Benchmark Log Analysis
After=docker.service

[Service]
Type=oneshot
User=tu_usuario
WorkingDirectory=/ruta/a/benchmark-SO
ExecStart=/bin/bash auto_analysis.sh --docker
EOF2

    # Crear timer
    sudo tee /etc/systemd/system/benchmark-analysis.timer > /dev/null << EOF2
[Unit]
Description=Run benchmark analysis daily
Requires=benchmark-analysis.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF2

    # Habilitar timer
    sudo systemctl enable benchmark-analysis.timer
    sudo systemctl start benchmark-analysis.timer

📋 Opción 3: Script Wrapper
    # Crear script que ejecute después de cada benchmark
    echo '#!/bin/bash' > post_benchmark.sh
    echo 'cd /ruta/a/benchmark-SO' >> post_benchmark.sh
    echo './daily_benchmark.sh && ./auto_analysis.sh --docker' >> post_benchmark.sh
    chmod +x post_benchmark.sh

    # Usar este script en lugar de daily_benchmark.sh

🔍 Verificar Programación:
    # Ver crontab actual
    crontab -l

    # Ver timers systemd
    systemctl list-timers

    # Ver logs de ejecución
    journalctl -u benchmark-analysis.service

EOF
}

# Función principal
main() {
    local use_docker=false
    local use_python=false
    local show_manual=false
    local show_schedule=false
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--docker)
                use_docker=true
                shift
                ;;
            -p|--python)
                use_python=true
                shift
                ;;
            -m|--manual)
                show_manual=true
                shift
                ;;
            -s|--schedule)
                show_schedule=true
                shift
                ;;
            --days)
                DAYS_TO_ANALYZE="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log "❌ Opción desconocida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Mostrar información si se solicita
    if [[ "$show_manual" == true ]]; then
        show_manual_commands
        exit 0
    fi
    
    if [[ "$show_schedule" == true ]]; then
        show_schedule_info
        exit 0
    fi
    
    # Verificar que se seleccionó un método
    if [[ "$use_docker" == false && "$use_python" == false ]]; then
        log "❌ Debes especificar --docker o --python"
        show_help
        exit 1
    fi
    
    # Verificar que no se seleccionaron ambos
    if [[ "$use_docker" == true && "$use_python" == true ]]; then
        log "❌ No puedes usar --docker y --python al mismo tiempo"
        exit 1
    fi
    
    log "🚀 Iniciando análisis automático de logs..."
    log "📊 Analizando últimos $DAYS_TO_ANALYZE días"
    
    # Ejecutar análisis según método seleccionado
    if [[ "$use_docker" == true ]]; then
        analyze_with_docker
    elif [[ "$use_python" == true ]]; then
        analyze_with_python
    fi
    
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        log "✅ Proceso completado exitosamente"
        log "📄 Ver log completo en: $LOG_FILE"
        
        # Mostrar resumen de archivos generados
        if [[ -d "$ANALYSIS_DIR" ]]; then
            log "📁 Archivos generados:"
            ls -la "$ANALYSIS_DIR"/*${DATE}* 2>/dev/null | while read line; do
                log "  📄 $line"
            done
        fi
    else
        log "❌ Proceso completado con errores"
        log "📄 Ver detalles en: $LOG_FILE"
    fi
    
    exit $exit_code
}

# Ejecutar función principal con todos los argumentos
main "$@"