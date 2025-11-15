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
        log_manager = get_log_manager()  # Obtener instancia del LogManager
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
                
                # Log de métricas del sistema
                log_manager.system_logger.debug(
                    f"CPU: {cpu_percent:.1f}% | Memory: {memory.used/(1024*1024):.1f}MB | "
                    f"Disk R: {disk.read_bytes if disk else 0} | Disk W: {disk.write_bytes if disk else 0} | "
                    f"Net TX: {network.bytes_sent} | Net RX: {network.bytes_recv}"
                )
                
                time.sleep(0.5)  # Monitorear cada 500ms
                
            except Exception as e:
                self.console.print(f"[red]Error en monitoreo: {e}[/red]")
                log_manager.log_error(f"Error en monitoreo de sistema: {e}")
                
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
            log_manager.log_error(f"Request error: {url} -> {e}", exc_info=False)
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
        
        result = BenchmarkResult(
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
        
        # Log del resultado del endpoint
        log_manager = get_log_manager()
        log_manager.log_endpoint_result(asdict(result))
        
        return result

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
        
        # 1. Distribución de RPS por endpoint (Docker Local)
        plt.figure(figsize=(15, 8))
        sns.boxplot(data=df, x='endpoint_name', y='requests_per_second')
        plt.title('Distribución de Requests per Second por Endpoint (Docker Local)')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Requests per Second')
        
        # Agregar línea de promedio general
        overall_mean = df['requests_per_second'].mean()
        plt.axhline(y=overall_mean, color='red', linestyle='--', alpha=0.7, label=f'Promedio General: {overall_mean:.2f}')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(viz_dir / 'rps_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Análisis completo de latencia por percentiles
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        latency_cols = ['avg_latency_ms', 'p50_latency_ms', 'p95_latency_ms', 'p99_latency_ms']
        titles = ['Latencia Promedio', 'Latencia P50 (Mediana)', 'Latencia P95', 'Latencia P99']
        
        for i, (col, title) in enumerate(zip(latency_cols, titles)):
            ax = axes[i // 2, i % 2]
            sns.histplot(data=df, x=col, kde=True, ax=ax, alpha=0.7)
            ax.set_title(f'{title} - Docker Local')
            ax.set_xlabel('Latencia (ms)')
            ax.set_ylabel('Frecuencia')
            
            # Agregar línea de promedio
            mean_val = df[col].mean()
            ax.axvline(x=mean_val, color='red', linestyle='--', label=f'Promedio: {mean_val:.1f}ms')
            ax.legend()
        
        plt.tight_layout()
        plt.savefig(viz_dir / 'latency_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Análisis de uso de recursos del sistema
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # CPU Usage
        sns.histplot(data=df, x='cpu_usage_percent', kde=True, ax=axes[0,0], alpha=0.7)
        axes[0,0].set_title('Distribución de Uso de CPU')
        axes[0,0].set_xlabel('CPU (%)')
        cpu_mean = df['cpu_usage_percent'].mean()
        axes[0,0].axvline(x=cpu_mean, color='red', linestyle='--', label=f'Promedio: {cpu_mean:.1f}%')
        axes[0,0].legend()
        
        # Memory Usage
        sns.histplot(data=df, x='memory_usage_mb', kde=True, ax=axes[0,1], alpha=0.7)
        axes[0,1].set_title('Distribución de Uso de Memoria')
        axes[0,1].set_xlabel('Memoria (MB)')
        mem_mean = df['memory_usage_mb'].mean()
        axes[0,1].axvline(x=mem_mean, color='red', linestyle='--', label=f'Promedio: {mem_mean:.1f}MB')
        axes[0,1].legend()
        
        # Throughput
        sns.histplot(data=df, x='throughput_mbps', kde=True, ax=axes[1,0], alpha=0.7)
        axes[1,0].set_title('Distribución de Throughput')
        axes[1,0].set_xlabel('Throughput (Mbps)')
        throughput_mean = df['throughput_mbps'].mean()
        axes[1,0].axvline(x=throughput_mean, color='red', linestyle='--', label=f'Promedio: {throughput_mean:.1f}Mbps')
        axes[1,0].legend()
        
        # Error Rate
        sns.histplot(data=df, x='error_rate', kde=True, ax=axes[1,1], alpha=0.7)
        axes[1,1].set_title('Distribución de Tasa de Error')
        axes[1,1].set_xlabel('Error Rate (%)')
        error_mean = df['error_rate'].mean()
        axes[1,1].axvline(x=error_mean, color='red', linestyle='--', label=f'Promedio: {error_mean:.2f}%')
        axes[1,1].legend()
        
        plt.tight_layout()
        plt.savefig(viz_dir / 'resource_analysis.png', dpi=300, bbox_inches='tight')
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
        
        # 5. Timeline de performance y tendencias
        fig, axes = plt.subplots(2, 1, figsize=(15, 12))
        
        # Timeline de RPS por endpoint
        for endpoint in df['endpoint_name'].unique():
            endpoint_data = df[df['endpoint_name'] == endpoint]
            axes[0].plot(endpoint_data['test_number'], endpoint_data['requests_per_second'], 
                        marker='o', label=endpoint, alpha=0.8, linewidth=2)
        
        axes[0].set_title('Evolución del RPS por Endpoint a lo largo de las pruebas')
        axes[0].set_xlabel('Número de Test')
        axes[0].set_ylabel('Requests per Second')
        axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[0].grid(True, alpha=0.3)
        
        # Timeline de latencia promedio
        for endpoint in df['endpoint_name'].unique():
            endpoint_data = df[df['endpoint_name'] == endpoint]
            axes[1].plot(endpoint_data['test_number'], endpoint_data['avg_latency_ms'], 
                        marker='s', label=endpoint, alpha=0.8, linewidth=2)
        
        axes[1].set_title('Evolución de la Latencia Promedio por Endpoint')
        axes[1].set_xlabel('Número de Test')
        axes[1].set_ylabel('Latencia Promedio (ms)')
        axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[1].grid(True, alpha=0.3)
        
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
        
        # Análisis del entorno único (Docker Local)
        env_data = df  # Solo hay un entorno
        avg_rps = env_data['requests_per_second'].mean()
        avg_latency = env_data['avg_latency_ms'].mean()
        avg_cpu = env_data['cpu_usage_percent'].mean()
        max_rps = env_data['requests_per_second'].max()
        min_rps = env_data['requests_per_second'].min()
        
        report_lines.append(f"### DOCKER LOCAL - Análisis Completo")
        report_lines.append(f"- **RPS Promedio:** {avg_rps:.2f}")
        report_lines.append(f"- **RPS Máximo:** {max_rps:.2f}")
        report_lines.append(f"- **RPS Mínimo:** {min_rps:.2f}")
        report_lines.append(f"- **Latencia Promedio:** {avg_latency:.2f} ms")
        report_lines.append(f"- **CPU Promedio:** {avg_cpu:.2f}%")
        report_lines.append(f"- **Total de Pruebas:** {len(env_data)}")
        report_lines.append("")
        
        # Análisis detallado por endpoint
        report_lines.append("## Análisis por Endpoint")
        report_lines.append("")
        
        for endpoint in df['endpoint_name'].unique():
            report_lines.append(f"### {endpoint}")
            endpoint_data = df[df['endpoint_name'] == endpoint]
            
            # Estadísticas por endpoint
            stats = {
                'RPS Promedio': endpoint_data['requests_per_second'].mean(),
                'RPS Desv. Std': endpoint_data['requests_per_second'].std(),
                'Latencia Promedio (ms)': endpoint_data['avg_latency_ms'].mean(),
                'Latencia Desv. Std (ms)': endpoint_data['avg_latency_ms'].std(),
                'P95 Latencia (ms)': endpoint_data['p95_latency_ms'].mean(),
                'P99 Latencia (ms)': endpoint_data['p99_latency_ms'].mean(),
                'Error Rate (%)': endpoint_data['error_rate'].mean(),
                'CPU Promedio (%)': endpoint_data['cpu_usage_percent'].mean(),
                'Throughput (Mbps)': endpoint_data['throughput_mbps'].mean()
            }
            
            for metric, value in stats.items():
                report_lines.append(f"- **{metric}:** {value:.2f}")
            report_lines.append("")
        
        # Estadísticas de estabilidad y consistencia
        report_lines.append("## Análisis de Estabilidad y Consistencia")
        report_lines.append("")
        
        # Análisis global de estabilidad
        rps_cv = (df['requests_per_second'].std() / df['requests_per_second'].mean()) * 100
        latency_cv = (df['avg_latency_ms'].std() / df['avg_latency_ms'].mean()) * 100
        cpu_cv = (df['cpu_usage_percent'].std() / df['cpu_usage_percent'].mean()) * 100
        
        report_lines.append(f"### DOCKER LOCAL - Métricas de Consistencia")
        report_lines.append(f"- **Coeficiente de Variación RPS:** {rps_cv:.2f}% {'(Excelente)' if rps_cv < 10 else '(Moderado)' if rps_cv < 20 else '(Alto)'}")
        report_lines.append(f"- **Coeficiente de Variación Latencia:** {latency_cv:.2f}% {'(Excelente)' if latency_cv < 15 else '(Moderado)' if latency_cv < 30 else '(Alto)'}")
        report_lines.append(f"- **Coeficiente de Variación CPU:** {cpu_cv:.2f}% {'(Estable)' if cpu_cv < 25 else '(Variable)' if cpu_cv < 50 else '(Muy Variable)'}")
        
        # Análisis de tendencias por número de test
        test_numbers = sorted(df['test_number'].unique())
        if len(test_numbers) > 1:
            # Correlación entre número de test y rendimiento
            rps_correlation = df['test_number'].corr(df['requests_per_second'])
            latency_correlation = df['test_number'].corr(df['avg_latency_ms'])
            
            report_lines.append("")
            report_lines.append("### Análisis de Tendencias")
            report_lines.append(f"- **Correlación Test-RPS:** {rps_correlation:.3f} {'(Mejora con el tiempo)' if rps_correlation > 0.1 else '(Degrada con el tiempo)' if rps_correlation < -0.1 else '(Estable en el tiempo)'}")
            report_lines.append(f"- **Correlación Test-Latencia:** {latency_correlation:.3f} {'(Empeora con el tiempo)' if latency_correlation > 0.1 else '(Mejora con el tiempo)' if latency_correlation < -0.1 else '(Estable en el tiempo)'}")
        
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