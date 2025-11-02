#!/bin/bash

# Script de Comparación Docker vs Bare Metal para Linux/Mac
# Ejecutar desde tu máquina local hacia los droplets

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función de ayuda
show_help() {
    echo -e "${GREEN}Script de Comparación Docker vs Bare Metal${NC}"
    echo ""
    echo "Uso: $0 -b BARE_METAL_IP -d DOCKER_IP [opciones]"
    echo ""
    echo "Argumentos requeridos:"
    echo "  -b, --bare-metal IP    IP del droplet bare metal"
    echo "  -d, --docker IP        IP del droplet con Docker"
    echo ""
    echo "Opciones:"
    echo "  -r, --runs NUM         Número de runs (default: 3)"
    echo "  -t, --duration SEC     Duración por test en segundos (default: 10)"
    echo "  -h, --help            Mostrar esta ayuda"
    echo ""
    echo "Ejemplo:"
    echo "  $0 -b 192.168.1.100 -d 192.168.1.101 -r 5"
}

# Valores por defecto
RUNS=3
DURATION=10
BARE_METAL_IP=""
DOCKER_IP=""

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--bare-metal)
            BARE_METAL_IP="$2"
            shift 2
            ;;
        -d|--docker)
            DOCKER_IP="$2"
            shift 2
            ;;
        -r|--runs)
            RUNS="$2"
            shift 2
            ;;
        -t|--duration)
            DURATION="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Argumento desconocido: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Validar argumentos requeridos
if [ -z "$BARE_METAL_IP" ] || [ -z "$DOCKER_IP" ]; then
    echo -e "${RED}Error: Se requieren las IPs de ambos droplets${NC}"
    show_help
    exit 1
fi

# Timestamp para el archivo de resultados
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULT_FILE="comparacion_docker_bare_${TIMESTAMP}.txt"

echo -e "${GREEN}🚀 Comparación Docker vs Bare Metal${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""
echo -e "${YELLOW}Bare Metal IP:${NC} $BARE_METAL_IP"
echo -e "${YELLOW}Docker IP:${NC} $DOCKER_IP"
echo -e "${YELLOW}Runs:${NC} $RUNS"
echo -e "${YELLOW}Duration per test:${NC} ${DURATION}s"
echo ""

# Crear archivo de resultados
{
    echo "COMPARACIÓN DOCKER VS BARE METAL"
    echo "Fecha: $(date)"
    echo "Bare Metal IP: $BARE_METAL_IP"
    echo "Docker IP: $DOCKER_IP"
    echo "Runs: $RUNS"
    echo "Duration: ${DURATION}s"
    echo "=================================================="
    echo ""
} > "$RESULT_FILE"

# Función para verificar conectividad
check_connectivity() {
    local ip=$1
    local name=$2

    echo -e "${CYAN}Verificando conectividad con $name ($ip)...${NC}"

    if curl -s --max-time 5 "http://$ip/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name droplet responding${NC}"
        return 0
    else
        echo -e "${RED}❌ $name droplet not responding${NC}"
        return 1
    fi
}

# Función para ejecutar test con wrk
run_wrk_test() {
    local name=$1
    local ip=$2
    local endpoint=$3
    local connections=$4

    echo -e "${CYAN}Testing $name - $endpoint...${NC}"

    if command -v wrk &> /dev/null; then
        echo "$name - $endpoint" >> "$RESULT_FILE"
        wrk -t4 -c"$connections" -d"${DURATION}s" "http://$ip$endpoint" >> "$RESULT_FILE" 2>&1
        echo "" >> "$RESULT_FILE"
    else
        echo -e "${RED}  wrk no encontrado. Instálalo:${NC}"
        echo -e "${YELLOW}  Ubuntu/Debian: sudo apt install wrk${NC}"
        echo -e "${YELLOW}  macOS: brew install wrk${NC}"
        return 1
    fi
}

# Verificar conectividad
echo -e "${YELLOW}Verificando conectividad...${NC}"

if ! check_connectivity "$BARE_METAL_IP" "Bare Metal"; then
    exit 1
fi

if ! check_connectivity "$DOCKER_IP" "Docker"; then
    exit 1
fi

echo ""
echo -e "${GREEN}Ejecutando benchmarks...${NC}"
echo ""

# Ejecutar múltiples runs
for ((run=1; run<=RUNS; run++)); do
    echo -e "${MAGENTA}=== RUN $run de $RUNS ===${NC}"

    {
        echo "=== RUN $run de $RUNS ==="
        echo "Fecha: $(date)"
        echo ""
    } >> "$RESULT_FILE"

    # Baseline
    run_wrk_test "BARE METAL - Baseline" "$BARE_METAL_IP" "/" 100
    run_wrk_test "DOCKER - Baseline" "$DOCKER_IP" "/" 100

    # Heavy endpoint
    run_wrk_test "BARE METAL - Heavy" "$BARE_METAL_IP" "/heavy" 50
    run_wrk_test "DOCKER - Heavy" "$DOCKER_IP" "/heavy" 50

    # JSON Large (con menos conexiones por ser problemático)
    run_wrk_test "BARE METAL - JSON Large" "$BARE_METAL_IP" "/json-large" 20
    run_wrk_test "DOCKER - JSON Large" "$DOCKER_IP" "/json-large" 20

    {
        echo "=== FIN RUN $run ==="
        echo "------------------------------"
        echo ""
    } >> "$RESULT_FILE"

    if [ $run -lt $RUNS ]; then
        echo -e "${CYAN}Esperando 5 segundos antes del siguiente run...${NC}"
        sleep 5
    fi
done

echo ""
echo -e "${GREEN}✅ Comparación completada!${NC}"
echo -e "${YELLOW}Resultados guardados en: $RESULT_FILE${NC}"
echo ""

# Resumen rápido de Requests/sec
echo -e "${GREEN}Resumen rápido de Requests/sec:${NC}"
if command -v grep &> /dev/null; then
    grep -A 1 "Req/sec" "$RESULT_FILE" | tail -12 | while read -r line; do
        echo -e "${CYAN}  $line${NC}"
    done
fi

echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo -e "${CYAN}  - Revisa el archivo $RESULT_FILE para análisis detallado${NC}"
echo -e "${CYAN}  - Compara especialmente los valores de Req/sec y Latencia${NC}"
echo -e "${CYAN}  - El overhead de Docker suele ser 5-15% en VPS${NC}"
echo -e "${CYAN}  - Considera la latencia de red en tus mediciones${NC}"