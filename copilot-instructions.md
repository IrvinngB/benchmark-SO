# GitHub Copilot Instructions - FastAPI Performance Testing

## Contexto del Proyecto

Este es un proyecto de **pruebas de rendimiento y benchmarking** para aplicaciones FastAPI. El objetivo es comparar el rendimiento de FastAPI ejecutándose:
- **Sin containerización** (directamente en el sistema operativo)
- **Con Docker** (containerizado)

### Entorno de Despliegue
- **Plataforma**: DigitalOcean Droplet / VPS (Virtual Private Server)
- **Propósito**: Realizar pruebas de carga y rendimiento en un entorno de producción realista
- **Métricas clave**: Requests por segundo, latencia, uso de recursos (CPU/RAM)

## Estructura del Proyecto

```
fastapi-performance-test/
├── app/
│   ├── __init__.py
│   └── main.py          # Aplicación FastAPI principal
├── requirements.txt     # Dependencias Python
├── Dockerfile          # Imagen Docker para la app
├── .dockerignore       # Archivos excluidos de Docker
├── .gitignore          # Archivos excluidos de Git
├── README.md           # Documentación principal
└── .github/
    └── copilot-instructions.md
```

## Tecnologías y Stack

### Core
- **FastAPI**: Framework web asíncrono de alto rendimiento
- **Uvicorn**: Servidor ASGI con soporte para múltiples workers
- **Python 3.11+**: Versión moderna con mejoras de rendimiento

### Containerización
- **Docker**: Para pruebas con containerización
- **Docker Compose** (opcional): Para orquestar múltiples servicios

### Herramientas de Benchmarking
- **wrk**: Herramienta de benchmarking HTTP moderna
- **hey**: Alternativa a Apache Bench escrita en Go
- **docker stats**: Para monitorear recursos de contenedores

## Endpoints de la API

### 1. `/` (GET)
- **Propósito**: Endpoint ligero para baseline de rendimiento
- **Respuesta**: JSON simple con mensaje de confirmación
- **Sin operaciones pesadas**: Solo retorna datos estáticos

### 2. `/heavy` (GET)
- **Propósito**: Simular carga computacional intensiva
- **Operaciones**: Cálculos matemáticos (factoriales, logaritmos, raíces)
- **Mide**: Capacidad de procesamiento bajo carga de CPU

### 3. `/health` (GET)
- **Propósito**: Health check para monitoreo
- **Respuesta**: Estado de salud de la aplicación

## Guías para Copilot

### Al Crear Nuevos Endpoints

```python
# SIEMPRE usar async/await para endpoints
@app.get("/endpoint")
async def endpoint_name():
    return {"key": "value"}

# Para operaciones de I/O, usar async
# Para operaciones CPU-bound, considerar ThreadPoolExecutor
```

### Al Agregar Dependencias

```bash
# Usar versiones específicas en requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0

# NO usar versiones flotantes tipo fastapi>=0.104.1
```

### Configuración de Workers

```python
# En VPS/Droplet, calcular workers óptimos:
# workers = (2 x núcleos_CPU) + 1
# Ejemplo: CPU con 2 cores = 5 workers máximo

# Comando Uvicorn recomendado:
# uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Optimizaciones para VPS

```python
# 1. Evitar operaciones bloqueantes en endpoints
# MAL:
import time
time.sleep(1)  # Bloquea el event loop

# BIEN:
import asyncio
await asyncio.sleep(1)  # No bloquea

# 2. Para operaciones CPU intensivas, usar procesamiento en background
from concurrent.futures import ProcessPoolExecutor

# 3. Configurar timeouts apropiados
# 4. Implementar rate limiting si es necesario
```

### Docker Best Practices

```dockerfile
# Usar imágenes slim para reducir tamaño
FROM python:3.11-slim

# Multi-stage builds si se necesita compilación
# Copiar solo lo necesario (.dockerignore configurado)
# No exponer secretos en la imagen
# Usar usuario no-root en producción

USER appuser
```

### Monitoreo y Logging

```python
# Incluir logging estructurado
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/endpoint")
async def endpoint():
    logger.info("Processing request")
    # ... código ...
    return response
```

## Comandos Esenciales para VPS

### Setup Inicial en Droplet

```bash
# 1. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Docker (si se usa)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Instalar Python y pip
sudo apt install python3-pip python3-venv -y

# 4. Clonar repositorio
git clone https://github.com/IrvinngB/benchmark-SO.git
cd SistemasOperativos

# 5. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 6. Instalar dependencias
pip install -r requirements.txt
```

### Despliegue Sin Docker

```bash
# Ejecutar con 4 workers (ajustar según CPU del VPS)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# En background con nohup
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 &

# O usar systemd service (recomendado para producción)
```

### Despliegue Con Docker

```bash
# Build
docker build -t fastapi-perf:latest .

# Run
docker run -d \
  --name fastapi-app \
  -p 8000:8000 \
  --restart unless-stopped \
  fastapi-perf:latest

# Ver logs
docker logs -f fastapi-app

# Stats en tiempo real
docker stats fastapi-app
```

### Pruebas de Carga

```bash
# Instalar wrk en VPS
sudo apt install wrk -y

# Test básico (30 segundos, 100 conexiones)
wrk -t4 -c100 -d30s http://localhost:8000/

# Test endpoint pesado
wrk -t4 -c100 -d30s http://localhost:8000/heavy

# Desde máquina externa (reemplazar IP_VPS)
wrk -t4 -c100 -d30s http://IP_VPS:8000/
```

### Monitoreo de Recursos

```bash
# CPU y RAM en tiempo real
htop

# Recursos de proceso específico
top -p $(pgrep -f uvicorn)

# Recursos de Docker
docker stats fastapi-app

# Logs del sistema
journalctl -u fastapi -f  # Si usas systemd
```

## Consideraciones de Seguridad para VPS

### Firewall

```bash
# Configurar UFW (Ubuntu)
sudo ufw allow 22      # SSH
sudo ufw allow 8000    # FastAPI
sudo ufw enable

# O usar DigitalOcean Cloud Firewall
```

### Variables de Entorno

```python
# Usar .env para secretos (NO commitear)
# Usar python-dotenv

from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
```

### Rate Limiting (Opcional)

```python
# Instalar: pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/endpoint")
@limiter.limit("100/minute")
async def limited_endpoint():
    return {"status": "ok"}
```

## Métricas a Recolectar

### Durante las Pruebas

1. **Requests por segundo (RPS)**: Throughput total
2. **Latencia**:
   - Promedio
   - P50 (mediana)
   - P95 (percentil 95)
   - P99 (percentil 99)
3. **Uso de CPU**: % durante la prueba
4. **Uso de RAM**: MB consumidos
5. **Network I/O**: Tráfico de red
6. **Errores**: Timeouts, 5xx, conexiones rechazadas

### Comparación Docker vs Sin Docker

Crear tabla comparativa con las métricas anteriores para identificar overhead de containerización en el VPS específico.

## Notas para Extensiones Futuras

### Base de Datos

```python
# Cuando se agregue DB, usar SQLAlchemy con async
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Connection pooling optimizado para VPS
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0
)
```

### Cache

```python
# Redis para cache si se necesita
from redis import asyncio as aioredis

redis = await aioredis.from_url("redis://localhost")
```

### Load Balancer

```nginx
# Si se escala horizontalmente, usar Nginx
upstream fastapi_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}
```

## Checklist de Deployment en VPS

- [ ] VPS configurado y accesible por SSH
- [ ] Python 3.11+ instalado
- [ ] Docker instalado (si se usa)
- [ ] Repositorio clonado
- [ ] Variables de entorno configuradas
- [ ] Firewall configurado
- [ ] Aplicación corriendo
- [ ] Health check responde correctamente
- [ ] wrk o hey instalado para benchmarks
- [ ] Monitoring configurado (htop, docker stats)
- [ ] Logs accesibles
- [ ] Backup strategy definida (si es necesario)

## Comandos Útiles para Troubleshooting

```bash
# Ver procesos Python
ps aux | grep python

# Ver puertos abiertos
sudo netstat -tulpn | grep :8000

# Logs de Uvicorn
tail -f uvicorn.log

# Matar proceso por puerto
sudo kill -9 $(sudo lsof -t -i:8000)

# Espacio en disco
df -h

# Memoria disponible
free -m

# Reiniciar servicio
sudo systemctl restart fastapi
```

## Objetivos del Proyecto

1. **Benchmarking objetivo**: Medir rendimiento real en VPS
2. **Comparación Docker**: Cuantificar overhead de containerización
3. **Optimización**: Identificar cuellos de botella
4. **Documentación**: Crear guía reproducible para otros proyectos
5. **Best Practices**: Establecer patrones para deploys en VPS

## Restricciones Importantes

- ❌ **NO usar localStorage/sessionStorage** (no aplica para FastAPI backend)
- ❌ **NO exponer secretos** en código o Docker images
- ❌ **NO hacer operaciones bloqueantes** en endpoints async
- ✅ **SÍ usar async/await** correctamente
- ✅ **SÍ configurar workers** apropiadamente al hardware del VPS
- ✅ **SÍ documentar** todos los resultados de benchmarks

---

**Entorno Target**: DigitalOcean Droplet / VPS con Ubuntu 22.04+  
**Objetivo Principal**: Medición de rendimiento y comparación Docker vs Bare Metal  
**Audiencia**: Desarrolladores backend, DevOps, y equipos de performance testing