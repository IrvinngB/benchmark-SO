# FastAPI Benchmark con Docker - Guía Multi-Plataforma

Esta guía te permitirá ejecutar los benchmarks de FastAPI con logging completo usando Docker en diferentes sistemas operativos Linux.

## 📋 Requisitos Previos

### Para Todos los Sistemas
- **Docker Engine** 20.10.0 o superior
- **Docker Compose** v2.0.0 o superior  
- **Git** para clonar el repositorio
- **4GB RAM** mínimo recomendado
- **2GB** de espacio libre en disco

### Para Análisis de Logs (Opcional)
- **Python 3.10+** instalado en el sistema host
- **Dependencias Python** instaladas (ver sección de instalación)

## 🖥️ Instalación por Sistema Operativo

### 🟦 Debian 12 (Bookworm)

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y ca-certificates curl gnupg lsb-release git

# Agregar clave GPG oficial de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Agregar repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar:
newgrp docker

# Verificar instalación
docker --version
docker compose version
```

### 🔵 Arch Linux

```bash
# Actualizar sistema
sudo pacman -Syu

# Instalar Docker
sudo pacman -S docker docker-compose git

# Habilitar y iniciar Docker
sudo systemctl enable docker.service
sudo systemctl start docker.service

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar:
newgrp docker

# Verificar instalación
docker --version
docker compose version
```

### 🟠 Kubuntu 22.04/24.04

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y ca-certificates curl gnupg lsb-release git

# Agregar clave GPG oficial de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Agregar repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar:
newgrp docker

# Verificar instalación
docker --version
docker compose version
```

### 🟡 Ubuntu 22.04/24.04 LTS

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y ca-certificates curl gnupg lsb-release git

# Agregar clave GPG oficial de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Agregar repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar:
newgrp docker

# Verificar instalación
docker --version
docker compose version
```

## 🚀 Configuración del Proyecto

### 1. Clonar Repositorio

```bash
# Clonar el proyecto
git clone https://github.com/IrvinngB/benchmark-SO.git
cd benchmark-SO

# Verificar estructura
ls -la
```

### 2. Verificar Archivos Docker

Asegúrate de que tienes estos archivos:
- `Dockerfile` - Imagen para benchmarking
- `docker-compose.yml` - Orquestación de servicios
- `benchmark_python.py` - Script principal
- `logging_manager.py` - Sistema de logging
- `.logs/` - Directorio para logs (se crea automáticamente)

## 🐳 Ejecución con Docker

### Método 1: Docker Compose (Recomendado)

```bash
# Construir y ejecutar servicios
docker compose up --build

# Para ejecutar en background
docker compose up -d --build

# Ver logs en tiempo real
docker compose logs -f benchmark

# Detener servicios
docker compose down
```

### Método 2: Docker Manual

```bash
# Construir imagen
docker build -t fastapi-benchmark:latest .

# Ejecutar benchmark con logs persistentes
docker run -it --rm \
  -v $(pwd)/.logs:/app/.logs \
  -v $(pwd)/benchmark_results:/app/benchmark_results \
  -v $(pwd)/resultados_nuevos:/app/resultados_nuevos \
  -v $(pwd)/resultados_vps:/app/resultados_vps \
  --name fastapi-benchmark \
  fastapi-benchmark:latest

# Para ejecutar con parámetros específicos
docker run -it --rm \
  -v $(pwd)/.logs:/app/.logs \
  -v $(pwd)/benchmark_results:/app/benchmark_results \
  fastapi-benchmark:latest \
  python benchmark_python.py --tests 5 --connections 50
```

# Correr contenedor
docker run -d --name bench -p 8000:8000 fastapi-benchmark:latest


## 📊 Ejecución Diaria Recomendada (4 Semanas)

### Configuración de Ejecución Diaria

1. **Crear script diario** (`daily_benchmark.sh`):

```bash
#!/bin/bash
# daily_benchmark.sh

DATE=$(date +%Y-%m-%d)
LOG_FILE=".logs/daily/execution_${DATE}.log"

echo "========================================" >> $LOG_FILE
echo "Iniciando benchmark diario: $DATE" >> $LOG_FILE
echo "Sistema: $(uname -a)" >> $LOG_FILE
echo "Docker: $(docker --version)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# Ejecutar benchmark
docker compose up --build >> $LOG_FILE 2>&1

echo "Benchmark completado: $(date)" >> $LOG_FILE
```

2. **Hacer ejecutable:**
```bash
chmod +x daily_benchmark.sh
```

3. **Ejecutar manualmente cada día:**
```bash
./daily_benchmark.sh
```

### Calendario de Ejecución Manual (4 Semanas)

**Semana 1:**
- Lunes: `./daily_benchmark.sh`
- Miércoles: `./daily_benchmark.sh`  
- Viernes: `./daily_benchmark.sh`

**Semana 2:**
- Lunes: `./daily_benchmark.sh`
- Miércoles: `./daily_benchmark.sh`
- Viernes: `./daily_benchmark.sh`

**Semana 3:**
- Lunes: `./daily_benchmark.sh`
- Miércoles: `./daily_benchmark.sh`
- Viernes: `./daily_benchmark.sh`

**Semana 4:**
- Lunes: `./daily_benchmark.sh`
- Miércoles: `./daily_benchmark.sh`
- Viernes: `./daily_benchmark.sh`

## 📁 Estructura de Logs

Después de ejecutar los benchmarks, tendrás esta estructura:

```
.logs/
├── daily/                 # Logs generales diarios
│   ├── 2025-11-14.log
│   ├── 2025-11-15.log
│   └── ...
├── errors/                # Logs de errores
│   ├── 2025-11-14_errors.log
│   └── ...
├── performance/           # Métricas de rendimiento
│   ├── 2025-11-14_performance.log
│   ├── 2025-11-14_connectivity.log
│   └── ...
├── archive/               # Logs comprimidos antiguos
│   └── *.log.gz
└── README.md             # Documentación del sistema
```

## 🐍 Instalación de Python para Análisis (Opcional)

Si prefieres ejecutar el análisis de logs directamente en tu sistema sin Docker:

### Debian/Ubuntu/Kubuntu
```bash
# Instalar Python y herramientas
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Crear entorno virtual
python3 -m venv benchmark-env
source benchmark-env/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalación
python --version
python -c "import pandas, matplotlib, seaborn; print('✅ Dependencias instaladas')"
```

### Arch Linux
```bash
# Instalar Python
sudo pacman -S python python-pip python-virtualenv

# Crear entorno virtual
python -m venv benchmark-env
source benchmark-env/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### Desactivar Entorno Virtual
```bash
# Cuando termines el análisis
deactivate
```

## 🔧 Comandos Útiles

### Monitoreo de Recursos

```bash
# Ver uso de recursos del contenedor
docker stats

# Ver logs específicos
docker compose logs benchmark

# Acceder al contenedor en ejecución
docker compose exec benchmark /bin/bash

# Limpiar sistema Docker
docker system prune -a
```

### Análisis de Logs

#### 🤖 Opción 1: Automático (Nuevo)
```bash
# Hacer ejecutable el script
chmod +x auto_analysis.sh

# Análisis automático con Docker (recomendado)
./auto_analysis.sh --docker

# Análisis automático con Python local
./auto_analysis.sh --python

# Programar ejecución diaria automática
./auto_analysis.sh --schedule  # Ver opciones de cron/systemd
```

#### 🐳 Opción 2: Manual con Docker
```bash
# Ejecutar análisis usando el contenedor
docker compose --profile tools run log-analyzer

# Análisis específico con parámetros
docker compose run --rm benchmark python analyze_logs.py --days 7 --format all

# Generar reporte en JSON
docker compose run --rm benchmark python analyze_logs.py --days 14 --format json --output reporte.json
```

#### 🐍 Opción 3: Manual con Python Local (Requiere instalación)
```bash
# PRIMERO: Instalar Python y dependencias
# Ubuntu/Debian/Kubuntu:
sudo apt install python3 python3-pip python3-venv

# Arch Linux:
sudo pacman -S python python-pip

# Crear entorno virtual e instalar dependencias
python3 -m venv benchmark-env
source benchmark-env/bin/activate  # En Linux/Mac
# O en Windows: benchmark-env\Scripts\activate

pip install -r requirements.txt

# LUEGO: Ejecutar análisis
python analyze_logs.py --days 7 --format all
python analyze_logs.py --days 14 --format json --output reporte.json
python analyze_logs.py --clean --dry-run --days 10

# Ver logs de rendimiento en tiempo real
tail -f .logs/performance/$(date +%Y-%m-%d)_performance.log
```

#### 📋 Ver Comandos Manuales Detallados
```bash
# Ver todos los comandos manuales disponibles
./auto_analysis.sh --manual
```

## 🐛 Solución de Problemas

### Error: "Permission denied"
```bash
# Verificar permisos de Docker
sudo usermod -aG docker $USER
newgrp docker

# O ejecutar con sudo
sudo docker compose up --build
```

### Error: "Port already in use"
```bash
# Ver qué proceso usa el puerto
sudo netstat -tulpn | grep :8000

# Detener servicios conflictivos
docker compose down
sudo pkill -f "python.*8000"
```

### Error: "Out of disk space"
```bash
# Limpiar imágenes y contenedores no usados
docker system prune -a

# Ver uso de espacio
docker system df
```

### Logs no se generan
```bash
# Verificar permisos del directorio
chmod -R 755 .logs/

# Verificar montaje de volúmenes
docker compose config
```

## 📈 Interpretación de Resultados

### Métricas Importantes

1. **RPS (Requests per Second):** Throughput del sistema
2. **Latencia Promedio:** Tiempo de respuesta
3. **P95/P99 Latencia:** Percentiles para análisis de cola larga
4. **CPU Usage:** Utilización de recursos
5. **Error Rate:** Porcentaje de errores

### Archivos de Salida

- **CSV:** Para análisis en Excel/LibreOffice
- **JSON:** Para procesamiento automatizado
- **Markdown:** Para reportes legibles
- **Gráficos PNG:** Para visualización

## 🔄 Backup y Sincronización

### Respaldar Logs

```bash
# Crear respaldo comprimido
tar -czvf benchmark_logs_$(date +%Y%m%d).tar.gz .logs/

# Subir a repositorio (opcional)
git add .logs/daily/*.log
git commit -m "Logs del $(date +%Y-%m-%d)"
git push origin main
```

### Sincronizar entre Sistemas

```bash
# Exportar logs para análisis en otro sistema
cp -r .logs/ /path/to/backup/

# O usar rsync
rsync -av .logs/ user@remote:/path/to/backup/logs/
```

## 🆘 Soporte

Si encuentras problemas:

1. **Revisa los logs:** `.logs/errors/`
2. **Verifica Docker:** `docker --version`
3. **Consulta documentación:** Este README
4. **Reporta issues:** GitHub Issues del proyecto

## 📝 Notas Adicionales

- **Recursos:** Cada ejecución usa ~1-2GB RAM
- **Tiempo:** Cada benchmark toma 10-30 minutos
- **Espacio:** ~100MB de logs por ejecución
- **Red:** Requiere conexión a VPS para pruebas

¡Buena suerte con tus benchmarks! 🚀