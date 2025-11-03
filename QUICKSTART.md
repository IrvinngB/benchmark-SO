# 🚀 Guía de Inicio Rápido - Benchmarks Mejorados

## 📋 IPs Actualizadas del Proyecto

```
✅ VPS SIN DOCKER: 138.68.233.15:8000
✅ VPS CON DOCKER: 68.183.168.86:8000
```

---

## ⚡ Ejecución Rápida (3 pasos)

### 0️⃣ Pre-requisito: Bombardier (OPCIONAL)

**⚠️ NO ES OBLIGATORIO** - El script tiene fallback automático a `Invoke-WebRequest`

**Si quieres benchmarks más rápidos, instala bombardier:**

```powershell
# Instalar bombardier automáticamente
.\install-bombardier.ps1
```

O manualmente:
```bash
choco install bombardier
```

---

### 1️⃣ Verificar Conectividad

**Salida esperada:**
```
✅ Ambos VPS están operacionales y listos para benchmarking
📝 Próximo paso: Ejecutar .\benchmark-improved.ps1
```

---

### 2️⃣ Ejecutar Benchmarks (6 runs)
```powershell
.\benchmark-improved.ps1
```

**Qué sucede:**
- 🔄 6 pruebas por entorno
- 5️⃣ 5 endpoints por prueba
- 📊 60 pruebas totales
- ⏱️ ~12-18 minutos de duración
- 💾 Resultados en `benchmark_results_improved/`

---

### 3️⃣ Analizar Resultados
```powershell
python analyze_benchmarks_improved.py benchmark_results_improved
```

**Genera:**
- 📊 4 gráficos PNG profesionales
- 📄 Reporte JSON con datos detallados
- 📋 Estadísticas CSV
- 🎯 Recomendaciones en consola

---

## 📊 Estructura de Resultados

```
benchmark_results_improved/
├── vps_no_docker/        ← 10 pruebas × 5 endpoints
├── vps_docker/           ← 10 pruebas × 5 endpoints
├── evidencia/            ← Gráficos generados
│   ├── 01_distribution_boxplot.png
│   ├── 02_stability_comparison.png
│   ├── 03_overhead_with_ci.png
│   └── 04_consistency_over_runs.png
├── analysis_improved_*.json
├── analysis_improved_*.csv
└── RESULTADOS.txt
```

---

## 🎯 Endpoints Testeados

| # | Endpoint | Propósito | Tipo |
|---|----------|----------|------|
| 1 | `/` | Baseline mínimo | Estático |
| 2 | `/health` | Health check | Ligero |
| 3 | `/async-light` | Operación async | Ligero |
| 4 | `/heavy` | CPU intensiva | Pesado |
| 5 | `/json-large?page=1&limit=50` | JSON grande | I/O |

---

## 📈 Métricas por Prueba

```json
{
  "timestamp": "2025-11-02 10:30:45",
  "test_number": 1,
  "endpoint": "Root Endpoint (Baseline)",
  "environment": "vps_no_docker",
  "requests_per_second": 5432.45,
  "avg_latency_ms": 0.18,
  "max_latency_ms": 12.34,
  "total_requests": 1000,
  "successful_requests": 1000,
  "failed_requests": 0
}
```

---

## 🔍 Interpretación Rápida

### Verde 🟢 = Excelente
- CV% < 5% (muy estable)
- Overhead Docker < 3%
- 0% de errores

### Amarillo 🟡 = Aceptable
- CV% 5-15% (estable con variaciones)
- Overhead Docker 3-8%
- < 1% de errores

### Rojo 🔴 = Crítico
- CV% > 15% (muy variable)
- Overhead Docker > 15%
- > 1% de errores

---

## 💡 Ejemplos de Uso

### Solo verificar conectividad
```powershell
.\verify-vps.ps1
```

### Ejecutar benchmarks sin analizar
```powershell
.\benchmark-improved.ps1
# Los resultados se guardan automáticamente
```

### Analizar resultados existentes
```powershell
python analyze_benchmarks_improved.py benchmark_results_improved
```

### Borrar resultados previos y empezar limpio
```powershell
Remove-Item -Path "benchmark_results_improved" -Recurse -Force -ErrorAction SilentlyContinue
.\benchmark-improved.ps1
```

---

## 📝 Configuración Personalizada

### Cambiar número de requests por prueba
Editar `benchmark-improved.ps1`:
```powershell
[int]$Requests = 2000        # Cambiar de 1000 a 2000
```

### Cambiar conexiones concurrentes
Editar `benchmark-improved.ps1`:
```powershell
[int]$Connections = 100      # Cambiar de 50 a 100
```

### Cambiar número de runs
Editar `benchmark-improved.ps1`:
```powershell
$NUM_TESTS = 20              # Cambiar de 10 a 20
```

---

## 🐛 Troubleshooting Rápido

### "❌ No se puede conectar a 138.68.233.15:8000"
```bash
# SSH al VPS sin Docker
ssh root@138.68.233.15

# Verificar si uvicorn corre
ps aux | grep uvicorn

# Reiniciar si es necesario
cd /app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 &
```

### "❌ No se puede conectar a 68.183.168.86:8000"
```bash
# SSH al VPS con Docker
ssh root@68.183.168.86

# Verificar contenedor
docker ps

# Reiniciar si es necesario
docker restart fastapi-app
```

### "bombardier: comando no encontrado"
```bash
# Windows (usando choco)
choco install bombardier

# O descargar manualmente desde GitHub
# https://github.com/codesenberg/bombardier/releases
```

### "ImportError: No module named 'pandas'"
```bash
pip install pandas matplotlib seaborn
```

---

## 📊 Ejemplo de Salida

```
╔════════════════════════════════════════════════════════════════════════════════╗
║           🚀 FastAPI Performance Benchmark - 10 Runs per Environment         ║
║                                                                                ║
║  VPS Sin Docker:  138.68.233.15:8000                                          ║
║  VPS Con Docker:  68.183.168.86:8000                                          ║
║                                                                                ║
║  Ejecución: 10 pruebas por entorno                                            ║
║  Total:     100 pruebas (10 runs × 5 endpoints × 2 env)                      ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

════════════════════════════════════════════════════════════════════════════════
  🔍 AMBIENTE: VPS Sin Docker
  📍 IP: 138.68.233.15:8000
════════════════════════════════════════════════════════════════════════════════

✅ Servidor accesible: http://138.68.233.15:8000

📍 EJECUCIÓN 1/10
   ⏳ [1%] Root Endpoint (Baseline)
   Ejecutando... (http://138.68.233.15:8000/) ✅
   ...
```

---

## ✅ Checklist Pre-Ejecución

- [ ] ~~Bombardier instalado~~ (Opcional - tiene fallback automático)
- [ ] Ambos VPS están activos
- [ ] FastAPI corriendo en ambos VPS
- [ ] Bombardier instalado
- [ ] Python 3.8+ con dependencias
- [ ] Espacio en disco disponible (~500MB)
- [ ] Conexión a internet estable
- [ ] ~30-40 minutos disponibles

---

## 🔗 Links Útiles

- 📖 [BENCHMARK_CONFIG.md](./BENCHMARK_CONFIG.md) - Configuración detallada
- 📊 [analyze_benchmarks_improved.py](./analyze_benchmarks_improved.py) - Script de análisis
- 🔧 [benchmark-improved.ps1](./benchmark-improved.ps1) - Script de benchmarks
- ✅ [verify-vps.ps1](./verify-vps.ps1) - Script de verificación

---

**¡Listo para empezar! 🚀**

Ejecuta: `.\verify-vps.ps1` → `.\benchmark-improved.ps1` → `python analyze_benchmarks_improved.py benchmark_results_improved`
