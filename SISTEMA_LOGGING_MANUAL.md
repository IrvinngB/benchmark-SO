# 🤖 Sistema de Logging y Análisis - Manual Completo

## 📊 **¿Qué es Automático vs Manual?**

### ✅ **YA Automático (Sin configuración adicional):**
- **Logging durante benchmarks**: Cada vez que ejecutas `benchmark_python.py` o `daily_benchmark.sh`
- **Rotación de logs**: Los archivos se organizan por fecha automáticamente
- **Estructura de carpetas**: `.logs/daily/`, `.logs/errors/`, etc. se crean solos
- **Compresión**: Logs antiguos se comprimen después de 7 días

### 🎯 **Puedes Hacer Automático (Nueva funcionalidad):**
- **Análisis de logs**: Generar reportes automáticamente
- **Limpieza de logs**: Borrar archivos antiguos automáticamente  
- **Programación**: Ejecutar análisis cada día/semana automáticamente

### 🔧 **Siempre Manual (Tienes control):**
- **Cuándo ejecutar benchmarks**: Tú decides cuándo correr las pruebas
- **Configuración de análisis**: Días a analizar, formato de salida, etc.
- **Parámetros de benchmark**: Conexiones, duración, endpoints a probar

---

## 🚀 **Opciones de Uso del Sistema:**

### 1️⃣ **Solo Benchmarks (Sin análisis)**
```bash
# Ejecutar benchmark diario
./daily_benchmark.sh

# Los logs se generan automáticamente en:
# .logs/daily/2025-11-14.log
# .logs/performance/2025-11-14_performance.log
# .logs/errors/2025-11-14_errors.log (si hay errores)
```

### 2️⃣ **Benchmark + Análisis Manual**
```bash
# 1. Ejecutar benchmark
./daily_benchmark.sh

# 2. Analizar logs cuando quieras (Docker)
docker compose run --rm benchmark python analyze_logs.py --days 7

# O con Python local (si lo instalaste)
source benchmark-env/bin/activate
python analyze_logs.py --days 7
deactivate
```

### 3️⃣ **Benchmark + Análisis Automático** ⭐ **NUEVO**
```bash
# 1. Ejecutar benchmark
./daily_benchmark.sh

# 2. Análisis automático inmediato
./auto_analysis.sh --docker

# Esto genera automáticamente:
# - analysis_results/auto_analysis_FECHA.json
# - analysis_results/auto_report_FECHA.md  
# - analysis_results/auto_data_FECHA.csv
```

### 4️⃣ **Todo Automático con Programación**
```bash
# Configurar cron para ejecutar benchmark + análisis diariamente
crontab -e

# Agregar línea (ejecutar cada día a las 23:00):
0 23 * * * cd /ruta/a/benchmark-SO && ./daily_benchmark.sh && ./auto_analysis.sh --docker
```

---

## 🔧 **Detalles del Nuevo Script `auto_analysis.sh`:**

### **Funcionalidades:**
- 🤖 **Análisis automático** con Docker o Python local
- 📊 **Múltiples formatos**: JSON, CSV, Markdown
- 📁 **Organización**: Resultados en carpeta `analysis_results/`
- 🔍 **Logging**: Cada ejecución se registra
- ⚙️ **Configurable**: Días a analizar, formato de salida

### **Comandos Disponibles:**
```bash
# Ver ayuda completa
./auto_analysis.sh --help

# Análisis automático con Docker (recomendado)
./auto_analysis.sh --docker

# Análisis automático con Python local
./auto_analysis.sh --python

# Analizar últimos 14 días en lugar de 7
./auto_analysis.sh --docker --days 14

# Ver comandos manuales detallados
./auto_analysis.sh --manual

# Ver cómo programar ejecución automática
./auto_analysis.sh --schedule
```

### **Archivos Generados:**
```
analysis_results/
├── auto_analysis_2025-11-14_10-30-15.json    # Datos procesables
├── auto_report_2025-11-14_10-30-15.md        # Reporte legible
├── auto_data_2025-11-14_10-30-15.csv         # Para Excel
└── ...

.logs/daily/
├── auto_analysis_2025-11-14_10-30-15.log     # Log del proceso
└── ...
```

---

## 📅 **Flujos de Trabajo Recomendados:**

### **🎯 Para Principiantes (Simple):**
```bash
# 1. Ejecutar benchmark
./daily_benchmark.sh

# 2. Analizar cuando quieras ver resultados
./auto_analysis.sh --docker

# 3. Ver reporte generado
cat analysis_results/auto_report_*.md
```

### **🔥 Para Usuarios Avanzados (Control Total):**
```bash
# Benchmark personalizado
./daily_benchmark.sh --clean --verbose

# Análisis específico
docker compose run --rm benchmark python analyze_logs.py \
    --days 14 \
    --format json \
    --output mi_analisis_$(date +%Y%m%d).json

# Limpieza selectiva
docker compose run --rm benchmark python analyze_logs.py \
    --clean --days 30 --dry-run
```

### **⚡ Para Automatización Completa:**
```bash
# Crear script combinado
cat > benchmark_completo.sh << 'EOF'
#!/bin/bash
cd /ruta/a/benchmark-SO

# Ejecutar benchmark
./daily_benchmark.sh --clean

# Si benchmark exitoso, analizar logs
if [ $? -eq 0 ]; then
    ./auto_analysis.sh --docker --days 7
    echo "✅ Benchmark y análisis completados: $(date)"
else
    echo "❌ Error en benchmark: $(date)"
fi
EOF

chmod +x benchmark_completo.sh

# Programar en cron
crontab -e
# 0 23 * * * /ruta/a/benchmark-SO/benchmark_completo.sh
```

---

## 🎛️ **Opciones de Personalización:**

### **Cambiar Días a Analizar:**
```bash
# Solo últimos 3 días
./auto_analysis.sh --docker --days 3

# Último mes completo
./auto_analysis.sh --docker --days 30
```

### **Formatos de Salida Manual:**
```bash
# Solo JSON (para programas)
docker compose run --rm benchmark python analyze_logs.py --days 7 --format json --output datos.json

# Solo Markdown (para leer)
docker compose run --rm benchmark python analyze_logs.py --days 7 --format markdown --output reporte.md

# Solo CSV (para Excel)
docker compose run --rm benchmark python analyze_logs.py --days 7 --format csv --output datos.csv

# Todos los formatos
docker compose run --rm benchmark python analyze_logs.py --days 7 --format all --output completo
```

### **Limpieza Personalizada:**
```bash
# Ver qué se borraría (simulación)
docker compose run --rm benchmark python analyze_logs.py --clean --dry-run --days 15

# Borrar logs de más de 30 días
docker compose run --rm benchmark python analyze_logs.py --clean --days 30
```

---

## 🚨 **Solución de Problemas:**

### **Script auto_analysis.sh no ejecuta:**
```bash
# Hacer ejecutable
chmod +x auto_analysis.sh

# Verificar Docker
docker --version

# Probar manualmente
./auto_analysis.sh --docker --days 1
```

### **No se generan archivos:**
```bash
# Verificar permisos
ls -la analysis_results/

# Crear directorio manualmente
mkdir -p analysis_results

# Ver logs de error
tail -f .logs/daily/auto_analysis_*.log
```

### **Python local falla:**
```bash
# Verificar entorno virtual
source benchmark-env/bin/activate
python --version
pip list | grep pandas

# Reinstalar si es necesario
pip install --force-reinstall -r requirements.txt
```

---

## 💡 **Recomendaciones por Uso:**

### **📊 Para Análisis Casual:**
- ✅ Usa Docker: `./auto_analysis.sh --docker`
- ✅ No instales Python local
- ✅ Ejecuta análisis cuando quieras ver resultados

### **🔬 Para Análisis Científico:**
- ✅ Instala Python local con entorno virtual
- ✅ Usa comandos manuales específicos
- ✅ Personaliza parámetros según necesites

### **🏭 Para Producción/Automatización:**
- ✅ Usa Docker para consistencia
- ✅ Programa con cron/systemd
- ✅ Combina benchmark + análisis en un script

### **🎓 Para Aprendizaje:**
- ✅ Empieza con Docker
- ✅ Experimenta con comandos manuales
- ✅ Luego prueba Python local si te interesa

---

## 📋 **Resumen de Comandos Rápidos:**

```bash
# 🚀 BENCHMARK
./daily_benchmark.sh                    # Ejecutar benchmark

# 🤖 ANÁLISIS AUTOMÁTICO (Recomendado)
./auto_analysis.sh --docker             # Análisis completo automático
./auto_analysis.sh --docker --days 14   # Últimos 14 días

# 📋 ANÁLISIS MANUAL
docker compose run --rm benchmark python analyze_logs.py --days 7  # Básico
./auto_analysis.sh --manual             # Ver todos los comandos

# ⚙️ CONFIGURACIÓN
./auto_analysis.sh --schedule           # Ver cómo automatizar
./auto_analysis.sh --help               # Ver todas las opciones

# 🔍 INFORMACIÓN
ls -la .logs/                           # Ver logs generados
ls -la analysis_results/                # Ver análisis generados
```

¡Ahora tienes control total sobre cuándo y cómo analizar tus logs! 🎯