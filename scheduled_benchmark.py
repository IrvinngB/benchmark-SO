#!/usr/bin/env python3
"""
Script de Benchmark Programado
===============================
Script wrapper para ejecuciones programadas del benchmark.
Carga la configuración de servidores y ejecuta el benchmark diario.

Uso:
    python scheduled_benchmark.py
    python scheduled_benchmark.py --config benchmark_config_servers.json
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from logging_manager import get_log_manager
from daily_benchmark import DailyBenchmarkRunner


async def main():
    """Ejecutar benchmark programado"""
    parser = argparse.ArgumentParser(
        description="Benchmark Programado para Servidores Remotos"
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='benchmark_config_servers.json',
        help='Archivo de configuración (default: benchmark_config_servers.json)'
    )
    
    parser.add_argument(
        '--log-dir',
        type=str,
        default='.logs_scheduled',
        help='Directorio de logs (default: .logs_scheduled)'
    )
    
    args = parser.parse_args()
    
    # Verificar que existe el archivo de configuración
    if not Path(args.config).exists():
        print(f"❌ Error: No se encontró el archivo de configuración: {args.config}")
        print(f"💡 Asegúrate de que el archivo existe en el directorio actual")
        sys.exit(1)
    
    # Crear instancia del runner
    print(f"🚀 Iniciando benchmark programado...")
    print(f"📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚙️  Configuración: {args.config}")
    print(f"📝 Logs: {args.log_dir}")
    print("-" * 60)
    
    runner = DailyBenchmarkRunner(
        config_file=args.config,
        log_dir=args.log_dir
    )
    
    # Ejecutar benchmark
    success, result = await runner.run()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ BENCHMARK COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"📊 Tests ejecutados: {result.get('total_tests_executed', 0)}")
        print(f"🌐 Entornos probados: {', '.join(result.get('environments_tested', []))}")
        print(f"📍 Endpoints probados: {len(result.get('endpoints_tested', []))}")
        print(f"⏱️  Duración: {result.get('execution_duration_seconds', 0):.1f} segundos")
        print(f"📈 RPS Promedio: {result.get('avg_rps', 0):.2f}")
        print(f"⚡ Latencia Promedio: {result.get('avg_latency_ms', 0):.2f} ms")
        print(f"❌ Tasa de Error: {result.get('error_rate_percent', 0):.2f}%")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ BENCHMARK FALLÓ")
        print("=" * 60)
        print(f"💥 Error: {result.get('error', 'Error desconocido')}")
        print(f"📝 Revisa los logs en: {args.log_dir}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
