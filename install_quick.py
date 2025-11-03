#!/usr/bin/env python3
"""
Instalación Rápida FastAPI Benchmark
===================================
Script simple para instalar solo las dependencias esenciales.
"""

import subprocess
import sys
import importlib

def install_essentials():
    """Instala solo las dependencias esenciales una por una"""
    print("🚀 Instalación Rápida de FastAPI Benchmark")
    print("=" * 50)
    
    # Dependencias en orden de importancia
    essential_packages = [
        "requests",      # HTTP básico
        "aiohttp",       # HTTP asíncrono  
        "pandas",        # Análisis datos
        "numpy",         # Matemáticas
        "psutil",        # Sistema
        "matplotlib",    # Gráficos básicos
        "rich",          # Terminal bonito
        "seaborn",       # Gráficos estadísticos
        "openpyxl",      # Excel
        "colorama",      # Colores Windows
        "tqdm"           # Progress bars
    ]
    
    successful = []
    failed = []
    
    for package in essential_packages:
        try:
            print(f"\n📦 Instalando {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"   ✅ {package} - Instalado")
                successful.append(package)
            else:
                print(f"   ❌ {package} - Error: {result.stderr[:100]}...")
                failed.append(package)
                
        except Exception as e:
            print(f"   ❌ {package} - Excepción: {str(e)[:100]}...")
            failed.append(package)
    
    print(f"\n{'='*50}")
    print("📊 RESUMEN DE INSTALACIÓN")
    print("=" * 50)
    print(f"✅ Exitosos: {len(successful)} paquetes")
    print(f"❌ Fallidos: {len(failed)} paquetes")
    
    if successful:
        print(f"\n✅ Instalados correctamente:")
        for pkg in successful:
            print(f"   - {pkg}")
    
    if failed:
        print(f"\n❌ No se pudieron instalar:")
        for pkg in failed:
            print(f"   - {pkg}")
        
        print(f"\n💡 Alternativas para los fallidos:")
        print("   - Actualizar pip: python -m pip install --upgrade pip")
        print("   - Instalar manualmente: pip install <paquete>")
        print("   - Usar conda: conda install <paquete>")
    
    # Verificar instalación
    print(f"\n🔍 Verificando instalación...")
    working_packages = []
    
    for package in successful:
        try:
            importlib.import_module(package)
            working_packages.append(package)
            print(f"   ✅ {package} - Funciona")
        except ImportError:
            print(f"   ❌ {package} - No se puede importar")
    
    print(f"\n🎯 Resultado final:")
    if len(working_packages) >= 6:  # Al menos las 6 más críticas
        print("   ✅ ¡Listo para ejecutar el benchmark!")
        print("   🚀 Ejecutar con: python benchmark_python.py")
    elif len(working_packages) >= 3:  # Mínimo funcional
        print("   ⚠️ Instalación parcial - funcionalidad limitada")
        print("   🚀 Ejecutar con: python benchmark_python.py --quick")
    else:
        print("   ❌ Instalación insuficiente")
        print("   💡 Instalar manualmente las dependencias críticas")
    
    return len(working_packages) >= 3

def check_python():
    """Verifica versión de Python"""
    if sys.version_info < (3, 7):
        print(f"❌ Python {sys.version.split()[0]} - Se requiere 3.7+")
        return False
    else:
        print(f"✅ Python {sys.version.split()[0]} - Compatible")
        return True

if __name__ == "__main__":
    if not check_python():
        sys.exit(1)
    
    install_essentials()