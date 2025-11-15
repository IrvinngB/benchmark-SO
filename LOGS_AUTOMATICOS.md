# 📁 Sistema de Creación Automática de Logs

## ✅ **¿Se Crean las Carpetas Automáticamente?**

**SÍ - TODO ES AUTOMÁTICO** 🤖

### **Al ejecutar cualquier benchmark:**
```bash
# Cualquiera de estos comandos crea automáticamente toda la estructura:
python benchmark_python.py
./daily_benchmark.sh
docker compose up benchmark
```

### **Estructura que se crea automáticamente:**
```
.logs/                           # ✅ Se crea automáticamente
├── daily/                       # ✅ Se crea automáticamente
│   ├── 2025-11-15.log          # ✅ Fecha actual automática
│   ├── 2025-11-16.log          # ✅ Rotación diaria automática
│   └── execution_2025-11-15_14-30-25.log  # ✅ Con hora exacta
├── errors/                      # ✅ Se crea automáticamente
│   ├── 2025-11-15_errors.log   # ✅ Solo si hay errores
│   └── 2025-11-16_errors.log   # ✅ Rotación diaria
├── performance/                 # ✅ Se crea automáticamente
│   ├── 2025-11-15_performance.log      # ✅ Métricas
│   ├── 2025-11-15_connectivity.log     # ✅ Tests de conexión
│   └── 2025-11-16_performance.log      # ✅ Día siguiente
├── archive/                     # ✅ Se crea automáticamente
│   ├── 2025-11-08.log.gz       # ✅ Logs antiguos comprimidos
│   └── 2025-11-07_performance.log.gz   # ✅ Archivos > 7 días
└── README.md                    # ✅ Documentación automática
```

## 🕐 **Sistema de Fechas y Horas:**

### **Formatos de Nombres de Archivo:**
```bash
# Logs diarios (rotación automática a medianoche)
2025-11-15.log                   # Formato: YYYY-MM-DD

# Logs con timestamp específico
execution_2025-11-15_14-30-25.log   # Formato: YYYY-MM-DD_HH-MM-SS

# Logs por categoría con fecha
2025-11-15_errors.log            # Solo errores del día
2025-11-15_performance.log       # Solo métricas del día
2025-11-15_connectivity.log      # Solo tests de conexión
```

### **Contenido con Timestamps:**
```bash
# Cada línea de log incluye timestamp completo:
[2025-11-15 14:30:25,123] INFO - Iniciando benchmark FastAPI
[2025-11-15 14:30:26,456] INFO - Conectividad verificada: localhost:8000
[2025-11-15 14:30:27,789] INFO - Test 1/10: Root Endpoint
[2025-11-15 14:30:45,321] INFO - RPS: 1234.56, Latencia: 25.67ms
```

## 🤖 **Código que Hace la Magia:**

### **En `logging_manager.py`:**
```python
# Línea 151 - Crea TODAS las carpetas automáticamente
for dir_path in [self.daily_dir, self.error_dir, self.performance_dir, self.archive_dir]:
    dir_path.mkdir(parents=True, exist_ok=True)
    
# Línea 41 - Crea carpetas padre si no existen
self.log_dir.mkdir(parents=True, exist_ok=True)
```

### **En `daily_benchmark.sh`:**
```bash
# Línea 12 - Crea directorio de logs si no existe
mkdir -p "$LOG_DIR"

# Genera nombres con timestamp completo
DATE=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE=".logs/daily/execution_${DATE}.log"
```

## 📝 **Ejemplos Prácticos:**

### **Primera Ejecución (Carpetas No Existen):**
```bash
# Estado inicial: NO hay carpeta .logs
ls -la .logs
# ls: cannot access '.logs': No such file or directory

# Ejecutar benchmark
python benchmark_python.py

# Estado después: TODO creado automáticamente
ls -la .logs/
# drwxr-xr-x daily/
# drwxr-xr-x errors/
# drwxr-xr-x performance/
# drwxr-xr-x archive/
# -rw-r--r-- README.md

ls -la .logs/daily/
# -rw-r--r-- 2025-11-15.log
```

### **Múltiples Ejecuciones (Mismo Día):**
```bash
# Ejecución 1 (10:00 AM)
./daily_benchmark.sh
# Crea: .logs/daily/execution_2025-11-15_10-00-15.log

# Ejecución 2 (2:30 PM)  
./daily_benchmark.sh
# Crea: .logs/daily/execution_2025-11-15_14-30-22.log

# Ejecución 3 (8:45 PM)
./daily_benchmark.sh  
# Crea: .logs/daily/execution_2025-11-15_20-45-33.log
```

### **Rotación Automática (Días Diferentes):**
```bash
# Día 1 (15 Nov)
python benchmark_python.py
# Crea: .logs/daily/2025-11-15.log

# Día 2 (16 Nov) - Nuevo archivo automáticamente
python benchmark_python.py  
# Crea: .logs/daily/2025-11-16.log

# Día 8 (22 Nov) - Archiva automáticamente logs > 7 días
python benchmark_python.py
# Crea: .logs/daily/2025-11-22.log
# Mueve: .logs/archive/2025-11-15.log.gz (comprimido)
```

## 🔧 **Personalización de Ubicación:**

### **Cambiar Directorio de Logs:**
```bash
# Opción 1: Argumento en CLI
python benchmark_python.py --log-dir /mi/carpeta/logs

# Opción 2: Variable de entorno
export LOG_DIR="/mi/carpeta/logs"
python benchmark_python.py

# Opción 3: En daily_benchmark.sh
LOG_DIR="/mi/carpeta/personalizada"
```

### **En Docker:**
```yaml
# docker-compose.yml - logs persistentes
volumes:
  - ./mi-carpeta-logs:/app/.logs  # Tu carpeta personalizada
```

## 🚨 **Verificación y Solución de Problemas:**

### **Verificar que Todo se Creó:**
```bash
# Verificar estructura completa
find .logs -type d -exec ls -la {} \;

# Verificar permisos
ls -la .logs/
# drwxr-xr-x = permisos correctos

# Ver contenido de un log
tail -f .logs/daily/2025-11-15.log
```

### **Si NO se Crean las Carpetas:**
```bash
# Problema 1: Permisos
chmod 755 .
chmod +x daily_benchmark.sh

# Problema 2: Espacio en disco
df -h .  # Verificar espacio disponible

# Problema 3: Crear manualmente (último recurso)
mkdir -p .logs/{daily,errors,performance,archive}
```

### **Si los Timestamps No Aparecen:**
```bash
# Verificar zona horaria del sistema
date
timedatectl  # En sistemas Linux

# En Docker verificar TZ
docker compose exec benchmark date
```

## 📊 **Resumen Visual del Proceso:**

```
1. 🚀 Ejecutas: python benchmark_python.py
   ↓
2. 📁 LogManager detecta que no existe .logs/
   ↓
3. 🤖 Crea automáticamente:
   ├── .logs/daily/
   ├── .logs/errors/
   ├── .logs/performance/
   └── .logs/archive/
   ↓
4. ⏰ Genera archivo con fecha actual:
   📄 .logs/daily/2025-11-15.log
   ↓
5. 📝 Escribe logs con timestamp completo:
   [2025-11-15 14:30:25] INFO - Mensaje...
   ↓
6. 🔄 Al día siguiente, crea nuevo archivo automáticamente
   📄 .logs/daily/2025-11-16.log
```

## 💡 **Consejos Útiles:**

### **Para Ver Logs en Tiempo Real:**
```bash
# Ver log principal
tail -f .logs/daily/$(date +%Y-%m-%d).log

# Ver solo errores
tail -f .logs/errors/$(date +%Y-%m-%d)_errors.log

# Ver múltiples logs
tail -f .logs/daily/*.log .logs/performance/*.log
```

### **Para Análisis Histórico:**
```bash
# Buscar en logs de fechas específicas
grep "ERROR" .logs/daily/2025-11-15.log

# Analizar tendencias
grep "RPS:" .logs/performance/*.log | sort
```

---

## ✅ **Conclusión:**

**TODO ES AUTOMÁTICO** 🎉
- ✅ Carpetas se crean solas
- ✅ Archivos con fecha/hora automática  
- ✅ Rotación diaria automática
- ✅ Compresión de antiguos automática
- ✅ Solo ejecuta y funciona

**NO necesitas hacer NADA manualmente** para la gestión de logs! 🚀