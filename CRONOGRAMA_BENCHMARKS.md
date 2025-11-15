# 📊 Cronograma de Benchmarks - 4 Semanas

Este documento te ayuda a llevar un registro manual de las ejecuciones de benchmark durante 4 semanas en diferentes sistemas operativos.

## 🗓️ Calendario de Ejecución

### ✅ Lista de Verificación por Sistema

#### 🟦 Debian 12
- [ ] **Lunes Semana 1** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 1** - Fecha: ___/___/2024  
- [ ] **Viernes Semana 1** - Fecha: ___/___/2024
- [ ] **Lunes Semana 2** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 2** - Fecha: ___/___/2024
- [ ] **Viernes Semana 2** - Fecha: ___/___/2024
- [ ] **Lunes Semana 3** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 3** - Fecha: ___/___/2024
- [ ] **Viernes Semana 3** - Fecha: ___/___/2024
- [ ] **Lunes Semana 4** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 4** - Fecha: ___/___/2024
- [ ] **Viernes Semana 4** - Fecha: ___/___/2024

#### 🔵 Arch Linux
- [ ] **Lunes Semana 1** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 1** - Fecha: ___/___/2024  
- [ ] **Viernes Semana 1** - Fecha: ___/___/2024
- [ ] **Lunes Semana 2** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 2** - Fecha: ___/___/2024
- [ ] **Viernes Semana 2** - Fecha: ___/___/2024
- [ ] **Lunes Semana 3** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 3** - Fecha: ___/___/2024
- [ ] **Viernes Semana 3** - Fecha: ___/___/2024
- [ ] **Lunes Semana 4** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 4** - Fecha: ___/___/2024
- [ ] **Viernes Semana 4** - Fecha: ___/___/2024

#### 🟠 Kubuntu 22.04/24.04
- [ ] **Lunes Semana 1** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 1** - Fecha: ___/___/2024  
- [ ] **Viernes Semana 1** - Fecha: ___/___/2024
- [ ] **Lunes Semana 2** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 2** - Fecha: ___/___/2024
- [ ] **Viernes Semana 2** - Fecha: ___/___/2024
- [ ] **Lunes Semana 3** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 3** - Fecha: ___/___/2024
- [ ] **Viernes Semana 3** - Fecha: ___/___/2024
- [ ] **Lunes Semana 4** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 4** - Fecha: ___/___/2024
- [ ] **Viernes Semana 4** - Fecha: ___/___/2024

#### 🟡 Ubuntu 22.04/24.04 LTS
- [ ] **Lunes Semana 1** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 1** - Fecha: ___/___/2024  
- [ ] **Viernes Semana 1** - Fecha: ___/___/2024
- [ ] **Lunes Semana 2** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 2** - Fecha: ___/___/2024
- [ ] **Viernes Semana 2** - Fecha: ___/___/2024
- [ ] **Lunes Semana 3** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 3** - Fecha: ___/___/2024
- [ ] **Viernes Semana 3** - Fecha: ___/___/2024
- [ ] **Lunes Semana 4** - Fecha: ___/___/2024
- [ ] **Miércoles Semana 4** - Fecha: ___/___/2024
- [ ] **Viernes Semana 4** - Fecha: ___/___/2024

## 📋 Comandos de Ejecución

### Comando Principal
```bash
./daily_benchmark.sh
```

### Comandos Alternativos
```bash
# Con limpieza previa
./daily_benchmark.sh --clean

# Con limpieza profunda
./daily_benchmark.sh --deep-clean

# Solo información del sistema
./daily_benchmark.sh --info-only

# Modo verbose
./daily_benchmark.sh --verbose
```

### Con Docker Compose Directo
```bash
# Ejecución estándar
docker compose up --build

# En background
docker compose up -d --build

# Ver logs
docker compose logs -f benchmark
```

## 📊 Plantilla de Registro Diario

### Información a Registrar por Ejecución

**Fecha:** ___/___/2024  
**Sistema Operativo:** ________________  
**Hora de Inicio:** __:__  
**Hora de Fin:** __:__  

#### ✅ Estado de Ejecución
- [ ] Benchmark completado exitosamente
- [ ] Errores durante la ejecución
- [ ] Logs generados correctamente

#### 📈 Métricas Clave (completar después del análisis)
- **RPS Promedio:** ______
- **Latencia P95:** ______ ms
- **Error Rate:** ______%
- **CPU Usage:** ______%
- **Memoria Used:** ______ MB

#### 📁 Archivos Generados
- [ ] `.logs/daily/YYYY-MM-DD.log`
- [ ] `.logs/performance/YYYY-MM-DD_performance.log`
- [ ] `benchmark_results/benchmark_YYYYMMDD_HHMMSS.csv`
- [ ] `resultados_nuevos/benchmark_detailed_YYYYMMDD_HHMMSS.json`

#### 🔍 Observaciones
```
_________________________________________________________
_________________________________________________________
_________________________________________________________
```

## 📈 Análisis Semanal

### Semana 1 (___/___/2024 - ___/___/2024)
- **Ejecuciones completadas:** ___/12 (3 por sistema × 4 sistemas)
- **Sistemas más estables:** _________________
- **Problemas encontrados:** _________________

### Semana 2 (___/___/2024 - ___/___/2024)
- **Ejecuciones completadas:** ___/12
- **Sistemas más estables:** _________________
- **Problemas encontrados:** _________________

### Semana 3 (___/___/2024 - ___/___/2024)
- **Ejecuciones completadas:** ___/12
- **Sistemas más estables:** _________________
- **Problemas encontrados:** _________________

### Semana 4 (___/___/2024 - ___/___/2024)
- **Ejecuciones completadas:** ___/12
- **Sistemas más estables:** _________________
- **Problemas encontrados:** _________________

## 🔧 Comandos de Análisis

### Análisis de Logs
```bash
# Análisis semanal
python analyze_logs.py --days 7 --format all

# Análisis completo del mes
python analyze_logs.py --days 30 --format json --output monthly_report.json

# Generar gráficos
python analyze_logs.py --days 14 --format markdown --output weekly_report.md
```

### Limpieza de Logs
```bash
# Ver qué se eliminaría (simulación)
python analyze_logs.py --clean --dry-run --days 7

# Limpiar logs antiguos
python analyze_logs.py --clean --days 30
```

## 📊 Resumen Final

### Total de Ejecuciones Esperadas: 48
- **Debian:** 12 ejecuciones
- **Arch:** 12 ejecuciones  
- **Kubuntu:** 12 ejecuciones
- **Ubuntu:** 12 ejecuciones

### Métricas de Éxito
- [ ] **≥90%** de ejecuciones completadas (≥43/48)
- [ ] **<5%** tasa de errores promedio
- [ ] **Logs completos** para todas las ejecuciones
- [ ] **Análisis comparativo** entre sistemas

### 📋 Checklist Final
- [ ] Todos los logs respaldados
- [ ] Análisis comparativo generado
- [ ] Gráficos de rendimiento creados
- [ ] Reporte final documentado
- [ ] Datos exportados para análisis adicional

## 🚨 Solución de Problemas Comunes

### Docker no inicia
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

### Sin espacio en disco
```bash
docker system prune -a
du -sh .logs/
python analyze_logs.py --clean --days 7
```

### Falla el benchmark
```bash
# Ver logs de error
tail -f .logs/errors/$(date +%Y-%m-%d)_errors.log

# Reiniciar contenedores
docker compose down
docker compose up --build
```

---

## 📞 Información de Contacto

**Proyecto:** FastAPI Benchmark Multi-plataforma  
**Documentación:** README_DOCKER_MULTIPLATFORM.md  
**Scripts:** daily_benchmark.sh, docker-compose.yml  
**Análisis:** analyze_logs.py  

¡Buena suerte con tus benchmarks! 🚀