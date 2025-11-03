# ⚡ QUICK FIX - Instalar Bombardier

## El Problema
```
Error: The term 'bombardier' is not recognized as a name of a cmdlet
```

## ✅ La Solución (elige una)

### Opción 1: Script Automático (MÁS FÁCIL) ⭐
```powershell
.\install-bombardier.ps1
```
Esto descarga e instala bombardier automáticamente en `C:\Program Files\Bombardier\`

---

### Opción 2: Chocolatey
```powershell
choco install bombardier
```

---

### Opción 3: Descargar Manual
1. Ve a: https://github.com/codesenberg/bombardier/releases
2. Descarga: `bombardier-windows-amd64.exe`
3. Pon en: `C:\Program Files\Bombardier\bombardier.exe`

---

## ✔️ Verificar que Funcionó

Abre una **NUEVA terminal PowerShell** y ejecuta:
```powershell
bombardier --version
```

Deberías ver:
```
Bombardier 1.2.5
```

---

## 🚀 Luego Ejecuta

```powershell
# Verificar VPS
.\verify-vps.ps1

# Ejecutar benchmarks (6 pruebas, ~15 min)
.\benchmark-improved.ps1

# Analizar resultados
python analyze_benchmarks_improved.py benchmark_results_improved
```

---

## 🆘 Si Aún No Funciona

Ver: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

**Instalador automático disponible en:** `.\install-bombardier.ps1`
