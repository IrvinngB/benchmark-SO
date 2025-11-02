# FastAPI Performance Testing - Dockerfile
# Multi-stage build para optimización de tamaño
# Optimizado para Python 3.10 LTS

# Stage 1: Builder
FROM python:3.10-slim as builder

# Establecer directorio de trabajo
WORKDIR /app

# Copiar solo requirements para aprovechar cache de Docker
COPY requirements-linux.txt ./requirements.txt

# Instalar dependencias en entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

# Metadatos
LABEL maintainer="Performance Testing Team"
LABEL description="FastAPI Performance Testing Container"

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Establecer directorio de trabajo
WORKDIR /app

# Copiar entorno virtual desde builder
COPY --from=builder /opt/venv /opt/venv

# Copiar código de la aplicación
COPY --chown=appuser:appuser ./app ./app

# Configurar PATH para usar el venv
ENV PATH="/opt/venv/bin:$PATH"

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando de inicio con workers optimizados
# Por defecto 4 workers (ajustar según CPU del VPS)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
