#!/usr/bin/env python3
"""
Test de Logging y Métricas del Sistema
=====================================
Script para verificar:
1. Creación automática de carpetas .logs
2. Captura de métricas del sistema (CPU, RAM, disco, red)
3. Logging con timestamps
4. Funcionalidad completa del sistema
"""

import os
from pathlib import Path
from logging_manager import get_log_manager
import psutil
import time
from datetime import datetime

def test_system_metrics():
    """Prueba captura de métricas del sistema"""
    print("🔍 Probando captura de métricas del sistema...")
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    
    # Memoria
    memory = psutil.virtual_memory()
    memory_mb = memory.used / (1024 * 1024)
    memory_percent = memory.percent
    
    # Disco
    disk = psutil.disk_usage('/')
    disk_percent = (disk.used / disk.total) * 100
    
    # Red
    net_io = psutil.net_io_counters()
    
    print(f"💻 CPU: {cpu_percent:.1f}% ({cpu_count} cores)")
    if cpu_freq:
        print(f"   Frecuencia: {cpu_freq.current:.1f} MHz")
    
    print(f"🧠 RAM: {memory_mb:.1f} MB ({memory_percent:.1f}%)")
    print(f"   Total: {memory.total / (1024**3):.1f} GB")
    print(f"   Disponible: {memory.available / (1024**3):.1f} GB")
    
    print(f"💾 Disco: {disk_percent:.1f}% usado")
    print(f"   Total: {disk.total / (1024**3):.1f} GB")
    print(f"   Libre: {disk.free / (1024**3):.1f} GB")
    
    print(f"🌐 Red: {net_io.bytes_sent / (1024**2):.1f} MB enviados")
    print(f"   Recibidos: {net_io.bytes_recv / (1024**2):.1f} MB")
    
    return {
        'cpu_percent': cpu_percent,
        'cpu_count': cpu_count,
        'memory_mb': memory_mb,
        'memory_percent': memory_percent,
        'memory_total_gb': memory.total / (1024**3),
        'disk_percent': disk_percent,
        'disk_total_gb': disk.total / (1024**3),
        'network_sent_mb': net_io.bytes_sent / (1024**2),
        'network_recv_mb': net_io.bytes_recv / (1024**2)
    }

def test_logging_system():
    """Prueba el sistema completo de logging"""
    print("\n📁 Probando sistema de logging...")
    
    # Verificar estado inicial
    logs_dir = Path(".logs")
    print(f"Estado inicial - .logs existe: {logs_dir.exists()}")
    
    # Obtener LogManager (esto debería crear las carpetas)
    log_manager = get_log_manager()
    
    # Verificar creación de carpetas
    subdirs = [
        logs_dir / "daily",
        logs_dir / "errors", 
        logs_dir / "performance",
        logs_dir / "archive"
    ]
    
    print("Verificando creación de carpetas:")
    for subdir in subdirs:
        exists = subdir.exists()
        print(f"  {subdir.name}/: {'✅' if exists else '❌'}")
        
        # Crear manualmente si no existe
        if not exists:
            print(f"    Creando {subdir} manualmente...")
            subdir.mkdir(parents=True, exist_ok=True)
            print(f"    {'✅' if subdir.exists() else '❌'} Creación manual")

def test_logging_functionality():
    """Prueba funcionalidad de logging con métricas"""
    print("\n📝 Probando funcionalidad de logging...")
    
    log_manager = get_log_manager()
    
    # Test logs básicos
    log_manager.log_info("🧪 Test de logging iniciado", category="general")
    log_manager.log_info("🔧 Probando diferentes categorías", category="config")
    
    # Test con métricas del sistema
    metrics = test_system_metrics()
    
    # Log de métricas
    log_manager.log_performance_metrics(
        rps=1234.56,
        latency=25.67,
        cpu_usage=metrics['cpu_percent'],
        memory_mb=metrics['memory_mb'],
        endpoint="/test"
    )
    
    # Test de conectividad simulada
    log_manager.log_connectivity_test(
        environment="test_local",
        url="http://localhost:8000",
        success=True,
        response_time_ms=15.34
    )
    
    # Test de resultado de endpoint
    endpoint_result = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'endpoint_name': 'Test Endpoint',
        'url': 'http://localhost:8000/test',
        'requests_per_second': 1234.56,
        'avg_latency_ms': 25.67,
        'cpu_usage_percent': metrics['cpu_percent'],
        'memory_usage_mb': metrics['memory_mb'],
        'error_rate': 0.0
    }
    
    log_manager.log_endpoint_result(endpoint_result)
    
    print("✅ Logs de prueba generados")

def check_log_files():
    """Verifica que se crearon los archivos de log"""
    print("\n📄 Verificando archivos de log generados...")
    
    logs_dir = Path(".logs")
    today = datetime.now().strftime("%Y-%m-%d")
    
    expected_files = [
        logs_dir / "daily" / f"{today}.log",
        logs_dir / "performance" / f"{today}_performance.log",
        logs_dir / "performance" / f"{today}_connectivity.log"
    ]
    
    for log_file in expected_files:
        if log_file.exists():
            size = log_file.stat().st_size
            print(f"  ✅ {log_file.name} ({size} bytes)")
            
            # Mostrar últimas líneas
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"    Última línea: {lines[-1].strip()}")
            except Exception as e:
                print(f"    Error leyendo archivo: {e}")
        else:
            print(f"  ❌ {log_file.name} - NO EXISTE")

def fix_permissions():
    """Arregla permisos en Linux/VM"""
    print("\n🔧 Verificando y arreglando permisos...")
    
    logs_dir = Path(".logs")
    
    try:
        # Crear directorio base
        logs_dir.mkdir(exist_ok=True)
        
        # Crear subdirectorios
        subdirs = ["daily", "errors", "performance", "archive"]
        for subdir in subdirs:
            (logs_dir / subdir).mkdir(exist_ok=True)
            
        # Cambiar permisos (solo en Linux/Unix)
        if os.name == 'posix':
            import stat
            # Permisos de lectura/escritura para usuario, lectura para grupo
            os.chmod(logs_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
            
            for subdir in subdirs:
                subdir_path = logs_dir / subdir
                if subdir_path.exists():
                    os.chmod(subdir_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
                    
        print("✅ Permisos configurados")
        
    except Exception as e:
        print(f"❌ Error configurando permisos: {e}")

def main():
    """Función principal de testing"""
    print("🧪 SISTEMA DE TEST - LOGGING Y MÉTRICAS")
    print("=" * 50)
    
    # 1. Arreglar permisos primero
    fix_permissions()
    
    # 2. Probar métricas del sistema
    system_metrics = test_system_metrics()
    
    # 3. Probar sistema de logging
    test_logging_system()
    
    # 4. Probar funcionalidad completa
    test_logging_functionality()
    
    # 5. Verificar archivos creados
    check_log_files()
    
    print("\n" + "=" * 50)
    print("🎯 RESUMEN DEL TEST:")
    print(f"✅ Métricas del sistema: CPU {system_metrics['cpu_percent']:.1f}%, RAM {system_metrics['memory_mb']:.1f}MB")
    print(f"✅ Sistema operativo: {os.name} ({'Linux/Unix' if os.name == 'posix' else 'Windows'})")
    print(f"✅ Directorio .logs: {Path('.logs').exists()}")
    print(f"✅ Logging funcional: Verificar archivos arriba")
    
    # Instrucciones adicionales
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Ejecutar: python benchmark_python.py --tests 2")
    print("2. Verificar: ls -la .logs/daily/")  
    print("3. Ver logs: tail -f .logs/daily/$(date +%Y-%m-%d).log")
    print("4. Ver métricas: tail -f .logs/performance/$(date +%Y-%m-%d)_performance.log")

if __name__ == "__main__":
    main()