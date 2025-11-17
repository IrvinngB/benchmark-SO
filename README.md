# FastAPI Performance Testing 🚀

Sistema **automatizado** de benchmarking para FastAPI con Docker, ejecución programada y logging completo.

## 📋 Descripción

Sistema que ejecuta benchmarks automáticamente 2 veces al día (9:00 AM y 9:00 PM):
- ✅ FastAPI corriendo 24/7 en contenedor
- ✅ Scheduler automático con cron
- ✅ Sistema de logging completo
- ✅ Análisis de resultados
- ✅ Logs y resultados fuera del repositorio (organización limpia)

## 🚀 Inicio Rápido

```bash
# Clonar y cambiar a rama automatico
git clone https://github.com/IrvinngB/benchmark-SO.git
cd SistemasOperativos
git checkout automatico

# Iniciar sistema (Windows)
.\control_automatico.ps1 -Action start

# Iniciar sistema (Linux/Mac)
./control_automatico.sh start
```

**¡Listo!** El sistema ahora:
- FastAPI en `http://localhost:8000`
- Benchmarks automáticos programados
- Logs en `../benchmark-logs/`
- Resultados en `../benchmark-results/`

Ver [INICIO_RAPIDO.md](INICIO_RAPIDO.md) para más detalles.

## 📖 Documentación

- **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - Guía de 3 pasos
- **[README_AUTOMATICO.md](README_AUTOMATICO.md)** - Documentación completa
  - Todos los comandos disponibles
  - Configuración avanzada
  - Troubleshooting
  - Deployment en VPS
  - Análisis de resultados

## 🏗️ Arquitectura

```
ProyectosP/
├── SistemasOperativos/              # Proyecto (Git)
│   ├── app/                         # FastAPI app
│   ├── scripts/                     # Scripts y cron
│   ├── docker-compose.automatico.yml
│   ├── Dockerfile.benchmark
│   ├── control_automatico.ps1       # Control Windows
│   ├── control_automatico.sh        # Control Linux/Mac
│   ├── benchmark_python.py
│   ├── logging_manager.py
│   └── analyze_logs.py
├── benchmark-logs/                  # Logs (fuera de Git)
│   ├── daily/
│   ├── errors/
│   ├── performance/
│   └── archive/
└── benchmark-results/               # Resultados (fuera de Git)
    ├── benchmark_results/
    ├── resultados_diarios/
    └── resultados_nuevos/
```

## 🎯 Comandos Principales

### Windows
```powershell
.\control_automatico.ps1 -Action start              # Iniciar
.\control_automatico.ps1 -Action stop               # Detener
.\control_automatico.ps1 -Action status             # Ver estado
.\control_automatico.ps1 -Action logs               # Ver logs
.\control_automatico.ps1 -Action benchmark-manual   # Ejecutar ahora
```

### Linux/Mac
```bash
./control_automatico.sh start              # Iniciar
./control_automatico.sh stop               # Detener
./control_automatico.sh status             # Ver estado
./control_automatico.sh logs               # Ver logs
./control_automatico.sh benchmark-manual   # Ejecutar ahora
```

## 🔌 Endpoints FastAPI

| Endpoint | Descripción |
|----------|-------------|
| `/` | Baseline ligero |
| `/health` | Health check |
| `/heavy` | Carga CPU intensiva |
| `/async-light` | I/O asíncrono |
| `/json-large` | JSON grande con paginación |

Documentación interactiva: `http://localhost:8000/docs`

## ⏰ Programación Automática

- **9:00 AM** - Benchmark matutino
- **9:00 PM** - Benchmark nocturno
- **Domingos 11:00 PM** - Análisis semanal

Modificar horarios en `scripts/crontab`

## 🐳 Deployment en VPS

```bash
# Conectar a VPS
ssh root@TU_VPS_IP

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clonar y ejecutar
git clone https://github.com/IrvinngB/benchmark-SO.git
cd SistemasOperativos
git checkout automatico
./control_automatico.sh start

# Configurar firewall
sudo ufw allow 8000/tcp
sudo ufw enable
```

## 📊 Características

- **Automatización completa**: Cron integrado en Docker
- **Logs organizados**: Fuera del repositorio Git
- **Ejecución manual**: Cuando lo necesites
- **Análisis de logs**: Reportes automáticos
- **Monitoreo**: Health checks y métricas
- **Seguridad**: Usuario no-root, límites de recursos
- **Persistencia**: Volúmenes Docker mapeados

## 🛠️ Requisitos

- Docker y Docker Compose
- Git
- Puertos: 8000 (FastAPI)

## 📚 Recursos

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Cron Syntax](https://crontab.guru/)

## 🤝 Contribuciones

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -m 'Agregar mejora'`)
4. Push (`git push origin feature/mejora`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - 2025

---

**Sistema Automatizado de Benchmarks** 🚀
