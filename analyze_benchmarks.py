"""
Análisis de resultados de benchmarks FastAPI - VPS Only
Compara rendimiento entre VPS sin Docker vs VPS con Docker
Análisis modular y seccionalizado con múltiples pruebas
Uso: python analyze_benchmarks.py [archivo_csv o directorio]
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import glob
import json
from datetime import datetime
import statistics

# Configurar estilo de gráficos
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# Configuración de directorios
EVIDENCE_DIR = Path('benchmark_results/evidencia')
RESULTS_DIR = Path('benchmark_results')

def load_benchmark_data(path):
    """Carga datos de benchmark desde CSV o directorio, filtrando solo VPS."""
    if Path(path).is_file():
        print(f"📂 Cargando archivo: {path}")
        df = pd.read_csv(path)
    elif Path(path).is_dir():
        csv_files = sorted(glob.glob(f"{path}/*.csv"))
        # Filtrar solo los archivos de benchmark (no resumen)
        csv_files = [f for f in csv_files if 'summary' not in f]
        if not csv_files:
            print(f"❌ No se encontraron archivos CSV en {path}")
            return None
        print(f"📂 Cargando {len(csv_files)} archivos CSV...")
        dfs = [pd.read_csv(f) for f in csv_files]
        df = pd.concat(dfs, ignore_index=True)
    else:
        print(f"❌ Ruta no válida: {path}")
        return None
    
    # FILTRAR: Solo datos de VPS (excluir local)
    vps_envs = ['vps_no_docker', 'vps_docker']
    df_filtered = df[df['environment'].isin(vps_envs)]
    
    if df_filtered.empty:
        print(f"❌ No se encontraron datos de VPS en los archivos")
        print(f"   Entornos disponibles: {df['environment'].unique()}")
        print(f"   Se esperaban: {vps_envs}")
        return None
    
    print(f"✅ Datos de VPS cargados: {len(df_filtered)} registros")
    print(f"   Entornos encontrados: {df_filtered['environment'].unique()}")
    
    return df_filtered

def print_summary_stats(df):
    """Imprime estadísticas resumidas para VPS."""
    print("\n" + "="*70)
    print("📊 RESUMEN ESTADÍSTICO - COMPARACIÓN VPS")
    print("="*70 + "\n")
    
    # Estadísticas por endpoint y entorno
    print("Métricas por Endpoint y Entorno:")
    print("-" * 70)
    summary = df.groupby(['name', 'environment']).agg({
        'requests_per_second': ['mean', 'std'],
        'avg_latency_ms': ['mean', 'std'],
        'failed_requests': 'sum'
    }).round(2)
    print(summary)
    print()
    
    # Comparación directa entre entornos
    print("\n" + "="*70)
    print("🔄 COMPARACIÓN DOCKER vs SIN DOCKER")
    print("="*70 + "\n")
    
    pivot_rps = df.pivot_table(
        values='requests_per_second',
        index='name',
        columns='environment',
        aggfunc='mean'
    ).round(2)
    
    # Calcular diferencia si tenemos ambos entornos
    if 'vps_no_docker' in pivot_rps.columns and 'vps_docker' in pivot_rps.columns:
        pivot_rps['diferencia_rps'] = (pivot_rps['vps_no_docker'] - pivot_rps['vps_docker']).round(2)
        pivot_rps['overhead_%'] = ((pivot_rps['vps_docker'] / pivot_rps['vps_no_docker'] - 1) * 100).round(2)
    
    print("Requests por Segundo:")
    print(pivot_rps)
    print()
    
    pivot_latency = df.pivot_table(
        values='avg_latency_ms',
        index='name',
        columns='environment',
        aggfunc='mean'
    ).round(2)
    
    # Calcular diferencia si tenemos ambos entornos
    if 'vps_no_docker' in pivot_latency.columns and 'vps_docker' in pivot_latency.columns:
        pivot_latency['diferencia_ms'] = (pivot_latency['vps_docker'] - pivot_latency['vps_no_docker']).round(2)
        pivot_latency['aumento_%'] = ((pivot_latency['vps_docker'] / pivot_latency['vps_no_docker'] - 1) * 100).round(2)
    
    print("Latencia Promedio (ms):")
    print(pivot_latency)
    print()
    
    # Resumen de overhead de Docker
    if 'vps_no_docker' in df['environment'].values and 'vps_docker' in df['environment'].values:
        print("\n" + "="*70)
        print("📦 OVERHEAD DE DOCKER")
        print("="*70 + "\n")
        
        no_docker = df[df['environment'] == 'vps_no_docker']
        with_docker = df[df['environment'] == 'vps_docker']
        
        avg_rps_no_docker = no_docker['requests_per_second'].mean()
        avg_rps_docker = with_docker['requests_per_second'].mean()
        rps_diff = ((avg_rps_docker / avg_rps_no_docker - 1) * 100)
        
        avg_lat_no_docker = no_docker['avg_latency_ms'].mean()
        avg_lat_docker = with_docker['avg_latency_ms'].mean()
        lat_diff = ((avg_lat_docker / avg_lat_no_docker - 1) * 100)
        
        print(f"RPS Promedio sin Docker: {avg_rps_no_docker:.2f}")
        print(f"RPS Promedio con Docker: {avg_rps_docker:.2f}")
        print(f"Impacto en RPS: {rps_diff:+.2f}%")
        print()
        print(f"Latencia Promedio sin Docker: {avg_lat_no_docker:.2f} ms")
        print(f"Latencia Promedio con Docker: {avg_lat_docker:.2f} ms")
        print(f"Impacto en Latencia: {lat_diff:+.2f}%")
        print()
        
        if abs(rps_diff) < 5:
            print("✅ El overhead de Docker es mínimo (<5%)")
        elif abs(rps_diff) < 15:
            print("⚠️  Docker tiene un overhead moderado (5-15%)")
        else:
            print("❌ Docker tiene un overhead significativo (>15%)")
    
    # Errores totales
    total_errors = df['failed_requests'].sum()
    total_requests = df['total_requests'].sum()
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
    print(f"\n❌ Errores totales: {total_errors} de {total_requests} requests ({error_rate:.2f}%)\n")

def plot_performance_comparison(df, output_dir='benchmark_results'):
    """Genera gráficos de comparación de rendimiento VPS."""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Colores personalizados para cada entorno
    colors = {'vps_no_docker': '#2ecc71', 'vps_docker': '#3498db'}
    
    # 1. Requests por segundo - Comparación lado a lado
    plt.figure(figsize=(14, 7))
    ax = sns.barplot(data=df, x='name', y='requests_per_second', hue='environment', 
                     palette=colors, errorbar='sd')
    plt.title('Comparación RPS: VPS Sin Docker vs Con Docker', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Endpoint', fontsize=13)
    plt.ylabel('Requests por Segundo', fontsize=13)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Entorno', labels=['Sin Docker', 'Con Docker'], fontsize=11)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/vps_rps_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: {output_dir}/vps_rps_comparison.png")
    plt.close()
    
    # 2. Latencia promedio - Comparación lado a lado
    plt.figure(figsize=(14, 7))
    ax = sns.barplot(data=df, x='name', y='avg_latency_ms', hue='environment', 
                     palette=colors, errorbar='sd')
    plt.title('Comparación Latencia: VPS Sin Docker vs Con Docker', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Endpoint', fontsize=13)
    plt.ylabel('Latencia Promedio (ms)', fontsize=13)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Entorno', labels=['Sin Docker', 'Con Docker'], fontsize=11)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/vps_latency_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: {output_dir}/vps_latency_comparison.png")
    plt.close()
    
    # 3. Percentiles de latencia por entorno
    latency_data = df.melt(
        id_vars=['name', 'environment'],
        value_vars=['p50_latency_ms', 'p95_latency_ms', 'p99_latency_ms'],
        var_name='percentil',
        value_name='latency'
    )
    
    plt.figure(figsize=(16, 7))
    ax = sns.barplot(data=latency_data, x='name', y='latency', hue='percentil', 
                     palette='viridis', errorbar=None)
    plt.title('Distribución de Latencias (P50, P95, P99) - Ambos Entornos', 
              fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Endpoint', fontsize=13)
    plt.ylabel('Latencia (ms)', fontsize=13)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Percentil', labels=['P50 (Mediana)', 'P95', 'P99'], fontsize=11)
    
    # Separar visualmente por entorno
    envs = df['environment'].unique()
    if len(envs) > 1:
        plt.text(0.02, 0.98, f'Incluye: {", ".join(envs)}', 
                transform=plt.gca().transAxes, fontsize=10, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/vps_latency_percentiles.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: {output_dir}/vps_latency_percentiles.png")
    plt.close()
    
    # 4. Overhead de Docker (solo si tenemos ambos entornos)
    if len(df['environment'].unique()) == 2:
        # Calcular overhead por endpoint
        pivot_df = df.pivot_table(
            values=['requests_per_second', 'avg_latency_ms'],
            index='name',
            columns='environment',
            aggfunc='mean'
        )
        
        if 'vps_no_docker' in df['environment'].values and 'vps_docker' in df['environment'].values:
            overhead_data = []
            for endpoint in pivot_df.index:
                rps_no_docker = pivot_df.loc[endpoint, ('requests_per_second', 'vps_no_docker')]
                rps_docker = pivot_df.loc[endpoint, ('requests_per_second', 'vps_docker')]
                overhead_rps = ((rps_docker / rps_no_docker - 1) * 100) if rps_no_docker > 0 else 0
                
                lat_no_docker = pivot_df.loc[endpoint, ('avg_latency_ms', 'vps_no_docker')]
                lat_docker = pivot_df.loc[endpoint, ('avg_latency_ms', 'vps_docker')]
                overhead_lat = ((lat_docker / lat_no_docker - 1) * 100) if lat_no_docker > 0 else 0
                
                overhead_data.append({
                    'endpoint': endpoint,
                    'RPS_overhead_%': overhead_rps,
                    'Latencia_overhead_%': overhead_lat
                })
            
            overhead_df = pd.DataFrame(overhead_data)
            
            fig, axes = plt.subplots(1, 2, figsize=(16, 6))
            
            # Overhead en RPS
            axes[0].barh(overhead_df['endpoint'], overhead_df['RPS_overhead_%'], 
                        color=['red' if x < 0 else 'green' for x in overhead_df['RPS_overhead_%']])
            axes[0].set_title('Overhead de Docker en RPS', fontsize=14, fontweight='bold')
            axes[0].set_xlabel('Cambio en RPS (%)', fontsize=12)
            axes[0].axvline(x=0, color='black', linestyle='--', alpha=0.5)
            axes[0].grid(axis='x', alpha=0.3)
            
            # Overhead en Latencia
            axes[1].barh(overhead_df['endpoint'], overhead_df['Latencia_overhead_%'], 
                        color=['green' if x < 0 else 'red' for x in overhead_df['Latencia_overhead_%']])
            axes[1].set_title('Overhead de Docker en Latencia', fontsize=14, fontweight='bold')
            axes[1].set_xlabel('Cambio en Latencia (%)', fontsize=12)
            axes[1].axvline(x=0, color='black', linestyle='--', alpha=0.5)
            axes[1].grid(axis='x', alpha=0.3)
            
            plt.suptitle('Impacto de Docker en el Rendimiento del VPS', 
                        fontsize=16, fontweight='bold', y=1.02)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/vps_docker_overhead.png', dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico guardado: {output_dir}/vps_docker_overhead.png")
            plt.close()
    
    # 5. Tasa de éxito
    df['success_rate'] = ((df['successful_requests'] / df['total_requests']) * 100).round(2)
    
    plt.figure(figsize=(14, 7))
    ax = sns.barplot(data=df, x='name', y='success_rate', hue='environment', 
                     palette=colors, errorbar=None)
    plt.title('Tasa de Éxito por Entorno', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Endpoint', fontsize=13)
    plt.ylabel('Tasa de Éxito (%)', fontsize=13)
    plt.ylim(0, 105)
    plt.xticks(rotation=45, ha='right')
    plt.axhline(y=100, color='green', linestyle='--', alpha=0.5, label='100%')
    plt.legend(title='Entorno', labels=['Sin Docker', 'Con Docker', '100%'], fontsize=11)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/vps_success_rate.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: {output_dir}/vps_success_rate.png")
    plt.close()

def export_summary_report(df, output_dir='benchmark_results'):
    """Exporta reporte resumido en CSV - Solo VPS."""
    summary = df.groupby(['name', 'environment']).agg({
        'requests_per_second': ['mean', 'std', 'min', 'max'],
        'avg_latency_ms': ['mean', 'std', 'min', 'max'],
        'p95_latency_ms': ['mean', 'max'],
        'p99_latency_ms': ['mean', 'max'],
        'failed_requests': 'sum',
        'total_requests': 'sum'
    }).round(2)
    
    # Aplanar columnas multi-nivel
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    
    # Calcular tasa de error
    summary['error_rate_%'] = (
        (summary['failed_requests_sum'] / summary['total_requests_sum']) * 100
    ).round(2)
    
    output_file = f'{output_dir}/vps_benchmark_summary.csv'
    summary.to_csv(output_file, index=False)
    print(f"✅ Reporte resumido guardado: {output_file}")
    
    return summary

def main():
    """Función principal."""
    print("\n" + "="*70)
    print("📊 FastAPI Benchmark Analyzer - VPS Comparison")
    print("   Comparación: VPS Sin Docker vs VPS Con Docker")
    print("="*70 + "\n")
    
    # Determinar ruta de entrada
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = 'benchmark_results'
    
    # Cargar datos (filtrado a solo VPS)
    df = load_benchmark_data(input_path)
    
    if df is None or df.empty:
        print("❌ No hay datos de VPS para analizar.")
        print("\n💡 Asegúrate de ejecutar:")
        print("   .\benchmark-vps.ps1")
        print("   .\benchmark-vps-docker.ps1")
        return
    
    print(f"\n✅ Datos de VPS cargados: {len(df)} registros\n")
    
    # Convertir timestamp a datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Análisis y visualizaciones
    print_summary_stats(df)
    
    print("\n" + "="*70)
    print("📈 Generando gráficos...")
    print("="*70 + "\n")
    
    plot_performance_comparison(df)
    summary_df = export_summary_report(df)
    
    print("\n" + "="*70)
    print("✅ Análisis completado!")
    print("="*70 + "\n")
    
    print("📁 Archivos generados en 'benchmark_results/':")
    print("  - vps_rps_comparison.png          (RPS sin Docker vs con Docker)")
    print("  - vps_latency_comparison.png      (Latencia sin Docker vs con Docker)")
    print("  - vps_latency_percentiles.png     (P50, P95, P99)")
    print("  - vps_success_rate.png            (Tasa de éxito)")
    if len(df['environment'].unique()) == 2:
        print("  - vps_docker_overhead.png         (Impacto de Docker)")
    print("  - vps_benchmark_summary.csv       (Resumen en CSV)")
    print()
    
    print("🎯 Próximos pasos:")
    print("  - Revisa los gráficos para identificar diferencias")
    print("  - Analiza el overhead de Docker en cada endpoint")
    print("  - Documenta tus hallazgos en el README.md")
    print()

if __name__ == "__main__":
    main()