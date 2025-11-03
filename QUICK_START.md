# ⚡ FastAPI Benchmark Python - Guía Rápida

## 🚀 Inicio Ultrarrápido (3 pasos)

### 1️⃣ Instalar Dependencias
```bash
# Opción A: Instalación automática (RECOMENDADA)
python install_quick.py

# Opción B: Manual (si la automática falla)
pip install aiohttp pandas matplotlib rich psutil requests numpy seaborn
```

### 2️⃣ Verificar Instalación  
```bash
# Verificar que todo funciona
python test_benchmark.py
```

### 3️⃣ Ejecutar Benchmark
```bash
# Benchmark completo
python benchmark_python.py

# Prueba rápida (2 tests, menos tiempo)
python benchmark_python.py --tests 2 --requests 50
```

## 📊 ¿Qué hace este benchmark?

### Prueba tus servidores FastAPI
- **VPS Sin Docker**: 138.68.233.15:8000  
- **VPS Con Docker**: 68.183.168.86:8000

### Mide rendimiento real
- **RPS**: Requests por segundo
- **Latencia**: Tiempo de respuesta (P50, P95, P99)
- **Recursos**: CPU, RAM, Network en tiempo real
- **Estabilidad**: Variabilidad entre pruebas

### Genera resultados automáticos
- **CSV**: Para análisis en Excel/Python
- **Gráficos**: Comparativas visuales automáticas
- **Reportes**: Markdown con conclusiones

## 🎯 Comandos Útiles

```bash
# Benchmark básico (6 pruebas por servidor)
python benchmark_python.py

# Benchmark rápido (ideal para pruebas)
python benchmark_python.py --tests 2 --requests 100

# Benchmark intensivo (para análisis profundo)  
python benchmark_python.py --tests 10 --requests 1000 --connections 100

# Solo analizar datos existentes
python benchmark_python.py --analyze-only benchmark_results_python/

# Con dashboard web (http://localhost:5000)
python benchmark_python.py --dashboard
```

## 📁 Resultados

Después de ejecutar, encuentra tus resultados en:
```
benchmark_results_python/
├── benchmark_detailed_YYYYMMDD_HHMMSS.csv     # Datos completos
├── benchmark_report_YYYYMMDD_HHMMSS.md        # Reporte automático  
└── visualizations_YYYYMMDD_HHMMSS/            # Gráficos
    ├── rps_comparison.png                      # 📊 Comparativa RPS
    ├── latency_analysis.png                    # ⏱️ Análisis latencia
    └── resource_usage.png                      # 💻 Uso CPU/RAM
```

## 🔧 Solución de Problemas

### ❌ Error de dependencias
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar uno por uno
pip install aiohttp
pip install pandas  
pip install matplotlib
pip install rich
pip install psutil
```

### ❌ Servidores VPS no disponibles
```bash
# El benchmark detecta automáticamente y continúa
# También puedes verificar manualmente:
curl http://138.68.233.15:8000/health  # VPS Sin Docker
curl http://68.183.168.86:8000/health   # VPS Con Docker
```

### ❌ Error de memoria/recursos
```bash
# Usar configuración ligera
python benchmark_python.py --tests 2 --requests 50 --connections 25
```

## 📈 Interpretación Rápida

### RPS (Requests per Second)
- **Más alto = mejor rendimiento**
- Docker típicamente 5-15% más lento que bare metal
- Variación baja = más estable

### Latencia
- **Más bajo = mejor**  
- P95/P99 importantes para experiencia usuario
- Aumenta con carga

### Recursos
- **CPU**: >80% indica bottleneck
- **RAM**: Crecimiento sostenido = posible leak
- **Network**: Limitado por ancho de banda

## 🎉 Ventajas vs PowerShell

| Aspecto | PowerShell | Python |
|---------|------------|---------|
| **Velocidad** | Lento (secuencial) | **10x más rápido** (async) |
| **Funciones** | Básico | **100+ métricas** |
| **Análisis** | Manual | **Automático** |
| **Gráficos** | Ninguno | **Profesionales** |
| **Monitoreo** | No | **Tiempo real** |
| **Exportación** | CSV básico | **CSV/Excel/JSON/MD** |

## 🚀 Casos de Uso

### Para Development
```bash
# Prueba rápida durante desarrollo
python benchmark_python.py --tests 1 --requests 100
```

### Para Testing
```bash  
# Análisis completo para decisiones
python benchmark_python.py --tests 6 --requests 1000
```

### Para Production
```bash
# Benchmarking intensivo con dashboard
python benchmark_python.py --tests 10 --dashboard --connections 200
```

### Para Research  
```bash
# Solo análisis de datos históricos
python benchmark_python.py --analyze-only results_folder/
```

---

**¿Listo?** Ejecuta `python install_quick.py` y después `python benchmark_python.py` 🚀