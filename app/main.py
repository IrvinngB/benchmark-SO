import logging
import asyncio
import math
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
    logger.info("Available endpoints: /, /health, /heavy, /async-light, /json-large")


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
