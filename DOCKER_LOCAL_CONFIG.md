# 🐳 Configuración Docker Local para Benchmarks

Este archivo actualiza la configuración para ejecutar benchmarks únicamente en **Docker Local** (localhost:8000).

## 🎯 **Cambios Realizados:**

### ✅ **Configuración Simplificada:**
- **Un solo entorno**: Docker Local (localhost:8000)
- **Sin VPS remotos**: Eliminados para focus en rendimiento local
- **Mismo conjunto de endpoints**: Root, Health, Async-Light, Heavy, Large JSON

### 📊 **Métricas Optimizadas:**
- **Análisis de consistencia**: Coeficientes de variación para estabilidad
- **Análisis de tendencias**: Correlación entre número de test y rendimiento
- **Distribuciones detalladas**: Histogramas en lugar de comparaciones entre entornos
- **Timeline por endpoint**: Evolución de RPS y latencia por tipo de endpoint

### 🎨 **Visualizaciones Mejoradas:**
1. **`rps_distribution.png`**: Distribución de RPS por endpoint
2. **`latency_distribution.png`**: Histogramas de latencia por percentiles
3. **`resource_analysis.png`**: CPU, Memoria, Throughput, Error Rate
4. **`correlation_matrix.png`**: Correlaciones entre métricas
5. **`performance_timeline.png`**: Evolución temporal por endpoint

### 📋 **Reportes Adaptados:**
- **Resumen ejecutivo**: Métricas globales del Docker Local
- **Análisis por endpoint**: Estadísticas detalladas por endpoint
- **Análisis de estabilidad**: Consistencia y tendencias temporales
- **Métricas de calidad**: Evaluación automática de estabilidad

## 🚀 **Cómo Usar:**

### **Prerequisito: FastAPI corriendo en Docker**
```bash
# Asegurate de que tienes FastAPI ejecutándose en Docker
docker compose up -d fastapi-app
# O el equivalente en tu configuración
```

### **Ejecutar Benchmark:**
```bash
# Benchmark básico (10 pruebas por endpoint)
python benchmark_python.py

# Benchmark extendido (20 pruebas)
python benchmark_python.py --tests 20

# Con más conexiones concurrentes
python benchmark_python.py --tests 10 --connections 200

# Con dashboard web
python benchmark_python.py --dashboard
```

### **Verificar que FastAPI esté disponible:**
```bash
# Verificar que responde
curl http://localhost:8000/health

# Verificar endpoints
curl http://localhost:8000/
curl http://localhost:8000/async-light
curl http://localhost:8000/heavy
curl http://localhost:8000/json-large?page=1&limit=50
```

## 📈 **Análisis Enfocado:**

### **Métricas Clave para Docker Local:**
- **Consistencia de RPS**: ¿Es estable el rendimiento?
- **Escalabilidad de endpoints**: ¿Cuáles manejan mejor la carga?
- **Uso de recursos**: ¿Qué tan eficiente es el contenedor?
- **Latencia por complejidad**: ¿Cómo afecta la complejidad del endpoint?

### **Interpretación de Coeficientes de Variación:**
- **RPS < 10%**: Excelente consistencia
- **RPS 10-20%**: Consistencia moderada
- **RPS > 20%**: Alta variabilidad (investigar causas)

- **Latencia < 15%**: Excelente estabilidad
- **Latencia 15-30%**: Estabilidad moderada
- **Latencia > 30%**: Alta variabilidad

### **Análisis de Tendencias:**
- **Correlación positiva**: Mejora con el tiempo (warm-up)
- **Correlación negativa**: Degrada con el tiempo (resource exhaustion)
- **Sin correlación**: Rendimiento estable

## 🎛️ **Configuración Avanzada:**

### **Personalizar Endpoints:**
```python
# Modificar en BenchmarkConfig.__post_init__()
self.endpoints = [
    {"name": "Custom Endpoint", "path": "/mi-endpoint", "requests": 1000},
    {"name": "Heavy Load Test", "path": "/heavy", "requests": 3000},
    # ... más endpoints
]
```

### **Ajustar Recursos:**
```python
# Modificar conexiones por defecto
default_connections: int = 150  # Aumentar para más concurrencia

# Modificar timeout
timeout: int = 90  # Aumentar para endpoints lentos
```

## 🔍 **Casos de Uso:**

### **1. Desarrollo Local:**
- Verificar rendimiento antes de deploy
- Comparar cambios de código
- Optimizar configuración de Docker

### **2. CI/CD Integration:**
- Benchmarks automáticos post-build
- Regression testing de performance
- Quality gates basados en métricas

### **3. Análisis de Capacidad:**
- Determinar límites del contenedor
- Optimizar resource limits
- Planificar escalamiento horizontal

## 💡 **Tips de Optimización:**

### **Docker Compose:**
```yaml
# Asegurar recursos suficientes
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 4G
    reservations:
      cpus: '2.0'
      memory: 2G
```

### **FastAPI Configuration:**
```python
# En tu aplicación FastAPI
uvicorn app:main --host 0.0.0.0 --port 8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### **Sistema Anfitrión:**
```bash
# Limpiar Docker antes del benchmark
docker system prune -f

# Verificar recursos disponibles
docker system df
free -h
htop
```

---

**🎯 Objetivo**: Obtener métricas precisas y consistentes del rendimiento de FastAPI en Docker Local para optimización y análisis de capacidad.

**📊 Resultado**: Análisis detallado de rendimiento con visualizaciones enfocadas en el comportamiento local del contenedor Docker.