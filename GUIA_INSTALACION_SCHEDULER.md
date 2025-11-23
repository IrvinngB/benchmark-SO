# Guía de Instalación - Sistema de Benchmarking Automático

## 📋 Descripción

Sistema automatizado para ejecutar benchmarks contra tres servidores remotos diariamente a las **11:00 AM** y **11:00 PM**.

### Servidores Configurados
- **Server 1:** 143.110.201.94
- **Server 2:** 104.248.217.252
- **Server 3:** 206.189.215.59

---

## 🚀 Instalación Rápida

### Paso 1: Verificar Dependencias

Asegúrate de tener Python 3.8+ instalado:

```bash
python --version
```

### Paso 2: Instalar Dependencias de Python

```bash
pip install -r requirements.txt
```

### Paso 3: Configurar el Scheduler

#### En Windows (PowerShell como Administrador):

```powershell
.\setup_scheduler_windows.ps1
```

#### En Linux/macOS:

```bash
chmod +x setup_scheduler_linux.sh
./setup_scheduler_linux.sh
```

---

## ⚙️ Configuración

### Archivo de Configuración

El archivo `benchmark_config_servers.json` contiene la configuración completa:

```json
{
  "num_tests": 10,
  "default_requests": 500,
  "default_connections": 100,
  "timeout": 60,
  "results_dir": "resultados_automaticos",
  "servers": {
    "server_1": "143.110.201.94:8000",
    "server_2": "104.248.217.252:8000",
    "server_3": "206.189.215.59:8000"
  },
  "environments": [
    {
      "name": "server_1",
      "label": "Server 1 (143.110.201.94)",
      "ip": "143.110.201.94"
    },
    ...
  ],
  "endpoints": [
    {
      "name": "Root Endpoint (Baseline)",
      "path": "/",
      "requests": 500
    },
    ...
  ]
}
```

### Personalizar Configuración

Puedes modificar:
- **num_tests**: Número de pruebas por servidor
- **default_requests**: Requests por endpoint
- **timeout**: Timeout en segundos
- **endpoints**: Agregar o modificar endpoints a probar

---

## 📅 Horarios de Ejecución

El sistema está configurado para ejecutarse automáticamente:

- **11:00 AM** - Todos los días
- **11:00 PM** - Todos los días

### Modificar Horarios

#### Windows:
Edita las tareas en Task Scheduler o modifica el script `setup_scheduler_windows.ps1` y vuelve a ejecutarlo.

#### Linux/macOS:
Edita el crontab:
```bash
crontab -e
```

---

## 🧪 Prueba Manual

Para ejecutar un benchmark manualmente:

```bash
python scheduled_benchmark.py
```

Con configuración personalizada:
```bash
python scheduled_benchmark.py --config mi_config.json
```

---

## 📊 Resultados

### Ubicación de Resultados

```
resultados_automaticos/
├── benchmark_detailed_YYYYMMDD_HHMMSS.csv
├── benchmark_detailed_YYYYMMDD_HHMMSS.json
├── benchmark_analysis_YYYYMMDD_HHMMSS.xlsx
├── benchmark_report_YYYYMMDD_HHMMSS.md
└── visualizations_YYYYMMDD_HHMMSS/
    ├── rps_distribution.png
    ├── latency_distribution.png
    ├── resource_analysis.png
    ├── correlation_matrix.png
    └── performance_timeline.png
```

### Logs

Los logs se guardan en:

```
logs/
├── benchmark/       # Logs generales de ejecución
├── errors/          # Logs de errores
├── requests/        # Logs de requests HTTP
├── system/          # Logs de recursos del sistema
└── connectivity/    # Logs de pruebas de conectividad
```

Ver logs en tiempo real:
```bash
# Windows (PowerShell)
Get-Content -Path "logs\benchmark\benchmark_$(Get-Date -Format 'yyyy-MM-dd').log" -Wait

# Linux/macOS
tail -f logs/benchmark/benchmark_$(date +%Y-%m-%d).log
```

---

## 🔧 Comandos Útiles

### Windows

```powershell
# Ver tareas programadas
Get-ScheduledTask | Where-Object {$_.TaskName -like 'BenchmarkServers*'}

# Ejecutar tarea ahora
Start-ScheduledTask -TaskName "BenchmarkServers_11AM"

# Desactivar tareas
Disable-ScheduledTask -TaskName "BenchmarkServers_11AM"
Disable-ScheduledTask -TaskName "BenchmarkServers_11PM"

# Desinstalar completamente
.\setup_scheduler_windows.ps1 -Uninstall
```

### Linux/macOS

```bash
# Ver tareas programadas
crontab -l

# Editar tareas
crontab -e

# Ver logs de cron
tail -f .logs_scheduled/cron_output.log

# Desinstalar
./setup_scheduler_linux.sh --uninstall
```

---

## 🐛 Solución de Problemas

### El benchmark no se ejecuta automáticamente

**Windows:**
1. Verifica que las tareas estén habilitadas en Task Scheduler
2. Revisa los logs en: `C:\Windows\System32\Tasks\`
3. Asegúrate de que Python esté en el PATH

**Linux/macOS:**
1. Verifica que cron esté corriendo: `systemctl status cron` o `service cron status`
2. Revisa los logs: `tail -f .logs_scheduled/cron_output.log`
3. Verifica permisos del script: `chmod +x scheduled_benchmark.py`

### Errores de conectividad

1. Verifica que los servidores estén accesibles:
   ```bash
   curl http://143.110.201.94:8000/health
   curl http://104.248.217.252:8000/health
   curl http://206.189.215.59:8000/health
   ```

2. Revisa los logs de conectividad:
   ```bash
   cat logs/connectivity/connectivity_$(date +%Y-%m-%d).log
   ```

### Errores de permisos

**Windows:**
- Ejecuta PowerShell como Administrador

**Linux/macOS:**
- Asegúrate de tener permisos de escritura en el directorio del proyecto
- Verifica permisos de cron: `ls -la /var/spool/cron/crontabs/`

---

## 📈 Monitoreo

### Verificar Última Ejecución

**Windows:**
```powershell
Get-ScheduledTaskInfo -TaskName "BenchmarkServers_11AM" | Select-Object LastRunTime, LastTaskResult
```

**Linux/macOS:**
```bash
ls -lt resultados_automaticos/ | head -n 5
```

### Estadísticas de Ejecución

Revisa el archivo de resumen más reciente:
```bash
# Encuentra el último reporte
ls -t resultados_automaticos/benchmark_report_*.md | head -n 1

# Léelo
cat $(ls -t resultados_automaticos/benchmark_report_*.md | head -n 1)
```

---

## 🔄 Actualización de Configuración

Para actualizar la configuración sin detener el sistema:

1. Edita `benchmark_config_servers.json`
2. Los cambios se aplicarán en la próxima ejecución automática
3. No es necesario reiniciar las tareas programadas

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs en `logs/errors/`
2. Ejecuta manualmente para ver errores: `python scheduled_benchmark.py`
3. Verifica la configuración en `benchmark_config_servers.json`

---

## 🎯 Próximos Pasos

Después de la instalación:

1. ✅ Espera la primera ejecución automática (11:00 AM o 11:00 PM)
2. ✅ Revisa los resultados en `resultados_automaticos/`
3. ✅ Monitorea los logs en `logs/`
4. ✅ Ajusta la configuración según sea necesario

---

**Versión:** 1.0  
**Última actualización:** 2025-11-21
