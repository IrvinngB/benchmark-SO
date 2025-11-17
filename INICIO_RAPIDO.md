# 🚀 Inicio Rápido - Sistema Automatizado

## ⚡ En 3 Pasos

### 1️⃣ Clonar y Cambiar a la Rama

```bash
git clone https://github.com/IrvinngB/benchmark-SO.git
cd SistemasOperativos
git checkout automatico
```

### 2️⃣ Iniciar el Sistema

**Windows:**
```powershell
.\control_automatico.ps1 -Action start
```

**Linux/Mac:**
```bash
chmod +x control_automatico.sh
./control_automatico.sh start
```

### 3️⃣ Verificar que Funciona

```bash
# Ver estado
.\control_automatico.ps1 -Action status    # Windows
./control_automatico.sh status             # Linux/Mac

# Probar FastAPI
curl http://localhost:8000/health
```

## ✅ ¡Listo!

El sistema ahora:
- ✅ FastAPI corriendo en `http://localhost:8000`
- ✅ Benchmarks automáticos a las **9:00 AM** y **9:00 PM**
- ✅ Logs guardándose en `../benchmark-logs/` (fuera del proyecto)
- ✅ Resultados en `../benchmark-results/` (fuera del proyecto)

## 🎯 Comandos Útiles

```bash
# Ver logs en tiempo real
.\control_automatico.ps1 -Action logs      # Windows
./control_automatico.sh logs               # Linux/Mac

# Ejecutar benchmark ahora (sin esperar)
.\control_automatico.ps1 -Action benchmark-manual
./control_automatico.sh benchmark-manual

# Detener todo
.\control_automatico.ps1 -Action stop
./control_automatico.sh stop
```

## 📖 Más Información

Lee el [README_AUTOMATICO.md](README_AUTOMATICO.md) completo para:
- Configuración avanzada
- Troubleshooting
- Deployment en VPS
- Análisis de resultados

---

**¿Problemas?** Ejecuta: `.\control_automatico.ps1 -Action status` para diagnóstico
