# 📊 Resultados del Benchmark FastAPI - Python Edition

Esta carpeta contiene todos los resultados generados por el script de benchmarking `benchmark_python.py`.

## 📁 Estructura de Archivos

Después de ejecutar el benchmark, encontrarás los siguientes archivos:

### 📈 Archivos de Datos
- **`benchmark_detailed_YYYYMMDD_HHMMSS.csv`** - Datos detallados en formato CSV
  - Una fila por cada prueba individual
  - Columnas: timestamp, test_number, environment, endpoint_name, RPS, latencia, CPU, RAM, etc.
  - Importable directamente en Excel, Python, R, etc.

- **`benchmark_detailed_YYYYMMDD_HHMMSS.json`** - Datos completos en formato JSON
  - Estructura jerárquica completa
  - Ideal para análisis programático
  - Compatible con todas las plataformas

- **`benchmark_analysis_YYYYMMDD_HHMMSS.xlsx`** - Análisis en Excel
  - **Hoja "Raw Data"**: Todos los datos sin procesar
  - **Hoja "Summary"**: Análisis automático por entorno y endpoint
  - Gráficos y formateo automático

### 📝 Reportes
- **`benchmark_report_YYYYMMDD_HHMMSS.md`** - Reporte ejecutivo en Markdown
  - Resumen ejecutivo
  - Análisis detallado por endpoint
  - Estadísticas de estabilidad
  - Coeficientes de variación
  - Listo para documentación

### 🎨 Visualizaciones
- **`visualizations_YYYYMMDD_HHMMSS/`** - Carpeta con gráficos profesionales
  - `rps_comparison.png` - Comparativa de RPS por endpoint
  - `latency_analysis.png` - Análisis de latencia (P50, P95, P99)
  - `resource_usage.png` - Uso de CPU y RAM
  - `correlation_matrix.png` - Matriz de correlación entre métricas
  - `performance_timeline.png` - Evolución temporal del rendimiento

### 🗂️ Carpetas Adicionales (si existen datos previos)
- **`vps_no_docker/`** - Resultados específicos del VPS sin Docker
- **`vps_docker/`** - Resultados específicos del VPS con Docker
- **`evidencia/`** - Evidencia de pruebas anteriores

## 🚀 Cómo Ejecutar

```bash
# Benchmark completo (6 tests, resultados en resultados_muestra/)
python benchmark_python.py

# Prueba rápida (2 tests)
python benchmark_python.py --tests 2 --requests 100

# Solo analizar datos existentes
python benchmark_python.py --analyze-only resultados_muestra/
```

## 📊 Métricas Incluidas

### Por Request
- **RPS** (Requests per Second) - Throughput
- **Latencia** - Promedio, P50, P95, P99
- **Tasa de error** - Porcentaje de fallos
- **Throughput** - Ancho de banda (Mbps)

### Recursos del Sistema
- **CPU** - Porcentaje de uso durante el test
- **Memoria** - MB utilizados
- **Network** - Bytes enviados/recibidos

### Estadística
- **Desviación estándar** - Variabilidad
- **Min/Max** - Valores extremos
- **Coeficiente de variación** - Estabilidad (%)

## 📋 Comparación Docker vs Bare Metal

Los datos incluyen automáticamente:
- **VPS Sin Docker** (138.68.233.15:8000)
- **VPS Con Docker** (68.183.168.86:8000)

Permitiendo análisis comparativo directo.

## 💡 Tips Útiles

1. **Abrir en Excel**: Los archivos `.xlsx` se abren directamente en Excel/Calc
2. **Análisis en Python**: 
   ```python
   import pandas as pd
   df = pd.read_csv('benchmark_detailed_*.csv')
   df.groupby('environment').mean()
   ```
3. **Compartir resultados**: Los `.md` y `.xlsx` son perfectos para presentaciones
4. **Timeline**: Ver `performance_timeline.png` para identificar tendencias

## 🔄 Reproducibilidad

Cada ejecución genera archivos con timestamp único:
- Evita sobrescrituras accidentales
- Fácil comparar múltiples ejecuciones
- Historial completo disponible

## 📅 Changelog de Ejecuciones

| Fecha | Tests | Endpoint | RPS | Latencia | Notas |
|-------|-------|----------|-----|----------|-------|
| (Por rellenar) | | | | | |

---

**Última actualización**: Auto-generada por `benchmark_python.py`