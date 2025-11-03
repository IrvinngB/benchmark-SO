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

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

@dataclass
class BenchmarkConfig:
    """Configuración del benchmark"""
    num_tests: int = 6
    default_requests: int = 100
    default_connections: int = 50
    timeout: int = 30
    results_dir: str = "benchmark_results_python"
    
    servers: Dict[str, str] = None
    endpoints: List[Dict] = None
    environments: List[Dict] = None
    
    def __post_init__(self):
        if self.servers is None:
            self.servers = {
                "local": "localhost:8000",
                "vps_no_docker": "138.68.233.15:8000",
                "vps_docker": "68.183.168.86:8000"
            }
        
        if self.endpoints is None:
            self.endpoints = [
                {"name": "Root Endpoint (Baseline)", "path": "/", "requests": 100},
                {"name": "Health Check", "path": "/health", "requests": 100},
                {"name": "Async Light", "path": "/async-light", "requests": 100},
                {"name": "Heavy Computation", "path": "/heavy", "requests": 1000},
                {"name": "Large JSON Response", "path": "/json-large?page=1&limit=50", "requests": 1000}
            ]
        
        if self.environments is None:
            self.environments = [
                {"name": "vps_no_docker", "label": "VPS Sin Docker", "ip": "138.68.233.15"},
                {"name": "vps_docker", "label": "VPS Con Docker", "ip": "68.183.168.86"}
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

# ============================================================================
# MONITOR DE RECURSOS
# ============================================================================

class SystemMonitor:
    """Monitor de recursos del sistema en tiempo real"""
    
    def __init__(self):
        self.console = Console()
        self.metrics_queue = queue.Queue()
        self.monitoring = False
        self.metrics_history = []
        
    def start_monitoring(self):
        """Inicia el monitoreo en un hilo separado"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Detiene el monitoreo"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2)
    
    def _monitor_loop(self):
        """Loop principal del monitoreo"""
        while self.monitoring:
            try:
                # Obtener métricas del sistema
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                network = psutil.net_io_counters()
                disk = psutil.disk_io_counters()
                
                metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_mb=memory.used / (1024 * 1024),
                    network_sent=network.bytes_sent,
                    network_recv=network.bytes_recv,
                    disk_io_read=disk.read_bytes if disk else 0,
                    disk_io_write=disk.write_bytes if disk else 0
                )
                
                self.metrics_queue.put(metrics)
                self.metrics_history.append(metrics)
                
                time.sleep(0.5)  # Monitorear cada 500ms
                
            except Exception as e:
                self.console.print(f"[red]Error en monitoreo: {e}[/red]")
                
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
        self.monitor = SystemMonitor()
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
        
        try:
            async with self.session.get(health_url) as response:
                if response.status == 200:
                    self.console.print(f"[green]✅ Servidor accesible: {health_url}[/green]")
                    return True
                else:
                    self.console.print(f"[red]❌ Servidor responde con código {response.status}[/red]")
                    return False
        except Exception as e:
            self.console.print(f"[red]❌ Error de conectividad: {e}[/red]")
            return False
    
    async def single_request(self, url: str) -> Tuple[bool, float, int]:
        """Realiza una request individual y mide latencia"""
        start_time = time.perf_counter()
        try:
            async with self.session.get(url) as response:
                content = await response.read()
                end_time = time.perf_counter()
                
                latency_ms = (end_time - start_time) * 1000
                response_size = len(content)
                success = 200 <= response.status < 400
                
                return success, latency_ms, response_size
                
        except Exception as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            return False, latency_ms, 0
    
    async def benchmark_endpoint(
        self, 
        endpoint: Dict[str, any], 
        environment: Dict[str, str],
        test_number: int,
        semaphore: asyncio.Semaphore
    ) -> BenchmarkResult:
        """Ejecuta benchmark para un endpoint específico"""
        
        server_addr = self.config.servers[environment["name"]]
        url = f"http://{server_addr}{endpoint['path']}"
        num_requests = endpoint['requests']
        
        # Métricas de sistema al inicio
        start_time = datetime.now()
        start_metrics = self.monitor.get_current_metrics()
        
        # Preparar semáforo para controlar concurrencia
        async with semaphore:
            # Listas para almacenar resultados
            latencies = []
            response_sizes = []
            successes = 0
            failures = 0
            
            # Crear tareas concurrentes
            tasks = []
            benchmark_start = time.perf_counter()
            
            for _ in range(num_requests):
                task = asyncio.create_task(self.single_request(url))
                tasks.append(task)
            
            # Ejecutar todas las requests
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            benchmark_end = time.perf_counter()
            total_time = benchmark_end - benchmark_start
            
            # Procesar resultados
            for result in results:
                if isinstance(result, Exception):
                    failures += 1
                    latencies.append(0)
                    response_sizes.append(0)
                else:
                    success, latency, size = result
                    if success:
                        successes += 1
                    else:
                        failures += 1
                    latencies.append(latency)
                    response_sizes.append(size)
        
        # Métricas de sistema al final
        end_time = datetime.now()
        end_metrics = self.monitor.get_current_metrics()
        
        # Calcular estadísticas
        valid_latencies = [l for l in latencies if l > 0]
        
        if valid_latencies:
            avg_latency = statistics.mean(valid_latencies)
            min_latency = min(valid_latencies)
            max_latency = max(valid_latencies)
            p50_latency = np.percentile(valid_latencies, 50)
            p95_latency = np.percentile(valid_latencies, 95)
            p99_latency = np.percentile(valid_latencies, 99)
        else:
            avg_latency = min_latency = max_latency = p50_latency = p95_latency = p99_latency = 0
        
        # Calcular throughput
        rps = num_requests / total_time if total_time > 0 else 0
        total_bytes = sum(response_sizes)
        throughput_mbps = (total_bytes * 8) / (total_time * 1024 * 1024) if total_time > 0 else 0
        error_rate = (failures / num_requests) * 100 if num_requests > 0 else 0
        
        # Métricas de sistema (promedio durante el período)
        period_metrics = self.monitor.get_metrics_during_period(start_time, end_time)
        
        if period_metrics:
            avg_cpu = statistics.mean([m.cpu_percent for m in period_metrics])
            avg_memory = statistics.mean([m.memory_mb for m in period_metrics])
            network_sent = max([m.network_sent for m in period_metrics]) - min([m.network_sent for m in period_metrics])
            network_recv = max([m.network_recv for m in period_metrics]) - min([m.network_recv for m in period_metrics])
        else:
            avg_cpu = avg_memory = network_sent = network_recv = 0
        
        return BenchmarkResult(
            timestamp=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            test_number=test_number,
            environment=environment["name"],
            endpoint_name=endpoint["name"],
            url=url,
            requests_per_second=rps,
            avg_latency_ms=avg_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            total_requests=num_requests,
            successful_requests=successes,
            failed_requests=failures,
            error_rate=error_rate,
            total_time_seconds=total_time,
            throughput_mbps=throughput_mbps,
            cpu_usage_percent=avg_cpu,
            memory_usage_mb=avg_memory,
            network_bytes_sent=network_sent,
            network_bytes_recv=network_recv
        )

# ============================================================================
# VISUALIZACIÓN Y ANÁLISIS
# ============================================================================

class BenchmarkAnalyzer:
    """Analizador y visualizador de resultados"""
    
    def __init__(self, results_dir: str):
        self.results_dir = Path(results_dir)
        self.console = Console()
        
        # Configurar estilo de matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def save_results(self, results: List[BenchmarkResult], timestamp: str):
        """Guarda resultados en múltiples formatos"""
        self.results_dir.mkdir(exist_ok=True)
        
        # Convertir a DataFrame
        df = pd.DataFrame([asdict(result) for result in results])
        
        # CSV detallado
        csv_path = self.results_dir / f"benchmark_detailed_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        self.console.print(f"[green]✅ CSV guardado: {csv_path}[/green]")
        
        # JSON estructurado
        json_path = self.results_dir / f"benchmark_detailed_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump([asdict(result) for result in results], f, indent=2, ensure_ascii=False)
        self.console.print(f"[green]✅ JSON guardado: {json_path}[/green]")
        
        # Excel con múltiples hojas
        excel_path = self.results_dir / f"benchmark_analysis_{timestamp}.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Raw Data', index=False)
            
            # Resumen por entorno
            summary = df.groupby(['environment', 'endpoint_name']).agg({
                'requests_per_second': ['mean', 'std', 'min', 'max'],
                'avg_latency_ms': ['mean', 'std', 'min', 'max'],
                'error_rate': ['mean', 'max'],
                'cpu_usage_percent': ['mean', 'max'],
                'memory_usage_mb': ['mean', 'max']
            }).round(2)
            
            summary.to_excel(writer, sheet_name='Summary')
            
        self.console.print(f"[green]✅ Excel guardado: {excel_path}[/green]")
        
        return df
    
    def create_visualizations(self, df: pd.DataFrame, timestamp: str):
        """Crea visualizaciones detalladas"""
        viz_dir = self.results_dir / f"visualizations_{timestamp}"
        viz_dir.mkdir(exist_ok=True)
        
        # 1. Comparación de RPS por endpoint y entorno
        plt.figure(figsize=(15, 8))
        sns.boxplot(data=df, x='endpoint_name', y='requests_per_second', hue='environment')
        plt.title('Requests per Second por Endpoint y Entorno')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(viz_dir / 'rps_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Latencia por percentiles
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        latency_cols = ['avg_latency_ms', 'p50_latency_ms', 'p95_latency_ms', 'p99_latency_ms']
        titles = ['Latencia Promedio', 'Latencia P50', 'Latencia P95', 'Latencia P99']
        
        for i, (col, title) in enumerate(zip(latency_cols, titles)):
            ax = axes[i // 2, i % 2]
            sns.boxplot(data=df, x='environment', y=col, ax=ax)
            ax.set_title(title)
            ax.set_ylabel('Latencia (ms)')
        
        plt.tight_layout()
        plt.savefig(viz_dir / 'latency_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Uso de recursos
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # CPU Usage
        sns.boxplot(data=df, x='environment', y='cpu_usage_percent', ax=axes[0])
        axes[0].set_title('Uso de CPU durante benchmarks')
        axes[0].set_ylabel('CPU (%)')
        
        # Memory Usage
        sns.boxplot(data=df, x='environment', y='memory_usage_mb', ax=axes[1])
        axes[1].set_title('Uso de Memoria durante benchmarks')
        axes[1].set_ylabel('Memoria (MB)')
        
        plt.tight_layout()
        plt.savefig(viz_dir / 'resource_usage.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Correlación entre métricas
        plt.figure(figsize=(12, 10))
        correlation_cols = ['requests_per_second', 'avg_latency_ms', 'cpu_usage_percent', 
                          'memory_usage_mb', 'error_rate', 'throughput_mbps']
        
        correlation_matrix = df[correlation_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, fmt='.2f')
        plt.title('Matriz de Correlación entre Métricas')
        plt.tight_layout()
        plt.savefig(viz_dir / 'correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 5. Timeline de performance
        plt.figure(figsize=(15, 8))
        for env in df['environment'].unique():
            env_data = df[df['environment'] == env]
            plt.plot(env_data['test_number'], env_data['requests_per_second'], 
                    marker='o', label=env, alpha=0.7)
        
        plt.title('Evolución del RPS a lo largo de las pruebas')
        plt.xlabel('Número de Test')
        plt.ylabel('Requests per Second')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(viz_dir / 'performance_timeline.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        self.console.print(f"[green]✅ Visualizaciones guardadas en: {viz_dir}[/green]")
        
    def generate_report(self, df: pd.DataFrame, timestamp: str) -> str:
        """Genera reporte estadístico detallado"""
        report_lines = []
        
        report_lines.append("# FastAPI Performance Benchmark Report")
        report_lines.append(f"**Fecha de ejecución:** {timestamp}")
        report_lines.append("")
        
        # Resumen ejecutivo
        report_lines.append("## Resumen Ejecutivo")
        report_lines.append("")
        
        for env in df['environment'].unique():
            env_data = df[df['environment'] == env]
            avg_rps = env_data['requests_per_second'].mean()
            avg_latency = env_data['avg_latency_ms'].mean()
            avg_cpu = env_data['cpu_usage_percent'].mean()
            
            report_lines.append(f"### {env.upper()}")
            report_lines.append(f"- **RPS Promedio:** {avg_rps:.2f}")
            report_lines.append(f"- **Latencia Promedio:** {avg_latency:.2f} ms")
            report_lines.append(f"- **CPU Promedio:** {avg_cpu:.2f}%")
            report_lines.append("")
        
        # Análisis detallado por endpoint
        report_lines.append("## Análisis por Endpoint")
        report_lines.append("")
        
        for endpoint in df['endpoint_name'].unique():
            report_lines.append(f"### {endpoint}")
            endpoint_data = df[df['endpoint_name'] == endpoint]
            
            comparison_table = endpoint_data.groupby('environment').agg({
                'requests_per_second': ['mean', 'std'],
                'avg_latency_ms': ['mean', 'std'],
                'error_rate': 'mean'
            }).round(2)
            
            report_lines.append(comparison_table.to_markdown())
            report_lines.append("")
        
        # Estadísticas de estabilidad
        report_lines.append("## Análisis de Estabilidad")
        report_lines.append("")
        
        for env in df['environment'].unique():
            env_data = df[df['environment'] == env]
            rps_cv = (env_data['requests_per_second'].std() / env_data['requests_per_second'].mean()) * 100
            latency_cv = (env_data['avg_latency_ms'].std() / env_data['avg_latency_ms'].mean()) * 100
            
            report_lines.append(f"### {env.upper()}")
            report_lines.append(f"- **Coeficiente de Variación RPS:** {rps_cv:.2f}%")
            report_lines.append(f"- **Coeficiente de Variación Latencia:** {latency_cv:.2f}%")
            report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        # Guardar reporte
        report_path = self.results_dir / f"benchmark_report_{timestamp}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.console.print(f"[green]✅ Reporte generado: {report_path}[/green]")
        return report_content

# ============================================================================
# INTERFAZ DE USUARIO
# ============================================================================

class BenchmarkUI:
    """Interfaz de usuario con Rich para visualización en tiempo real"""
    
    def __init__(self):
        self.console = Console()
        
    def show_header(self, config: BenchmarkConfig):
        """Muestra el header del benchmark"""
        self.console.print(Panel.fit(
            "[bold cyan]🚀 FastAPI Performance Benchmark - Python Edition[/bold cyan]\n\n"
            f"📊 Ejecutando {config.num_tests} pruebas por entorno\n"
            f"🎯 Total de pruebas: {config.num_tests * len(config.endpoints) * len(config.environments)}\n"
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
    """Ejecuta el benchmark completo"""
    
    ui = BenchmarkUI()
    analyzer = BenchmarkAnalyzer(config.results_dir)
    
    if verbose:
        ui.show_header(config)
    
    all_results = []
    
    async with AsyncBenchmarkEngine(config) as engine:
        # Iniciar monitoreo de sistema
        engine.monitor.start_monitoring()
        
        try:
            # Crear semáforo para controlar concurrencia
            semaphore = asyncio.Semaphore(config.default_connections)
            
            total_tests = config.num_tests * len(config.endpoints) * len(config.environments)
            current_test = 0
            
            for env in config.environments:
                # Verificar conectividad
                if not await engine.test_connectivity(env):
                    engine.console.print(f"[red]❌ Saltando entorno {env['name']} por falta de conectividad[/red]")
                    continue
                
                engine.console.print(f"\n[bold blue]🌍 Ejecutando benchmarks para {env['label']}[/bold blue]")
                
                # Ejecutar múltiples runs
                for test_num in range(1, config.num_tests + 1):
                    engine.console.print(f"\n[yellow]📍 Ejecución {test_num}/{config.num_tests}[/yellow]")
                    
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
                            engine.console.print(f"[red]Error en benchmark: {result}[/red]")
                        else:
                            all_results.append(result)
                            current_test += 1
                            
                            if verbose:
                                progress = (current_test / total_tests) * 100
                                engine.console.print(
                                    f"   ✅ [{progress:5.1f}%] {result.endpoint_name}: "
                                    f"{result.requests_per_second:.2f} RPS, "
                                    f"{result.avg_latency_ms:.2f}ms latency"
                                )
        
        finally:
            # Detener monitoreo
            engine.monitor.stop_monitoring()
    
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
    
    parser.add_argument('--tests', '-t', type=int, default=6,
                       help='Número de pruebas por entorno (default: 6)')
    parser.add_argument('--connections', '-c', type=int, default=50,
                       help='Conexiones concurrentes (default: 50)')
    parser.add_argument('--requests', '-r', type=int, default=100,
                       help='Requests por endpoint ligero (default: 100)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Timeout por request en segundos (default: 30)')
    parser.add_argument('--output', '-o', type=str, default='benchmark_results_python',
                       help='Directorio de resultados (default: benchmark_results_python)')
    parser.add_argument('--dashboard', '-d', action='store_true',
                       help='Iniciar dashboard web en puerto 5000')
    parser.add_argument('--verbose', '-v', action='store_true', default=True,
                       help='Output detallado')
    parser.add_argument('--analyze-only', '-a', type=str,
                       help='Solo analizar resultados existentes (ruta al directorio)')
    
    args = parser.parse_args()
    
    # Configurar benchmark
    config = BenchmarkConfig(
        num_tests=args.tests,
        default_connections=args.connections,
        default_requests=args.requests,
        timeout=args.timeout,
        results_dir=args.output
    )
    
    console = Console()
    
    # Solo análisis de datos existentes
    if args.analyze_only:
        analyzer = BenchmarkAnalyzer(args.analyze_only)
        
        # Buscar archivos CSV más recientes
        csv_files = list(Path(args.analyze_only).glob("benchmark_detailed_*.csv"))
        if csv_files:
            latest_csv = sorted(csv_files)[-1]
            df = pd.read_csv(latest_csv)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analyzer.create_visualizations(df, timestamp)
            report = analyzer.generate_report(df, timestamp)
            
            console.print("[green]✅ Análisis completado[/green]")
        else:
            console.print("[red]❌ No se encontraron archivos CSV en el directorio[/red]")
        return
    
    # Iniciar dashboard web si se solicita
    if args.dashboard:
        dashboard_thread = threading.Thread(target=create_live_dashboard, daemon=True)
        dashboard_thread.start()
        console.print("[green]🌐 Dashboard iniciado en http://localhost:5000[/green]")
    
    # Ejecutar benchmark
    async def run():
        try:
            console.print("[bold green]🚀 Iniciando benchmark...[/bold green]")
            
            results = await run_benchmark(config, args.verbose)
            
            if results:
                # Guardar y analizar resultados
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                analyzer = BenchmarkAnalyzer(config.results_dir)
                
                console.print(f"\n[bold cyan]📊 Procesando {len(results)} resultados...[/bold cyan]")
                
                df = analyzer.save_results(results, timestamp)
                analyzer.create_visualizations(df, timestamp)
                report = analyzer.generate_report(df, timestamp)
                
                console.print(f"\n[bold green]✅ Benchmark completado exitosamente[/bold green]")
                console.print(f"📁 Resultados guardados en: {config.results_dir}/")
                
                # Mostrar resumen rápido
                console.print("\n[bold cyan]📈 Resumen Rápido:[/bold cyan]")
                for env in config.environments:
                    env_results = [r for r in results if r.environment == env['name']]
                    if env_results:
                        avg_rps = statistics.mean([r.requests_per_second for r in env_results])
                        avg_latency = statistics.mean([r.avg_latency_ms for r in env_results])
                        console.print(f"  {env['label']}: {avg_rps:.2f} RPS, {avg_latency:.2f}ms latency")
                
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