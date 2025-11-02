# FastAPI Performance Testing 🚀

Proyecto de **benchmarking y pruebas de rendimiento** para FastAPI en entornos VPS, comparando el rendimiento entre ejecución **sin containerización** (bare metal) vs **con Docker**.

## 📋 Descripción

Este proyecto proporciona una aplicación FastAPI con múltiples endpoints diseñados para diferentes tipos de carga, permitiendo realizar pruebas de rendimiento exhaustivas en un VPS (DigitalOcean Droplet u otros).

### Objetivos

- ✅ Medir rendimiento real de FastAPI en VPS
- ✅ Comparar overhead de containerización con Docker
- ✅ Identificar cuellos de botella en diferentes escenarios
- ✅ Establecer best practices para deployment en producción

## 🏗️ Estructura del Proyecto

```
fastapi-performance-test/
├── app/
│   ├── __init__.py
│   └── main.py              # Aplicación FastAPI
├── requirements.txt         # Dependencias Python
├── Dockerfile              # Imagen Docker optimizada
├── .dockerignore           # Exclusiones Docker
├── .gitignore              # Exclusiones Git
├── README.md               # Esta documentación
└── copilot-instructions.md # Instrucciones para GitHub Copilot
```

## 🔌 Endpoints Disponibles

| Endpoint | Método | Descripción | Uso |
|----------|--------|-------------|-----|
| `/` | GET | Baseline ligero | Medición de throughput básico |
| `/health` | GET | Health check | Monitoreo de disponibilidad |
| `/heavy` | GET | Carga CPU intensiva | Test de procesamiento |
| `/async-light` | GET | I/O asíncrono simulado | Test de concurrencia |
| `/json-large` | GET | JSON grande (1000 items) | Test de serialización |

## 🚀 Quick Start

### Prerrequisitos

- Python 3.11+
- pip
- Docker (opcional, para pruebas containerizadas)
- VPS con Ubuntu 22.04+ (DigitalOcean, AWS, etc.)

### Instalación Local (Desarrollo)

```bash
# Clonar repositorio
git clone <repo-url>
cd SistemasOperativos

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows PowerShell:
.\venv\Scripts\Activate.ps1
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias (Windows)
pip install -r requirements.txt

# En Linux/Unix usar:
# pip install -r requirements-linux.txt
```

**Nota sobre dependencias:**
- `requirements.txt`: Para desarrollo en Windows (versiones compatibles sin Rust)
- `requirements-linux.txt`: Para producción en Linux/VPS (versiones optimizadas con uvloop)

La API estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

## 🖥️ Deployment en VPS

### Deployment en VPS (Linux)

```bash
# Instalar Python y pip
sudo apt install python3-pip python3-venv -y

# Clonar repositorio
git clone <repo-url>
cd SistemasOperativos

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias optimizadas para Linux
pip install -r requirements-linux.txt

# Ejecutar con workers (ajustar según CPU)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Opción 2: Con Docker

```bash
# Instalar Docker en VPS
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clonar repositorio
git clone <repo-url>
cd SistemasOperativos

# Build imagen
docker build -t fastapi-perf:latest .

# Ejecutar contenedor
docker run -d \
  --name fastapi-app \
  -p 8000:8000 \
  --restart unless-stopped \
  fastapi-perf:latest

# Ver logs
docker logs -f fastapi-app

# Monitorear recursos
docker stats fastapi-app
```

## 📊 Pruebas de Rendimiento

### Instalar Herramientas de Benchmarking

```bash
# En VPS Ubuntu
sudo apt install wrk -y

# Alternativa: hey (más portable)
wget https://hey-release.s3.us-east-2.amazonaws.com/hey_linux_amd64
chmod +x hey_linux_amd64
sudo mv hey_linux_amd64 /usr/local/bin/hey
```

### Ejecutar Benchmarks

#### Test Endpoint Ligero

```bash
# 30 segundos, 100 conexiones concurrentes, 4 threads
wrk -t4 -c100 -d30s http://localhost:8000/

# Desde máquina externa (reemplazar IP)
wrk -t4 -c100 -d30s http://YOUR_VPS_IP:8000/
```

#### Test Endpoint Pesado

```bash
wrk -t4 -c100 -d30s http://localhost:8000/heavy
```

#### Test con hey

```bash
# 10,000 requests, 50 concurrentes
hey -n 10000 -c 50 http://localhost:8000/

# Con timeout personalizado
hey -n 10000 -c 50 -t 5 http://localhost:8000/heavy
```

### Monitoreo de Recursos Durante Tests

```bash
# CPU y RAM en tiempo real
htop

# Recursos de proceso específico
top -p $(pgrep -f uvicorn)

# Si usa Docker
docker stats fastapi-app

# Network I/O
sudo iftop
```

## 📈 Métricas a Recolectar

### Rendimiento

- **Requests por segundo (RPS)**: Throughput total
- **Latencia promedio**: Tiempo de respuesta medio
- **Latencia P50**: Mediana (50% de requests)
- **Latencia P95**: 95% de requests más rápidos
- **Latencia P99**: 99% de requests más rápidos
- **Errores**: Timeouts, 5xx, conexiones rechazadas

### Recursos del Sistema

- **CPU**: % de uso durante prueba
- **RAM**: MB consumidos
- **Network I/O**: Tráfico de red
- **Disk I/O**: Lectura/escritura (si aplica)

### Comparación Docker vs Bare Metal

Crear tabla comparativa:

| Métrica | Sin Docker | Con Docker | Diferencia |
|---------|-----------|-----------|-----------|
| RPS | X req/s | Y req/s | Z% |
| Latencia P50 | X ms | Y ms | Z% |
| Latencia P95 | X ms | Y ms | Z% |
| CPU promedio | X% | Y% | Z% |
| RAM usada | X MB | Y MB | Z MB |

## 🔐 Configuración de Seguridad en VPS

### Firewall (UFW)

```bash
# Configurar firewall
sudo ufw allow 22      # SSH
sudo ufw allow 8000    # FastAPI
sudo ufw enable
sudo ufw status
```

### Variables de Entorno

```bash
# Crear archivo .env (NO commitear)
touch .env

# Ejemplo de contenido:
# SECRET_KEY=your-secret-key-here
# DATABASE_URL=postgresql://...
# DEBUG=False
```

En el código, usar:

```python
from dotenv import load_dotenv
import os

load_load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
```

## 🛠️ Troubleshooting

### Ver procesos Python activos

```bash
ps aux | grep python
```

### Ver qué usa el puerto 8000

```bash
sudo netstat -tulpn | grep :8000
# O en sistemas modernos:
sudo ss -tulpn | grep :8000
```

### Matar proceso en puerto específico

```bash
# Encontrar PID
sudo lsof -t -i:8000

# Matar proceso
sudo kill -9 $(sudo lsof -t -i:8000)
```

### Logs de aplicación

```bash
# Si usa nohup
tail -f nohup.out

# Si usa systemd
sudo journalctl -u fastapi -f

# Docker logs
docker logs -f fastapi-app
```

### Recursos del sistema

```bash
# Espacio en disco
df -h

# Memoria disponible
free -m

# Información de CPU
lscpu
```

## 📚 Recursos Adicionales

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
- [wrk Benchmarking Tool](https://github.com/wg/wrk)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [DigitalOcean VPS Setup](https://docs.digitalocean.com/)

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## ✨ Autor

Performance Testing Team - 2025

---

**Happy Benchmarking! 🚀**
