#!/bin/bash
# Script de benchmarking automatizado para FastAPI Performance Testing
# Uso: ./benchmark.sh [docker|bare] [host]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuración
MODE=${1:-bare}  # docker o bare
HOST=${2:-localhost:8000}
DURATION="30s"
CONNECTIONS=100
THREADS=4

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}FastAPI Performance Benchmark${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Mode: ${YELLOW}${MODE}${NC}"
echo -e "Host: ${YELLOW}${HOST}${NC}"
echo -e "Duration: ${YELLOW}${DURATION}${NC}"
echo -e "Connections: ${YELLOW}${CONNECTIONS}${NC}"
echo -e "Threads: ${YELLOW}${THREADS}${NC}"
echo ""

# Crear directorio para resultados
RESULTS_DIR="benchmark_results"
mkdir -p ${RESULTS_DIR}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULT_FILE="${RESULTS_DIR}/benchmark_${MODE}_${TIMESTAMP}.txt"

# Función para ejecutar benchmark
run_benchmark() {
    local endpoint=$1
    local name=$2
    
    echo -e "${YELLOW}Testing endpoint: ${endpoint}${NC}"
    echo "Testing ${name} - ${endpoint}" >> ${RESULT_FILE}
    echo "----------------------------------------" >> ${RESULT_FILE}
    
    if command -v wrk &> /dev/null; then
        wrk -t${THREADS} -c${CONNECTIONS} -d${DURATION} "http://${HOST}${endpoint}" >> ${RESULT_FILE} 2>&1
    else
        echo -e "${RED}wrk not found! Please install it first.${NC}"
        exit 1
    fi
    
    echo "" >> ${RESULT_FILE}
    echo "" >> ${RESULT_FILE}
}

# Verificar que el servidor esté corriendo
echo -e "${YELLOW}Checking if server is running...${NC}"
if curl -s -f "http://${HOST}/health" > /dev/null; then
    echo -e "${GREEN}✓ Server is running${NC}"
else
    echo -e "${RED}✗ Server is not responding${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Starting benchmarks...${NC}"
echo ""

# Header del archivo de resultados
echo "FastAPI Performance Benchmark Results" > ${RESULT_FILE}
echo "Mode: ${MODE}" >> ${RESULT_FILE}
echo "Date: $(date)" >> ${RESULT_FILE}
echo "Host: ${HOST}" >> ${RESULT_FILE}
echo "=======================================" >> ${RESULT_FILE}
echo "" >> ${RESULT_FILE}

# Ejecutar benchmarks
run_benchmark "/" "Root Endpoint (Baseline)"
sleep 2

run_benchmark "/health" "Health Check"
sleep 2

run_benchmark "/async-light" "Async Light"
sleep 2

run_benchmark "/heavy" "Heavy Computation"
sleep 2

run_benchmark "/json-large" "Large JSON Response"

echo ""
echo -e "${GREEN}✓ Benchmarks completed!${NC}"
echo -e "Results saved to: ${YELLOW}${RESULT_FILE}${NC}"
echo ""

# Mostrar resumen si existe
if command -v grep &> /dev/null; then
    echo -e "${GREEN}Quick Summary:${NC}"
    grep -A 1 "Requests/sec:" ${RESULT_FILE} | head -20
fi
