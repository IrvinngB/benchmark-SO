#!/bin/bash

# daily_benchmark.sh - Script para ejecución diaria de benchmarks
# Uso: ./daily_benchmark.sh [opciones]

# Configuración
DATE=$(date +%Y-%m-%d_%H-%M-%S)
LOG_DIR=".logs/daily"
EXEC_LOG="$LOG_DIR/execution_${DATE}.log"
SYSTEM_INFO_LOG="$LOG_DIR/system_info_${DATE}.log"

# Crear directorio si no existe
mkdir -p "$LOG_DIR"

# Función para logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$EXEC_LOG"
}

# Función para capturar información del sistema
capture_system_info() {
    log "Capturando información del sistema..."
    
    {
        echo "=========================================="
        echo "INFORMACIÓN DEL SISTEMA - $DATE"
        echo "=========================================="
        echo
        echo "📋 Sistema Operativo:"
        cat /etc/os-release 2>/dev/null || echo "No disponible"
        echo
        echo "🖥️ Hardware:"
        echo "CPU: $(nproc) cores"
        echo "RAM: $(free -h | awk '/^Mem:/ {print $2}') total"
        echo "Arquitectura: $(uname -m)"
        echo
        echo "🐳 Docker:"
        docker --version 2>/dev/null || echo "Docker no disponible"
        docker compose version 2>/dev/null || echo "Docker Compose no disponible"
        echo
        echo "💽 Espacio en Disco:"
        df -h . | tail -1
        echo
        echo "🌐 Conectividad:"
        ping -c 3 8.8.8.8 >/dev/null 2>&1 && echo "✅ Internet: OK" || echo "❌ Internet: FALLO"
        echo
        echo "🔧 Variables de Entorno Docker:"
        env | grep DOCKER || echo "Sin variables Docker específicas"
        echo
    } > "$SYSTEM_INFO_LOG"
    
    log "Información del sistema guardada en: $SYSTEM_INFO_LOG"
}

# Función para verificar prerequisitos
check_prerequisites() {
    log "Verificando prerequisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        log "❌ ERROR: Docker no está instalado"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! docker compose version &> /dev/null; then
        log "❌ ERROR: Docker Compose no está disponible"
        exit 1
    fi
    
    # Verificar que Docker esté ejecutándose
    if ! docker info &> /dev/null; then
        log "❌ ERROR: Docker daemon no está ejecutándose"
        log "Intenta: sudo systemctl start docker"
        exit 1
    fi
    
    # Verificar archivos necesarios
    if [[ ! -f "docker-compose.yml" ]]; then
        log "❌ ERROR: docker-compose.yml no encontrado"
        exit 1
    fi
    
    if [[ ! -f "Dockerfile" ]]; then
        log "❌ ERROR: Dockerfile no encontrado"
        exit 1
    fi
    
    log "✅ Todos los prerequisitos verificados"
}

# Función para limpiar recursos anteriores
cleanup_resources() {
    log "Limpiando recursos anteriores..."
    
    # Detener contenedores existentes
    docker compose down --remove-orphans &>/dev/null || true
    
    # Limpiar imágenes huérfanas (opcional)
    if [[ "$1" == "--deep-clean" ]]; then
        log "Realizando limpieza profunda..."
        docker system prune -f &>/dev/null || true
    fi
    
    log "✅ Limpieza completada"
}

# Función principal de benchmark
run_benchmark() {
    log "🚀 Iniciando benchmark diario: $DATE"
    log "Sistema: $(uname -a)"
    log "Usuario: $(whoami)"
    log "Directorio: $(pwd)"
    
    # Capturar información del sistema
    capture_system_info
    
    # Construir y ejecutar
    log "Construyendo imagen Docker..."
    if docker compose build --no-cache >> "$EXEC_LOG" 2>&1; then
        log "✅ Imagen construida exitosamente"
    else
        log "❌ ERROR: Fallo en construcción de imagen"
        return 1
    fi
    
    log "Ejecutando benchmark..."
    start_time=$(date +%s)
    
    if docker compose up --abort-on-container-exit >> "$EXEC_LOG" 2>&1; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        log "✅ Benchmark completado en ${duration} segundos"
        
        # Mostrar estadísticas básicas
        show_basic_stats
        
        return 0
    else
        log "❌ ERROR: Fallo en ejecución del benchmark"
        return 1
    fi
}

# Función para mostrar estadísticas básicas
show_basic_stats() {
    log "📊 Estadísticas básicas del benchmark:"
    
    # Contar archivos de log generados hoy
    today=$(date +%Y-%m-%d)
    log_count=$(find .logs -name "*${today}*" -type f 2>/dev/null | wc -l)
    log "📁 Archivos de log generados hoy: $log_count"
    
    # Tamaño total de logs
    if [[ -d ".logs" ]]; then
        total_size=$(du -sh .logs 2>/dev/null | cut -f1)
        log "💾 Tamaño total de logs: $total_size"
    fi
    
    # Verificar si hay resultados CSV recientes
    if [[ -d "benchmark_results" ]]; then
        recent_results=$(find benchmark_results -name "*.csv" -newer .logs/daily/execution_${DATE}.log 2>/dev/null | wc -l)
        log "📈 Archivos de resultados generados: $recent_results"
    fi
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
🚀 Script de Benchmark Diario FastAPI

Uso: $0 [opciones]

Opciones:
  -h, --help          Mostrar esta ayuda
  -c, --clean         Limpiar recursos Docker antes de ejecutar
  -d, --deep-clean    Limpieza profunda (incluye imágenes huérfanas)
  -i, --info-only     Solo capturar información del sistema
  -v, --verbose       Mostrar salida detallada en consola

Ejemplos:
  $0                  # Ejecución normal
  $0 --clean          # Limpiar antes de ejecutar
  $0 --deep-clean     # Limpieza profunda y ejecución
  $0 --info-only      # Solo información del sistema

Archivos generados:
  .logs/daily/execution_FECHA.log     # Log principal
  .logs/daily/system_info_FECHA.log   # Información del sistema
  benchmark_results/                  # Resultados del benchmark

EOF
}

# Función para manejo de señales
handle_signal() {
    log "⚠️ Señal recibida. Limpiando recursos..."
    docker compose down --remove-orphans &>/dev/null || true
    log "🛑 Script terminado por el usuario"
    exit 130
}

# Registrar manejadores de señales
trap handle_signal SIGINT SIGTERM

# Función principal
main() {
    local clean_mode=""
    local info_only=false
    local verbose=false
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--clean)
                clean_mode="--clean"
                shift
                ;;
            -d|--deep-clean)
                clean_mode="--deep-clean"
                shift
                ;;
            -i|--info-only)
                info_only=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            *)
                log "❌ Opción desconocida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Configurar verbosidad
    if [[ "$verbose" == true ]]; then
        set -x
    fi
    
    log "🔄 Iniciando script de benchmark diario..."
    
    # Solo capturar información del sistema si se solicita
    if [[ "$info_only" == true ]]; then
        capture_system_info
        log "ℹ️ Información del sistema capturada. Saliendo..."
        exit 0
    fi
    
    # Verificar prerequisitos
    check_prerequisites
    
    # Limpiar recursos si se solicita
    if [[ -n "$clean_mode" ]]; then
        cleanup_resources "$clean_mode"
    fi
    
    # Ejecutar benchmark
    if run_benchmark; then
        log "🎉 ¡Benchmark completado exitosamente!"
        log "📄 Log completo en: $EXEC_LOG"
        log "📊 Información del sistema en: $SYSTEM_INFO_LOG"
        exit 0
    else
        log "💥 Benchmark falló. Revisa los logs para más detalles."
        log "📄 Log de errores en: $EXEC_LOG"
        exit 1
    fi
}

# Ejecutar función principal con todos los argumentos
main "$@"