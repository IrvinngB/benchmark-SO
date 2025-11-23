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
    min_latency_ms: float
    max_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    total_time_seconds: float
    throughput_mbps: float
    cpu_usage_percent: float
    memory_usage_mb: float
    network_bytes_sent: int
    network_bytes_recv: int
    process_cpu_percent: float = 0.0
    process_memory_mb: float = 0.0
    jitter_ms: float = 0.0

@dataclass
class SystemMetrics:
    """Métricas del sistema durante el benchmark"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    network_sent: int
    network_recv: int
    disk_io_read: int
    disk_io_write: int
    process_cpu_percent: float = 0.0
    process_memory_mb: float = 0.0

# ============================================================================
# MONITOR DE RECURSOS
# ============================================================================

class SystemMonitor:
    """Monitor de recursos del sistema en tiempo real"""
    
    def __init__(self, target_process_name: str = "uvicorn"):
        self.console = Console()
        self.metrics_queue = queue.Queue()
        self.monitoring = False
        self.metrics_history = []
        self.target_process_name = target_process_name
        self.target_process = None
        self._monitor_thread = None

    def start_monitoring(self):
        """Inicia el monitoreo en un hilo separado"""
        self.monitoring = True
        self.metrics_queue = queue.Queue()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
    def stop_monitoring(self):
        """Detiene el monitoreo"""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
            
    def _find_process(self):
        """Intenta encontrar el proceso objetivo"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Buscar por nombre o línea de comando
                if self.target_process_name in proc.info['name'] or \
                   (proc.info['cmdline'] and any(self.target_process_name in arg for arg in proc.info['cmdline'])):
                    self.target_process = proc
                    # self.console.print(f"[green]✅ Proceso encontrado: {proc.info['name']} (PID: {proc.info['pid']})[/green]")
                    return
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def _monitor_loop(self):
        """Loop principal del monitoreo"""
        log_manager = get_log_manager()  # Obtener instancia del LogManager
        while self.monitoring:
            try:
                # Obtener métricas del sistema global
                cpu_percent = psutil.cpu_percent(interval=0.5)
                memory = psutil.virtual_memory()
                network = psutil.net_io_counters()
                disk = psutil.disk_io_counters()
                
                # Métricas del proceso específico
                proc_cpu = 0.0
                proc_mem = 0.0
                
                if self.target_process:
                    try:
                        with self.target_process.oneshot():
                            proc_cpu = self.target_process.cpu_percent()
                            proc_mem = self.target_process.memory_info().rss / (1024 * 1024)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        self.target_process = None  # Proceso perdido
                        self._find_process() # Intentar encontrarlo de nuevo
                else:
                     self._find_process() # Intentar encontrarlo si no lo tenemos
                
                metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_mb=memory.used / (1024 * 1024),
                    network_sent=network.bytes_sent,
                    network_recv=network.bytes_recv,
                    disk_io_read=disk.read_bytes if disk else 0,
                    disk_io_write=disk.write_bytes if disk else 0,
                    process_cpu_percent=proc_cpu,
                    process_memory_mb=proc_mem
                )
                
                self.metrics_queue.put(metrics)
                self.metrics_history.append(metrics)
                
                # Log de métricas del sistema
                log_msg = (
                    f"CPU: {cpu_percent:.1f}% | RAM: {memory.used/(1024*1024):.1f}MB"
                )
                if self.target_process:
                    log_msg += f" | Proc CPU: {proc_cpu:.1f}% | Proc RAM: {proc_mem:.1f}MB"
                
                log_manager.system_logger.debug(log_msg)
                
            except Exception as e:
                # self.console.print(f"[red]Error en monitoreo: {e}[/red]")
                pass
                
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Obtiene las métricas actuales"""
        try:
            return self.metrics_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_metrics_during_period(self, start_time: datetime, end_time: datetime) -> List[SystemMetrics]:
        """Obtiene métricas durante un período específico"""
        return [m for m in self.metrics_history 
                if start_time <= m.timestamp <= end_time]

# ============================================================================
# BENCHMARK ENGINE
# ============================================================================

class AsyncBenchmarkEngine:
    """Motor de benchmarking asíncrono con aiohttp"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.console = Console()
        self.monitor = SystemMonitor(target_process_name=config.target_process_name)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        # Configurar la sesión HTTP con optimizaciones
        connector = aiohttp.TCPConnector(
            limit=200,  # Pool de conexiones
            limit_per_host=100,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'FastAPI-Benchmark-Python/1.0'}
        )
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_connectivity(self, environment: Dict[str, str]) -> bool:
        """Verifica la conectividad con el servidor"""
        server_addr = self.config.servers[environment["name"]]
        health_url = f"http://{server_addr}/health"
        log_manager = get_log_manager()
        
        try:
            start_time = time.perf_counter()
            async with self.session.get(health_url) as response:
                end_time = time.perf_counter()
                response_time_ms = (end_time - start_time) * 1000
                
                if response.status == 200:
                    self.console.print(f"[green]✅ Servidor accesible: {health_url}[/green]")
                    log_manager.log_connectivity_test(environment["name"], health_url, True, response_time_ms)
                    return True
                else:
                    self.console.print(f"[red]❌ Servidor responde con código {response.status}[/red]")
                    log_manager.log_connectivity_test(environment["name"], health_url, False, response_time_ms)
                    return False
        except Exception as e:
            self.console.print(f"[red]❌ Error de conectividad: {e}[/red]")
            log_manager.log_connectivity_test(environment["name"], health_url, False)
            log_manager.log_error(f"Error de conectividad en {health_url}: {str(e)}", exc_info=False)
            return False
    
    async def single_request(self, url: str) -> Tuple[bool, float, int]:
        """Realiza una request individual y mide latencia"""
        log_manager = get_log_manager()
        start_time = time.perf_counter()
        try:
            async with self.session.get(url) as response:
                content = await response.read()
                end_time = time.perf_counter()
                
                latency_ms = (end_time - start_time) * 1000
                response_size = len(content)
                success = 200 <= response.status < 400
                
                if not success:
                    log_manager.log_warning(f"Request failed: {url} -> Status {response.status}")
                
                return success, latency_ms, response_size
                
        except Exception as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            log_manager.log_error(f"Request error: {url} -> {str(e)}", exc_info=False)
            return False, latency_ms, 0

    async def benchmark_endpoint(self, endpoint: str, env: Dict[str, str], test_num: int, semaphore: asyncio.Semaphore):
        """Realiza un benchmark en un endpoint específico"""
        # Iniciar monitoreo de recursos
        self.monitor.start_monitoring()
        
        # Crear tarea para el endpoint actual
        task = asyncio.create_task(
            self._benchmark_endpoint_task(endpoint, env, test_num, semaphore)
        )
        
        # Ejecutar la tarea y esperar su finalización
        result = await task
        
        # Detener monitoreo
        self.monitor.stop_monitoring()
        
        return result

    async def _benchmark_endpoint_task(self, endpoint: str, env: Dict[str, str], test_num: int, semaphore: asyncio.Semaphore):
        """Tarea para benchmark de un endpoint"""
        log_manager = get_log_manager()
        url = f"http://{self.config.servers[env['name']]}{endpoint}"
        num_requests = self.config.endpoints[endpoint].requests
        
        async with semaphore:
            async with self.console.status(f"[bold green]Ejecutando prueba {test_num} en {endpoint}..."):
                start_time = time.perf_counter()
                results = await asyncio.gather(*[self.single_request(url) for _ in range(num_requests)])
                end_time = time.perf_counter()
                
                # Procesar resultados
                success_count = sum(1 for success, _, _ in results if success)
                total_latency_ms = sum(latency for _, latency, _ in results)
                total_response_size = sum(size for _, _, size in results)
                
                avg_latency_ms = total_latency_ms / num_requests
                requests_per_second = num_requests / (end_time - start_time)
                error_rate = (1 - success_count / num_requests) * 100
                
                # Registrar resultado del endpoint
                log_manager.log_endpoint_result({
                    "endpoint_name": endpoint,
                    "requests_per_second": requests_per_second,
                    "avg_latency_ms": avg_latency_ms,
                    "error_rate": error_rate,
                    "total_response_size": total_response_size
                })
                
                return {
                    "endpoint_name": endpoint,
                    "requests_per_second": requests_per_second,
                    "avg_latency_ms": avg_latency_ms,
                    "error_rate": error_rate,
                    "total_response_size": total_response_size
                }

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