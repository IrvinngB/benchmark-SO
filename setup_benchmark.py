#!/usr/bin/env python3
"""
Setup rápido para FastAPI Benchmark Python Edition
=================================================
Este script configura automáticamente el entorno y ejecuta el benchmark.

Uso:
    python setup_benchmark.py --install    # Solo instalar dependencias
    python setup_benchmark.py --run        # Solo ejecutar benchmark
    python setup_benchmark.py --all        # Instalar y ejecutar
    python setup_benchmark.py --dashboard  # Con dashboard web
"""

import subprocess
import sys
import os
import platform
from pathlib import Path
import argparse
import time

def check_python_version():
    """Verifica que Python sea 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} detectado")

def install_dependencies():
    """Instala las dependencias necesarias"""
    print("📦 Instalando dependencias...")
    
    requirements_file = Path("requirements_benchmark.txt")
    
    if not requirements_file.exists():
        print("❌ Archivo requirements_benchmark.txt no encontrado")
        return False
    
    try:
        # Actualizar pip primero
        print("   Actualizando pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Instalar dependencias core (las más importantes primero)
        core_deps = [
            "aiohttp>=3.8.0",
            "pandas>=2.0.0", 
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "rich>=13.0.0",
            "psutil>=5.9.0",
            "numpy>=1.24.0",
            "requests>=2.31.0"
        ]
        
        print("   Instalando dependencias core...")
        for dep in core_deps:
            print(f"     - {dep}")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                          check=True, capture_output=True)
        
        # Instalar el resto de dependencias
        print("   Instalando dependencias adicionales...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                      check=True, capture_output=True)
        
        print("✅ Dependencias instaladas correctamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        print("   Intentando instalación básica...")
        
        # Fallback: instalar solo lo esencial
        essential_deps = ["aiohttp", "pandas", "matplotlib", "rich", "psutil"]
        
        for dep in essential_deps:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                              check=True, capture_output=True)
                print(f"     ✅ {dep} instalado")
            except:
                print(f"     ❌ Error instalando {dep}")
        
        return True  # Continuar aunque falten algunas dependencias

def check_servers():
    """Verifica conectividad con los servidores VPS"""
    print("🔍 Verificando conectividad con servidores...")
    
    servers = {
        "VPS Sin Docker": "138.68.233.15:8000",
        "VPS Con Docker": "68.183.168.86:8000"
    }
    
    import requests
    
    available_servers = []
    
    for name, address in servers.items():
        try:
            response = requests.get(f"http://{address}/health", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name} ({address}) - Disponible")
                available_servers.append(name)
            else:
                print(f"   ⚠️ {name} ({address}) - Responde con código {response.status_code}")
        except requests.RequestException:
            print(f"   ❌ {name} ({address}) - No disponible")
    
    if not available_servers:
        print("⚠️ Ningún servidor VPS disponible. El benchmark solo funcionará localmente.")
        return False
    
    return True

def run_benchmark(with_dashboard=False, quick_test=False):
    """Ejecuta el benchmark"""
    print("🚀 Iniciando benchmark...")
    
    benchmark_args = ["python", "benchmark_python.py"]
    
    if quick_test:
        benchmark_args.extend(["--tests", "2", "--requests", "50"])
        print("   Modo prueba rápida: 2 tests, 50 requests por endpoint")
    
    if with_dashboard:
        benchmark_args.append("--dashboard")
        print("   Dashboard web habilitado en http://localhost:5000")
    
    try:
        # Ejecutar benchmark
        process = subprocess.Popen(benchmark_args)
        
        if with_dashboard:
            print("\n" + "="*60)
            print("🌐 Dashboard disponible en: http://localhost:5000")
            print("⏹️ Presiona Ctrl+C para detener el benchmark")
            print("="*60 + "\n")
        
        process.wait()
        
        if process.returncode == 0:
            print("✅ Benchmark completado exitosamente")
            return True
        else:
            print(f"❌ Benchmark terminó con errores (código: {process.returncode})")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️ Benchmark interrumpido por el usuario")
        process.terminate()
        return False
    except Exception as e:
        print(f"❌ Error ejecutando benchmark: {e}")
        return False

def show_system_info():
    """Muestra información del sistema"""
    print("💻 Información del Sistema:")
    print(f"   Sistema Operativo: {platform.system()} {platform.release()}")
    print(f"   Arquitectura: {platform.machine()}")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Directorio actual: {Path.cwd()}")
    
    # CPU y RAM
    try:
        import psutil
        cpu_count = psutil.cpu_count(logical=True)
        memory_gb = psutil.virtual_memory().total / (1024**3)
        print(f"   CPU: {cpu_count} cores")
        print(f"   RAM: {memory_gb:.1f} GB")
    except ImportError:
        print("   CPU/RAM: No disponible (psutil no instalado)")

def create_batch_scripts():
    """Crea scripts de lote para Windows"""
    if platform.system() == "Windows":
        
        # Script para instalar
        install_bat = """@echo off
echo ===================================================
echo  FastAPI Benchmark - Instalacion de Dependencias
echo ===================================================
python setup_benchmark.py --install
pause
"""
        
        # Script para ejecutar
        run_bat = """@echo off
echo =====================================
echo  FastAPI Benchmark - Ejecucion
echo =====================================
python setup_benchmark.py --run
pause
"""
        
        # Script completo
        full_bat = """@echo off
echo ===============================================
echo  FastAPI Benchmark - Instalacion y Ejecucion
echo ===============================================
python setup_benchmark.py --all
pause
"""
        
        with open("install_benchmark.bat", "w") as f:
            f.write(install_bat)
        
        with open("run_benchmark.bat", "w") as f:
            f.write(run_bat)
            
        with open("benchmark_full.bat", "w") as f:
            f.write(full_bat)
        
        print("✅ Scripts de Windows creados:")
        print("   - install_benchmark.bat")
        print("   - run_benchmark.bat") 
        print("   - benchmark_full.bat")

def main():
    parser = argparse.ArgumentParser(description="Setup FastAPI Benchmark Python Edition")
    
    parser.add_argument('--install', action='store_true', 
                       help='Solo instalar dependencias')
    parser.add_argument('--run', action='store_true',
                       help='Solo ejecutar benchmark')
    parser.add_argument('--all', action='store_true',
                       help='Instalar y ejecutar')
    parser.add_argument('--dashboard', action='store_true',
                       help='Habilitar dashboard web')
    parser.add_argument('--quick', action='store_true',
                       help='Prueba rápida (2 tests, 50 requests)')
    parser.add_argument('--info', action='store_true',
                       help='Solo mostrar información del sistema')
    
    args = parser.parse_args()
    
    print("🎯 FastAPI Performance Benchmark - Setup")
    print("="*50)
    
    # Verificar Python
    check_python_version()
    
    if args.info:
        show_system_info()
        return
    
    # Mostrar info del sistema
    show_system_info()
    print()
    
    # Crear scripts de Windows
    create_batch_scripts()
    print()
    
    if args.install or args.all:
        if not install_dependencies():
            print("❌ Error en la instalación")
            return
        print()
    
    if args.run or args.all:
        # Verificar servidores
        servers_ok = check_servers()
        print()
        
        if not servers_ok:
            response = input("⚠️ Servidores VPS no disponibles. ¿Continuar solo con tests locales? (y/n): ")
            if response.lower() != 'y':
                print("❌ Benchmark cancelado")
                return
        
        # Ejecutar benchmark
        success = run_benchmark(with_dashboard=args.dashboard, quick_test=args.quick)
        
        if success:
            print("\n🎉 ¡Benchmark completado!")
            print("📁 Revisa la carpeta 'benchmark_results_python' para los resultados")
        else:
            print("\n❌ Hubo problemas durante el benchmark")
    
    if not (args.install or args.run or args.all or args.info):
        print("ℹ️ Uso:")
        print("   python setup_benchmark.py --install    # Solo instalar")
        print("   python setup_benchmark.py --run        # Solo ejecutar")
        print("   python setup_benchmark.py --all        # Instalar y ejecutar")
        print("   python setup_benchmark.py --dashboard  # Con dashboard web")
        print("   python setup_benchmark.py --quick      # Prueba rápida")
        print("   python setup_benchmark.py --info       # Info del sistema")

if __name__ == "__main__":
    main()