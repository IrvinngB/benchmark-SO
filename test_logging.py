#!/usr/bin/env python3
"""
Test del Sistema de Logging
===========================
Prueba rápida para verificar que el sistema de logging funciona correctamente.
"""

import sys
import time
from pathlib import Path

# Importar LogManager
from logging_manager import get_log_manager


def test_logging_system():
    """Prueba del sistema de logging"""
    print("🧪 Iniciando prueba del sistema de logging...")
    
    # Obtener instancia de LogManager
    log_manager = get_log_manager()
    
    print("✅ LogManager inicializado correctamente")
    
    # Probar diferentes tipos de logs
    print("\n📝 Probando diferentes tipos de logs...")
    
    # 1. Logs generales
    log_manager.log_info("Test: Mensaje de información general", category="general")
    log_manager.log_debug("Test: Mensaje de debug", category="general")
    
    # 2. Logs de configuración
    config_test = {
        'num_tests': 5,
        'default_requests': 100,
        'environments': [
            {'name': 'test_env', 'label': 'Test Environment'}
        ]
    }
    log_manager.log_benchmark_start(config_test)
    
    # 3. Logs de conectividad
    log_manager.log_connectivity_test('test_env', 'http://test.example.com', True, 25.3)
    log_manager.log_connectivity_test('test_env2', 'http://test2.example.com', False, 0)
    
    # 4. Logs de rendimiento
    test_result = {
        'endpoint_name': 'Test Endpoint',
        'environment': 'test_env',
        'requests_per_second': 150.5,
        'avg_latency_ms': 45.2,
        'p95_latency_ms': 78.9,
        'p99_latency_ms': 125.3,
        'error_rate': 0.5,
        'cpu_usage_percent': 35.7,
        'memory_usage_mb': 256.8,
        'failed_requests': 1,
        'total_requests': 200
    }
    log_manager.log_endpoint_result(test_result)
    
    # 5. Logs de errores y advertencias
    log_manager.log_warning("Test: Mensaje de advertencia")
    log_manager.log_error("Test: Mensaje de error simulado", exc_info=False)
    
    # 6. Logs de entorno
    log_manager.log_environment_start({'name': 'test_env', 'label': 'Test Environment'})
    log_manager.log_environment_end('test_env', True)
    
    # 7. Métricas del sistema
    test_metrics = {
        'cpu_percent': 42.5,
        'memory_mb': 1024.8,
        'network_sent': 50000,
        'network_recv': 75000
    }
    log_manager.log_system_metrics(test_metrics)
    
    # 8. Resumen final
    test_summary = {
        'total_time': 125.67,
        'total_tests': 15,
        'successful_tests': 14,
        'failed_tests': 1,
        'avg_rps': 145.2,
        'avg_latency_ms': 52.8
    }
    log_manager.log_summary(test_summary)
    log_manager.log_benchmark_end(125.67, 15)
    
    print("✅ Logs de prueba generados correctamente")
    
    # Verificar archivos creados
    print("\n📁 Verificando archivos de log creados...")
    
    log_summary = log_manager.get_log_files_summary()
    
    for category, files in log_summary.items():
        if files:
            print(f"  📂 {category.capitalize()}: {len(files)} archivo(s)")
            for file in files[:3]:  # Mostrar solo los primeros 3
                print(f"    - {file}")
            if len(files) > 3:
                print(f"    ... y {len(files) - 3} más")
        else:
            print(f"  📂 {category.capitalize()}: Sin archivos")
    
    print("\n✅ Sistema de logging funcionando correctamente!")
    print("\n🔍 Para ver los logs generados:")
    print("   - Logs generales:     .logs/daily/")
    print("   - Logs de errores:    .logs/errors/") 
    print("   - Logs de rendimiento: .logs/performance/")
    
    return True


if __name__ == "__main__":
    try:
        success = test_logging_system()
        
        if success:
            print("\n🎉 ¡Prueba del sistema de logging exitosa!")
            sys.exit(0)
        else:
            print("\n❌ Prueba fallida")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n💥 Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)