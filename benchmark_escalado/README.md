# Benchmark Escalado - Pruebas de Alto Volumen

Esta carpeta contiene los resultados de **pruebas de rendimiento escaladas** del sistema FastAPI, diseñadas para generar datos estadísticamente más robustos y probar la estabilidad bajo cargas mayores.

## Configuración de Pruebas Escaladas

### Parámetros Aumentados
- **Corridas por entorno**: 10 (vs 6 en pruebas normales)
- **Timeout por request**: 60 segundos (vs 30s)
- **Conexiones concurrentes**: 100 (vs 50)

### Requests por Endpoint
- **Root Endpoint (Baseline)**: 500 requests (vs 100)
- **Health Check**: 500 requests (vs 100) 
- **Async Light**: 750 requests (vs 100)
- **Heavy Computation**: 2000 requests (vs 1000)
- **Large JSON Response**: 1500 requests (vs 1000)

## Objetivos de las Pruebas Escaladas

1. **Mayor significancia estadística** - Con 10 corridas se reduce el margen de error
2. **Detección de degradación progresiva** - Más requests revelan problemas de memoria/performance
3. **Prueba de estabilidad sostenida** - Cargas mayores por más tiempo
4. **Identificación de puntos de quiebre** - Encontrar límites reales de throughput
5. **Análisis de percentiles confiables** - P95/P99 más representativos con muestras grandes

## Tipos de Archivos Generados

### Datos Primarios
- `benchmark_detailed_YYYYMMDD_HHMMSS.csv` - Todas las métricas por test
- `benchmark_detailed_YYYYMMDD_HHMMSS.json` - Datos estructurados para análisis
- `benchmark_analysis_YYYYMMDD_HHMMSS.xlsx` - Excel con múltiples hojas y estadísticas

### Análisis y Reportes  
- `benchmark_report_YYYYMMDD_HHMMSS.md` - Reporte estadístico detallado
- `visualizations_YYYYMMDD_HHMMSS/` - Gráficos profesionales (PNG alta resolución)

### Visualizaciones Incluidas
- **RPS Comparison**: Boxplots de throughput por endpoint/entorno
- **Latency Analysis**: P50/P95/P99 por entorno
- **Resource Usage**: CPU/RAM durante benchmarks  
- **Correlation Matrix**: Heatmap de correlaciones entre métricas
- **Performance Timeline**: Evolución del rendimiento a lo largo de las 10 corridas

## Interpretación de Resultados Escalados

### Métricas de Estabilidad
- **Coeficiente de Variación (CV)** - Menor variabilidad = mayor estabilidad
- **Tendencia RPS** - ¿Se degrada performance en corridas posteriores?
- **Error Rate Progresivo** - ¿Aumentan errores con el tiempo?

### Indicadores de Alerta
- CV > 15% en RPS indica inestabilidad
- P95 > 3x P50 sugiere colas/bottlenecks severos  
- Error rate > 1% requiere investigación
- Crecimiento progresivo de latencia indica memory leaks

## Comandos para Ejecutar

```bash
# Ejecución completa (puede tomar 30-45 minutos)
python benchmark_python.py

# Solo análisis de resultados existentes
python benchmark_python.py --analyze-only benchmark_escalado

# Con dashboard web en tiempo real
python benchmark_python.py --dashboard

# Personalización avanzada
python benchmark_python.py --tests 15 --connections 200 --timeout 90
```

## Comparación con Pruebas Normales

| Métrica | Normales | Escaladas | Factor |
|---------|----------|-----------|--------|
| Corridas | 6 | 10 | 1.67x |
| Total Requests | ~3,200 | ~10,500 | 3.28x |
| Tiempo estimado | 10-15 min | 30-45 min | 3x |
| Significancia estadística | Básica | Alta | - |
| Detección de problemas | Limitada | Robusta | - |

---

**⚠️ Nota**: Las pruebas escaladas consumen más recursos del servidor y cliente. Monitorear CPU/RAM durante ejecución.

**💡 Recomendación**: Ejecutar estas pruebas durante horas de menor carga para evitar impacto en usuarios reales.