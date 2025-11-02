# Script de Comparación Docker vs Bare Metal
# Ejecutar desde una máquina externa (NO desde los droplets)

#!/bin/bash

# Configuración
DURATION=60
CONNECTIONS=100
THREADS=4
DROPLET_BARE_METAL="TU_DROPLET_IP_BARE_METAL"
DROPLET_DOCKER="TU_DROPLET_IP_DOCKER"

echo "🚀 Iniciando comparación Docker vs Bare Metal"
echo "============================================"
echo "Duración: ${DURATION}s | Conexiones: ${CONNECTIONS} | Threads: ${THREADS}"
echo ""

# Función para ejecutar pruebas
run_test() {
    local endpoint=$1
    local name=$2

    echo "📊 Probando ${name} - Endpoint: ${endpoint}"
    echo "--------------------------------------------"

    echo "🔸 Bare Metal (${DROPLET_BARE_METAL}):"
    wrk -t${THREADS} -c${CONNECTIONS} -d${DURATION}s "http://${DROPLET_BARE_METAL}:8000${endpoint}"

    echo ""
    echo "🐳 Docker (${DROPLET_DOCKER}):"
    wrk -t${THREADS} -c${CONNECTIONS} -d${DURATION}s "http://${DROPLET_DOCKER}:8000${endpoint}"

    echo ""
    echo "============================================"
}

# Verificar conectividad
echo "🔍 Verificando conectividad..."
curl -s "http://${DROPLET_BARE_METAL}:8000/health" > /dev/null && echo "✅ Bare Metal: OK" || echo "❌ Bare Metal: FAIL"
curl -s "http://${DROPLET_DOCKER}:8000/health" > /dev/null && echo "✅ Docker: OK" || echo "❌ Docker: FAIL"
echo ""

# Ejecutar pruebas por endpoint
run_test "/" "Endpoint Ligero"
run_test "/heavy" "Endpoint Pesado"
run_test "/async-light" "Endpoint Async"
run_test "/json-large" "Endpoint JSON Grande"

echo "✅ Comparación completada"
echo "📋 Revisa los resultados arriba y documenta en PERFORMANCE_REPORT.md"