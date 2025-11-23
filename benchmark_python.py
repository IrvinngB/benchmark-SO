#!/usr/bin/env python3
"""
FastAPI Performance Benchmark - Python Edition
==============================================
Script avanzado de benchmarking con monitoreo en tiempo real de recursos,
visualización de datos, y análisis estadístico detallado.

Features:
- Monitoreo en tiempo real de CPU/RAM
- Benchmarking concurrente con asyncio/aiohttp
- Visualización de métricas en vivo
- Análisis estadístico avanzado
- Exportación a múltiples formatos
- Dashboard web opcional con Flask

Dependencias:
pip install aiohttp asyncio psutil matplotlib pandas seaborn tqdm rich flask plotly
"""

import asyncio
import aiohttp
import time
import json
import csv
import statistics
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psutil
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import argparse
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.live import Live
from rich.panel import Panel
from rich import box
import warnings
warnings.filterwarnings('ignore')

# Importar LogManager
from logging_manager import get_log_manager

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

#!/usr/bin/env python3
"""
FastAPI Performance Benchmark - Python Edition
==============================================
Script avanzado de benchmarking con monitoreo en tiempo real de recursos,
visualización de datos, y análisis estadístico detallado.

Features:
- Monitoreo en tiempo real de CPU/RAM
- Benchmarking concurrente con asyncio/aiohttp
- Visualización de métricas en vivo
- Análisis estadístico avanzado
- Exportación a múltiples formatos
- Dashboard web opcional con Flask

Dependencias:
pip install aiohttp asyncio psutil matplotlib pandas seaborn tqdm rich flask plotly
"""

import asyncio
import aiohttp
import time
import json
import csv
import statistics
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psutil
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import argparse
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.live import Live
from rich.panel import Panel
from rich import box
import warnings
warnings.filterwarnings('ignore')

# Importar LogManager
from logging_manager import get_log_manager

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

@dataclass
class BenchmarkConfig:
    """Configuración del benchmark"""
    num_tests: int = 10
    default_requests: int = 500
    default_connections: int = 100
    timeout: int = 60
    target_process_name: str = "uvicorn"  # Nombre del proceso a monitorear
    results_dir: str = "resultados_nuevos"
    
    servers: Dict[str, str] = None
    endpoints: List[Dict] = None
    environments: List[Dict] = None
    
    def __post_init__(self):
        if self.servers is None:
            self.servers = {
                "local_docker": "localhost:8000"
            }
        
        if self.endpoints is None:
            self.endpoints = [
                {"name": "Root Endpoint (Baseline)", "path": "/", "requests": 500},
                {"name": "Health Check", "path": "/health", "requests": 500},
                {"name": "Async Light", "path": "/async-light", "requests": 750},
                {"name": "Heavy Computation", "path": "/heavy", "requests": 2000},
                {"name": "Large JSON Response", "path": "/json-large?page=1&limit=50", "requests": 1500}
            ]
        
        if self.environments is None:
            self.environments = [
                {"name": "local_docker", "label": "Docker Local", "ip": "localhost"}
            ]

@dataclass
class BenchmarkResult:
    """Resultado de una prueba individual"""
    timestamp: str
    test_number: int
    environment: str
    endpoint_name: str
    url: str
    requests_per_second: float
    avg_latency_ms: float
class BenchmarkUI:
    """Interfaz de usuario con Rich para visualización en tiempo real"""
    
    def __init__(self):
        self.console = Console()
        
    def show_header(self, config: BenchmarkConfig):
        """Muestra el header del benchmark"""
        self.console.print(Panel.fit(
            "[bold cyan]🚀 FastAPI Performance Benchmark - Python Edition[/bold cyan]\n\n"
            f"📊 Ejecutando {config.num_tests} pruebas en Docker Local\n"
            f"🎯 Total de pruebas: {config.num_tests * len(config.endpoints)} (modo ALTO VOLUMEN)\n"
            f"🐳 Entorno: Docker en localhost:8000\n"
            f"⚡ Motor: AsyncIO + aiohttp\n"
            f"📈 Monitoreo: CPU, RAM, Network en tiempo real",
            title="Benchmark Configuration",
            border_style="bright_blue"
        ))
    
    def create_progress_table(self) -> Table:
        """Crea tabla de progreso en tiempo real"""
        table = Table(title="Progreso del Benchmark", box=box.ROUNDED)
        table.add_column("Entorno", style="cyan")
        table.add_column("Endpoint", style="magenta")
        table.add_column("Test", style="yellow")
        table.add_column("RPS", style="green")
        table.add_column("Latencia (ms)", style="blue")
        table.add_column("CPU %", style="red")
        table.add_column("Estado", style="bright_green")
        
        return table
    
    def update_progress_table(self, table: Table, result: BenchmarkResult):
        """Actualiza la tabla de progreso"""
        table.add_row(
            result.environment,
            result.endpoint_name,
            str(result.test_number),
            f"{result.requests_per_second:.2f}",
            f"{result.avg_latency_ms:.2f}",
            f"{result.cpu_usage_percent:.1f}",
            "✅" if result.error_rate < 1 else "⚠️"
        )

# ============================================================================
# MAIN BENCHMARK RUNNER
# ============================================================================

async def run_benchmark(config: BenchmarkConfig, verbose: bool = True) -> List[BenchmarkResult]:
    """Ejecuta el benchmark completo con logging integrado"""
    
    # Obtener instancia del LogManager
    log_manager = get_log_manager()
    
    # Registrar inicio del benchmark
    log_manager.log_benchmark_start(asdict(config) if hasattr(config, '__dict__') else config.__dict__)
    
    ui = BenchmarkUI()
    analyzer = BenchmarkAnalyzer(config.results_dir)
    
    if verbose:
        ui.show_header(config)
    
    all_results = []
    benchmark_start_time = time.perf_counter()
    
    async with AsyncBenchmarkEngine(config) as engine:
        # Iniciar monitoreo de sistema
        engine.monitor.start_monitoring()
        log_manager.log_info("Monitoreo de recursos iniciado", category="general")
        
        try:
            # Crear semáforo para controlar concurrencia
            semaphore = asyncio.Semaphore(config.default_connections)
            
            total_tests = config.num_tests * len(config.endpoints) * len(config.environments)
            current_test = 0
            
            for env in config.environments:
                # Verificar conectividad
                if not await engine.test_connectivity(env):
                    engine.console.print(f"[red]❌ Saltando entorno {env['name']} por falta de conectividad[/red]")
                    log_manager.log_warning(f"Entorno {env['name']} omitido por falta de conectividad")
                    continue
                
                # Registrar inicio de entorno
                log_manager.log_info(f"Iniciando benchmarks para entorno: {env['label']}")
                engine.console.print(f"\n[bold blue]🌍 Ejecutando benchmarks para {env['label']}[/bold blue]")
                
                # Ejecutar múltiples runs
                for test_num in range(1, config.num_tests + 1):
                    engine.console.print(f"\n[yellow]📍 Ejecución {test_num}/{config.num_tests}[/yellow]")
                    log_manager.log_info(f"Ejecutando test {test_num}/{config.num_tests}")
                    
                    # Crear tareas para todos los endpoints del run actual
                    tasks = []
                    for endpoint in config.endpoints:
                        task = asyncio.create_task(
                            engine.benchmark_endpoint(endpoint, env, test_num, semaphore)
                        )
                        tasks.append(task)
                    
                    # Ejecutar todos los endpoints del run concurrentemente
                    with engine.console.status(f"[bold green]Ejecutando prueba {test_num}..."):
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Procesar resultados
                    for result in results:
                        if isinstance(result, Exception):
                            error_msg = f"Error en benchmark: {str(result)}"
                            engine.console.print(f"[red]{error_msg}[/red]")
                            log_manager.log_error(error_msg, exc_info=False)
                        else:
                            all_results.append(result)
                            current_test += 1
                            
                            # Registrar resultado del endpoint
                            log_manager.log_endpoint_result(asdict(result))
                            
                            if verbose:
                                progress = (current_test / total_tests) * 100
                                engine.console.print(
                                    f"   ✅ [{progress:5.1f}%] {result.endpoint_name}: "
                                    f"{result.requests_per_second:.2f} RPS, "
                                    f"{result.avg_latency_ms:.2f}ms latency"
                                )
                
                # Registrar fin de entorno
                log_manager.log_info(f"Completados benchmarks para entorno: {env['label']}")
        
        except Exception as e:
            log_manager.log_error(f"Error crítico en benchmark: {str(e)}", exc_info=True)
            engine.console.print(f"[red]❌ Error crítico durante ejecución: {e}[/red]")
            raise
        
        finally:
            # Detener monitoreo
            engine.monitor.stop_monitoring()
            log_manager.log_info("Monitoreo de recursos detenido", category="general")
    
    # Registrar fin del benchmark y guardar resumen
    benchmark_end_time = time.perf_counter()
    total_time = benchmark_end_time - benchmark_start_time
    log_manager.log_benchmark_end(total_time, len(all_results))
    
    return all_results

def create_live_dashboard():
    """Crea dashboard web opcional con Flask (ejecutar en hilo separado)"""
    try:
        from flask import Flask, render_template_string, jsonify
        
        app = Flask(__name__)
        
        @app.route('/')
        def dashboard():
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>FastAPI Benchmark Dashboard</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .metric { display: inline-block; margin: 10px; padding: 15px; 
                             border: 1px solid #ddd; border-radius: 8px; }
                </style>
            </head>
            <body>
                <h1>🚀 FastAPI Benchmark Dashboard</h1>
                <div id="metrics"></div>
                <div id="chart" style="width:100%; height:400px;"></div>
                
                <script>
                    // Actualizar métricas cada 2 segundos
                    setInterval(function() {
                        fetch('/api/metrics')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('metrics').innerHTML = 
                                '<div class="metric"><h3>CPU: ' + data.cpu + '%</h3></div>' +
                                '<div class="metric"><h3>RAM: ' + data.memory + ' MB</h3></div>' +
                                '<div class="metric"><h3>Tests: ' + data.tests_completed + '</h3></div>';
                        });
                    }, 2000);
                </script>
            </body>
            </html>
            """)
        
        @app.route('/api/metrics')
        def api_metrics():
            # En una implementación real, esto vendría de las métricas actuales
            return jsonify({
                'cpu': psutil.cpu_percent(),
                'memory': round(psutil.virtual_memory().used / (1024*1024)),
                'tests_completed': 0  # Actualizar con progreso real
            })
        
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError:
        print("Flask no disponible. Dashboard web deshabilitado.")

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="FastAPI Performance Benchmark - Python Edition")
    
    parser.add_argument('--tests', '-t', type=int, default=10,
                       help='Número de pruebas por entorno (default: 10)')
    parser.add_argument('--connections', '-c', type=int, default=100,
                       help='Conexiones concurrentes (default: 100)')
    parser.add_argument('--requests', '-r', type=int, default=500,
                       help='Requests por endpoint ligero (default: 500)')
    parser.add_argument('--timeout', type=int, default=60,
                       help='Timeout por request en segundos (default: 60)')
    parser.add_argument('--output', '-o', type=str, default='resultados_nuevos',
                       help='Directorio de resultados (default: resultados_nuevos)')
    parser.add_argument('--dashboard', '-d', action='store_true',
                       help='Iniciar dashboard web en puerto 5000')
    parser.add_argument('--verbose', '-v', action='store_true', default=True,
                       help='Output detallado')
    parser.add_argument('--analyze-only', '-a', type=str,
                       help='Solo analizar resultados existentes (ruta al directorio)')
    parser.add_argument('--log-dir', type=str, default='logs',
                       help='Directorio para logs (default: logs)')
    
    args = parser.parse_args()
    
    # Inicializar LogManager con directorio personalizado
    log_manager = get_log_manager(args.log_dir)
    
    # Configurar benchmark
    config = BenchmarkConfig(
        num_tests=args.tests,
        default_connections=args.connections,
        default_requests=args.requests,
        timeout=args.timeout,
        results_dir=args.output
    )
    
    console = Console()
    log_manager.log_info(f"Iniciando FastAPI Performance Benchmark", category="general")
    log_manager.log_info(f"Argumentos: tests={args.tests}, connections={args.connections}, requests={args.requests}", category="config")
    
    # Solo análisis de datos existentes
    if args.analyze_only:
        log_manager.log_info(f"Ejecutando modo análisis-solo para directorio: {args.analyze_only}", category="general")
        analyzer = BenchmarkAnalyzer(args.analyze_only)
        
        # Buscar archivos CSV más recientes
        csv_files = list(Path(args.analyze_only).glob("benchmark_detailed_*.csv"))
        if csv_files:
            latest_csv = sorted(csv_files)[-1]
            log_manager.log_info(f"Analizando archivo: {latest_csv}", category="general")
            df = pd.read_csv(latest_csv)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analyzer.create_visualizations(df, timestamp)
            report = analyzer.generate_report(df, timestamp)
            
            console.print("[green]✅ Análisis completado - Resultados en: resultados_muestra/[/green]")
            log_manager.log_info("Análisis completado exitosamente", category="general")
        else:
            console.print("[red]❌ No se encontraron archivos CSV en el directorio[/red]")
            log_manager.log_warning("No se encontraron archivos CSV para analizar")
        return
    
    # Iniciar dashboard web si se solicita
    if args.dashboard:
        dashboard_thread = threading.Thread(target=create_live_dashboard, daemon=True)
        dashboard_thread.start()
        console.print("[green]🌐 Dashboard iniciado en http://localhost:5000[/green]")
        log_manager.log_info("Dashboard web iniciado en http://localhost:5000", category="general")
    
    # Ejecutar benchmark
    async def run():
        try:
            console.print("[bold green]🚀 Iniciando benchmark...[/bold green]")
            log_manager.log_info("Iniciando ejecución del benchmark", category="general")
            
            results = await run_benchmark(config, args.verbose)
            
            if results:
                # Guardar y analizar resultados
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                analyzer = BenchmarkAnalyzer(config.results_dir)
                
                console.print(f"\n[bold cyan]📊 Procesando {len(results)} resultados...[/bold cyan]")
                log_manager.log_info(f"Procesando {len(results)} resultados de benchmark", category="general")
                
                df = analyzer.save_results(results, timestamp)
                analyzer.create_visualizations(df, timestamp)
                report = analyzer.generate_report(df, timestamp)
                
                console.print(f"\n[bold green]✅ Benchmark completado exitosamente[/bold green]")
                console.print(f"📁 Resultados guardados en: {config.results_dir}/")
                log_manager.log_info("Benchmark completado exitosamente", category="general")
                log_manager.log_info(f"Resultados guardados en: {config.results_dir}/", category="general")
                console.print(f"📋 Logs guardados en: logs/")
                console.print(f"📊 Archivos generados:")
                console.print(f"   - CSV detallado con todas las métricas")
                console.print(f"   - JSON estructurado para análisis")
                console.print(f"   - Excel con múltiples hojas y análisis automático")
                console.print(f"   - Reporte Markdown")
                console.print(f"   - Gráficos profesionales en carpeta visualizations_*")
                
                # Mostrar resumen rápido del entorno Docker local
                console.print("\n[bold cyan]📈 Resumen Docker Local:[/bold cyan]")
                if results:
                    avg_rps = statistics.mean([r.requests_per_second for r in results])
                    avg_latency = statistics.mean([r.avg_latency_ms for r in results])
                    max_rps = max([r.requests_per_second for r in results])
                    min_rps = min([r.requests_per_second for r in results])
                    avg_cpu = statistics.mean([r.cpu_usage_percent for r in results])
                    avg_error_rate = statistics.mean([r.error_rate for r in results])
                    
                    console.print(f"  📊 RPS - Promedio: {avg_rps:.2f} | Máximo: {max_rps:.2f} | Mínimo: {min_rps:.2f}")
                    console.print(f"  ⏱️  Latencia Promedio: {avg_latency:.2f}ms")
                    console.print(f"  🖥️  CPU Promedio: {avg_cpu:.1f}%")
                    console.print(f"  ❌ Tasa de Error: {avg_error_rate:.2f}%")
                    
                    # Mejores y peores endpoints
                    best_endpoint = max(results, key=lambda x: x.requests_per_second)
                    worst_endpoint = min(results, key=lambda x: x.requests_per_second)
                    console.print(f"  🥇 Mejor Endpoint: {best_endpoint.endpoint_name} ({best_endpoint.requests_per_second:.2f} RPS)")
                    console.print(f"  🔴 Endpoint con más carga: {worst_endpoint.endpoint_name} ({worst_endpoint.requests_per_second:.2f} RPS)")
                
            else:
                console.print("[red]❌ No se pudieron completar las pruebas[/red]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Benchmark interrumpido por el usuario[/yellow]")
        except Exception as e:
            console.print(f"\n[red]❌ Error durante el benchmark: {e}[/red]")
            raise
    
    # Ejecutar el benchmark asíncrono
    asyncio.run(run())

if __name__ == "__main__":
    main()