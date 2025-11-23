#!/usr/bin/env python3
"""
Script de Ejecución Diaria - FastAPI Performance Benchmark
==========================================================
Script diseñado para ejecutarse automáticamente cada día durante 4 semanas.
Incluye logging completo, manejo de errores y reportes automáticos.

Uso:
    python daily_benchmark.py
    python daily_benchmark.py --config-file daily_config.json
    python daily_benchmark.py --tests 15 --skip-connectivity-check
"""

import sys
import argparse
import json
import traceback
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import time

# Importar módulos del proyecto
from logging_manager import get_log_manager
from benchmark_python import BenchmarkConfig, run_benchmark, BenchmarkAnalyzer


class DailyBenchmarkRunner:
    """Runner para ejecución diaria automatizada"""
    
    def __init__(self, config_file: str = None, log_dir: str = '.logs'):
        self.log_manager = get_log_manager(log_dir)
        self.config_file = config_file
        self.start_time = datetime.now()
        
        # Configuración por defecto para ejecuciones diarias
        self.default_config = {
            'num_tests': 10,
            'default_requests': 500,
            'default_connections': 100,
            'timeout': 60,
            'results_dir': 'resultados_diarios',
            'skip_connectivity_check': False,
            'max_retries': 3,
            'retry_delay_seconds': 60,
        }
    
    def load_config(self) -> dict:
        """Cargar configuración desde archivo o usar defaults"""
        config = self.default_config.copy()
        
        if self.config_file and Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config.update(file_config)
                self.log_manager.log_info(f"Configuración cargada desde: {self.config_file}", category="general")
            except Exception as e:
                self.log_manager.log_warning(f"Error cargando configuración desde archivo: {e}. Usando defaults.")
        
        return config
    
    def create_benchmark_config(self, config_dict: dict) -> BenchmarkConfig:
        """Crear objeto BenchmarkConfig"""
        benchmark_config = BenchmarkConfig(
            num_tests=config_dict['num_tests'],
            default_requests=config_dict['default_requests'],
            default_connections=config_dict['default_connections'],
            timeout=config_dict['timeout'],
            results_dir=config_dict['results_dir']
        )
        
        # Cargar servers, environments y endpoints si están en el config
        if 'servers' in config_dict:
            benchmark_config.servers = config_dict['servers']
        
        if 'environments' in config_dict:
            benchmark_config.environments = config_dict['environments']
        
        if 'endpoints' in config_dict:
            benchmark_config.endpoints = config_dict['endpoints']
        
        return benchmark_config
    
    def save_daily_config(self, config_dict: dict):
        """Guardar configuración usada para el día"""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        config_file = f"daily_config_{timestamp}.json"
        
        config_to_save = config_dict.copy()
        config_to_save['execution_date'] = self.start_time.isoformat()
        config_to_save['timestamp'] = timestamp
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            
            self.log_manager.log_info(f"Configuración del día guardada: {config_file}", category="general")
        except Exception as e:
            self.log_manager.log_warning(f"Error guardando configuración diaria: {e}")
    
    async def run_with_retries(self, benchmark_config: BenchmarkConfig, max_retries: int, retry_delay: int):
        """Ejecutar benchmark con reintentos automáticos"""
        last_exception = None
        
        for attempt in range(1, max_retries + 1):
            try:
                self.log_manager.log_info(f"Intento {attempt}/{max_retries} de ejecución", category="general")
                
                results = await run_benchmark(benchmark_config, verbose=True)
                
                if results and len(results) > 0:
                    self.log_manager.log_info(f"Benchmark exitoso en intento {attempt}", category="general")
                    return results
                else:
                    raise Exception("Benchmark retornó resultados vacíos")
            
            except Exception as e:
                last_exception = e
                self.log_manager.log_error(f"Intento {attempt} falló: {str(e)}", exc_info=True)
                
                if attempt < max_retries:
                    self.log_manager.log_info(f"Reintentando en {retry_delay} segundos...", category="general")
                    await asyncio.sleep(retry_delay)
                else:
                    self.log_manager.log_error(f"Todos los intentos ({max_retries}) fallaron", exc_info=False)
        
        raise last_exception
    
    def create_failure_report(self, error: Exception, config_dict: dict):
        """Crear reporte de fallo"""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        failure_report = {
            'execution_date': self.start_time.isoformat(),
            'timestamp': timestamp,
            'status': 'FAILED',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'config_used': config_dict,
            'execution_duration_seconds': (datetime.now() - self.start_time).total_seconds()
        }
        
        # Guardar reporte de fallo
        failure_file = f"failure_report_{timestamp}.json"
        try:
            with open(failure_file, 'w', encoding='utf-8') as f:
                json.dump(failure_report, f, indent=2, ensure_ascii=False)
            
            self.log_manager.log_info(f"Reporte de fallo guardado: {failure_file}", category="general")
        except Exception as save_error:
            self.log_manager.log_error(f"Error guardando reporte de fallo: {save_error}")
    
    def create_success_summary(self, results: list, config_dict: dict):
        """Crear resumen de éxito"""
        end_time = datetime.now()
        execution_duration = (end_time - self.start_time).total_seconds()
        
        # Calcular estadísticas básicas
        total_requests = sum(r.total_requests for r in results)
        total_errors = sum(r.failed_requests for r in results)
        avg_rps = sum(r.requests_per_second for r in results) / len(results) if results else 0
        avg_latency = sum(r.avg_latency_ms for r in results) / len(results) if results else 0
        
        summary = {
            'execution_date': self.start_time.isoformat(),
            'completion_date': end_time.isoformat(),
            'execution_duration_seconds': execution_duration,
            'status': 'SUCCESS',
            'total_tests_executed': len(results),
            'total_requests': total_requests,
            'total_errors': total_errors,
            'error_rate_percent': (total_errors / total_requests * 100) if total_requests else 0,
            'avg_rps': round(avg_rps, 2),
            'avg_latency_ms': round(avg_latency, 2),
            'environments_tested': list(set(r.environment for r in results)),
            'endpoints_tested': list(set(r.endpoint_name for r in results)),
            'config_used': config_dict
        }
        
        # Log del resumen
        self.log_manager.log_summary(summary)
        
        return summary
    
    async def run(self, **kwargs):
        """Ejecutar benchmark diario completo"""
        try:
            # Log de inicio
            self.log_manager.log_info(
                f"=== INICIO EJECUCIÓN DIARIA {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} ===", 
                category="general"
            )
            
            # Cargar configuración
            config_dict = self.load_config()
            
            # Aplicar argumentos de línea de comandos
            config_dict.update({k: v for k, v in kwargs.items() if v is not None})
            
            # Guardar configuración del día
            self.save_daily_config(config_dict)
            
            # Crear configuración de benchmark
            benchmark_config = self.create_benchmark_config(config_dict)
            
            # Ejecutar benchmark con reintentos
            results = await self.run_with_retries(
                benchmark_config,
                config_dict.get('max_retries', 3),
                config_dict.get('retry_delay_seconds', 60)
            )
            
            # Procesar y guardar resultados
            if results:
                timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
                analyzer = BenchmarkAnalyzer(benchmark_config.results_dir)
                
                # Guardar resultados
                df = analyzer.save_results(results, timestamp)
                analyzer.create_visualizations(df, timestamp)
                analyzer.generate_report(df, timestamp)
                
                # Crear resumen de éxito
                summary = self.create_success_summary(results, config_dict)
                
                self.log_manager.log_info(
                    f"=== EJECUCIÓN DIARIA COMPLETADA EXITOSAMENTE ({len(results)} resultados) ===", 
                    category="general"
                )
                
                return True, summary
            else:
                raise Exception("No se obtuvieron resultados del benchmark")
        
        except Exception as e:
            # Crear reporte de fallo
            self.create_failure_report(e, config_dict if 'config_dict' in locals() else {})
            
            self.log_manager.log_error(
                f"=== EJECUCIÓN DIARIA FALLÓ: {str(e)} ===", 
                exc_info=True
            )
            
            return False, {'error': str(e), 'traceback': traceback.format_exc()}


def create_default_config_file():
    """Crear archivo de configuración por defecto"""
    config = {
        "num_tests": 10,
        "default_requests": 500,
        "default_connections": 100,
        "timeout": 60,
        "results_dir": "resultados_diarios",
        "skip_connectivity_check": False,
        "max_retries": 3,
        "retry_delay_seconds": 60,
        "description": "Configuración por defecto para ejecuciones diarias de benchmarking"
    }
    
    with open('daily_config_default.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Archivo de configuración por defecto creado: daily_config_default.json")


def log_summary(self, summary: dict):
    """Registrar resumen completo de ejecución"""
    self.benchmark_logger.info("=" * 80)
    self.benchmark_logger.info("📊 RESUMEN DE EJECUCIÓN")
    self.benchmark_logger.info("=" * 80)
    
    for key, value in summary.items():
        if isinstance(value, (list, dict)):
            self.benchmark_logger.info(f"{key}: {json.dumps(value, indent=2)}")
        else:
            self.benchmark_logger.info(f"{key}: {value}")
    
    self.benchmark_logger.info("=" * 80)


async def main():
    parser = argparse.ArgumentParser(description="Ejecución Diaria de FastAPI Performance Benchmark")
    
    parser.add_argument('--config-file', type=str,
                       help='Archivo de configuración JSON')
    parser.add_argument('--log-dir', type=str, default='.logs',
                       help='Directorio de logs (default: .logs)')
    parser.add_argument('--tests', '-t', type=int,
                       help='Número de pruebas por entorno')
    parser.add_argument('--requests', '-r', type=int,
                       help='Requests por endpoint ligero')
    parser.add_argument('--connections', '-c', type=int,
                       help='Conexiones concurrentes')
    parser.add_argument('--timeout', type=int,
                       help='Timeout por request en segundos')
    parser.add_argument('--results-dir', type=str,
                       help='Directorio de resultados')
    parser.add_argument('--max-retries', type=int,
                       help='Número máximo de reintentos')
    parser.add_argument('--retry-delay', type=int,
                       help='Segundos entre reintentos')
    parser.add_argument('--create-config', action='store_true',
                       help='Crear archivo de configuración por defecto')
    
    args = parser.parse_args()
    
    # Crear archivo de configuración si se solicita
    if args.create_config:
        create_default_config_file()
        return
    
    # Crear y ejecutar runner
    runner = DailyBenchmarkRunner(
        config_file=args.config_file,
        log_dir=args.log_dir
    )
    
    # Preparar argumentos para la ejecución
    run_kwargs = {
        'num_tests': args.tests,
        'default_requests': args.requests,
        'default_connections': args.connections,
        'timeout': args.timeout,
        'results_dir': args.results_dir,
        'max_retries': args.max_retries,
        'retry_delay_seconds': args.retry_delay,
    }
    
    # Ejecutar
    success, result = await runner.run(**run_kwargs)
    
    if success:
        print("✅ Ejecución diaria completada exitosamente")
        print(f"📊 Resultados: {result.get('total_tests_executed', 0)} tests ejecutados")
        print(f"⏱️  Duración: {result.get('execution_duration_seconds', 0):.1f} segundos")
        sys.exit(0)
    else:
        print("❌ Ejecución diaria falló")
        print(f"💥 Error: {result.get('error', 'Error desconocido')}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())