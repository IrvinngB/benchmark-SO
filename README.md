# FastAPI Performance Testing 🚀

Proyecto de **benchmarking y pruebas de rendimiento** para FastAPI en entornos VPS, comparando el rendimiento entre ejecución **sin containerización** (bare metal) vs **con Docker**.

## 📋 Descripción

Este proyecto proporciona una aplicación FastAPI con múltiples endpoints diseñados para diferentes tipos de carga, permitiendo realizar pruebas de rendimiento exhaustivas en un VPS (DigitalOcean Droplet u otros).

### Objetivos

- ✅ Medir rendimiento real de FastAPI en VPS
- ✅ Comparar overhead de containerización con Docker
- ✅ Identificar cuellos de botella en diferentes escenarios
- ✅ Establecer best practices para deployment en producción

## 🔗 Repositorio

**GitHub**: https://github.com/IrvinngB/benchmark-SO.git

```bash
git clone https://github.com/IrvinngB/benchmark-SO.git
cd benchmark-SO
```

## 🏗️ Estructura del Proyecto

```
fastapi-performance-test/
├── app/
│   ├── __init__.py
│   └── main.py              # Aplicación FastAPI
├── requirements.txt         # Dependencias Python (Windows)
├── requirements-linux.txt   # Dependencias Python (Linux/VPS)
├── Dockerfile              # Imagen Docker optimizada
├── compare-docker-bare.sh  # Script de comparación (Linux/Mac)
├── compare-docker-bare.ps1 # Script de comparación (Windows)
├── benchmark-local.ps1     # Script de benchmark local
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

- Python 3.10+ (recomendado 3.10 LTS)
- pip
- Docker (opcional, para pruebas containerizadas)
- VPS con Ubuntu 22.04+ (DigitalOcean, AWS, etc.)

### Instalación Local (Desarrollo)

```bash
# Clonar repositorio
git clone https://github.com/IrvinngB/benchmark-SO.git
cd benchmark-SO

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
git clone https://github.com/IrvinngB/benchmark-SO.git
cd benchmark-SO

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
git clone https://github.com/IrvinngB/benchmark-SO.git
cd benchmark-SO

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

### Ejecutar Benchmarks desde Máquina Local (Recomendado)

**Para pruebas más realistas**, ejecuta los benchmarks desde tu máquina local hacia los droplets remotos. Esto mide el rendimiento end-to-end incluyendo latencia de red.

#### Instalar Herramientas en tu Máquina Local

**Windows (PowerShell):**
```powershell
# Instalar bombardier (recomendado)
# Descargar desde: https://github.com/codesenberg/bombardier/releases
# O usar el script incluido
.\benchmark-local.ps1 -ServerHost "TU_DROPLET_IP:8000"
```

**Linux/Mac:**
```bash
# Instalar wrk
sudo apt install wrk  # Ubuntu/Debian
# o
brew install wrk      # macOS

# Ejecutar benchmarks
wrk -t4 -c100 -d30s http://TU_DROPLET_IP:8000/
```

#### Comparación Docker vs Bare Metal

```bash
# Benchmark al droplet SIN Docker
echo "=== BENCHMARK BARE METAL ==="
wrk -t4 -c100 -d30s http://BARE_METAL_IP:8000/
wrk -t4 -c100 -d30s http://BARE_METAL_IP:8000/heavy

# Benchmark al droplet CON Docker
echo "=== BENCHMARK DOCKER ==="
wrk -t4 -c100 -d30s http://DOCKER_IP:8000/
wrk -t4 -c100 -d30s http://DOCKER_IP:8000/heavy

# Comparar latencia de red
echo "=== LATENCY TEST ==="
ping BARE_METAL_IP
ping DOCKER_IP
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

## � Metodología de Benchmarking Recomendada

### 1. Configuración de Pruebas
- **Cliente**: Tu máquina local (Windows/Linux/Mac)
- **Servidores**: 2 droplets de DigitalOcean (uno bare metal, uno Docker)
- **Herramienta**: wrk o bombardier (desde máquina local)
- **Duración**: 30-60 segundos por test
- **Conexiones**: 50-100 concurrentes
- **Repeticiones**: 3-5 veces por endpoint

### 2. Endpoints a Probar
```bash
# 1. Baseline (medir throughput máximo)
wrk -t4 -c100 -d30s http://DROPLET_IP:8000/

# 2. Health check (operación ligera)
wrk -t4 -c100 -d30s http://DROPLET_IP:8000/health

# 3. CPU intensivo (bottleneck de procesamiento)
wrk -t4 -c50 -d30s http://DROPLET_IP:8000/heavy

# 4. JSON grande (bottleneck de serialización)
wrk -t4 -c20 -d30s http://DROPLET_IP:8000/json-large
```

### 3. Métricas a Recolectar
- **Requests/sec**: Throughput principal
- **Latencia promedio**: P50, P95, P99
- **Errores**: Timeouts, conexiones fallidas
- **CPU/RAM**: En el servidor durante las pruebas
- **Red**: Latencia base con ping

### 4. Comparación Docker vs Bare Metal
```bash
# Script de comparación
echo "=== COMPARACIÓN DOCKER VS BARE METAL ===" > comparacion.txt
echo "Fecha: $(date)" >> comparacion.txt
echo "" >> comparacion.txt

# Ping test (latencia de red)
echo "PING BARE METAL:" >> comparacion.txt
ping -c 5 BARE_METAL_IP >> comparacion.txt
echo "" >> comparacion.txt

echo "PING DOCKER:" >> comparacion.txt
ping -c 5 DOCKER_IP >> comparacion.txt
echo "" >> comparacion.txt

# Benchmarks (ejecutar múltiples veces)
for i in {1..3}; do
    echo "=== RUN $i ===" >> comparacion.txt
    
    echo "BARE METAL - Baseline:" >> comparacion.txt
    wrk -t4 -c100 -d10s http://BARE_METAL_IP:8000/ >> comparacion.txt
    
    echo "DOCKER - Baseline:" >> comparacion.txt
    wrk -t4 -c100 -d10s http://DOCKER_IP:8000/ >> comparacion.txt
    
    echo "BARE METAL - Heavy:" >> comparacion.txt
    wrk -t4 -c50 -d10s http://BARE_METAL_IP:8000/heavy >> comparacion.txt
    
    echo "DOCKER - Heavy:" >> comparacion.txt
    wrk -t4 -c50 -d10s http://DOCKER_IP:8000/heavy >> comparacion.txt
done
```

### 5. Script Automatizado

Para facilitar la comparación, usa los scripts incluidos según tu sistema operativo:

**Windows PowerShell:**
```powershell
# Ejecutar comparación automatizada
.\compare-docker-bare.ps1 -BareMetalIP "IP_DROPLET_BARE" -DockerIP "IP_DROPLET_DOCKER" -Runs 3
```

**Linux/Mac (Bash):**
```bash
# Hacer ejecutable el script
chmod +x compare-docker-bare.sh

# Ejecutar comparación automatizada
./compare-docker-bare.sh -b IP_DROPLET_BARE -d IP_DROPLET_DOCKER -r 3
```

**Ambos scripts:**
- ✅ Verifican conectividad de ambos droplets
- ✅ Ejecutan múltiples runs para mayor precisión
- ✅ Guardan resultados en archivo de texto con timestamp
- ✅ Muestran resumen de Requests/sec
- ✅ Incluyen consejos de análisis

## 🤔 ¿Por qué ejecutar desde máquina local?

Ejecutar los benchmarks desde tu máquina local hacia los droplets remotos es **muy superior** que hacerlo desde el mismo VPS:

### ✅ Ventajas de benchmarks remotos:
- **Realismo**: Simula cómo los usuarios reales acceden a tu aplicación
- **Latencia de red**: Mide el impacto real de la red en el rendimiento
- **Sin interferencia**: El VPS puede dedicar todos sus recursos a la aplicación
- **Condiciones reales**: Pruebas end-to-end incluyendo red, DNS, etc.
- **Escalabilidad**: Puedes probar desde múltiples ubicaciones geográficas

### ❌ Problemas de benchmarks locales:
- **Sin latencia de red**: Resultados irreales para aplicaciones web
- **Interferencia**: El proceso de benchmarking consume recursos del mismo servidor
- **Loopback**: Conexiones localhost no representan el uso real
- **CPU compartido**: Benchmark y aplicación compiten por CPU

### 📊 Diferencias típicas observadas:
- **Latencia**: +10-50ms adicionales por salto de red
- **Throughput**: 5-15% menos por overhead de red
- **Realismo**: 100% más representativo del uso real

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
