# Sistema Automatizado de Benchmarks con Docker 🐳

Sistema automatizado para ejecutar benchmarks de FastAPI con logging completo, programado para ejecutarse 2 veces al día.

## 📋 Descripción

Este sistema utiliza Docker para:
- **FastAPI**: Servidor de pruebas corriendo 24/7
- **Benchmark Scheduler**: Ejecuta benchmarks automáticamente a las 9:00 AM y 9:00 PM
- **Log Manager**: Analiza logs y genera reportes (ejecución manual)

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Network                         │
│                                                         │
│  ┌──────────────┐      ┌─────────────────────┐        │
│  │  FastAPI     │◄─────┤ Benchmark Scheduler │        │
│  │  Container   │      │  (cron: 9AM, 9PM)   │        │
│  │  Port: 8000  │      │                     │        │
│  └──────────────┘      └─────────────────────┘        │
│         │                        │                     │
│         │                        │                     │
│         ▼                        ▼                     │
│  ┌─────────────────────────────────────┐              │
│  │      Volúmenes Compartidos          │              │
│  │  - .logs/                           │              │
│  │  - benchmark_results/               │              │
│  │  - resultados_diarios/              │              │
│  └─────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Inicio Rápido

### Windows (PowerShell)

```powershell
# Iniciar sistema completo
.\control_automatico.ps1 -Action start

# Ver estado
.\control_automatico.ps1 -Action status

# Ver logs en tiempo real
.\control_automatico.ps1 -Action logs
```

### Linux/Mac

```bash
# Dar permisos de ejecución
chmod +x control_automatico.sh

# Iniciar sistema completo
./control_automatico.sh start

# Ver estado
./control_automatico.sh status

# Ver logs en tiempo real
./control_automatico.sh logs
```

## 📝 Comandos Disponibles

### Windows PowerShell

| Comando | Descripción |
|---------|-------------|
| `.\control_automatico.ps1 -Action start` | Inicia todo el sistema |
| `.\control_automatico.ps1 -Action stop` | Detiene todo el sistema |
| `.\control_automatico.ps1 -Action restart` | Reinicia los servicios |
| `.\control_automatico.ps1 -Action status` | Muestra estado y recursos |
| `.\control_automatico.ps1 -Action logs` | Logs en tiempo real |
| `.\control_automatico.ps1 -Action benchmark-manual` | Ejecuta benchmark manualmente |
| `.\control_automatico.ps1 -Action analyze-logs` | Analiza logs y genera reportes |
| `.\control_automatico.ps1 -Action build` | Reconstruye imágenes Docker |

### Linux/Mac

```bash
./control_automatico.sh start              # Inicia sistema
./control_automatico.sh stop               # Detiene sistema
./control_automatico.sh restart            # Reinicia servicios
./control_automatico.sh status             # Estado y recursos
./control_automatico.sh logs               # Logs en tiempo real
./control_automatico.sh benchmark-manual   # Benchmark manual
./control_automatico.sh analyze-logs       # Analiza logs
./control_automatico.sh build              # Reconstruye imágenes
```

## ⏰ Programación Automática

Los benchmarks se ejecutan automáticamente:
- **9:00 AM** - Benchmark matutino
- **9:00 PM** - Benchmark nocturno
- **Domingos 11:00 PM** - Análisis semanal de logs

### Modificar Horarios

Edita el archivo `scripts/crontab`:

```cron
# Formato: minuto hora día mes día_semana comando
0 9 * * * cd /app && python benchmark_python.py
0 21 * * * cd /app && python benchmark_python.py
```

Después de modificar, reconstruye:
```bash
./control_automatico.sh build
./control_automatico.sh restart
```

## 📊 Ejecución Manual

### Ejecutar Benchmark Inmediatamente

```bash
# Windows
.\control_automatico.ps1 -Action benchmark-manual

# Linux/Mac
./control_automatico.sh benchmark-manual
```

### Analizar Logs

```bash
# Windows
.\control_automatico.ps1 -Action analyze-logs

# Linux/Mac
./control_automatico.sh analyze-logs
```

### Comandos Docker Directos

```bash
# Ejecutar benchmark con configuración personalizada
docker compose -f docker-compose.automatico.yml run --rm benchmark-scheduler \
    python benchmark_python.py --duration 60 --concurrency 100

# Analizar logs de últimos 14 días
docker compose -f docker-compose.automatico.yml --profile tools run --rm log-manager \
    python analyze_logs.py --days 14 --format markdown
```

## 📁 Estructura de Archivos

```
ProyectosP/
├── SistemasOperativos/              # Proyecto principal
│   ├── docker-compose.automatico.yml
│   ├── Dockerfile.benchmark
│   ├── control_automatico.ps1
│   ├── control_automatico.sh
│   ├── app/
│   ├── scripts/
│   │   └── crontab
│   ├── benchmark_python.py
│   ├── logging_manager.py
│   └── analyze_logs.py
├── benchmark-logs/                  # Logs (fuera del proyecto)
│   ├── daily/
│   ├── errors/
│   ├── performance/
│   └── archive/
└── benchmark-results/               # Resultados (fuera del proyecto)
    ├── benchmark_results/
    ├── resultados_diarios/
    └── resultados_nuevos/
```

## 🔍 Monitoreo

### Ver Estado de Contenedores

```bash
# Windows
.\control_automatico.ps1 -Action status

# Linux/Mac
./control_automatico.sh status

# Docker directo
docker compose -f docker-compose.automatico.yml ps
```

### Ver Logs en Tiempo Real

```bash
# Todos los servicios
docker compose -f docker-compose.automatico.yml logs -f

# Solo FastAPI
docker compose -f docker-compose.automatico.yml logs -f fastapi-app

# Solo Benchmark Scheduler
docker compose -f docker-compose.automatico.yml logs -f benchmark-scheduler
```

### Uso de Recursos

```bash
# Estadísticas en tiempo real
docker stats

# Estadísticas específicas
docker stats fastapi-app benchmark-scheduler
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Edita `docker-compose.automatico.yml`:

```yaml
environment:
  - LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
  - TZ=America/Mexico_City  # Zona horaria
  - TARGET_URL=http://fastapi-app:8000
```

### Límites de Recursos

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Máximo 2 CPUs
      memory: 2G       # Máximo 2GB RAM
    reservations:
      cpus: '0.5'      # Mínimo 0.5 CPU
      memory: 512M     # Mínimo 512MB RAM
```

### Persistencia de Datos

Los volúmenes están mapeados fuera del proyecto:
- `../benchmark-logs/` → Logs persistentes (fuera del repositorio)
- `../benchmark-results/` → Resultados persistentes (fuera del repositorio)

**Ventajas:**
- No contamina el repositorio Git
- Fácil backup independiente
- Mejor organización de datos

## 🐛 Troubleshooting

### Contenedor no inicia

```bash
# Ver logs de error
docker compose -f docker-compose.automatico.yml logs

# Verificar estado
docker compose -f docker-compose.automatico.yml ps -a

# Reconstruir imágenes
docker compose -f docker-compose.automatico.yml build --no-cache
```

### Benchmarks no se ejecutan

```bash
# Verificar cron dentro del contenedor
docker exec -it benchmark-scheduler crontab -l

# Ver logs de cron
docker exec -it benchmark-scheduler cat /var/log/cron.log

# Ejecutar manualmente para debug
docker compose -f docker-compose.automatico.yml run --rm benchmark-scheduler \
    python benchmark_python.py
```

### Puerto 8000 ocupado

```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Cambiar puerto en docker-compose.automatico.yml
ports:
  - "8080:8000"  # Usar puerto 8080 en host
```

### Limpiar todo y empezar de nuevo

```bash
# Detener y eliminar contenedores
docker compose -f docker-compose.automatico.yml down -v

# Eliminar imágenes
docker rmi $(docker images -q 'sistemasoperativos*')

# Limpiar volúmenes
docker volume prune

# Reiniciar
./control_automatico.sh start
```

## 📈 Análisis de Resultados

### Ubicación de Resultados

- **Logs**: `../benchmark-logs/daily/` (fuera del proyecto)
- **Benchmarks**: `../benchmark-results/` (fuera del proyecto)
- **Análisis**: Generados por `analyze_logs.py`

Los resultados se guardan fuera del proyecto para mantener el repositorio limpio.

### Generar Reportes

```bash
# Reporte semanal
docker compose -f docker-compose.automatico.yml --profile tools run --rm log-manager \
    python analyze_logs.py --days 7 --format markdown --output reporte_semanal.md

# Reporte mensual en JSON
docker compose -f docker-compose.automatico.yml --profile tools run --rm log-manager \
    python analyze_logs.py --days 30 --format json --output reporte_mensual.json
```

## 🔐 Seguridad

- Contenedores ejecutan como usuario no-root (`benchuser`)
- Límites de recursos configurados
- Logs rotan automáticamente (max 10MB, 5 archivos)
- Red Docker aislada

## 🚦 Deployment en VPS

### Preparar VPS

```bash
# Conectar por SSH
ssh root@TU_VPS_IP

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Clonar repositorio
git clone https://github.com/IrvinngB/benchmark-SO.git
cd SistemasOperativos
git checkout automatico
```

### Iniciar en VPS

```bash
# Construir e iniciar
./control_automatico.sh start

# Verificar
./control_automatico.sh status

# Configurar firewall
sudo ufw allow 8000/tcp
sudo ufw enable
```

### Monitoreo Remoto

```bash
# Ver logs remotos
ssh root@TU_VPS_IP "cd SistemasOperativos && docker compose -f docker-compose.automatico.yml logs -f"

# Ver estado remoto
ssh root@TU_VPS_IP "cd SistemasOperativos && docker stats --no-stream"
```

## 📚 Recursos Adicionales

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Cron Syntax](https://crontab.guru/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Soporte

Si algo falla:
1. Revisa logs: `./control_automatico.sh logs`
2. Verifica estado: `./control_automatico.sh status`
3. Ejecuta manual: `./control_automatico.sh benchmark-manual`
4. Reconstruye: `./control_automatico.sh build`

---

**Sistema Automatizado de Benchmarks - 2025** 🚀
