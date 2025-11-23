#!/bin/bash
# ============================================================================
# Script de Configuración de Cron - Linux/macOS
# ============================================================================
# Este script configura cron para ejecutar benchmarks automáticamente
# a las 11:00 AM y 11:00 PM todos los días.
#
# REQUISITOS:
# - Python 3.8+ instalado
# - Todas las dependencias instaladas (requirements.txt)
# - Permisos de ejecución: chmod +x setup_scheduler_linux.sh
#
# USO:
#   ./setup_scheduler_linux.sh
#   ./setup_scheduler_linux.sh --python-path /usr/bin/python3
#   ./setup_scheduler_linux.sh --uninstall
# ============================================================================

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Configuración por defecto
PYTHON_PATH="python3"
WORKING_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$WORKING_DIR/scheduled_benchmark.py"
CONFIG_PATH="$WORKING_DIR/benchmark_config_servers.json"
LOG_DIR="$WORKING_DIR/.logs_scheduled"
UNINSTALL=false

# Procesar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --python-path)
            PYTHON_PATH="$2"
            shift 2
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        *)
            echo -e "${RED}❌ Argumento desconocido: $1${NC}"
            echo "Uso: $0 [--python-path PATH] [--uninstall]"
            exit 1
            ;;
    esac
done

# Función para eliminar tareas de cron
uninstall_cron() {
    echo -e "\n${CYAN}🗑️  Eliminando tareas de cron...${NC}"
    
    # Crear crontab temporal sin las líneas del benchmark
    crontab -l 2>/dev/null | grep -v "scheduled_benchmark.py" | grep -v "# Benchmark Servers" > /tmp/crontab_temp || true
    
    # Instalar el nuevo crontab
    crontab /tmp/crontab_temp
    rm /tmp/crontab_temp
    
    echo -e "${GREEN}✅ Tareas de cron eliminadas${NC}"
    echo -e "\n${GREEN}✅ Proceso de desinstalación completado${NC}"
    exit 0
}

# Si se solicita desinstalación
if [ "$UNINSTALL" = true ]; then
    uninstall_cron
fi

# Verificar que el script existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}❌ Error: No se encontró el script scheduled_benchmark.py${NC}"
    echo -e "${YELLOW}   Ruta esperada: $SCRIPT_PATH${NC}"
    exit 1
fi

# Verificar que existe la configuración
if [ ! -f "$CONFIG_PATH" ]; then
    echo -e "${RED}❌ Error: No se encontró el archivo de configuración${NC}"
    echo -e "${YELLOW}   Ruta esperada: $CONFIG_PATH${NC}"
    exit 1
fi

# Verificar Python
echo -e "\n${CYAN}🔍 Verificando instalación de Python...${NC}"
if command -v "$PYTHON_PATH" &> /dev/null; then
    PYTHON_VERSION=$($PYTHON_PATH --version 2>&1)
    echo -e "${GREEN}✅ Python encontrado: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Error: No se pudo ejecutar Python${NC}"
    echo -e "${YELLOW}   Intenta especificar la ruta completa con --python-path${NC}"
    exit 1
fi

# Crear directorio de logs si no existe
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    echo -e "${GREEN}✅ Directorio de logs creado: $LOG_DIR${NC}"
fi

# Hacer el script ejecutable
chmod +x "$SCRIPT_PATH"

echo -e "\n${CYAN}📅 Configurando tareas de cron...${NC}"
echo -e "${GRAY}   Directorio de trabajo: $WORKING_DIR${NC}"
echo -e "${GRAY}   Script: $SCRIPT_PATH${NC}"
echo -e "${GRAY}   Python: $PYTHON_PATH${NC}"

# Crear entradas de cron
CRON_COMMENT="# Benchmark Servers - Automated Daily Execution"
CRON_AM="0 11 * * * cd $WORKING_DIR && $PYTHON_PATH $SCRIPT_PATH --config $CONFIG_PATH >> $LOG_DIR/cron_output.log 2>&1"
CRON_PM="0 23 * * * cd $WORKING_DIR && $PYTHON_PATH $SCRIPT_PATH --config $CONFIG_PATH >> $LOG_DIR/cron_output.log 2>&1"

# Obtener crontab actual (si existe)
crontab -l 2>/dev/null > /tmp/crontab_current || true

# Eliminar entradas antiguas del benchmark si existen
grep -v "scheduled_benchmark.py" /tmp/crontab_current | grep -v "# Benchmark Servers" > /tmp/crontab_new || true

# Agregar nuevas entradas
echo "" >> /tmp/crontab_new
echo "$CRON_COMMENT" >> /tmp/crontab_new
echo "$CRON_AM" >> /tmp/crontab_new
echo "$CRON_PM" >> /tmp/crontab_new

# Instalar el nuevo crontab
crontab /tmp/crontab_new

# Limpiar archivos temporales
rm /tmp/crontab_current /tmp/crontab_new 2>/dev/null || true

echo -e "${GREEN}✅ Tareas de cron configuradas${NC}"

# ============================================================================
# RESUMEN
# ============================================================================

echo -e "\n$(printf '=%.0s' {1..70})"
echo -e "${GREEN}✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE${NC}"
echo -e "$(printf '=%.0s' {1..70})\n"

echo -e "${CYAN}📋 Tareas programadas creadas:${NC}"
echo -e "${GRAY}   1. Benchmark 11:00 AM - Ejecuta diariamente a las 11:00${NC}"
echo -e "${GRAY}   2. Benchmark 11:00 PM - Ejecuta diariamente a las 23:00${NC}"

echo -e "\n${CYAN}🎯 Servidores a monitorear:${NC}"
echo -e "${GRAY}   • 143.110.201.94${NC}"
echo -e "${GRAY}   • 104.248.217.252${NC}"
echo -e "${GRAY}   • 206.189.215.59${NC}"

echo -e "\n${CYAN}📝 Logs y resultados:${NC}"
echo -e "${GRAY}   • Logs: $LOG_DIR${NC}"
echo -e "${GRAY}   • Resultados: $WORKING_DIR/resultados_automaticos${NC}"
echo -e "${GRAY}   • Cron output: $LOG_DIR/cron_output.log${NC}"

echo -e "\n${CYAN}🔧 Comandos útiles:${NC}"
echo -e "${GRAY}   Ver tareas:      crontab -l${NC}"
echo -e "${GRAY}   Editar tareas:   crontab -e${NC}"
echo -e "${GRAY}   Ejecutar ahora:  cd $WORKING_DIR && $PYTHON_PATH $SCRIPT_PATH${NC}"
echo -e "${GRAY}   Desinstalar:     ./setup_scheduler_linux.sh --uninstall${NC}"

echo -e "\n${CYAN}💡 Horarios configurados:${NC}"
echo -e "${GRAY}   11:00 AM - Todos los días${NC}"
echo -e "${GRAY}   11:00 PM - Todos los días${NC}"

echo -e "\n${CYAN}📊 Verificar estado del servicio cron:${NC}"
if command -v systemctl &> /dev/null; then
    echo -e "${GRAY}   systemctl status cron${NC}"
elif command -v service &> /dev/null; then
    echo -e "${GRAY}   service cron status${NC}"
fi

echo -e "\n$(printf '=%.0s' {1..70})\n"
