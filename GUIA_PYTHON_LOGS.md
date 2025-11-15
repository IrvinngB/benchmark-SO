# 🐍 Guía de Instalación Python para Análisis de Logs

Esta guía te ayuda a instalar Python y las dependencias necesarias para ejecutar el análisis de logs **sin Docker**.

## 🎯 ¿Cuándo Necesitas Esto?

- ✅ Quieres ejecutar `analyze_logs.py` directamente en tu sistema
- ✅ Prefieres no usar Docker para el análisis
- ✅ Necesitas personalizar el análisis con librerías adicionales
- ✅ Quieres integrar el análisis con otras herramientas Python

**🐳 Alternativa:** Si prefieres no instalar Python, usa: `docker compose run --rm benchmark python analyze_logs.py --days 7`

## 📋 Requisitos Previos

- Sistema operativo Linux (Debian, Ubuntu, Kubuntu, Arch)
- Acceso a terminal con permisos sudo
- Conexión a internet para descargar paquetes

## 🖥️ Instalación por Sistema Operativo

### 🟦 Debian 12 (Bookworm)

```bash
# Actualizar repositorios
sudo apt update

# Instalar Python 3.11 y herramientas
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verificar instalación
python3 --version  # Debe mostrar Python 3.11.x
pip3 --version     # Debe mostrar pip 23.x o superior
```

### 🔵 Arch Linux

```bash
# Actualizar sistema
sudo pacman -Syu

# Instalar Python y herramientas
sudo pacman -S python python-pip python-virtualenv

# Verificar instalación
python --version   # Debe mostrar Python 3.11.x o superior
pip --version      # Debe mostrar pip 23.x o superior
```

### 🟠 Kubuntu 22.04/24.04

```bash
# Actualizar repositorios
sudo apt update

# Para Kubuntu 22.04 (instalar Python 3.11 desde PPA)
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev

# Para Kubuntu 24.04 (Python 3.12 por defecto)
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verificar instalación
python3.11 --version || python3 --version
```

### 🟡 Ubuntu 22.04/24.04 LTS

```bash
# Actualizar repositorios
sudo apt update

# Para Ubuntu 22.04 (instalar Python 3.11)
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev

# Para Ubuntu 24.04 (Python 3.12 por defecto)
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verificar instalación
python3.11 --version || python3 --version
```

## 🔧 Configuración del Entorno Virtual

### 1. Crear Entorno Virtual

```bash
# Navegar al directorio del proyecto
cd benchmark-SO

# Crear entorno virtual
python3 -m venv benchmark-env
# En sistemas con Python 3.11 específico:
# python3.11 -m venv benchmark-env

# Verificar que se creó
ls -la benchmark-env/
```

### 2. Activar Entorno Virtual

```bash
# Activar entorno (Linux/Mac)
source benchmark-env/bin/activate

# Verificar activación (debe mostrar el nombre del entorno)
which python
python --version
```

### 3. Actualizar pip

```bash
# Asegurar pip actualizado
pip install --upgrade pip

# Verificar versión
pip --version  # Debe ser 23.0+ o superior
```

## 📦 Instalación de Dependencias

### 1. Instalar Dependencias Principales

```bash
# Instalar desde requirements.txt
pip install -r requirements.txt

# Si tienes problemas, instalar una por una:
pip install pandas>=1.5.0
pip install matplotlib>=3.6.0
pip install seaborn>=0.12.0
pip install requests>=2.28.0
pip install numpy>=1.24.0
```

### 2. Verificar Instalación

```bash
# Verificar que las librerías se instalaron correctamente
python -c "
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import numpy as np
print('✅ Todas las dependencias instaladas correctamente')
print(f'Pandas: {pd.__version__}')
print(f'Matplotlib: {plt.matplotlib.__version__}')
print(f'Seaborn: {sns.__version__}')
print(f'Requests: {requests.__version__}')
print(f'NumPy: {np.__version__}')
"
```

### 3. Dependencias Opcionales (Para análisis avanzado)

```bash
# Para gráficos mejorados
pip install plotly>=5.0.0

# Para manejo de archivos Excel
pip install openpyxl>=3.0.0

# Para análisis estadístico avanzado
pip install scipy>=1.10.0
```

## 🧪 Probar el Análisis

```bash
# Asegurar que el entorno esté activado
source benchmark-env/bin/activate

# Crear logs de prueba (si no tienes)
mkdir -p .logs/daily .logs/performance .logs/errors

# Ejecutar análisis de prueba
python analyze_logs.py --help

# Si tienes logs existentes
python analyze_logs.py --days 7 --format all

# Prueba simple
python -c "
from analyze_logs import LogAnalyzer
print('✅ LogAnalyzer importado correctamente')
"
```

## 🔄 Uso Diario

### Activar Entorno
```bash
# Siempre activar antes de usar
cd benchmark-SO
source benchmark-env/bin/activate
```

### Ejecutar Análisis
```bash
# Análisis básico
python analyze_logs.py --days 7

# Análisis con reporte JSON
python analyze_logs.py --days 14 --format json --output reporte_$(date +%Y%m%d).json

# Análisis con gráficos
python analyze_logs.py --days 7 --format markdown --output reporte.md
```

### Desactivar Entorno
```bash
# Al terminar
deactivate
```

## 🚨 Solución de Problemas

### Error: "python3: command not found"
```bash
# Verificar instalación de Python
which python3
sudo apt install python3  # Debian/Ubuntu
sudo pacman -S python     # Arch
```

### Error: "pip: command not found"
```bash
# Instalar pip
sudo apt install python3-pip      # Debian/Ubuntu
sudo pacman -S python-pip         # Arch
```

### Error: "No module named 'pandas'"
```bash
# Verificar que el entorno esté activado
source benchmark-env/bin/activate

# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt
```

### Error: "Permission denied"
```bash
# NO usar sudo con pip en entorno virtual
# Si tienes problemas, recrear entorno:
rm -rf benchmark-env
python3 -m venv benchmark-env
source benchmark-env/bin/activate
pip install -r requirements.txt
```

### Error en matplotlib (GUI)
```bash
# Instalar dependencias para gráficos
sudo apt install python3-tk        # Debian/Ubuntu
sudo pacman -S tk                   # Arch

# O usar backend sin GUI
export MPLBACKEND=Agg
python analyze_logs.py --days 7
```

## 📊 Comandos de Análisis Completos

```bash
# Activar entorno
source benchmark-env/bin/activate

# Análisis básico últimos 7 días
python analyze_logs.py --days 7

# Análisis detallado con gráficos
python analyze_logs.py --days 14 --format all --output analysis_report

# Limpieza de logs antiguos (simulación)
python analyze_logs.py --clean --dry-run --days 30

# Análisis por sistema operativo (si tienes logs separados)
python analyze_logs.py --days 30 --format csv --output os_comparison.csv

# Generar reporte mensual
python analyze_logs.py --days 30 --format markdown --output monthly_$(date +%Y%m).md
```

## 🔄 Automatización con Cron

### Crear script de análisis diario
```bash
# Crear script
cat > daily_analysis.sh << 'EOF'
#!/bin/bash
cd /path/to/benchmark-SO
source benchmark-env/bin/activate
python analyze_logs.py --days 7 --format json --output daily_analysis_$(date +%Y%m%d).json
deactivate
EOF

chmod +x daily_analysis.sh
```

### Agregar a crontab
```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar todos los días a las 23:00
0 23 * * * /path/to/benchmark-SO/daily_analysis.sh
```

## 📝 Notas Importantes

1. **Siempre activar el entorno virtual** antes de ejecutar scripts
2. **No usar sudo** dentro del entorno virtual
3. **Verificar versiones** de Python y dependencias regularmente
4. **Respaldar el entorno** si funciona correctamente
5. **Usar Docker** si tienes problemas con dependencias

## 🆘 Soporte

Si tienes problemas:

1. **Verifica versiones:** `python --version`, `pip --version`
2. **Revisa logs:** Errores durante instalación
3. **Recrea entorno:** `rm -rf benchmark-env` y empezar de nuevo
4. **Usa Docker:** Alternativa sin configuración local

---

**💡 Tip:** Si esto es muy complicado, simplemente usa Docker:
```bash
docker compose run --rm benchmark python analyze_logs.py --days 7
```

¡Es más simple y no requiere instalación local! 🐳