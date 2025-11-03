#!/usr/bin/env python3
"""
Script para ejecutar el benchmark y preparar resultados para Git
===============================================================
Este script ejecuta el benchmark Python y automáticamente organiza
los resultados en la carpeta resultados_muestra para subirlos a Git.

Uso:
    python run_benchmark_to_git.py
    python run_benchmark_to_git.py --quick        # Prueba rápida
    python run_benchmark_to_git.py --full         # Benchmark completo
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import json

def run_benchmark(quick_test=False):
    """Ejecuta el benchmark Python"""
    
    print("🚀 Iniciando benchmark FastAPI Python Edition")
    print("=" * 60)
    
    # Preparar comando
    cmd = ["python", "benchmark_python.py"]
    
    if quick_test:
        print("⚡ Modo prueba rápida (2 tests, 100 requests)")
        cmd.extend(["--tests", "2", "--requests", "100", "--connections", "25"])
    else:
        print("📊 Benchmark completo (6 tests)")
        cmd.extend(["--tests", "6"])
    
    # Ejecutar
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando benchmark: {e}")
        return False

def verify_results():
    """Verifica que los resultados se generaron correctamente"""
    
    print("\n✅ Verificando resultados...")
    print("=" * 60)
    
    resultados_dir = Path("resultados_muestra")
    
    if not resultados_dir.exists():
        print("❌ Carpeta resultados_muestra no encontrada")
        return False
    
    # Buscar archivos generados
    csv_files = list(resultados_dir.glob("benchmark_detailed_*.csv"))
    json_files = list(resultados_dir.glob("benchmark_detailed_*.json"))
    xlsx_files = list(resultados_dir.glob("benchmark_analysis_*.xlsx"))
    md_files = list(resultados_dir.glob("benchmark_report_*.md"))
    viz_dirs = list(resultados_dir.glob("visualizations_*"))
    
    print(f"📊 Archivos generados:")
    print(f"   CSV: {len(csv_files)} archivo(s)")
    print(f"   JSON: {len(json_files)} archivo(s)")
    print(f"   XLSX: {len(xlsx_files)} archivo(s)")
    print(f"   Reportes MD: {len(md_files)} archivo(s)")
    print(f"   Carpetas de visualizaciones: {len(viz_dirs)}")
    
    if csv_files:
        latest_csv = sorted(csv_files)[-1]
        csv_size = latest_csv.stat().st_size / (1024 * 1024)  # MB
        print(f"\n   📈 Último CSV: {latest_csv.name} ({csv_size:.2f} MB)")
    
    if viz_dirs:
        latest_viz = sorted(viz_dirs)[-1]
        png_count = len(list(latest_viz.glob("*.png")))
        print(f"   🎨 Gráficos: {png_count} imagen(s)")
    
    all_ok = len(csv_files) > 0 and len(json_files) > 0
    
    if all_ok:
        print("\n✅ Todos los archivos generados correctamente")
    else:
        print("\n⚠️ Algunos archivos pueden no haberse generado")
    
    return all_ok

def create_summary():
    """Crea un resumen de la ejecución"""
    
    summary_file = Path("resultados_muestra") / "LAST_RUN_SUMMARY.json"
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "benchmark_version": "Python Edition 1.0",
        "status": "completed",
        "output_directory": "resultados_muestra",
        "git_ready": True,
        "files_generated": {
            "csv": len(list(Path("resultados_muestra").glob("benchmark_detailed_*.csv"))),
            "json": len(list(Path("resultados_muestra").glob("benchmark_detailed_*.json"))),
            "xlsx": len(list(Path("resultados_muestra").glob("benchmark_analysis_*.xlsx"))),
            "markdown": len(list(Path("resultados_muestra").glob("benchmark_report_*.md"))),
            "visualizations": len(list(Path("resultados_muestra").glob("visualizations_*")))
        }
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📝 Resumen guardado en: LAST_RUN_SUMMARY.json")

def show_git_commands():
    """Muestra los comandos Git para subir los resultados"""
    
    print("\n" + "=" * 60)
    print("📤 PRÓXIMOS PASOS - Subir resultados a Git")
    print("=" * 60)
    
    commands = [
        ("Verificar estado", "git status"),
        ("Agregar resultados", "git add resultados_muestra/"),
        ("Crear commit", 'git commit -m "Benchmarks Python: resultados del 02/11/2025"'),
        ("Subir a remote", "git push origin main"),
    ]
    
    for step, cmd in commands:
        print(f"\n{step}:")
        print(f"  $ {cmd}")
    
    print("\n💡 Alternativamente, combina en un comando:")
    print("  $ git add resultados_muestra/ && git commit -m 'Benchmark results' && git push")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ejecutar benchmark y preparar para Git"
    )
    parser.add_argument('--quick', action='store_true', 
                       help='Modo prueba rápida (2 tests)')
    parser.add_argument('--full', action='store_true',
                       help='Benchmark completo (6 tests, default)')
    parser.add_argument('--verify-only', action='store_true',
                       help='Solo verificar resultados existentes')
    
    args = parser.parse_args()
    
    # Si solo verificar
    if args.verify_only:
        print("🔍 Verificando resultados existentes...")
        verify_results()
        show_git_commands()
        return
    
    # Ejecutar benchmark
    print("🎯 Pipeline: Benchmark → Resultados → Git Ready")
    print()
    
    quick = args.quick or not args.full
    
    if run_benchmark(quick_test=quick):
        print("\n✅ Benchmark ejecutado exitosamente\n")
        
        if verify_results():
            create_summary()
            show_git_commands()
            
            print("\n✨ Los resultados están listos para Git!")
            print("   Todos los archivos están en la carpeta: resultados_muestra/")
        else:
            print("\n⚠️ Hay problemas con los resultados generados")
            sys.exit(1)
    else:
        print("\n❌ Error durante el benchmark")
        sys.exit(1)

if __name__ == "__main__":
    main()