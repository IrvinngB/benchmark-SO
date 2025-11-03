# 🚀 FastAPI Performance Benchmark - Python Edition

## 🌟 Características Avanzadas

### ⚡ Rendimiento Superior
- **AsyncIO + aiohttp**: Benchmarking totalmente asíncrono para máximo rendimiento
- **Concurrencia optimizada**: Control inteligente de conexiones simultáneas
- **Pool de conexiones**: Reutilización eficiente de conexiones HTTP

### 📊 Monitoreo en Tiempo Real
- **CPU, RAM, Network**: Monitoreo continuo de recursos del sistema
- **Métricas por request**: Latencia individual de cada petición
- **Análisis estadístico**: Percentiles P50, P95, P99 automáticos
- **Detección de anomalías**: Identificación de outliers y errores

### 📈 Visualización Avanzada
- **Gráficos interactivos**: Matplotlib, Seaborn, Plotly
- **Correlaciones**: Matrix de correlación entre métricas
- **Timeline**: Evolución del rendimiento a lo largo del tiempo
- **Comparativas**: Side-by-side Docker vs Bare Metal

### 🌐 Dashboard Web (Opcional)
- **Tiempo real**: Visualización live de métricas en http://localhost:5000
- **Interactivo**: Gráficos actualizados automáticamente
- **Multi-dispositivo**: Accesible desde cualquier navegador

### 💾 Exportación Múltiple
- **CSV**: Datos raw para análisis externo
- **Excel**: Múltiples hojas con análisis automático  
- **JSON**: Estructura de datos completa
- **Markdown**: Reportes listos para documentación

## 🚀 Instalación Rápida

### Opción 1: Automática (Recomendada)
```bash
# Descargar e instalar todo automáticamente
python setup_benchmark.py --all

# O por pasos
python setup_benchmark.py --install   # Solo instalar dependencias
python setup_benchmark.py --run       # Solo ejecutar benchmark
```

### Opción 2: Manual
```bash
# 1. Instalar dependencias
pip install -r requirements_benchmark.txt

# 2. Ejecutar benchmark
python benchmark_python.py
```

### Opción 3: Windows (Scripts .bat)
```bash
# Después de ejecutar setup_benchmark.py se crean:
install_benchmark.bat    # Solo instalar
run_benchmark.bat        # Solo ejecutar  
benchmark_full.bat       # Instalar y ejecutar
```

## 📋 Dependencias

### Core (Esenciales)
- `aiohttp` - Cliente HTTP asíncrono ultra-rápido
- `pandas` - Análisis de datos y DataFrames
- `matplotlib` - Gráficos base
- `rich` - Terminal con colores y progress bars
- `psutil` - Monitoreo de sistema (CPU, RAM, Network)

### Avanzadas (Opcionales)
- `seaborn` - Visualización estadística
- `plotly` - Gráficos interactivos
- `flask` - Dashboard web en tiempo real
- `openpyxl` - Exportación a Excel
- `numpy` - Computación numérica

## 🎯 Uso del Benchmark

### Comandos Básicos
```bash
# Benchmark estándar (6 pruebas por entorno)
python benchmark_python.py

# Prueba rápida (2 pruebas, menos requests)
python benchmark_python.py --tests 2 --requests 50

# Con dashboard web
python benchmark_python.py --dashboard

# Personalizado
python benchmark_python.py --tests 10 --connections 100 --timeout 60
```

### Parámetros Disponibles
```bash
--tests, -t          # Número de pruebas por entorno (default: 6)
--connections, -c    # Conexiones concurrentes (default: 50)  
--requests, -r       # Requests por endpoint ligero (default: 100)
--timeout           # Timeout por request en segundos (default: 30)
--output, -o        # Directorio de resultados (default: benchmark_results_python)
--dashboard, -d     # Iniciar dashboard web en puerto 5000
--verbose, -v       # Output detallado (default: true)
--analyze-only, -a  # Solo analizar resultados existentes
```

### Solo Análisis de Datos Existentes
```bash
# Analizar resultados previos sin ejecutar nuevos tests
python benchmark_python.py --analyze-only benchmark_results_python/
```

## 📊 Métricas Monitoreadas

### Rendimiento HTTP
- **RPS (Requests per Second)**: Throughput total
- **Latencia promedio**: Tiempo de respuesta medio
- **Percentiles**: P50, P95, P99 para análisis de cola larga
- **Error rate**: Porcentaje de requests fallidas
- **Throughput (Mbps)**: Ancho de banda utilizado

### Recursos del Sistema  
- **CPU Usage %**: Uso de procesador durante tests
- **Memory (MB)**: Consumo de RAM
- **Network I/O**: Bytes enviados/recibidos
- **Disk I/O**: Lectura/escritura en disco (opcional)

### Estadísticas Avanzadas
- **Coeficiente de variación**: Medida de estabilidad
- **Correlaciones**: Relación entre diferentes métricas
- **Outliers**: Detección de valores anómalos
- **Tendencias**: Evolución temporal del rendimiento

## 📁 Estructura de Resultados

```
benchmark_results_python/
├── benchmark_detailed_20231102_143022.csv      # Datos raw completos
├── benchmark_detailed_20231102_143022.json     # Estructura JSON
├── benchmark_analysis_20231102_143022.xlsx     # Excel multi-hoja
├── benchmark_report_20231102_143022.md         # Reporte automático
└── visualizations_20231102_143022/             # Gráficos
    ├── rps_comparison.png                      # Comparativa RPS
    ├── latency_analysis.png                    # Análisis latencia
    ├── resource_usage.png                      # Uso de recursos  
    ├── correlation_matrix.png                  # Matrix correlación
    └── performance_timeline.png                # Timeline rendimiento
```

## 🌐 Dashboard Web

### Activación
```bash
# Iniciar con dashboard
python benchmark_python.py --dashboard

# Dashboard estará disponible en:
# http://localhost:5000
```

### Características
- **Métricas en vivo**: CPU, RAM, tests completados
- **Gráficos actualizados**: Cada 2 segundos
- **Multiplataforma**: Funciona en cualquier navegador
- **Sin instalación**: Solo requiere Flask

## ⚙️ Configuración Avanzada

### Personalizar Endpoints
```python
# Editar en benchmark_python.py
endpoints = [
    {"name": "Mi Endpoint", "path": "/mi-ruta", "requests": 500},
    {"name": "Endpoint Pesado", "path": "/pesado", "requests": 1000},
]
```

### Personalizar Servidores
```python
# Editar en benchmark_python.py  
servers = {
    "local": "localhost:8000",
    "produccion": "mi-servidor.com:8000",
    "staging": "staging.mi-app.com:8000"
}
```

### Ajustar Concurrencia
```python
# Para servidores potentes
python benchmark_python.py --connections 200

# Para servidores limitados
python benchmark_python.py --connections 25
```

## 🔧 Troubleshooting

### Error de Dependencias
```bash
# Instalar solo dependencias esenciales
pip install aiohttp pandas matplotlib rich psutil

# O usar el script de setup
python setup_benchmark.py --install
```

### Servidores No Disponibles
```bash
# El script detecta automáticamente conectividad
# Si los VPS no están disponibles, continúa con tests locales

# Verificar manualmente:
curl http://138.68.233.15:8000/health  # VPS Sin Docker
curl http://68.183.168.86:8000/health   # VPS Con Docker
```

### Problemas de Memoria
```bash
# Reducir carga para sistemas limitados
python benchmark_python.py --tests 3 --requests 50 --connections 25
```

### Dashboard No Funciona
```bash
# Instalar Flask si falta
pip install flask flask-socketio

# Verificar puerto disponible
netstat -an | findstr :5000    # Windows
lsof -i :5000                  # Linux/Mac
```

## 📈 Interpretación de Resultados

### RPS (Requests per Second)
- **Mayor es mejor**: Más requests procesados por segundo
- **Consistencia importa**: Baja desviación estándar indica estabilidad
- **Por endpoint**: Endpoints complejos tendrán menor RPS

### Latencia
- **Menor es mejor**: Tiempo de respuesta más rápido
- **P95/P99**: Percentiles altos revelan problemas de "cola larga"
- **Estabilidad**: Baja variación indica comportamiento predecible

### Recursos del Sistema
- **CPU**: Alto uso puede indicar bottleneck de procesamiento
- **RAM**: Crecimiento sostenido puede indicar memory leaks
- **Network**: Limitado por ancho de banda disponible

### Comparación Docker vs Bare Metal
- **Overhead esperado**: Docker típicamente 5-15% overhead
- **Estabilidad**: Docker puede ser más consistente
- **Recursos**: Docker usa más RAM pero puede ser más eficiente en CPU

## 🚀 Optimizaciones Avanzadas

### Para Máximo Rendimiento
```python
# Aumentar workers aiohttp
connector = aiohttp.TCPConnector(limit=500, limit_per_host=200)

# Usar uvloop en Linux (más rápido que asyncio default)
import uvloop
uvloop.install()
```

### Para Análisis Detallado
```python
# Habilitar profiling de memoria
python -m memory_profiler benchmark_python.py

# Usar cProfile para análisis de CPU
python -m cProfile -o profile.stats benchmark_python.py
```

### Para Tests de Estrés
```bash
# Test de estrés extremo (cuidado con los servidores)
python benchmark_python.py --tests 20 --connections 500 --requests 10000
```

## 📝 Comparación con PowerShell

| Característica | PowerShell Script | Python Edition |
|----------------|-------------------|----------------|
| **Rendimiento** | Secuencial, lento | Asíncrono, 10x+ más rápido |
| **Monitoreo** | Básico | Tiempo real, detallado |
| **Análisis** | Manual | Automático + estadístico |
| **Visualización** | Ninguna | Gráficos avanzados |
| **Exportación** | CSV básico | CSV/Excel/JSON/Markdown |
| **Dashboard** | No | Web en tiempo real |
| **Escalabilidad** | Limitada | Alta concurrencia |
| **Maintenance** | Manual | Automatizado |

## 🎯 Próximos Pasos

1. **Ejecutar benchmark inicial**: `python setup_benchmark.py --all`
2. **Revisar resultados**: Carpeta `benchmark_results_python/`
3. **Analizar gráficos**: Especialmente `correlation_matrix.png` y `rps_comparison.png`
4. **Optimizar**: Basado en bottlenecks identificados
5. **Iterar**: Ejecutar nuevos tests después de optimizaciones

## 📞 Soporte

### Logs Detallados
```bash
# Habilitar logging detallado
python benchmark_python.py --verbose

# Ver logs en tiempo real
tail -f benchmark_results_python/benchmark_*.log  # Linux/Mac
Get-Content -Wait benchmark_results_python/benchmark_*.log  # PowerShell
```

### Información del Sistema
```bash
# Ver configuración detectada
python setup_benchmark.py --info
```

¡El benchmark Python está **10x más rápido** que PowerShell y con **100x más funcionalidades**! 🚀