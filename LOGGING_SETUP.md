# Sistema de Logging para FastAPI Performance Benchmark

## 📋 Descripción General

Este proyecto incluye un sistema de logging robusto diseñado para capturar todos los eventos, métricas y errores durante las ejecuciones diarias de benchmarking de 4 semanas.

## 🗂️ Estructura de Carpetas

```
.logs/
├── daily/                    # Logs generales diarios
│   ├── 2025-11-14.log       # Logs generales del día
│   ├── 2025-11-14_config.log # Configuración utilizada
│   └── ...
│
├── errors/                   # Logs de errores y advertencias
│   ├── 2025-11-14_errors.log # Errores y warnings del día
│   └── ...
│
├── performance/              # Logs de rendimiento
│   ├── 2025-11-14_performance.log  # Métricas de benchmarks
│   ├── 2025-11-14_connectivity.log # Estados de conexión
│   └── ...
│
├── archive/                  # Logs comprimidos (>7 días)
│   ├── 2025-11-07_performance.log.gz
│   ├── 2025-11-07_errors.log.gz
│   └── ...
│
└── README.md                 # Esta documentación
```

## 📊 Tipos de Logs

### 1. **Daily Logs** (`.logs/daily/`)
**Archivos:** `YYYY-MM-DD.log`, `YYYY-MM-DD_config.log`

Contiene todos los eventos principales:
- Inicio/fin de benchmarks
- Configuración de ejecución
- Progreso de pruebas
- Eventos importantes del sistema

**Ejemplo:**
```
2025-11-14 10:30:00 | benchmark.general | INFO | ================================================================================
2025-11-14 10:30:00 | benchmark.general | INFO | 🚀 INICIO DE BENCHMARK
2025-11-14 10:30:00 | benchmark.config | INFO | Número de pruebas: 10
2025-11-14 10:30:15 | benchmark.general | INFO | 🌍 INICIANDO PRUEBAS: VPS Sin Docker
```

### 2. **Error Logs** (`.logs/errors/`)
**Archivos:** `YYYY-MM-DD_errors.log`

Contiene solo errores y advertencias:
- Fallos de conexión
- Timeouts
- Excepciones
- Comportamientos anómalos

**Ejemplo:**
```
2025-11-14 10:35:42 | benchmark.errors | WARNING | Errores detectados en Heavy Computation: 5/500 requests
2025-11-14 10:45:18 | benchmark.errors | ERROR | Error de conectividad en http://138.68.233.15:8000/health
```

### 3. **Performance Logs** (`.logs/performance/`)
**Archivos:** `YYYY-MM-DD_performance.log`, `YYYY-MM-DD_connectivity.log`

Contiene métricas detalladas:
- RPS (Requests per Second)
- Latencia (avg, p95, p99)
- Uso de CPU y memoria
- Resultado de cada request
- Estados de conectividad

**Ejemplo:**
```
2025-11-14 10:30:22 | benchmark.performance | DEBUG | Endpoint: Root Endpoint | Environment: vps_no_docker | RPS: 682.79 | Latency: 534.14ms | P95: 612.95ms | P99: 631.43ms | CPU: 48.7% | Memory: 489.01MB | Errors: 0/500
2025-11-14 10:30:25 | benchmark.connectivity | INFO | ✅ Conectividad OK: http://138.68.233.15:8000/health (23.45ms)
```

## 🔄 Rotación Automática

### Política de Rotación
- **Diaria:** Automáticamente a medianoche, se crea un nuevo archivo con la fecha del día
- **Archivado:** Archivos de más de 7 días se comprimen automáticamente con gzip
- **Compresión:** Reduce el tamaño en ~60-80%
- **Limpieza:** Scripts de limpieza manual disponibles

### Espacios Estimados (4 semanas)

**Por ejecución diaria (30 benchmarks):**
- Logs generales: ~2-5 MB
- Logs de errores: ~100-500 KB
- Logs de rendimiento: ~3-8 MB
- **Total/día: ~5-13 MB**

**4 semanas (28 días):**
- Total sin comprimir: ~140-360 MB
- Total comprimido: ~30-80 MB

## 🚀 Uso del Sistema

### 1. Ejecutar Benchmark con Logging Automático

```bash
# Usar directorio de logs por defecto (.logs)
python benchmark_python.py --tests 10

# Usar directorio de logs personalizado
python benchmark_python.py --tests 10 --log-dir /path/to/logs

# Ver logs en tiempo real
tail -f .logs/daily/$(date +%Y-%m-%d).log
tail -f .logs/errors/$(date +%Y-%m-%d)_errors.log
tail -f .logs/performance/$(date +%Y-%m-%d)_performance.log
```

### 2. Analizar Logs Históricos

```bash
# Analizar últimos 7 días
python analyze_logs.py --days 7

# Generar reporte en formato JSON
python analyze_logs.py --days 7 --format json --output reporte_semanal.json

# Generar reporte en formato CSV
python analyze_logs.py --days 7 --format csv --output reporte_semanal.csv

# Mostrar estadísticas
python analyze_logs.py --days 14
```

### 3. Limpiar Logs Antiguos

```bash
# Vista previa de limpieza (dry-run)
python analyze_logs.py --clean --dry-run

# Comprimir y archivar logs más antiguos que 7 días
python analyze_logs.py --clean --days 7
```

## 📈 Monitoreo de Logs

### Ver Logs en Vivo
```bash
# Terminal 1: Logs generales
watch -n 1 'tail -20 .logs/daily/$(date +%Y-%m-%d).log'

# Terminal 2: Errores recientes
watch -n 2 'tail -10 .logs/errors/$(date +%Y-%m-%d)_errors.log'

# Terminal 3: Métricas de rendimiento
watch -n 5 'tail -5 .logs/performance/$(date +%Y-%m-%d)_performance.log'
```

### Buscar Eventos Específicos
```bash
# Buscar errores de hoy
grep ERROR .logs/errors/$(date +%Y-%m-%d)_errors.log

# Buscar resultados de un endpoint específico
grep "Heavy Computation" .logs/performance/$(date +%Y-%m-%d)_performance.log

# Contar fallos de conectividad
grep -c "Error de conectividad" .logs/errors/$(date +%Y-%m-%d)_errors.log

# Ver todos los RPS registrados
grep "RPS:" .logs/performance/$(date +%Y-%m-%d)_performance.log

# Buscar problemas en los últimos 2 días
find .logs/daily -name "*.log" -mtime -2 -exec grep -l "ERROR\|WARNING" {} \;
```

## 🔍 Ejemplo de Análisis Semanal

```bash
#!/bin/bash
# script_analisis_semanal.sh

FECHA=$(date +%Y-%m-%d_%H%M%S)
REPORTE="reporte_semanal_$FECHA"

echo "Generando reportes semanales..."

# Análisis en Markdown
python analyze_logs.py --days 7 --format markdown --output "$REPORTE.md"

# Análisis en JSON
python analyze_logs.py --days 7 --format json --output "$REPORTE.json"

# Análisis en CSV
python analyze_logs.py --days 7 --format csv --output "$REPORTE.csv"

# Resumen
echo ""
echo "📊 Resumen de Logs Semanales"
echo "================================"
echo "Fecha: $(date)"
echo ""

# Contar eventos
echo "Errores encontrados: $(grep -r ERROR .logs/errors -d skip | wc -l)"
echo "Advertencias: $(grep -r WARNING .logs/errors -d skip | wc -l)"
echo ""

# Tamaño de logs
echo "Tamaño total de logs activos: $(du -sh .logs/daily .logs/errors .logs/performance 2>/dev/null | tail -1 | cut -f1)"
echo "Tamaño de archivo: $(du -sh .logs/archive 2>/dev/null | cut -f1)"
echo ""

echo "✅ Reportes generados:"
ls -lh $REPORTE.*
```

## 🛠️ Configuración Avanzada

### Personalizar Niveles de Log

Editar `logging_manager.py` para ajustar niveles:

```python
# Cambiar nivel de logging para consola
handler.setLevel(logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Cambiar Directorios de Logs

```python
# Usar ruta personalizada
log_manager = get_log_manager('/custom/path/.logs')
```

## ⚙️ Implementación en Cron (Linux/Mac)

Para ejecutar automáticamente cada día:

```bash
# Editar crontab
crontab -e

# Agregar entrada (ejecutar diariamente a las 02:00 AM)
0 2 * * * cd /path/to/project && python benchmark_python.py --tests 10 --log-dir .logs >> cron_execution.log 2>&1
```

## 🪟 Implementación en Task Scheduler (Windows)

```batch
# Script: run_benchmark.bat
@echo off
cd C:\Users\YourUser\Projects\SistemasOperativos
python benchmark_python.py --tests 10 --log-dir .logs
```

Luego crear una tarea programada en Windows Task Scheduler.

## 📋 Checklist de Mantenimiento

- [ ] **Diario:** Revisar `.logs/errors/` para nuevos errores
- [ ] **Diario:** Verificar logs de conectividad en `.logs/performance/`
- [ ] **Semanal:** Generar reporte semanal con `analyze_logs.py`
- [ ] **Semanal:** Revisar tendencias de rendimiento
- [ ] **Mensual:** Hacer backup de `.logs/` antes de limpieza
- [ ] **Mensual:** Comprimir y archivar logs antiguos
- [ ] **Mensual:** Revisar uso total de espacio en disco

## 📚 Recursos Adicionales

- Módulo LogManager: `logging_manager.py`
- Script de análisis: `analyze_logs.py`
- Benchmarking: `benchmark_python.py`
- Artículo científico: `ARTICULO_CIENTIFICO_FASTAPI_PERFORMANCE.md`

## ❓ Preguntas Frecuentes

**P: ¿Dónde se guardan los logs?**
R: En la carpeta `.logs/` en el directorio raíz del proyecto, o en la ruta especificada con `--log-dir`.

**P: ¿Cada cuánto se rotan los logs?**
R: Automáticamente cada medianoche. Se crea un nuevo archivo con la fecha actual.

**P: ¿Cuánto espacio necesito para 4 semanas?**
R: Aproximadamente 140-360 MB sin comprimir, o 30-80 MB comprimidos.

**P: ¿Cómo recupero un log eliminado?**
R: Los logs nunca se eliminan, solo se comprimen a `.logs/archive/`. Puedes descomprimirlos con: `gzip -d archivo.log.gz`

**P: ¿Puedo cambiar la ubicación de los logs?**
R: Sí, usa `--log-dir /nueva/ruta` al ejecutar el benchmark.

---

**Última actualización:** 14-11-2025  
**Versión:** 1.0  
**Autor:** Irving B.
