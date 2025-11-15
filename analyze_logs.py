#!/usr/bin/env python3
"""
Análisis y Limpieza de Logs - FastAPI Performance Benchmark
==========================================================

Script para:
1. Analizar logs históricos
2. Generar reportes consolidados
3. Limpiar logs antiguos
4. Comprimir logs para archivo
5. Exportar logs a diferentes formatos

Uso:
    python analyze_logs.py --help
    python analyze_logs.py --days 7           # Analizar últimos 7 días
    python analyze_logs.py --clean --days 7  # Limpiar logs de más de 7 días
    python analyze_logs.py --compress         # Comprimir logs antigos
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import gzip
import shutil
import json
import csv
import re
from collections import defaultdict
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class LogStatistics:
    """Estadísticas de logs"""
    date: str
    total_files: int
    total_size_mb: float
    general_logs: int
    error_logs: int
    performance_logs: int
    archived_logs: int


class LogAnalyzer:
    """Analizador de logs para benchmarking"""
    
    def __init__(self, log_root: str = ".logs"):
        self.log_root = Path(log_root)
        self.daily_dir = self.log_root / "daily"
        self.error_dir = self.log_root / "errors"
        self.performance_dir = self.log_root / "performance"
        self.archive_dir = self.log_root / "archive"
    
    def analyze_logs(self, days: int = 7) -> Dict:
        """Analizar logs de los últimos N días"""
        print(f"📊 Analizando logs de los últimos {days} días...")
        
        cutoff_date = (datetime.now() - timedelta(days=days)).date()
        
        analysis = {
            'date_range': {
                'from': cutoff_date.isoformat(),
                'to': datetime.now().date().isoformat(),
                'days': days
            },
            'by_category': {},
            'summary': {
                'total_files': 0,
                'total_size_mb': 0.0,
                'errors_found': 0,
                'warnings_found': 0,
            },
            'performance_metrics': {},
        }
        
        # Analizar por categoría
        for category_name, category_dir in [
            ('general', self.daily_dir),
            ('errors', self.error_dir),
            ('performance', self.performance_dir),
        ]:
            if not category_dir.exists():
                continue
            
            files = []
            total_size = 0
            
            for log_file in sorted(category_dir.glob('*.log')):
                file_date = self._extract_date_from_filename(log_file.name)
                
                if file_date and file_date >= cutoff_date:
                    size = log_file.stat().st_size / (1024 * 1024)  # MB
                    total_size += size
                    files.append({
                        'name': log_file.name,
                        'date': file_date.isoformat(),
                        'size_mb': round(size, 2),
                        'lines': self._count_lines(log_file)
                    })
            
            analysis['by_category'][category_name] = {
                'file_count': len(files),
                'total_size_mb': round(total_size, 2),
                'files': files
            }
            
            analysis['summary']['total_files'] += len(files)
            analysis['summary']['total_size_mb'] += total_size
        
        # Contar errores y warnings
        analysis['summary']['errors_found'] = self._count_log_entries(
            self.error_dir, 'ERROR', days
        )
        analysis['summary']['warnings_found'] = self._count_log_entries(
            self.error_dir, 'WARNING', days
        )
        
        # Extraer métricas de rendimiento
        analysis['performance_metrics'] = self._extract_performance_metrics(days)
        
        return analysis
    
    def _extract_date_from_filename(self, filename: str) -> Optional[datetime.date]:
        """Extraer fecha del nombre del archivo"""
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if match:
            return datetime.strptime(match.group(1), '%Y-%m-%d').date()
        return None
    
    def _count_lines(self, filepath: Path) -> int:
        """Contar líneas en archivo"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def _count_log_entries(self, log_dir: Path, level: str, days: int) -> int:
        """Contar entradas de log con nivel específico"""
        count = 0
        cutoff_date = (datetime.now() - timedelta(days=days)).date()
        
        if not log_dir.exists():
            return count
        
        pattern = re.compile(f'\\| {level} \\|')
        
        for log_file in log_dir.glob('*.log'):
            file_date = self._extract_date_from_filename(log_file.name)
            if file_date and file_date >= cutoff_date:
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if pattern.search(line):
                                count += 1
                except:
                    pass
        
        return count
    
    def _extract_performance_metrics(self, days: int) -> Dict:
        """Extraer métricas de rendimiento de los logs"""
        metrics = {
            'total_requests': 0,
            'total_errors': 0,
            'avg_rps': 0.0,
            'avg_latency_ms': 0.0,
            'endpoints_tested': set(),
            'environments_tested': set(),
        }
        
        cutoff_date = (datetime.now() - timedelta(days=days)).date()
        
        if not self.performance_dir.exists():
            return metrics
        
        rps_values = []
        latency_values = []
        
        for log_file in self.performance_dir.glob('*performance*.log'):
            file_date = self._extract_date_from_filename(log_file.name)
            if file_date and file_date >= cutoff_date:
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            # Buscar líneas con métricas
                            if 'RPS:' in line:
                                match_rps = re.search(r'RPS: ([\d.]+)', line)
                                if match_rps:
                                    rps_values.append(float(match_rps.group(1)))
                            
                            if 'Latency:' in line:
                                match_lat = re.search(r'Latency: ([\d.]+)ms', line)
                                if match_lat:
                                    latency_values.append(float(match_lat.group(1)))
                            
                            if 'Endpoint:' in line:
                                match_ep = re.search(r'Endpoint: ([^|]+)', line)
                                if match_ep:
                                    metrics['endpoints_tested'].add(match_ep.group(1).strip())
                            
                            if 'Environment:' in line:
                                match_env = re.search(r'Environment: ([^|]+)', line)
                                if match_env:
                                    metrics['environments_tested'].add(match_env.group(1).strip())
                except:
                    pass
        
        # Calcular promedios
        if rps_values:
            metrics['avg_rps'] = round(sum(rps_values) / len(rps_values), 2)
        if latency_values:
            metrics['avg_latency_ms'] = round(sum(latency_values) / len(latency_values), 2)
        
        # Convertir sets a listas para JSON
        metrics['endpoints_tested'] = list(metrics['endpoints_tested'])
        metrics['environments_tested'] = list(metrics['environments_tested'])
        
        return metrics
    
    def generate_report(self, analysis: Dict, output_format: str = 'markdown') -> str:
        """Generar reporte de análisis"""
        if output_format == 'markdown':
            return self._generate_markdown_report(analysis)
        elif output_format == 'json':
            return json.dumps(analysis, indent=2)
        elif output_format == 'csv':
            return self._generate_csv_report(analysis)
        else:
            raise ValueError(f"Formato desconocido: {output_format}")
    
    def _generate_markdown_report(self, analysis: Dict) -> str:
        """Generar reporte en formato Markdown"""
        lines = []
        
        lines.append("# Reporte de Análisis de Logs")
        lines.append(f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Rango de fechas
        date_range = analysis['date_range']
        lines.append("## Rango de Fechas")
        lines.append(f"- **Desde:** {date_range['from']}")
        lines.append(f"- **Hasta:** {date_range['to']}")
        lines.append(f"- **Período:** {date_range['days']} días")
        lines.append("")
        
        # Resumen
        summary = analysis['summary']
        lines.append("## Resumen")
        lines.append(f"- **Archivos totales:** {summary['total_files']}")
        lines.append(f"- **Tamaño total:** {summary['total_size_mb']:.2f} MB")
        lines.append(f"- **Errores encontrados:** {summary['errors_found']}")
        lines.append(f"- **Advertencias encontradas:** {summary['warnings_found']}")
        lines.append("")
        
        # Por categoría
        lines.append("## Análisis por Categoría")
        for category, data in analysis['by_category'].items():
            lines.append(f"\n### {category.capitalize()}")
            lines.append(f"- **Archivos:** {data['file_count']}")
            lines.append(f"- **Tamaño:** {data['total_size_mb']:.2f} MB")
            if data['files']:
                lines.append("- **Archivos:**")
                for file_info in data['files']:
                    lines.append(f"  - {file_info['name']} ({file_info['size_mb']:.2f} MB, {file_info['lines']} líneas)")
        
        lines.append("")
        
        # Métricas de rendimiento
        perf = analysis['performance_metrics']
        lines.append("## Métricas de Rendimiento")
        lines.append(f"- **RPS Promedio:** {perf['avg_rps']:.2f}")
        lines.append(f"- **Latencia Promedio:** {perf['avg_latency_ms']:.2f} ms")
        lines.append(f"- **Endpoints probados:** {len(perf['endpoints_tested'])}")
        lines.append(f"- **Entornos probados:** {len(perf['environments_tested'])}")
        
        if perf['endpoints_tested']:
            lines.append("\n**Endpoints:**")
            for endpoint in perf['endpoints_tested']:
                lines.append(f"  - {endpoint}")
        
        if perf['environments_tested']:
            lines.append("\n**Entornos:**")
            for env in perf['environments_tested']:
                lines.append(f"  - {env}")
        
        return "\n".join(lines)
    
    def _generate_csv_report(self, analysis: Dict) -> str:
        """Generar reporte en formato CSV"""
        output = []
        
        # Header
        output.append("Categoría,Archivos,Tamaño_MB,Archivo,Fecha,Tamaño_Archivo_MB,Líneas")
        
        # Datos
        for category, data in analysis['by_category'].items():
            for file_info in data['files']:
                output.append(
                    f"{category},{data['file_count']},{data['total_size_mb']:.2f},"
                    f"{file_info['name']},{file_info['date']},"
                    f"{file_info['size_mb']:.2f},{file_info['lines']}"
                )
        
        return "\n".join(output)
    
    def clean_old_logs(self, days_to_keep: int = 7, dry_run: bool = True) -> Dict:
        """Limpiar logs antiguos"""
        print(f"🧹 Limpiando logs más antiguos que {days_to_keep} días (dry_run={dry_run})...")
        
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).date()
        
        results = {
            'deleted_files': [],
            'compressed_files': [],
            'total_freed_mb': 0.0,
        }
        
        for log_dir in [self.daily_dir, self.error_dir, self.performance_dir]:
            if not log_dir.exists():
                continue
            
            for log_file in log_dir.glob('*.log'):
                file_date = self._extract_date_from_filename(log_file.name)
                
                if file_date and file_date < cutoff_date:
                    file_size = log_file.stat().st_size / (1024 * 1024)
                    
                    if not dry_run:
                        # Comprimir primero
                        self._compress_file(log_file)
                        results['compressed_files'].append(log_file.name)
                        results['total_freed_mb'] += file_size
                    else:
                        results['deleted_files'].append(log_file.name)
                        results['total_freed_mb'] += file_size
        
        return results
    
    def _compress_file(self, filepath: Path) -> None:
        """Comprimir archivo log"""
        try:
            gzip_path = self.archive_dir / f"{filepath.name}.gz"
            
            with open(filepath, 'rb') as f_in:
                with gzip.open(gzip_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            filepath.unlink()
            print(f"✅ Comprimido: {filepath.name} -> {gzip_path.name}")
        except Exception as e:
            print(f"❌ Error comprimiendo {filepath}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Análisis y limpieza de logs para FastAPI Performance Benchmark"
    )
    
    parser.add_argument('--log-dir', type=str, default='.logs',
                       help='Directorio de logs (default: .logs)')
    parser.add_argument('--days', type=int, default=7,
                       help='Número de días a analizar/limpiar (default: 7)')
    parser.add_argument('--analyze', action='store_true', default=True,
                       help='Analizar logs (default: True)')
    parser.add_argument('--clean', action='store_true',
                       help='Limpiar logs antiguos')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulación de limpieza sin eliminar archivos')
    parser.add_argument('--format', choices=['markdown', 'json', 'csv'], default='markdown',
                       help='Formato de reporte (default: markdown)')
    parser.add_argument('--output', type=str,
                       help='Archivo de salida para reporte')
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(args.log_dir)
    
    # Analizar logs
    if args.analyze:
        print("\n" + "="*60)
        print("📊 ANÁLISIS DE LOGS")
        print("="*60)
        
        analysis = analyzer.analyze_logs(args.days)
        report = analyzer.generate_report(analysis, args.format)
        
        # Mostrar reporte
        print(report)
        
        # Guardar si se especifica output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n✅ Reporte guardado en: {args.output}")
    
    # Limpiar logs
    if args.clean:
        print("\n" + "="*60)
        print("🧹 LIMPIEZA DE LOGS")
        print("="*60)
        
        dry_run = args.dry_run or args.analyze
        results = analyzer.clean_old_logs(args.days, dry_run=dry_run)
        
        if dry_run:
            print(f"\n📋 Dry-run: Se eliminarían {len(results['deleted_files'])} archivos")
            print(f"   Espacio liberado: {results['total_freed_mb']:.2f} MB")
            if results['deleted_files']:
                print("\n   Archivos a eliminar:")
                for filename in results['deleted_files']:
                    print(f"     - {filename}")
        else:
            print(f"\n✅ Comprimidos: {len(results['compressed_files'])} archivos")
            print(f"   Espacio liberado: {results['total_freed_mb']:.2f} MB")


if __name__ == "__main__":
    main()
