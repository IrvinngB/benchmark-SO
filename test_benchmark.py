#!/usr/bin/env python3
"""
Test de Conectividad y Validación - FastAPI Benchmark
====================================================
Script para verificar que todo esté listo antes del benchmark completo.

Uso:
    python test_benchmark.py
"""

import sys
import importlib
import requests
import time
import json
from pathlib import Path

def test_python_version():
    """Verifica versión de Python"""
    print("🐍 Verificando Python...")
    
    if sys.version_info < (3, 8):
        print(f"   ❌ Python {sys.version.split()[0]} - Se requiere 3.8+")
        return False
    else:
        print(f"   ✅ Python {sys.version.split()[0]} - Compatible")
        return True

def test_dependencies():
    """Verifica dependencias críticas"""
    print("\n📦 Verificando dependencias...")
    
    critical_deps = [
        'aiohttp', 'pandas', 'matplotlib', 'rich', 'psutil',
        'numpy', 'seaborn', 'requests'
    ]
    
    optional_deps = [
        'flask', 'plotly', 'openpyxl', 'scipy'
    ]
    
    missing_critical = []
    missing_optional = []
    
    # Dependencias críticas
    for dep in critical_deps:
        try:
            importlib.import_module(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - FALTA (CRÍTICO)")
            missing_critical.append(dep)
    
    # Dependencias opcionales
    for dep in optional_deps:
        try:
            importlib.import_module(dep)
            print(f"   ✅ {dep} (opcional)")
        except ImportError:
            print(f"   ⚠️ {dep} - FALTA (opcional)")
            missing_optional.append(dep)
    
    if missing_critical:
        print(f"\n❌ Faltan dependencias críticas: {', '.join(missing_critical)}")
        print("   Ejecutar: pip install " + " ".join(missing_critical))
        return False
    
    if missing_optional:
        print(f"\n⚠️ Dependencias opcionales faltantes: {', '.join(missing_optional)}")
        print("   Funcionalidad limitada. Para instalar: pip install " + " ".join(missing_optional))
    
    return True

def test_server_connectivity():
    """Verifica conectividad con servidores VPS"""
    print("\n🌐 Verificando conectividad...")
    
    servers = {
        "VPS Sin Docker": "138.68.233.15:8000",
        "VPS Con Docker": "68.183.168.86:8000"
    }
    
    endpoints = ["/", "/health", "/heavy"]
    results = {}
    
    for name, address in servers.items():
        print(f"\n   🔍 Probando {name} ({address})...")
        server_results = {}
        
        for endpoint in endpoints:
            url = f"http://{address}{endpoint}"
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                
                latency = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    print(f"      ✅ {endpoint} - {response.status_code} ({latency:.2f}ms)")
                    server_results[endpoint] = {
                        'status': 'ok',
                        'status_code': response.status_code,
                        'latency_ms': round(latency, 2),
                        'response_size': len(response.content)
                    }
                else:
                    print(f"      ⚠️ {endpoint} - {response.status_code} ({latency:.2f}ms)")
                    server_results[endpoint] = {
                        'status': 'warning',
                        'status_code': response.status_code,
                        'latency_ms': round(latency, 2)
                    }
            
            except requests.exceptions.RequestException as e:
                print(f"      ❌ {endpoint} - {str(e)[:60]}...")
                server_results[endpoint] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        results[name] = server_results
    
    return results

def test_system_resources():
    """Verifica recursos del sistema"""
    print("\n💻 Verificando recursos del sistema...")
    
    try:
        import psutil
        
        # CPU
        cpu_count = psutil.cpu_count(logical=True)
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"   🔧 CPU: {cpu_count} cores ({cpu_percent:.1f}% uso actual)")
        
        # RAM  
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        memory_available_gb = memory.available / (1024**3)
        print(f"   💾 RAM: {memory_gb:.1f} GB total, {memory_available_gb:.1f} GB disponible ({memory.percent:.1f}% uso)")
        
        # Disk
        disk = psutil.disk_usage('.')
        disk_free_gb = disk.free / (1024**3)
        print(f"   💿 Disco: {disk_free_gb:.1f} GB libres")
        
        # Network
        network = psutil.net_io_counters()
        print(f"   🌐 Red: {network.bytes_sent / (1024**2):.1f} MB enviados, {network.bytes_recv / (1024**2):.1f} MB recibidos")
        
        # Verificar si hay suficientes recursos
        warnings = []
        if memory_available_gb < 1:
            warnings.append("⚠️ Poca RAM disponible (<1GB)")
        if cpu_percent > 80:
            warnings.append("⚠️ CPU muy ocupada (>80%)")
        if disk_free_gb < 1:
            warnings.append("⚠️ Poco espacio en disco (<1GB)")
        
        if warnings:
            print("\n   Advertencias:")
            for warning in warnings:
                print(f"   {warning}")
        
        return True
        
    except ImportError:
        print("   ❌ psutil no disponible - No se puede verificar recursos")
        return False

def test_benchmark_files():
    """Verifica que los archivos del benchmark existan"""
    print("\n📁 Verificando archivos...")
    
    required_files = [
        "benchmark_python.py",
        "setup_benchmark.py",
        "requirements_benchmark.txt"
    ]
    
    optional_files = [
        "README_Python_Benchmark.md"
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - FALTA")
            missing_files.append(file)
    
    for file in optional_files:
        if Path(file).exists():
            print(f"   ✅ {file} (opcional)")
        else:
            print(f"   ⚠️ {file} - FALTA (opcional)")
    
    return len(missing_files) == 0

def run_quick_test():
    """Ejecuta un test rápido de aiohttp"""
    print("\n⚡ Ejecutando test rápido de aiohttp...")
    
    try:
        import asyncio
        import aiohttp
        import time
        
        async def quick_benchmark():
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                
                # 10 requests concurrentes a httpbin.org (servicio de pruebas)
                for i in range(10):
                    task = asyncio.create_task(
                        session.get('https://httpbin.org/delay/0.1')
                    )
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                successful = sum(1 for r in responses if not isinstance(r, Exception))
                failed = len(responses) - successful
            
            end_time = time.time()
            total_time = end_time - start_time
            rps = len(responses) / total_time if total_time > 0 else 0
            
            return {
                'total_requests': len(responses),
                'successful': successful,
                'failed': failed,
                'total_time': total_time,
                'rps': rps
            }
        
        # Ejecutar test asíncrono
        result = asyncio.run(quick_benchmark())
        
        print(f"   📊 Resultados del test:")
        print(f"      - Requests: {result['total_requests']}")
        print(f"      - Exitosos: {result['successful']}")
        print(f"      - Fallidos: {result['failed']}")
        print(f"      - Tiempo total: {result['total_time']:.2f}s")
        print(f"      - RPS: {result['rps']:.2f}")
        
        if result['successful'] >= 8:  # Al menos 8 de 10 exitosos
            print("   ✅ aiohttp funcionando correctamente")
            return True
        else:
            print("   ⚠️ Algunos requests fallaron - Puede haber problemas de conectividad")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en test aiohttp: {e}")
        return False

def save_test_results(connectivity_results):
    """Guarda los resultados del test"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    test_data = {
        'timestamp': timestamp,
        'python_version': sys.version,
        'connectivity_results': connectivity_results
    }
    
    try:
        with open(results_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print(f"\n💾 Resultados guardados en: {results_file}")
        
    except Exception as e:
        print(f"\n⚠️ No se pudieron guardar resultados: {e}")

def main():
    print("🧪 FastAPI Benchmark - Test de Validación")
    print("=" * 50)
    
    all_good = True
    
    # Ejecutar todos los tests
    tests = [
        ("Versión de Python", test_python_version),
        ("Dependencias", test_dependencies),
        ("Archivos del benchmark", test_benchmark_files),
        ("Recursos del sistema", test_system_resources),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        if not result:
            all_good = False
    
    # Test de conectividad (separado porque puede fallar sin ser crítico)
    print(f"\n{'='*20} Conectividad {'='*20}")
    connectivity_results = test_server_connectivity()
    
    # Test rápido de aiohttp
    print(f"\n{'='*20} Test Rápido aiohttp {'='*20}")
    aiohttp_ok = run_quick_test()
    
    # Guardar resultados
    save_test_results(connectivity_results)
    
    # Resumen final
    print(f"\n{'='*50}")
    print("📋 RESUMEN DE VALIDACIÓN")
    print("=" * 50)
    
    if all_good and aiohttp_ok:
        print("🎉 ¡TODO LISTO! El benchmark debería funcionar perfectamente.")
        print("\n🚀 Para ejecutar el benchmark completo:")
        print("   python setup_benchmark.py --all")
        print("   python benchmark_python.py")
        
    elif all_good:
        print("⚠️ Configuración básica OK, pero hay problemas menores.")
        print("   El benchmark debería funcionar, pero con funcionalidad limitada.")
        print("\n🚀 Para ejecutar de todas formas:")
        print("   python benchmark_python.py --quick")
        
    else:
        print("❌ HAY PROBLEMAS CRÍTICOS que deben resolverse.")
        print("\n🔧 Pasos sugeridos:")
        print("1. Instalar dependencias: pip install -r requirements_benchmark.txt")
        print("2. Verificar versión de Python (requiere 3.8+)")
        print("3. Ejecutar este test nuevamente")
    
    # Información adicional
    has_vps_connectivity = any(
        any(endpoint.get('status') == 'ok' for endpoint in server_data.values())
        for server_data in connectivity_results.values()
    )
    
    if not has_vps_connectivity:
        print("\n📡 CONECTIVIDAD VPS:")
        print("   ⚠️ No hay conectividad con servidores VPS")
        print("   📝 El benchmark funcionará solo con servidores locales")
        print("   💡 Para usar VPS, verificar firewall y conectividad")
    else:
        print("\n📡 CONECTIVIDAD VPS:")
        print("   ✅ Al menos un servidor VPS está disponible")

if __name__ == "__main__":
    main()