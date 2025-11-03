# 🚀 Configuración de Benchmarks Mejorada

## 📋 IPs de VPS Actualizadas

### VPS Sin Docker
- **IP**: `138.68.233.15`
- **Puerto**: `8000`
- **URL**: `http://138.68.233.15:8000`

### VPS Con Docker
- **IP**: `68.183.168.86`
- **Puerto**: `8000`
- **URL**: `http://68.183.168.86:8000`

---

## 🎯 Scripts Disponibles

### 1️⃣ Ejecutar Benchmarks (10 Runs)
```powershell
.\benchmark-improved.ps1
```

**Parámetros:**
```powershell
# Parámetro: Environment (local | vps_no_docker | vps_docker)
.\benchmark-improved.ps1 -Environment "vps_no_docker"
```

**Qué hace:**
- ✅ Ejecuta 10 pruebas por entorno
- ✅ 5 endpoints por prueba
- ✅ Total: 100 pruebas (10 × 5 endpoints × 2 entornos)
- ✅ Guarda resultados en `benchmark_results_improved/`
- ✅ Organiza por entorno: `vps_no_docker/` y `vps_docker/`

---

### 2️⃣ Analizar Resultados
```powershell
python analyze_benchmarks_improved.py benchmark_results_improved
```

**Qué genera:**
- 📊 **4 Gráficos PNG** en `benchmark_results_improved/evidencia/`:
  - `01_distribution_boxplot.png` - Distribución de RPS (boxplots)
  - `02_stability_comparison.png` - Coeficiente de Variación (CV%)
  - `03_overhead_with_ci.png` - Overhead de Docker por endpoint
  - `04_consistency_over_runs.png` - Consistencia en las 10 pruebas

- 📄 **Reportes**:
  - `analysis_improved_TIMESTAMP.json` - Datos completos en JSON
  - `analysis_improved_TIMESTAMP.csv` - Estadísticas en CSV

- 📋 **Salida en Consola**:
  - Estadísticas detalladas (media, mediana, desv. est., CV%)
  - Análisis de confiabilidad y estabilidad
  - Comparación Docker vs Sin Docker
  - Recomendaciones de uso

---

## 📊 Estructura de Carpetas

```
benchmark_results_improved/
├── vps_no_docker/
│   ├── benchmark_Root_Endpoint_(Baseline)_1.csv
│   ├── benchmark_Root_Endpoint_(Baseline)_2.csv
│   ├── ... (hasta 10)
│   └── benchmark_Large_JSON_Response_10.csv
│
├── vps_docker/
│   ├── benchmark_Root_Endpoint_(Baseline)_1.csv
│   ├── benchmark_Root_Endpoint_(Baseline)_2.csv
│   ├── ... (hasta 10)
│   └── benchmark_Large_JSON_Response_10.csv
│
├── evidencia/
│   ├── 01_distribution_boxplot.png
│   ├── 02_stability_comparison.png
│   ├── 03_overhead_with_ci.png
│   └── 04_consistency_over_runs.png
│
├── analysis_improved_TIMESTAMP.json
├── analysis_improved_TIMESTAMP.csv
└── RESULTADOS.txt
```

---

## 🔄 Flujo Completo de Ejecución

### Paso 1: Ejecutar Benchmarks en VPS
```bash
# En el VPS (o desde tu máquina local si tienes acceso)
cd /ruta/del/proyecto
.\benchmark-improved.ps1
```

**Duración aproximada**: 12-18 minutos
- Cada prueba toma ~2 minutos
- 6 pruebas × 5 endpoints × 2 entornos = ~60 minutos total

### Paso 2: Descargar Resultados
```bash
# Si los benchmarks se ejecutaron en VPS remoto
scp -r user@138.68.233.15:/ruta/benchmark_results_improved ./
```

### Paso 3: Analizar Resultados Localmente
```powershell
python analyze_benchmarks_improved.py benchmark_results_improved
```

### Paso 4: Revisar Gráficos y Reportes
```bash
# Ver resultados en carpeta evidencia/
dir benchmark_results_improved/evidencia/
```

---

## 📈 Métricas Recolectadas

Por cada prueba se captura:
- **Requests por segundo (RPS)** - Throughput
- **Latencia promedio** - Tiempo medio de respuesta
- **Latencia máxima** - Peor caso
- **Requests exitosos** - Respuestas 2xx
- **Requests fallidos** - Respuestas 5xx
- **Total de requests** - Confirmación de prueba completa

---

## 🎯 Endpoints Testeados

1. **`/`** - Root Endpoint (Baseline - mínima carga)
2. **`/health`** - Health Check (sin procesamiento)
3. **`/async-light`** - Async sin I/O bloqueante
4. **`/heavy`** - Computación intensiva CPU
5. **`/json-large?page=1&limit=50`** - Respuesta JSON grande (con paginación)

---

## ✅ Checklist Antes de Ejecutar

- [ ] Ambos VPS están corriendo y accesibles
  ```powershell
  # Verificar Sin Docker
  Invoke-WebRequest -Uri "http://138.68.233.15:8000/health"
  
  # Verificar Con Docker
  Invoke-WebRequest -Uri "http://68.183.168.86:8000/health"
  ```

- [ ] FastAPI está corriendo en ambos VPS
- [ ] Bombardier está instalado en tu máquina:
  ```bash
  bombardier -h
  ```
  
  Si no está instalado:
  ```bash
  # Windows (choco)
  choco install bombardier
  
  # macOS (brew)
  brew install bombardier
  
  # Linux
  wget https://github.com/codesenberg/bombardier/releases/download/v1.2.5/bombardier-linux-x64
  chmod +x bombardier-linux-x64
  sudo mv bombardier-linux-x64 /usr/local/bin/bombardier
  ```

- [ ] Python 3.8+ con pandas, matplotlib, seaborn instalados
  ```bash
  pip install pandas matplotlib seaborn
  ```

---

## 🐛 Troubleshooting

### Error: "No se puede conectar a http://..."
```powershell
# Verificar si el VPS está corriendo la app
ssh user@138.68.233.15
ps aux | grep uvicorn

# Reiniciar la aplicación si es necesario
cd /ruta/app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Error: "bombardier: comando no encontrado"
Instalar bombardier o usar wget/curl en su lugar.

### Gráficos no se generan
```bash
# Verificar matplotlib backend
python -c "import matplotlib; print(matplotlib.get_backend())"

# Si hay error, especificar backend
export MPLBACKEND=Agg
python analyze_benchmarks_improved.py benchmark_results_improved
```

---

## 📊 Interpretación de Resultados

### Coeficiente de Variación (CV%)
- **< 3%**: 🟢 Excelente (muy consistente)
- **3-8%**: 🟡 Bueno (consistencia normal)
- **8-15%**: 🟠 Moderado (variabilidad aceptable)
- **> 15%**: 🔴 Crítico (muy variable)

### Overhead de Docker
- **< 3%**: 🟢 Excelente (Docker es prácticamente gratuito)
- **3-8%**: 🟡 Bueno (overhead mínimo)
- **8-15%**: 🟠 Moderado (considerar el costo)
- **> 15%**: 🔴 Crítico (alto costo de containerización)

---

## 📝 Ejemplo de Ejecución Completa

```powershell
# Ejecutar benchmarks
PS> .\benchmark-improved.ps1

# Esperar ~30 minutos...

# Analizar resultados
PS> python analyze_benchmarks_improved.py benchmark_results_improved

# Ver gráficos
PS> dir benchmark_results_improved/evidencia/
```

**Salida esperada:**
```
📊 SECCIÓN 1: ESTADÍSTICAS RESUMIDAS (10 PRUEBAS)
...
📌 Root Endpoint (Baseline)
   vps_no_docker | Media:    5432.23 | Mediana:    5423.45 | CV:  2.3% ✅
   vps_docker    | Media:    5412.12 | Mediana:    5401.23 | CV:  2.1% ✅

🐳 SECCIÓN 3: OVERHEAD DE DOCKER
...
📊 OVERHEAD PROMEDIO DE DOCKER: -0.37%
✅ El overhead de Docker es MÍNIMO (<5%)
   Recomendación: USAR DOCKER en producción
```

---

## 🔗 Referencias

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Uvicorn Docs**: https://www.uvicorn.org/
- **Bombardier**: https://github.com/codesenberg/bombardier
- **Pandas Docs**: https://pandas.pydata.org/
- **Matplotlib Docs**: https://matplotlib.org/

---

**Última actualización**: 2 de Noviembre, 2025  
**Estado**: ✅ Listo para producción
