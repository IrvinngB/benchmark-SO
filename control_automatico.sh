#!/bin/bash

set -e

COMPOSE_FILE="docker-compose.automatico.yml"

print_header() {
    echo ""
    echo "========================================================================"
    echo "  $1"
    echo "========================================================================"
    echo ""
}

print_success() {
    echo "✅ $1"
}

print_info() {
    echo "ℹ️  $1"
}

print_error() {
    echo "❌ $1"
}

show_usage() {
    echo "Uso: $0 {start|stop|restart|status|logs|benchmark-manual|analyze-logs|build}"
    echo ""
    echo "Comandos:"
    echo "  start            - Iniciar sistema automatizado"
    echo "  stop             - Detener sistema"
    echo "  restart          - Reiniciar sistema"
    echo "  status           - Ver estado de contenedores"
    echo "  logs             - Ver logs en tiempo real"
    echo "  benchmark-manual - Ejecutar benchmark manualmente"
    echo "  analyze-logs     - Analizar logs"
    echo "  build            - Reconstruir imágenes"
    exit 1
}

if [ $# -eq 0 ]; then
    show_usage
fi

ACTION=$1

case $ACTION in
    start)
        print_header "INICIANDO SISTEMA AUTOMATIZADO"
        print_info "Construyendo imágenes si es necesario..."
        docker compose -f $COMPOSE_FILE build
        
        print_info "Iniciando servicios..."
        docker compose -f $COMPOSE_FILE up -d
        
        print_success "Sistema iniciado correctamente"
        print_info "FastAPI disponible en: http://localhost:8000"
        print_info "Benchmarks programados: 9:00 AM y 9:00 PM"
        echo ""
        print_info "Ver logs con: ./control_automatico.sh logs"
        ;;
    
    stop)
        print_header "DETENIENDO SISTEMA"
        docker compose -f $COMPOSE_FILE down
        print_success "Sistema detenido"
        ;;
    
    restart)
        print_header "REINICIANDO SISTEMA"
        docker compose -f $COMPOSE_FILE restart
        print_success "Sistema reiniciado"
        ;;
    
    status)
        print_header "ESTADO DEL SISTEMA"
        docker compose -f $COMPOSE_FILE ps
        echo ""
        print_info "Uso de recursos:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
        ;;
    
    logs)
        print_header "LOGS DEL SISTEMA"
        print_info "Mostrando logs en tiempo real (Ctrl+C para salir)..."
        docker compose -f $COMPOSE_FILE logs -f
        ;;
    
    benchmark-manual)
        print_header "EJECUTANDO BENCHMARK MANUAL"
        print_info "Ejecutando benchmark fuera del horario programado..."
        
        docker compose -f $COMPOSE_FILE run --rm benchmark-scheduler python benchmark_python.py
        
        print_success "Benchmark completado"
        print_info "Resultados disponibles en: ./benchmark_results/"
        print_info "Logs disponibles en: ./.logs/"
        ;;
    
    analyze-logs)
        print_header "ANALIZANDO LOGS"
        print_info "Ejecutando análisis de logs..."
        
        docker compose -f $COMPOSE_FILE --profile tools run --rm log-manager
        
        print_success "Análisis completado"
        print_info "Reportes disponibles en: ./benchmark_results/"
        ;;
    
    build)
        print_header "CONSTRUYENDO IMAGENES"
        print_info "Reconstruyendo todas las imágenes..."
        docker compose -f $COMPOSE_FILE build --no-cache
        print_success "Imágenes construidas"
        ;;
    
    *)
        print_error "Acción no válida: $ACTION"
        show_usage
        ;;
esac

echo ""
