import logging
import asyncio
import math
import psutil
from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="FastAPI Performance Testing",
    description="API para pruebas de rendimiento en VPS (Docker vs Sin Docker)",
    version="1.0.0"
)


@app.get("/")
async def root():
    """
    Endpoint ligero para baseline de rendimiento.
    No realiza operaciones pesadas, solo retorna JSON simple.
    """
    logger.info("Processing request to /")
    return {
        "message": "FastAPI Performance Testing API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint para monitoreo.
    Verifica que la aplicación esté operativa.
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "fastapi-performance-test"
    }


@app.get("/metrics")
async def system_metrics():
    """
    Endpoint de métricas del sistema.
    Retorna información en tiempo real sobre CPU, RAM, disco y red del servidor.
    
    Útil para monitoreo durante benchmarks para obtener métricas del servidor remoto.
    """
    logger.info("System metrics requested")
    
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_mb_total = memory.total / (1024 * 1024)
        memory_mb_used = memory.used / (1024 * 1024)
        memory_mb_available = memory.available / (1024 * 1024)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_gb_total = disk.total / (1024 * 1024 * 1024)
        disk_gb_used = disk.used / (1024 * 1024 * 1024)
        disk_gb_free = disk.free / (1024 * 1024 * 1024)
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # System uptime (aproximado desde boot time)
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.now() - boot_time).total_seconds()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": round(cpu_percent, 2),
                "count": cpu_count,
                "per_cpu": [round(p, 2) for p in cpu_per_core] if cpu_per_core else []
            },
            "memory": {
                "total_mb": round(memory_mb_total, 2),
                "used_mb": round(memory_mb_used, 2),
                "available_mb": round(memory_mb_available, 2),
                "percent": round(memory.percent, 2)
            },
            "disk": {
                "total_gb": round(disk_gb_total, 2),
                "used_gb": round(disk_gb_used, 2),
                "free_gb": round(disk_gb_free, 2),
                "percent": round(disk.percent, 2)
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "uptime_seconds": round(uptime_seconds, 2)
        }
    
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to retrieve system metrics",
                "detail": str(e)
            }
        )


@app.get("/heavy")
async def heavy_computation():
    """
    Endpoint con carga computacional intensiva.
    Simula operaciones CPU-bound para medir capacidad de procesamiento.
    
    Operaciones:
    - Cálculo de factoriales grandes
    - Operaciones logarítmicas
    - Raíces cuadradas en bucle
    """
    logger.info("Processing heavy computation request")
    
    # Realizar operaciones matemáticas intensivas
    result = 0
    
    # Factoriales
    for i in range(1, 100):
        result += math.factorial(i % 20)  # Limitar para evitar números gigantes
    
    # Operaciones logarítmicas
    for i in range(1, 10000):
        result += math.log(i + 1)
    
    # Raíces cuadradas
    for i in range(1, 10000):
        result += math.sqrt(i)
    
    # Operaciones trigonométricas
    for i in range(1, 5000):
        result += math.sin(i) * math.cos(i)
    
    logger.info(f"Heavy computation completed with result: {result:.2f}")
    
    return {
        "status": "completed",
        "computation_result": round(result, 2),
        "operations_performed": {
            "factorials": 99,
            "logarithms": 9999,
            "square_roots": 9999,
            "trigonometric": 4999
        }
    }


@app.get("/async-light")
async def async_light():
    """
    Endpoint asíncrono ligero con delay simulado.
    Útil para medir concurrencia sin bloqueo del event loop.
    """
    logger.info("Processing async-light request")
    
    # Simular I/O asíncrono sin bloquear
    await asyncio.sleep(0.1)
    
    return {
        "status": "completed",
        "message": "Async operation finished",
        "delay_ms": 100
    }


@app.get("/json-large")
async def json_large(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)):
    """
    Endpoint que retorna JSON con paginación.
    MEJORADO: Ahora soporta paginación para mejor rendimiento.
    
    Parámetros:
    - page: número de página (default: 1)
    - limit: items por página (default: 50, máximo: 200)
    
    Ejemplo: /json-large?page=1&limit=50
    """
    logger.info(f"Processing paginated JSON request - page: {page}, limit: {limit}")
    
    total_items = 1000
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, total_items)
    
    # Generar lista de datos solo para la página solicitada
    data = []
    for i in range(start_idx, end_idx):
        data.append({
            "id": i,
            "name": f"Item {i}",
            "value": i * 3.14159,
            "description": f"Description for item number {i} with some additional text",
            "metadata": {
                "created": "2025-11-01",
                "updated": "2025-11-01",
                "tags": [f"tag{j}" for j in range(5)]
            }
        })
    
    # Calcular información de paginación
    total_pages = (total_items + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "status": "success",
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        },
        "count": len(data),
        "items": data
    }


@app.get("/json-large-full")
async def json_large_full():
    """
    Endpoint original que retorna TODO el JSON sin paginación.
    (Mantenido para compatibilidad histórica)
    ADVERTENCIA: Bajo rendimiento, usar /json-large con paginación en su lugar.
    """
    logger.warning("Using /json-large-full endpoint - consider using /json-large with pagination")
    
    # Generar lista grande de datos
    data = []
    for i in range(1000):
        data.append({
            "id": i,
            "name": f"Item {i}",
            "value": i * 3.14159,
            "description": f"Description for item number {i} with some additional text",
            "metadata": {
                "created": "2025-11-01",
                "updated": "2025-11-01",
                "tags": [f"tag{j}" for j in range(5)]
            }
        })
    
    return {
        "status": "success",
        "count": len(data),
        "items": data
    }


@app.on_event("startup")
async def startup_event():
    """Evento ejecutado al iniciar la aplicación."""
    logger.info("FastAPI Performance Testing API is starting up...")
    logger.info("Available endpoints: /, /health, /metrics, /heavy, /async-light, /json-large")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento ejecutado al cerrar la aplicación."""
    logger.info("FastAPI Performance Testing API is shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    # Configuración para desarrollo local
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
