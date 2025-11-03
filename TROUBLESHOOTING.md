# 🔧 Troubleshooting - Errores Comunes

## ❌ Error: "bombardier is not recognized"

### ¿Qué significa?
Bombardier no está instalado o no está en el PATH de Windows.

### 🔧 Soluciones

#### Opción 1: Instalador Automático (RECOMENDADO)
```powershell
.\install-bombardier.ps1
```

#### Opción 2: Instalar con Chocolatey
```powershell
# Primero instala Chocolatey desde https://chocolatey.org/install
choco install bombardier
```

#### Opción 3: Descargar Manualmente
1. Ve a: https://github.com/codesenberg/bombardier/releases
2. Descarga: `bombardier-windows-amd64.exe`
3. Coloca en: `C:\Program Files\Bombardier\`
4. Agrega a PATH en Variables de Entorno

#### Opción 4: Verificar Instalación
```powershell
# Verificar si está instalado
bombardier --version

# Si da error, intenta:
.\install-bombardier.ps1

# Abre una NUEVA terminal PowerShell después de instalar
```

---

## ❌ Error: "No se puede conectar a http://138.68.233.15:8000"

### ¿Qué significa?
El VPS Sin Docker no está accesible.

### 🔧 Soluciones

#### 1. Verificar si el VPS está corriendo
```bash
ping 138.68.233.15
```

#### 2. SSH al VPS y verifica FastAPI
```bash
ssh root@138.68.233.15

# Dentro del VPS:
ps aux | grep uvicorn

# Si no corre, inicia:
cd /app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 &
```

#### 3. Verificar firewall
```bash
# En el VPS
sudo ufw allow 8000
sudo ufw reload
```

---

## ❌ Error: "No se puede conectar a http://68.183.168.86:8000"

### ¿Qué significa?
El VPS Con Docker no está accesible.

### 🔧 Soluciones

#### 1. SSH al VPS Docker y verifica contenedor
```bash
ssh root@68.183.168.86

# Dentro del VPS:
docker ps

# Si no está corriendo:
docker run -d \
  --name fastapi-app \
  -p 8000:8000 \
  --restart unless-stopped \
  fastapi-perf:latest

# Si ya existe, reinicia:
docker restart fastapi-app
```

#### 2. Ver logs del contenedor
```bash
docker logs -f fastapi-app
```

#### 3. Verificar firewall
```bash
# En el VPS
sudo ufw allow 8000
sudo ufw reload
```

---

## ❌ Error: "ImportError: No module named 'pandas'"

### ¿Qué significa?
Faltan dependencias Python para el análisis.

### 🔧 Soluciones

```powershell
# Instalar dependencias
pip install pandas matplotlib seaborn

# Verificar instalación
python -c "import pandas; print(pandas.__version__)"
```

---

## ❌ Error: "ValueError: no objects to concatenate"

### ¿Qué significa?
No hay archivos CSV en la carpeta de resultados.

### 🔧 Soluciones

```powershell
# 1. Verifica que el benchmark generó archivos
dir benchmark_results_improved\

# 2. Si está vacío, ejecuta benchmarks primero
.\benchmark-improved.ps1

# 3. Luego analiza
python analyze_benchmarks_improved.py benchmark_results_improved
```

---

## ❌ Error: "FileNotFoundError: [Errno 2] No such file or directory"

### ¿Qué significa?
No encontró los archivos de benchmark.

### 🔧 Soluciones

```powershell
# Asegúrate de estar en el directorio correcto
cd d:\ProyectosP\SistemasOperativos

# Verifica que exista la carpeta
dir benchmark_results_improved\

# Si no existe, ejecuta benchmarks
.\benchmark-improved.ps1
```

---

## ⚠️ Advertencia: "CV% > 15% (muy variable)"

### ¿Qué significa?
El endpoint tiene mucha variabilidad en RPS.

### 🔧 Soluciones

1. **Ejecutar más pruebas**: Aumenta `$NUM_TESTS` en `benchmark-improved.ps1`
2. **Reducir conexiones concurrentes**: Cambia `-Connections 50` a `25`
3. **Aumentar requests**: Cambia `-Requests 1000` a `2000`
4. **Revisar VPS**: Verifica CPU/RAM disponible con `htop`

---

## 🚨 Problema: Script tarda mucho

### ¿Qué significa?
Los benchmarks están siendo lentos.

### 🔧 Soluciones

```powershell
# 1. Reducir número de pruebas
# Edita benchmark-improved.ps1
$NUM_TESTS = 3  # En lugar de 6

# 2. Reducir conexiones concurrentes
# Edita en Invoke-Benchmark
-Connections 25  # En lugar de 50

# 3. Reducir requests por prueba
# Edita en param()
[int]$Requests = 500  # En lugar de 1000
```

---

## 🔄 Cómo Reejecutar Benchmarks

```powershell
# 1. Limpiar resultados anteriores
Remove-Item -Path "benchmark_results_improved" -Recurse -Force

# 2. Ejecutar de nuevo
.\benchmark-improved.ps1

# 3. Analizar
python analyze_benchmarks_improved.py benchmark_results_improved
```

---

## ✅ Verificación Rápida del Sistema

```powershell
# 1. Verificar bombardier
bombardier --version

# 2. Verificar Python
python --version

# 3. Verificar módulos Python
python -c "import pandas; import matplotlib; print('✅ Modules OK')"

# 4. Verificar conectividad VPS Sin Docker
Invoke-WebRequest -Uri "http://138.68.233.15:8000/health"

# 5. Verificar conectividad VPS Con Docker
Invoke-WebRequest -Uri "http://68.183.168.86:8000/health"
```

---

## 📞 Contacto y Links

- **GitHub Issue**: Abre un issue en https://github.com/IrvinngB/benchmark-SO
- **Bombardier Docs**: https://github.com/codesenberg/bombardier
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pandas Docs**: https://pandas.pydata.org/

---

**¿Problema no resuelto?** Crea un issue en GitHub con:
1. El error exacto (copia y pega)
2. El comando que ejecutaste
3. Tu sistema operativo y versión PowerShell
