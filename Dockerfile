# FastAPI Benchmark - Multi-platform Dockerfile
# Optimizado para benchmarking con logging completo
# Soporte para Python 3.11 con argumentos de construcción

# Build argument para versión de Python (por defecto 3.11)
ARG PYTHON_VERSION=3.11

# Stage 1: Builder
FROM python:${PYTHON_VERSION}-slim as builder

# Metadatos
LABEL maintainer="Benchmark Team"
LABEL description="FastAPI Benchmark Container with Logging"
LABEL version="2.0"

# Variables de entorno para optimización
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar todos los archivos de requirements
COPY requirements*.txt ./

# Crear entorno virtual e instalar dependencias
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependencias según el sistema
RUN if [ -f "requirements-linux.txt" ]; then \
        pip install --no-cache-dir --upgrade pip && \
        pip install --no-cache-dir -r requirements-linux.txt; \
    else \
        pip install --no-cache-dir --upgrade pip && \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Stage 2: Runtime
FROM python:${PYTHON_VERSION}-slim as runtime

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    LOG_LEVEL=INFO \
    BENCHMARK_ENV=docker

# Instalar utilidades necesarias para runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 benchuser && \
    mkdir -p /app/.logs /app/benchmark_results && \
    chown -R benchuser:benchuser /app

# Establecer directorio de trabajo
WORKDIR /app

# Copiar entorno virtual desde builder
COPY --from=builder /opt/venv /opt/venv

# Copiar archivos de la aplicación
COPY --chown=benchuser:benchuser ./app ./app
COPY --chown=benchuser:benchuser benchmark_python.py .
COPY --chown=benchuser:benchuser logging_manager.py .
COPY --chown=benchuser:benchuser analyze_logs.py .

# Crear estructura de logs
RUN mkdir -p .logs/{daily,errors,performance,archive} && \
    chown -R benchuser:benchuser .logs

# Cambiar a usuario no-root
USER benchuser

# Exponer puerto para FastAPI (si se necesita)
EXPOSE 8000

# Health check para monitoreo
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; print('Container healthy'); sys.exit(0)" || exit 1

# Comando por defecto para benchmark
CMD ["python", "benchmark_python.py"]

# Stage 3: App stage (para FastAPI standalone)
FROM runtime as app-stage

# Copiar solo la aplicación FastAPI
COPY --chown=benchuser:benchuser ./app ./app

# Comando para ejecutar FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
