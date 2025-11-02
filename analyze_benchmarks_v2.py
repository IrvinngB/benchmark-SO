"""
Análisis Modular de Benchmarks FastAPI - VPS Only
Compara rendimiento entre VPS sin Docker vs VPS con Docker
Análisis multi-prueba con estadísticas robustas
Uso: python analyze_benchmarks_v2.py [directorio_benchmarks]
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
EVIDENCE_DIR = Path('benchmark_results/evidencia')
RESULTS_DIR = Path('benchmark_results')

def setup_directories():
    """Crea directorios necesarios."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Directorio de evidencia: {EVIDENCE_DIR}")

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

# ============================================================================
# SECCIÓN 1: ESTADÍSTICAS DESCRIPTIVAS
# ============================================================================

def section_descriptive_stats(df) -> Dict:
    """Sección 1: Estadísticas descriptivas por endpoint y entorno."""
    print("\n" + "="*80)
    print("📊 SECCIÓN 1: ESTADÍSTICAS DESCRIPTIVAS")
    print("="*80 + "\n")
    
    stats_data = []
    
    for endpoint in df['name'].unique():
        endpoint_data = df[df['name'] == endpoint]
        
        for env in endpoint_data['environment'].unique():
            env_data = endpoint_data[endpoint_data['environment'] == env]
            
            rps = env_data['requests_per_second'].values
            latency = env_data['avg_latency_ms'].values
            
            stats = {
                'Endpoint': endpoint,
                'Entorno': env,
                'RPS_Avg': rps.mean(),
                'RPS_Min': rps.min(),
                'RPS_Max': rps.max(),
                'RPS_Std': rps.std(),
                'Latency_Avg': latency.mean(),
                'Latency_Min': latency.min(),
                'Latency_Max': latency.max(),
                'Latency_Std': latency.std(),
                'Pruebas': len(env_data)
            }
            stats_data.append(stats)
    
    stats_df = pd.DataFrame(stats_data)
    
    print("Estadísticas por Endpoint y Entorno:")
    print("-" * 80)
    for endpoint in stats_df['Endpoint'].unique():
        print(f"\n📌 {endpoint}")
        endpoint_stats = stats_df[stats_df['Endpoint'] == endpoint]
        for _, row in endpoint_stats.iterrows():
            print(f"   {row['Entorno']:15} | RPS: {row['RPS_Avg']:7.2f}±{row['RPS_Std']:6.2f} | "
                  f"Latency: {row['Latency_Avg']:7.2f}ms | Pruebas: {int(row['Pruebas'])}")
    
    return stats_df.to_dict('records')

# ============================================================================
# SECCIÓN 2: COMPARACIÓN DOCKER vs SIN DOCKER
# ============================================================================

def section_docker_comparison(df) -> Dict:
    """Sección 2: Análisis comparativo del overhead de Docker."""
    print("\n" + "="*80)
    print("🔄 SECCIÓN 2: COMPARACIÓN DOCKER vs SIN DOCKER")
    print("="*80 + "\n")
    
    comparison_data = []
    
    for endpoint in df['name'].unique():
        endpoint_data = df[df['name'] == endpoint]
        
        if 'vps_no_docker' not in endpoint_data['environment'].values or \
           'vps_docker' not in endpoint_data['environment'].values:
            continue
        
        no_docker = endpoint_data[endpoint_data['environment'] == 'vps_no_docker']
        with_docker = endpoint_data[endpoint_data['environment'] == 'vps_docker']
        
        rps_no_docker = no_docker['requests_per_second'].mean()
        rps_docker = with_docker['requests_per_second'].mean()
        rps_overhead = ((rps_docker / rps_no_docker - 1) * 100) if rps_no_docker > 0 else 0
        
        lat_no_docker = no_docker['avg_latency_ms'].mean()
        lat_docker = with_docker['avg_latency_ms'].mean()
        lat_overhead = ((lat_docker / lat_no_docker - 1) * 100) if lat_no_docker > 0 else 0
        
        comparison = {
            'Endpoint': endpoint,
            'RPS_No_Docker': rps_no_docker,
            'RPS_Docker': rps_docker,
            'RPS_Overhead_%': rps_overhead,
            'Latency_No_Docker_ms': lat_no_docker,
            'Latency_Docker_ms': lat_docker,
            'Latency_Overhead_%': lat_overhead
        }
        comparison_data.append(comparison)
    
    comp_df = pd.DataFrame(comparison_data)
    
    print("Comparación RPS:")
    print("-" * 80)
    print(f"{'Endpoint':<25} {'Sin Docker':>15} {'Con Docker':>15} {'Overhead':>12}")
    print("-" * 80)
    for _, row in comp_df.iterrows():
        overhead_symbol = "⬇️ " if row['RPS_Overhead_%'] < 0 else "⬆️ "
        print(f"{row['Endpoint']:<25} {row['RPS_No_Docker']:>14.2f}  {row['RPS_Docker']:>14.2f}  "
              f"{overhead_symbol}{abs(row['RPS_Overhead_%']):>9.2f}%")
    
    print("\n\nComparación Latencia:")
    print("-" * 80)
    print(f"{'Endpoint':<25} {'Sin Docker':>15} {'Con Docker':>15} {'Overhead':>12}")
    print("-" * 80)
    for _, row in comp_df.iterrows():
        overhead_symbol = "⬆️ " if row['Latency_Overhead_%'] > 0 else "⬇️ "
        print(f"{row['Endpoint']:<25} {row['Latency_No_Docker_ms']:>14.2f}ms  "
              f"{row['Latency_Docker_ms']:>14.2f}ms  "
              f"{overhead_symbol}{abs(row['Latency_Overhead_%']):>9.2f}%")
    
    # Overhead promedio
    print("\n" + "="*80)
    avg_rps_overhead = comp_df['RPS_Overhead_%'].mean()
    avg_lat_overhead = comp_df['Latency_Overhead_%'].mean()
    print(f"📦 Overhead PROMEDIO de Docker:")
    print(f"   RPS: {avg_rps_overhead:+.2f}%")
    print(f"   Latencia: {avg_lat_overhead:+.2f}%")
    
    if abs(avg_rps_overhead) < 5:
        print("   ✅ El overhead de Docker es MÍNIMO (<5%)")
    elif abs(avg_rps_overhead) < 15:
        print("   ⚠️  Docker tiene un overhead MODERADO (5-15%)")
    else:
        print("   ❌ Docker tiene un overhead SIGNIFICATIVO (>15%)")
    
    return comp_df.to_dict('records')

# ============================================================================
# SECCIÓN 3: CONSISTENCIA Y VARIABILIDAD
# ============================================================================

def section_consistency(df) -> Dict:
    """Sección 3: Análisis de consistencia entre múltiples pruebas."""
    print("\n" + "="*80)
    print("📈 SECCIÓN 3: CONSISTENCIA Y VARIABILIDAD")
    print("="*80 + "\n")
    
    consistency_data = []
    
    for endpoint in df['name'].unique():
        for env in df['environment'].unique():
            env_data = df[(df['name'] == endpoint) & (df['environment'] == env)]
            
            if len(env_data) < 2:
                continue
            
            rps_values = env_data['requests_per_second'].values
            
            # Calcular coeficiente de variación
            cv = (rps_values.std() / rps_values.mean() * 100) if rps_values.mean() > 0 else 0
            
            consistency = {
                'Endpoint': endpoint,
                'Entorno': env,
                'Pruebas': len(env_data),
                'RPS_Promedio': rps_values.mean(),
                'RPS_Std': rps_values.std(),
                'CV_%': cv,
                'RPS_Min': rps_values.min(),
                'RPS_Max': rps_values.max()
            }
            consistency_data.append(consistency)
    
    cons_df = pd.DataFrame(consistency_data)
    
    print("Variabilidad de RPS entre pruebas:")
    print("-" * 80)
    print(f"{'Endpoint':<25} {'Entorno':<15} {'Pruebas':>7} {'Promedio':>10} {'CV%':>8}")
    print("-" * 80)
    for _, row in cons_df.iterrows():
        stability = "✅" if row['CV_%'] < 5 else "⚠️ " if row['CV_%'] < 15 else "❌"
        print(f"{row['Endpoint']:<25} {row['Entorno']:<15} {int(row['Pruebas']):>7} "
              f"{row['RPS_Promedio']:>10.2f}  {row['CV_%']:>7.2f}% {stability}")
    
    return cons_df.to_dict('records')

# ============================================================================
# SECCIÓN 4: IDENTIFICACIÓN DE CUELLOS DE BOTELLA
# ============================================================================

def section_bottlenecks(df) -> Dict:
    """Sección 4: Identifica endpoints con bajo rendimiento."""
    print("\n" + "="*80)
    print("🔴 SECCIÓN 4: CUELLOS DE BOTELLA")
    print("="*80 + "\n")
    
    bottleneck_data = []
    
    for endpoint in df['name'].unique():
        endpoint_data = df[df['name'] == endpoint]
        avg_rps = endpoint_data['requests_per_second'].mean()
        
        # Clasificar por rendimiento
        if avg_rps < 20:
            severity = "🔴 CRÍTICO"
            recommendation = "Necesita optimización urgente"
        elif avg_rps < 100:
            severity = "🟠 ALTO"
            recommendation = "Considera optimizar o implementar caché"
        elif avg_rps < 300:
            severity = "🟡 MODERADO"
            recommendation = "Monitorear en producción"
        else:
            severity = "🟢 BAJO"
            recommendation = "Rendimiento aceptable"
        
        bottleneck = {
            'Endpoint': endpoint,
            'RPS_Promedio': avg_rps,
            'Severidad': severity,
            'Recomendación': recommendation
        }
        bottleneck_data.append(bottleneck)
    
    # Ordenar por RPS
    bottleneck_df = pd.DataFrame(bottleneck_data).sort_values('RPS_Promedio')
    
    print("Endpoints por rendimiento (de menor a mayor RPS):")
    print("-" * 80)
    for _, row in bottleneck_df.iterrows():
        print(f"{row['Severidad']} {row['Endpoint']:<25} RPS: {row['RPS_Promedio']:>7.2f}")
        print(f"   → {row['Recomendación']}")
    
    return bottleneck_df.to_dict('records')

# ============================================================================
# SECCIÓN 5: RESUMEN EJECUTIVO
# ============================================================================

def section_executive_summary(df, stats, comparison, consistency, bottlenecks) -> Dict:
    """Sección 5: Resumen ejecutivo con conclusiones."""
    print("\n" + "="*80)
    print("📋 SECCIÓN 5: RESUMEN EJECUTIVO")
    print("="*80 + "\n")
    
    summary = {}
    
    # Total de pruebas
    total_tests = len(df)
    total_endpoints = df['name'].nunique()
    total_environments = df['environment'].nunique()
    
    print(f"📊 Datos Generales:")
    print(f"   • Total de pruebas: {total_tests}")
    print(f"   • Endpoints probados: {total_endpoints}")
    print(f"   • Entornos: {total_environments}")
    
    # Performance general
    avg_rps = df['requests_per_second'].mean()
    avg_latency = df['avg_latency_ms'].mean()
    
    print(f"\n⚡ Performance General:")
    print(f"   • RPS Promedio: {avg_rps:.2f} req/s")
    print(f"   • Latencia Promedio: {avg_latency:.2f} ms")
    
    # Errores
    total_errors = df['failed_requests'].sum() if 'failed_requests' in df.columns else 0
    total_requests = df['total_requests'].sum() if 'total_requests' in df.columns else total_tests * 1000
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
    
    print(f"\n❌ Confiabilidad:")
    print(f"   • Errores totales: {int(total_errors)} de {int(total_requests)}")
    print(f"   • Tasa de error: {error_rate:.2f}%")
    print(f"   • Estado: {'✅ EXCELENTE (0% errores)' if error_rate == 0 else '⚠️  REVISAR'}")
    
    # Mejores y peores endpoints
    if bottlenecks:
        bottleneck_df = pd.DataFrame(bottlenecks).sort_values('RPS_Promedio')
        best = bottleneck_df.iloc[-1]
        worst = bottleneck_df.iloc[0]
        
        print(f"\n🏆 Mejores y Peores Endpoints:")
        print(f"   ✅ Mejor: {best['Endpoint']} ({best['RPS_Promedio']:.2f} RPS)")
        print(f"   ❌ Peor: {worst['Endpoint']} ({worst['RPS_Promedio']:.2f} RPS)")
    
    # Recomendación Docker
    if comparison:
        comp_df = pd.DataFrame(comparison)
        avg_overhead = comp_df['RPS_Overhead_%'].mean()
        print(f"\n🐳 Recomendación Docker:")
        print(f"   • Overhead promedio: {avg_overhead:+.2f}%")
        if abs(avg_overhead) < 5:
            print(f"   • Conclusión: ✅ USAR DOCKER (overhead mínimo)")
        elif abs(avg_overhead) < 15:
            print(f"   • Conclusión: ⚖️  CONSIDERAR (overhead moderado)")
        else:
            print(f"   • Conclusión: ❌ BARE METAL (overhead significativo)")
    
    summary['total_tests'] = total_tests
    summary['total_endpoints'] = total_endpoints
    summary['avg_rps'] = float(avg_rps)
    summary['avg_latency'] = float(avg_latency)
    summary['error_rate'] = float(error_rate)
    
    return summary

# ============================================================================
# GRÁFICOS
# ============================================================================

def plot_rps_comparison(df):
    """Gráfico: Comparación RPS por endpoint y entorno."""
    plt.figure(figsize=(14, 7))
    colors = {'vps_no_docker': '#2ecc71', 'vps_docker': '#3498db'}
    ax = sns.barplot(data=df, x='name', y='requests_per_second', hue='environment', 
                     palette=colors, errorbar='sd')
    plt.title('RPS por Endpoint: Sin Docker vs Con Docker', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Endpoint', fontsize=12)
    plt.ylabel('Requests por Segundo', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Entorno', labels=['Sin Docker', 'Con Docker'], fontsize=10)
    plt.tight_layout()
    plt.savefig(EVIDENCE_DIR / '01_rps_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: 01_rps_comparison.png")
    plt.close()

def plot_latency_comparison(df):
    """Gráfico: Comparación Latencia por endpoint y entorno."""
    plt.figure(figsize=(14, 7))
    colors = {'vps_no_docker': '#2ecc71', 'vps_docker': '#3498db'}
    ax = sns.barplot(data=df, x='name', y='avg_latency_ms', hue='environment', 
                     palette=colors, errorbar='sd')
    plt.title('Latencia Promedio por Endpoint: Sin Docker vs Con Docker', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Endpoint', fontsize=12)
    plt.ylabel('Latencia (ms)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Entorno', labels=['Sin Docker', 'Con Docker'], fontsize=10)
    plt.tight_layout()
    plt.savefig(EVIDENCE_DIR / '02_latency_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: 02_latency_comparison.png")
    plt.close()

def plot_docker_overhead(df):
    """Gráfico: Overhead de Docker por endpoint."""
    comp_data = []
    
    for endpoint in df['name'].unique():
        endpoint_data = df[df['name'] == endpoint]
        
        if 'vps_no_docker' not in endpoint_data['environment'].values or \
           'vps_docker' not in endpoint_data['environment'].values:
            continue
        
        no_docker = endpoint_data[endpoint_data['environment'] == 'vps_no_docker']
        with_docker = endpoint_data[endpoint_data['environment'] == 'vps_docker']
        
        rps_no_docker = no_docker['requests_per_second'].mean()
        rps_docker = with_docker['requests_per_second'].mean()
        overhead = ((rps_docker / rps_no_docker - 1) * 100) if rps_no_docker > 0 else 0
        
        comp_data.append({'Endpoint': endpoint, 'Overhead': overhead})
    
    if comp_data:
        comp_df = pd.DataFrame(comp_data)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['red' if x < 0 else 'green' for x in comp_df['Overhead']]
        ax.barh(comp_df['Endpoint'], comp_df['Overhead'], color=colors, alpha=0.7)
        ax.set_title('Overhead de Docker por Endpoint', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Cambio en RPS (%)', fontsize=12)
        ax.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(EVIDENCE_DIR / '03_docker_overhead.png', dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico guardado: 03_docker_overhead.png")
        plt.close()

def plot_consistency(df):
    """Gráfico: Consistencia entre múltiples pruebas."""
    plt.figure(figsize=(14, 7))
    
    data_consistency = []
    for endpoint in df['name'].unique():
        for env in df['environment'].unique():
            env_data = df[(df['name'] == endpoint) & (df['environment'] == env)]
            if len(env_data) > 1:
                for idx, row in env_data.iterrows():
                    data_consistency.append({
                        'Endpoint': endpoint,
                        'Entorno': env,
                        'RPS': row['requests_per_second'],
                        'Prueba': idx
                    })
    
    if data_consistency:
        cons_df = pd.DataFrame(data_consistency)
        sns.lineplot(data=cons_df, x='Endpoint', y='RPS', hue='Entorno', 
                     marker='o', markersize=8, palette={'vps_no_docker': '#2ecc71', 'vps_docker': '#3498db'})
        plt.title('Consistencia de RPS entre Pruebas', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Endpoint', fontsize=12)
        plt.ylabel('Requests por Segundo', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Entorno', labels=['Sin Docker', 'Con Docker'], fontsize=10)
        plt.tight_layout()
        plt.savefig(EVIDENCE_DIR / '04_consistency.png', dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico guardado: 04_consistency.png")
        plt.close()

def plot_performance_heatmap(df):
    """Gráfico: Heatmap de rendimiento."""
    pivot_df = df.pivot_table(
        values='requests_per_second',
        index='name',
        columns='environment',
        aggfunc='mean'
    )
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_df, annot=True, fmt='.2f', cmap='RdYlGn', cbar_kws={'label': 'RPS'})
    plt.title('Heatmap de RPS: Endpoints vs Entornos', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(EVIDENCE_DIR / '05_heatmap_rps.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: 05_heatmap_rps.png")
    plt.close()

def generate_all_plots(df):
    """Genera todos los gráficos."""
    print("\n" + "="*80)
    print("📈 GENERANDO GRÁFICOS")
    print("="*80 + "\n")
    
    plot_rps_comparison(df)
    plot_latency_comparison(df)
    plot_docker_overhead(df)
    plot_consistency(df)
    plot_performance_heatmap(df)

# ============================================================================
# EXPORTAR RESULTADOS
# ============================================================================

def export_results(all_results: Dict):
    """Exporta todos los resultados a CSV, JSON y TXT."""
    print("\n" + "="*80)
    print("💾 EXPORTANDO RESULTADOS")
    print("="*80 + "\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Exportar a CSV
    stats_df = pd.DataFrame(all_results['descriptive_stats'])
    csv_file = RESULTS_DIR / f'analysis_results_{timestamp}.csv'
    stats_df.to_csv(csv_file, index=False)
    print(f"✅ CSV guardado: analysis_results_{timestamp}.csv")
    
    # Exportar a JSON
    json_file = RESULTS_DIR / f'analysis_results_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"✅ JSON guardado: analysis_results_{timestamp}.json")
    
    # Exportar a TXT
    txt_file = RESULTS_DIR / f'analysis_results_{timestamp}.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("ANÁLISIS DE BENCHMARKS FastAPI - VPS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Estadísticas
        f.write("ESTADÍSTICAS DESCRIPTIVAS\n")
        f.write("-" * 80 + "\n")
        f.write(stats_df.to_string())
        f.write("\n\n")
        
        # Comparación Docker
        if all_results['docker_comparison']:
            f.write("COMPARACIÓN DOCKER vs SIN DOCKER\n")
            f.write("-" * 80 + "\n")
            comp_df = pd.DataFrame(all_results['docker_comparison'])
            f.write(comp_df.to_string())
            f.write("\n\n")
    
    print(f"✅ TXT guardado: analysis_results_{timestamp}.txt")
    
    return timestamp

def generate_readme(all_results: Dict, timestamp: str):
    """Genera README con los resultados del análisis."""
    readme_file = RESULTS_DIR / 'ANALYSIS_README.md'
    
    summary = all_results['executive_summary']
    
    content = f"""# 📊 Análisis de Benchmarks FastAPI - VPS

**Fecha de Análisis:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 Resumen Ejecutivo

### Datos Generales
- **Total de pruebas:** {summary['total_tests']}
- **Endpoints probados:** {summary['total_endpoints']}
- **Entornos:** 2 (Sin Docker, Con Docker)

### Performance General
- **RPS Promedio:** {summary['avg_rps']:.2f} req/s
- **Latencia Promedio:** {summary['avg_latency']:.2f} ms
- **Tasa de Error:** {summary['error_rate']:.2f}%

---

## 📊 Secciones del Análisis

### 1️⃣ Estadísticas Descriptivas
Análisis detallado de RPS y latencia por endpoint y entorno.

**Métricas capturadas:**
- Promedio, mínimo, máximo y desviación estándar
- Múltiples pruebas por configuración
- Comparación lado a lado

### 2️⃣ Comparación Docker vs Sin Docker
Overhead de containerización.

**Hallazgos clave:**
- RPS Overhead: Ver gráficos en carpeta `evidencia/`
- Latencia Overhead: Ver gráficos en carpeta `evidencia/`
- Recomendación: Revisar `03_docker_overhead.png`

### 3️⃣ Consistencia y Variabilidad
Análisis de estabilidad entre múltiples pruebas.

**Coeficiente de Variación (CV%):**
- CV < 5%: ✅ Excelente estabilidad
- CV 5-15%: ⚠️ Moderada variabilidad
- CV > 15%: ❌ Alta variabilidad

### 4️⃣ Cuellos de Botella
Identificación de endpoints con bajo rendimiento.

**Clasificación:**
- 🔴 CRÍTICO: < 20 RPS
- 🟠 ALTO: 20-100 RPS
- 🟡 MODERADO: 100-300 RPS
- 🟢 BAJO: > 300 RPS

### 5️⃣ Resumen Ejecutivo
Conclusiones y recomendaciones.

---

## 📁 Estructura de Resultados

```
benchmark_results/
├── evidencia/
│   ├── 01_rps_comparison.png          # Comparación RPS
│   ├── 02_latency_comparison.png      # Comparación Latencia
│   ├── 03_docker_overhead.png         # Overhead de Docker
│   ├── 04_consistency.png             # Consistencia entre pruebas
│   └── 05_heatmap_rps.png             # Heatmap de rendimiento
├── analysis_results_{timestamp}.csv   # Datos en CSV
├── analysis_results_{timestamp}.json  # Datos en JSON
├── analysis_results_{timestamp}.txt   # Resumen en TXT
└── ANALYSIS_README.md                 # Este archivo
```

---

## 🎯 Recomendaciones

### Para Optimización
1. Revisar endpoints con severidad 🔴 CRÍTICO
2. Implementar caché para endpoints pesados
3. Considerar paginación para respuestas grandes

### Para Docker
- Revisar `03_docker_overhead.png` para decisión de deployment
- Si overhead < 5%: Usar Docker
- Si overhead 5-15%: Considerar necesidad de portabilidad
- Si overhead > 15%: Evaluar bare metal

### Para Testing
- Realizar pruebas durante diferentes horas del día
- Monitorear recursos del VPS durante benchmarks
- Aumentar número de pruebas para mayor precisión estadística

---

## 📊 Gráficos Disponibles

1. **01_rps_comparison.png**: Comparación de RPS entre entornos
2. **02_latency_comparison.png**: Comparación de latencia
3. **03_docker_overhead.png**: Impacto de Docker en RPS
4. **04_consistency.png**: Variabilidad entre múltiples pruebas
5. **05_heatmap_rps.png**: Vista general de rendimiento

---

## 🔧 Cómo Regenerar Análisis

```bash
# Con carpeta de benchmarks
python analyze_benchmarks_v2.py benchmark_results

# O con archivo CSV específico
python analyze_benchmarks_v2.py archivo.csv
```

---

**Generado por:** FastAPI Benchmark Analyzer v2.0
**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ README guardado: ANALYSIS_README.md")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal."""
    print("\n" + "="*80)
    print("🚀 FastAPI Benchmark Analyzer v2.0")
    print("   Análisis Modular y Seccionalizado de Benchmarks")
    print("="*80 + "\n")
    
    # Setup
    setup_directories()
    
    # Determinar ruta de entrada
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = 'benchmark_results'
    
    # Cargar datos
    df = load_benchmark_data(input_path)
    
    if df is None or df.empty:
        print("❌ No hay datos para analizar.")
        return
    
    # Convertir timestamp a datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Ejecutar secciones
    all_results = {}
    
    all_results['descriptive_stats'] = section_descriptive_stats(df)
    all_results['docker_comparison'] = section_docker_comparison(df)
    all_results['consistency'] = section_consistency(df)
    all_results['bottlenecks'] = section_bottlenecks(df)
    all_results['executive_summary'] = section_executive_summary(
        df, 
        all_results['descriptive_stats'],
        all_results['docker_comparison'],
        all_results['consistency'],
        all_results['bottlenecks']
    )
    
    # Generar gráficos
    generate_all_plots(df)
    
    # Exportar resultados
    timestamp = export_results(all_results)
    generate_readme(all_results, timestamp)
    
    # Resumen final
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80 + "\n")
    
    print("📁 Archivos generados:")
    print(f"   📊 Gráficos: benchmark_results/evidencia/")
    print(f"   📈 CSV: analysis_results_{timestamp}.csv")
    print(f"   📋 TXT: analysis_results_{timestamp}.txt")
    print(f"   📖 JSON: analysis_results_{timestamp}.json")
    print(f"   📄 README: ANALYSIS_README.md")
    print()

if __name__ == "__main__":
    main()
