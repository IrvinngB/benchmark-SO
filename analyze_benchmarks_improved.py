"""
Análisis Mejorado de Benchmarks FastAPI - 10 Runs
Compara rendimiento entre VPS sin Docker vs VPS con Docker
Con mejor precisión estadística (10 pruebas por entorno)
Uso: python analyze_benchmarks_improved.py [directorio]
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
from typing import Dict, Tuple, List

# Configurar estilo de gráficos
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# Configuración de directorios
EVIDENCE_DIR = Path('benchmark_results_improved/evidencia')
RESULTS_DIR = Path('benchmark_results_improved')

def setup_directories():
    """Crea directorios necesarios."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Directorio de evidencia: {EVIDENCE_DIR}")

def load_benchmark_data(path):
    """Carga datos de benchmark desde CSV o directorio, filtrando solo VPS."""
    print(f"\n📂 Buscando archivos de benchmark en: {path}\n")
    
    if Path(path).is_file():
        print(f"Cargando archivo: {path}")
        df = pd.read_csv(path)
    elif Path(path).is_dir():
        # Buscar en subdirectorios por entorno
        csv_files = []
        for env_dir in Path(path).glob("vps_*/"):
            env_csv = list(env_dir.glob("*.csv"))
            csv_files.extend(env_csv)
        
        # También buscar en raíz
        csv_files.extend(glob.glob(f"{path}/*.csv"))
        csv_files = sorted(list(set(csv_files)))
        
        if not csv_files:
            print(f"❌ No se encontraron archivos CSV en {path}")
            return None
        
        print(f"📂 Encontrados {len(csv_files)} archivos CSV:")
        for f in csv_files:
            print(f"   • {Path(f).name}")
        
        dfs = []
        for f in csv_files:
            try:
                df_temp = pd.read_csv(f)
                dfs.append(df_temp)
                print(f"   ✅ {Path(f).name}: {len(df_temp)} registros")
            except Exception as e:
                print(f"   ❌ Error leyendo {Path(f).name}: {e}")
        
        if not dfs:
            return None
        
        df = pd.concat(dfs, ignore_index=True)
    else:
        print(f"❌ Ruta no válida: {path}")
        return None
    
    print(f"\n✅ Total de registros cargados: {len(df)}\n")
    
    return df

# ============================================================================
# SECCIÓN 1: ESTADÍSTICAS MEJORADAS (10 RUNS)
# ============================================================================

def section_statistical_summary(df) -> Dict:
    """Sección 1: Estadísticas resumidas con 6 pruebas."""
    print("\n" + "="*80)
    print("📊 SECCIÓN 1: ESTADÍSTICAS RESUMIDAS (6 PRUEBAS)")
    print("="*80 + "\n")
    
    stats_data = []
    
    for endpoint in df['name'].unique():
        endpoint_data = df[df['name'] == endpoint]
        
        for env in endpoint_data['environment'].unique():
            env_data = endpoint_data[endpoint_data['environment'] == env]
            
            rps = env_data['requests_per_second'].values
            
            # Calcular estadísticas avanzadas
            stats = {
                'Endpoint': endpoint,
                'Entorno': env,
                'RPS_Media': rps.mean(),
                'RPS_Mediana': statistics.median(rps),
                'RPS_StDev': rps.std(),
                'RPS_Min': rps.min(),
                'RPS_Q1': statistics.quantiles(rps, n=4)[0],
                'RPS_Q3': statistics.quantiles(rps, n=4)[2],
                'RPS_Max': rps.max(),
                'RPS_Range': rps.max() - rps.min(),
                'CV_%': (rps.std() / rps.mean() * 100) if rps.mean() > 0 else 0,
                'IQR': statistics.quantiles(rps, n=4)[2] - statistics.quantiles(rps, n=4)[0],
                'Pruebas': len(env_data)
            }
            stats_data.append(stats)
    
    stats_df = pd.DataFrame(stats_data)
    
    print("Estadísticas Completas por Endpoint y Entorno:")
    print("-" * 80)
    
    for endpoint in stats_df['Endpoint'].unique():
        print(f"\n📌 {endpoint}")
        print("   " + "─" * 76)
        endpoint_stats = stats_df[stats_df['Endpoint'] == endpoint]
        
        for _, row in endpoint_stats.iterrows():
            cv_symbol = "✅" if row['CV_%'] < 5 else "⚠️ " if row['CV_%'] < 15 else "❌"
            
            print(f"   {row['Entorno']:15} | "
                  f"Media: {row['RPS_Media']:7.2f} | "
                  f"Mediana: {row['RPS_Mediana']:7.2f} | "
                  f"Rango: {row['RPS_Min']:6.2f}-{row['RPS_Max']:6.2f} | "
                  f"CV: {row['CV_%']:5.1f}% {cv_symbol}")
    
    return stats_df.to_dict('records')

# ============================================================================
# SECCIÓN 2: ANÁLISIS DE CONFIABILIDAD
# ============================================================================

def section_reliability_analysis(df) -> Dict:
    """Sección 2: Análisis de confiabilidad y consistencia."""
    print("\n" + "="*80)
    print("🔒 SECCIÓN 2: ANÁLISIS DE CONFIABILIDAD")
    print("="*80 + "\n")
    
    reliability_data = []
    
    for endpoint in df['name'].unique():
        for env in df['environment'].unique():
            env_data = df[(df['name'] == endpoint) & (df['environment'] == env)]
            
            if len(env_data) < 2:
                continue
            
            rps_values = env_data['requests_per_second'].values
            
            # Calcular coeficiente de variación
            cv = (rps_values.std() / rps_values.mean() * 100) if rps_values.mean() > 0 else 0
            
            # Determinar estabilidad
            if cv < 3:
                stability = "🟢 EXCELENTE"
            elif cv < 8:
                stability = "🟡 BUENA"
            elif cv < 15:
                stability = "🟠 MODERADA"
            else:
                stability = "🔴 CRÍTICA"
            
            reliability = {
                'Endpoint': endpoint,
                'Entorno': env,
                'Pruebas': len(env_data),
                'RPS_Media': rps_values.mean(),
                'CV_%': cv,
                'Rango': f"{rps_values.min():.2f}-{rps_values.max():.2f}",
                'Estabilidad': stability,
                'Recomendación': 'Producción' if cv < 10 else 'Testing'
            }
            reliability_data.append(reliability)
    
    rel_df = pd.DataFrame(reliability_data)
    
    print("Análisis de Estabilidad (Coeficiente de Variación):")
    print("-" * 80)
    print(f"{'Endpoint':<25} {'Entorno':<15} {'CV%':>8} {'Estabilidad':<20} {'Recomendación':<15}")
    print("-" * 80)
    
    for _, row in rel_df.iterrows():
        print(f"{row['Endpoint']:<25} {row['Entorno']:<15} {row['CV_%']:>7.2f}% {row['Estabilidad']:<20} {row['Recomendación']:<15}")
    
    return rel_df.to_dict('records')

# ============================================================================
# SECCIÓN 3: COMPARACIÓN DOCKER vs SIN DOCKER (MEJORADA)
# ============================================================================

def section_docker_overhead_improved(df) -> Dict:
    """Sección 3: Análisis mejorado del overhead de Docker."""
    print("\n" + "="*80)
    print("🐳 SECCIÓN 3: OVERHEAD DE DOCKER (ANÁLISIS MEJORADO)")
    print("="*80 + "\n")
    
    comparison_data = []
    
    for endpoint in df['name'].unique():
        endpoint_data = df[df['name'] == endpoint]
        
        if 'vps_no_docker' not in endpoint_data['environment'].values or \
           'vps_docker' not in endpoint_data['environment'].values:
            continue
        
        no_docker = endpoint_data[endpoint_data['environment'] == 'vps_no_docker']
        with_docker = endpoint_data[endpoint_data['environment'] == 'vps_docker']
        
        # Estadísticas
        rps_nd = no_docker['requests_per_second'].values
        rps_d = with_docker['requests_per_second'].values
        
        rps_nd_mean = rps_nd.mean()
        rps_d_mean = rps_d.mean()
        rps_overhead = ((rps_d_mean / rps_nd_mean - 1) * 100) if rps_nd_mean > 0 else 0
        
        # Determinar severidad
        if abs(rps_overhead) < 3:
            severity = "🟢 EXCELENTE"
        elif abs(rps_overhead) < 8:
            severity = "🟡 BUENO"
        elif abs(rps_overhead) < 15:
            severity = "🟠 MODERADO"
        else:
            severity = "🔴 CRÍTICO"
        
        comparison = {
            'Endpoint': endpoint,
            'RPS_Sin_Docker': rps_nd_mean,
            'RPS_Con_Docker': rps_d_mean,
            'Overhead_%': rps_overhead,
            'Severidad': severity,
            'Mejora_Docker': rps_d_mean > rps_nd_mean
        }
        comparison_data.append(comparison)
    
    comp_df = pd.DataFrame(comparison_data)
    
    print("Comparación Detallada:")
    print("-" * 80)
    print(f"{'Endpoint':<25} {'Sin Docker':>14} {'Con Docker':>14} {'Overhead':>12} {'Severidad':<15}")
    print("-" * 80)
    
    for _, row in comp_df.iterrows():
        overhead_str = f"{row['Overhead_%']:+.2f}%"
        print(f"{row['Endpoint']:<25} {row['RPS_Sin_Docker']:>13.2f}  {row['RPS_Con_Docker']:>13.2f}  "
              f"{overhead_str:>11} {row['Severidad']:<15}")
    
    # Resumen
    print("\n" + "="*80)
    avg_overhead = comp_df['Overhead_%'].mean()
    print(f"📊 OVERHEAD PROMEDIO DE DOCKER: {avg_overhead:+.2f}%")
    print("="*80)
    
    if abs(avg_overhead) < 5:
        print("✅ El overhead de Docker es MÍNIMO (<5%)")
        print("   Recomendación: USAR DOCKER en producción")
    elif abs(avg_overhead) < 15:
        print("⚠️  Docker tiene un overhead MODERADO (5-15%)")
        print("   Recomendación: CONSIDERAR caso por caso")
    else:
        print("❌ Docker tiene un overhead SIGNIFICATIVO (>15%)")
        print("   Recomendación: USAR BARE METAL")
    
    return comp_df.to_dict('records')

# ============================================================================
# GRÁFICOS MEJORADOS
# ============================================================================

def plot_distribution_boxplot(df):
    """Gráfico: Distribución de RPS con boxplots."""
    plt.figure(figsize=(14, 8))
    
    colors = {'vps_no_docker': '#2ecc71', 'vps_docker': '#3498db'}
    
    # Crear subplots por endpoint
    endpoints = df['name'].unique()
    n_plots = len(endpoints)
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()
    
    for idx, endpoint in enumerate(sorted(endpoints)):
        ax = axes[idx]
        endpoint_data = df[df['name'] == endpoint]
        
        sns.boxplot(data=endpoint_data, x='environment', y='requests_per_second', 
                   palette=colors, ax=ax)
        ax.set_title(f"{endpoint}", fontsize=12, fontweight='bold')
        ax.set_xlabel('Entorno')
        ax.set_ylabel('RPS')
        
        # Agregar puntos individuales
        sns.stripplot(data=endpoint_data, x='environment', y='requests_per_second',
                     color='black', alpha=0.3, ax=ax)
    
    # Ocultar subplot vacío
    if n_plots < 6:
        axes[-1].axis('off')
    
    plt.suptitle('Distribución de RPS por Endpoint (Boxplot - 10 Runs)', 
                fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(EVIDENCE_DIR / '01_distribution_boxplot.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: 01_distribution_boxplot.png")
    plt.close()

def plot_stability_comparison(df):
    """Gráfico: Comparación de estabilidad (CV%)."""
    plt.figure(figsize=(14, 8))
    
    # Calcular CV% por endpoint y entorno
    stability_data = []
    for endpoint in df['name'].unique():
        for env in df['environment'].unique():
            env_data = df[(df['name'] == endpoint) & (df['environment'] == env)]
            if len(env_data) > 1:
                rps = env_data['requests_per_second'].values
                cv = (rps.std() / rps.mean() * 100) if rps.mean() > 0 else 0
                stability_data.append({'Endpoint': endpoint, 'Entorno': env, 'CV%': cv})
    
    stab_df = pd.DataFrame(stability_data)
    
    ax = sns.barplot(data=stab_df, x='Endpoint', y='CV%', hue='Entorno',
                    palette={'vps_no_docker': '#2ecc71', 'vps_docker': '#3498db'})
    
    plt.title('Estabilidad por Endpoint (Coeficiente de Variación %)', 
             fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Endpoint', fontsize=12)
    plt.ylabel('Coeficiente de Variación (%)', fontsize=12)
    plt.axhline(y=5, color='green', linestyle='--', alpha=0.5, label='Excelente (< 5%)')
    plt.axhline(y=15, color='red', linestyle='--', alpha=0.5, label='Crítico (> 15%)')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(EVIDENCE_DIR / '02_stability_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: 02_stability_comparison.png")
    plt.close()

def plot_overhead_with_confidence(df):
    """Gráfico: Overhead de Docker con intervalos de confianza."""
    overhead_data = []
    
    for endpoint in df['name'].unique():
        endpoint_data = df[df['name'] == endpoint]
        
        if 'vps_no_docker' not in endpoint_data['environment'].values or \
           'vps_docker' not in endpoint_data['environment'].values:
            continue
        
        no_docker = endpoint_data[endpoint_data['environment'] == 'vps_no_docker']
        with_docker = endpoint_data[endpoint_data['environment'] == 'vps_docker']
        
        rps_nd = no_docker['requests_per_second'].values
        rps_d = with_docker['requests_per_second'].values
        
        overhead = ((rps_d.mean() / rps_nd.mean() - 1) * 100) if rps_nd.mean() > 0 else 0
        
        overhead_data.append({
            'Endpoint': endpoint,
            'Overhead_%': overhead
        })
    
    if overhead_data:
        over_df = pd.DataFrame(overhead_data)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = ['red' if x < 0 else 'green' for x in over_df['Overhead_%']]
        ax.barh(over_df['Endpoint'], over_df['Overhead_%'], color=colors, alpha=0.7)
        ax.set_title('Overhead de Docker por Endpoint (10 Runs)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Cambio en RPS (%)', fontsize=12)
        ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        ax.axvline(x=-5, color='orange', linestyle='--', alpha=0.5)
        ax.axvline(x=-15, color='red', linestyle='--', alpha=0.5)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(EVIDENCE_DIR / '03_overhead_with_ci.png', dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico guardado: 03_overhead_with_ci.png")
        plt.close()

def plot_consistency_over_runs(df):
    """Gráfico: Consistencia a lo largo de las 10 pruebas."""
    plt.figure(figsize=(14, 8))
    
    for endpoint in sorted(df['name'].unique()):
        for env in df['environment'].unique():
            env_data = df[(df['name'] == endpoint) & (df['environment'] == env)].sort_values('test_number')
            
            label = f"{endpoint[:15]:<15} ({env.split('_')[1]})"
            color = '#2ecc71' if env == 'vps_no_docker' else '#3498db'
            
            plt.plot(env_data['test_number'], env_data['requests_per_second'], 
                    marker='o', label=label, color=color, alpha=0.7, linewidth=2)
    
    plt.title('Consistencia de RPS a lo Largo de las 10 Pruebas', 
             fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Número de Prueba', fontsize=12)
    plt.ylabel('Requests por Segundo (RPS)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best', fontsize=9)
    plt.tight_layout()
    
    plt.savefig(EVIDENCE_DIR / '04_consistency_over_runs.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: 04_consistency_over_runs.png")
    plt.close()

def generate_all_plots_improved(df):
    """Genera todos los gráficos mejorados."""
    print("\n" + "="*80)
    print("📈 GENERANDO GRÁFICOS MEJORADOS")
    print("="*80 + "\n")
    
    plot_distribution_boxplot(df)
    plot_stability_comparison(df)
    plot_overhead_with_confidence(df)
    plot_consistency_over_runs(df)

# ============================================================================
# EXPORTAR RESULTADOS
# ============================================================================

def export_results_improved(all_results: Dict):
    """Exporta todos los resultados mejorados."""
    print("\n" + "="*80)
    print("💾 EXPORTANDO RESULTADOS MEJORADOS")
    print("="*80 + "\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON
    json_file = RESULTS_DIR / f'analysis_improved_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"✅ JSON guardado: analysis_improved_{timestamp}.json")
    
    # CSV
    if all_results['statistical_summary']:
        csv_file = RESULTS_DIR / f'analysis_improved_{timestamp}.csv'
        stats_df = pd.DataFrame(all_results['statistical_summary'])
        stats_df.to_csv(csv_file, index=False)
        print(f"✅ CSV guardado: analysis_improved_{timestamp}.csv")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal."""
    print("\n" + "="*80)
    print("🚀 FastAPI Benchmark Analyzer - MEJORADO (6 Runs)")
    print("="*80 + "\n")
    
    # Setup
    setup_directories()
    
    # Determinar ruta de entrada
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = 'benchmark_results_improved'
    
    # Cargar datos
    df = load_benchmark_data(input_path)
    
    if df is None or df.empty:
        print("❌ No hay datos para analizar.")
        return
    
    print(f"✅ Total de pruebas cargadas: {len(df)}")
    print(f"   Endpoints únicos: {df['name'].nunique()}")
    print(f"   Entornos: {df['environment'].unique().tolist()}\n")
    
    # Ejecutar secciones
    all_results = {}
    
    all_results['statistical_summary'] = section_statistical_summary(df)
    all_results['reliability_analysis'] = section_reliability_analysis(df)
    all_results['docker_overhead'] = section_docker_overhead_improved(df)
    
    # Generar gráficos
    generate_all_plots_improved(df)
    
    # Exportar resultados
    export_results_improved(all_results)
    
    # Resumen final
    print("\n" + "="*80)
    print("✅ ANÁLISIS MEJORADO COMPLETADO")
    print("="*80 + "\n")
    
    print("📁 Archivos generados:")
    print(f"   📊 Gráficos: {EVIDENCE_DIR}")
    print(f"   📈 Resultados: {RESULTS_DIR}")
    print("\n")

if __name__ == "__main__":
    main()
