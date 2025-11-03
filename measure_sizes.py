#!/usr/bin/env python3
"""
Mide el tamaño de datos que envían los endpoints
Ayuda a optimizar benchmarking eliminando endpoints innecesarios
"""

import requests
import json
from datetime import datetime
from colorama import init, Fore, Back, Style

init(autoreset=True)

# Endpoints a medir
ENDPOINTS = [
    {"name": "Root Endpoint (Baseline)", "path": "/"},
    {"name": "Health Check", "path": "/health"},
    {"name": "Async Light", "path": "/async-light"},
    {"name": "Heavy Computation", "path": "/heavy"},
    {"name": "Large JSON Response", "path": "/json-large?page=1&limit=50"},
]

SERVERS = {
    "local": "localhost:8000",
    "vps_no_docker": "138.68.233.15:8000",
    "vps_docker": "68.183.168.86:8000",
}

def get_content_size(url):
    """Obtiene el tamaño del contenido en bytes"""
    try:
        response = requests.get(url, timeout=10)
        
        # Tamaño del body
        body_size = len(response.content)
        
        # Tamaño de headers
        headers_size = sum(len(k) + len(v) for k, v in response.headers.items())
        
        # Tamaño total (aproximado)
        total_size = body_size + headers_size
        
        return {
            "status": response.status_code,
            "body_bytes": body_size,
            "headers_bytes": headers_size,
            "total_bytes": total_size,
            "success": True,
            "content_type": response.headers.get('content-type', 'unknown')
        }
    except Exception as e:
        return {
            "status": None,
            "body_bytes": 0,
            "headers_bytes": 0,
            "total_bytes": 0,
            "success": False,
            "error": str(e)
        }

def format_bytes(bytes_val):
    """Convierte bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} TB"

def main():
    print(f"\n{Back.CYAN}{Fore.BLACK}{'═' * 90}{Style.RESET_ALL}")
    print(f"{Back.CYAN}{Fore.BLACK}  📊 MEDIDOR DE TAMAÑO DE RESPUESTAS - FastAPI Endpoints{Style.RESET_ALL}")
    print(f"{Back.CYAN}{Fore.BLACK}{'═' * 90}{Style.RESET_ALL}\n")
    
    # Medir endpoints
    results = {}
    
    for server_name, server_url in SERVERS.items():
        print(f"\n{Fore.YELLOW}🌐 Servidor: {server_name} ({server_url}){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 90}{Style.RESET_ALL}")
        
        results[server_name] = {}
        
        # Verificar conectividad
        try:
            response = requests.get(f"http://{server_url}/health", timeout=5)
            print(f"{Fore.GREEN}✅ Servidor accesible{Style.RESET_ALL}\n")
        except:
            print(f"{Fore.RED}❌ No se puede conectar a {server_url}{Style.RESET_ALL}\n")
            continue
        
        # Medir cada endpoint
        for endpoint in ENDPOINTS:
            url = f"http://{server_url}{endpoint['path']}"
            result = get_content_size(url)
            results[server_name][endpoint['name']] = result
            
            if result['success']:
                print(f"{Fore.CYAN}{endpoint['name']:30}{Style.RESET_ALL} ", end="")
                print(f"│ {Fore.GREEN}{format_bytes(result['body_bytes']):>12}{Style.RESET_ALL} ", end="")
                print(f"│ {Fore.BLUE}({format_bytes(result['total_bytes']):>12} total){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{endpoint['name']:30} ❌ Error: {result['error']}{Style.RESET_ALL}")
    
    # Análisis y recomendaciones
    print(f"\n{Back.CYAN}{Fore.BLACK}{'═' * 90}{Style.RESET_ALL}")
    print(f"{Back.CYAN}{Fore.BLACK}  📈 ANÁLISIS Y RECOMENDACIONES{Style.RESET_ALL}")
    print(f"{Back.CYAN}{Fore.BLACK}{'═' * 90}{Style.RESET_ALL}\n")
    
    # Encontrar endpoint más ligero y más pesado (usando el primero disponible)
    first_server = list(results.keys())[0]
    server_results = results[first_server]
    
    if server_results:
        sizes = [(name, data['body_bytes']) for name, data in server_results.items() if data['success']]
        
        if sizes:
            sizes_sorted = sorted(sizes, key=lambda x: x[1])
            lightest = sizes_sorted[0]
            heaviest = sizes_sorted[-1]
            
            print(f"{Fore.GREEN}✨ Endpoint más ligero: {lightest[0]}")
            print(f"   Tamaño: {format_bytes(lightest[1])}{Style.RESET_ALL}\n")
            
            print(f"{Fore.RED}⚡ Endpoint más pesado: {heaviest[0]}")
            print(f"   Tamaño: {format_bytes(heaviest[1])}{Style.RESET_ALL}\n")
            
            ratio = heaviest[1] / lightest[1] if lightest[1] > 0 else 0
            print(f"{Fore.MAGENTA}📊 Ratio (pesado/ligero): {ratio:.1f}x{Style.RESET_ALL}\n")
    
    # Recomendaciones de benchmark optimizado
    print(f"{Fore.YELLOW}💡 RECOMENDACIONES PARA OPTIMIZAR BENCHMARK:{Style.RESET_ALL}\n")
    
    print(f"  {Fore.CYAN}1. Endpoints 'suaves' (Baseline, Health, Async Light):")
    print(f"     → Son rápidos y ligeros, no necesitan 1000 requests")
    print(f"     → Reducir a: 100-200 requests por prueba{Style.RESET_ALL}\n")
    
    print(f"  {Fore.GREEN}2. Endpoint 'Heavy':")
    print(f"     → Es el más importante para medir rendimiento real")
    print(f"     → Mantener con: 500-1000 requests por prueba{Style.RESET_ALL}\n")
    
    print(f"  {Fore.BLUE}3. Large JSON Response:")
    print(f"     → Importancia media (mide transferencia de datos)")
    print(f"     → Usar: 300-500 requests por prueba{Style.RESET_ALL}\n")
    
    print(f"{Fore.MAGENTA}✅ Beneficio: Reduce tiempo de benchmark ~70% con datos más relevantes{Style.RESET_ALL}\n")
    
    # Guardar datos en JSON para análisis
    output_file = "endpoint_sizes.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📁 Datos guardados en: {output_file}")

if __name__ == "__main__":
    main()
