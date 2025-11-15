#!/usr/bin/env python3
"""
Logging Manager para FastAPI Performance Benchmark
===================================================
Sistema avanzado de logging con:
- Rotación automática diaria
- Múltiples niveles de severidad
- Separación de logs por categoría específica
- Creación automática de directorios cross-platform
- Rutas absolutas para máxima compatibilidad
- Singleton thread-safe
- Logging resiliente ante crashes

Estructura de Carpetas:
logs/
├── errors/             # Logs de errores (error_YYYY-MM-DD.log)
├── requests/           # Logs de requests HTTP (requests_YYYY-MM-DD.log)
├── system/             # Monitoreo sistema (system_YYYY-MM-DD.log)
├── benchmark/          # Eventos benchmark (benchmark_YYYY-MM-DD.log)
├── connectivity/       # Tests conectividad (connectivity_YYYY-MM-DD.log)
└── README.md           # Documentación del sistema
"""

import logging
import logging.handlers
import os
import sys
import gzip
import shutil
import json
import warnings
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import threading
import traceback
import atexit


class SafeDailyRotatingFileHandler(logging.FileHandler):
    """Handler robusto con rotación diaria y manejo de errores"""
    
    def __init__(self, log_dir: Path, log_type: str):
        self.log_dir = Path(log_dir).resolve()  # Ruta absoluta
        self.log_type = log_type
        self.current_date = datetime.now().date()
        
        # Crear directorio con manejo de errores
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            warnings.warn(f"No se pudo crear directorio {self.log_dir} por permisos")
            # Fallback a directorio actual
            self.log_dir = Path.cwd().resolve() / "logs_fallback" / log_type
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        filename = self._get_filename()
        super().__init__(str(filename), mode='a', encoding='utf-8')
        
    def _get_filename(self) -> Path:
        """Genera nombre de archivo con formato específico"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{self.log_type}_{date_str}.log"
        return self.log_dir / filename
    
    def emit(self, record: logging.LogRecord) -> None:
        """Override para verificar rotación diaria y manejo seguro"""
        try:
            # Verificar si cambió la fecha
            current_date = datetime.now().date()
            if current_date != self.current_date:
                self._rotate_to_new_day()
                self.current_date = current_date
            
            super().emit(record)
            
        except Exception as e:
            # Fallback a stderr si hay problemas con archivos
            fallback_msg = f"[LOG ERROR] {record.getMessage()}"
            print(fallback_msg, file=sys.stderr)
            print(f"[LOG ERROR DETAILS] {e}", file=sys.stderr)
    
    def _rotate_to_new_day(self) -> None:
        """Rotar a nuevo archivo para el nuevo día"""
        try:
            new_filename = self._get_filename()
            self.close()
            self.baseFilename = str(new_filename)
            self.stream = self._open()
        except Exception as e:
            print(f"Error durante rotación: {e}", file=sys.stderr)


class BenchmarkLogManager:
    """Gestor centralizado de logging para benchmarking - Singleton thread-safe"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, log_root: Optional[str] = None):
        """Implementar patrón Singleton thread-safe"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, log_root: Optional[str] = None):
        """Inicializar LogManager con estructura de directorios requerida"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        # Configurar ruta raíz de logs con ruta absoluta (al mismo nivel del proyecto)
        if log_root is None:
            self.log_root = Path(__file__).parent.parent.resolve() / "logs"
        else:
            self.log_root = Path(log_root).resolve()
        
        # Definir estructura de directorios específica
        self.errors_dir = self.log_root / "errors"
        self.requests_dir = self.log_root / "requests" 
        self.system_dir = self.log_root / "system"
        self.benchmark_dir = self.log_root / "benchmark"
        self.connectivity_dir = self.log_root / "connectivity"
        
        # Crear directorios inmediatamente
        self.create_directories()
        
        # Inicializar loggers especializados
        self._setup_loggers()
        
        # Crear README
        self._create_readme()
        
        # Registrar cleanup en exit
        atexit.register(self._cleanup_on_exit)
        
        self._initialized = True
    
    def create_directories(self) -> None:
        """Crear TODAS las carpetas necesarias con manejo de errores"""
        directories = [
            self.errors_dir,
            self.requests_dir,
            self.system_dir, 
            self.benchmark_dir,
            self.connectivity_dir
        ]
        
        created_dirs = []
        failed_dirs = []
        
        for dir_path in directories:
            try:
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(str(dir_path))
                    print(f"✅ Directorio creado: {dir_path}")
                # No imprimir si ya existe
            except PermissionError as e:
                failed_dirs.append(str(dir_path))
                warnings.warn(f"⚠️ No se pudo crear {dir_path} por permisos: {e}")
            except Exception as e:
                failed_dirs.append(str(dir_path))
                warnings.warn(f"⚠️ Error creando {dir_path}: {e}")
        
        if created_dirs:
            print(f"📁 {len(created_dirs)} directorios nuevos creados")
        elif not failed_dirs:
            print(f"📁 Estructura de directorios verificada")
        if failed_dirs:
            print(f"⚠️ {len(failed_dirs)} directorios fallaron")
    
    def _cleanup_on_exit(self) -> None:
        """Cleanup al cerrar aplicación"""
        try:
            for logger_name, logger in self._get_all_loggers().items():
                for handler in logger.handlers:
                    handler.close()
        except:
            pass  # Ignore cleanup errors
    
    def _setup_loggers(self) -> None:
        """Configurar loggers especializados para cada categoría"""
        
        # 1. Logger de Errores (CONSOLE + FILE)
        self.error_logger = self._create_logger(
            name="benchmark.errors",
            handlers=[
                ('console', logging.StreamHandler(sys.stderr), logging.WARNING),
                ('file', SafeDailyRotatingFileHandler(self.errors_dir, "error"), logging.DEBUG),
            ]
        )
        
        # 2. Logger de Requests HTTP (CONSOLE + FILE)
        self.request_logger = self._create_logger(
            name="benchmark.requests",
            handlers=[
                ('console', logging.StreamHandler(sys.stdout), logging.INFO),
                ('file', SafeDailyRotatingFileHandler(self.requests_dir, "requests"), logging.DEBUG),
            ]
        )
        
        # 3. Logger de Sistema/Monitoreo (FILE ONLY)
        self.system_logger = self._create_logger(
            name="benchmark.system",
            handlers=[
                ('file', SafeDailyRotatingFileHandler(self.system_dir, "system"), logging.DEBUG),
            ]
        )
        
        # 4. Logger de Benchmark General (CONSOLE + FILE)
        self.benchmark_logger = self._create_logger(
            name="benchmark.general",
            handlers=[
                ('console', logging.StreamHandler(sys.stdout), logging.INFO),
                ('file', SafeDailyRotatingFileHandler(self.benchmark_dir, "benchmark"), logging.DEBUG),
            ]
        )
        
        # 5. Logger de Conectividad (CONSOLE + FILE)
        self.connectivity_logger = self._create_logger(
            name="benchmark.connectivity",
            handlers=[
                ('console', logging.StreamHandler(sys.stdout), logging.INFO),
                ('file', SafeDailyRotatingFileHandler(self.connectivity_dir, "connectivity"), logging.DEBUG),
            ]
        )
        
        # Diccionario para acceso fácil
        self.loggers = {
            'error': self.error_logger,
            'request': self.request_logger,
            'system': self.system_logger,
            'benchmark': self.benchmark_logger,
            'connectivity': self.connectivity_logger,
        }
    
    def _get_all_loggers(self) -> Dict[str, logging.Logger]:
        """Obtener todos los loggers para cleanup"""
        return getattr(self, 'loggers', {})
    
    def _create_logger(self, name: str, handlers: List[tuple]) -> logging.Logger:
        """Crear logger con handlers personalizados"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Limpiar handlers anteriores
        logger.handlers.clear()
        
        # Crear formato detallado
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Agregar handlers
        for handler_name, handler, level in handlers:
            handler.setLevel(level)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        # Prevenir propagación a root logger
        logger.propagate = False
        
        return logger
    
    def _create_readme(self) -> None:
        """Crear archivo README en el directorio de logs"""
        readme_path = self.log_root / "README.md"
        
        readme_content = """# Sistema de Logging - FastAPI Performance Benchmark

## Estructura de Directorios

```
.logs/
├── daily/           # Logs generales por día
│                   # Contiene logs de todas las operaciones
│
├── errors/          # Logs de errores y advertencias
│                   # Solamente logs con nivel ERROR y WARNING
│
├── performance/     # Logs de métricas de rendimiento
│                   # Datos de RPS, latencia, CPU, memoria
│
├── archive/         # Logs comprimidos (>7 días)
│                   # Estructura: YYYY-MM-DD_*.log.gz
│
└── README.md        # Este archivo
```

## Formatos de Archivo

### Logs Diarios
- **Patrón:** `YYYY-MM-DD.log`
- **Contenido:** Logs generales, inicio/fin de tests, eventos principales
- **Nivel:** DEBUG+
- **Ejemplo:** `2025-11-14.log`

### Logs de Errores
- **Patrón:** `YYYY-MM-DD_errors.log`
- **Contenido:** Errores y advertencias de ejecución
- **Nivel:** WARNING+
- **Ejemplo:** `2025-11-14_errors.log`

### Logs de Rendimiento
- **Patrón:** `YYYY-MM-DD_performance.log`
- **Contenido:** Métricas de cada prueba (RPS, latencia, CPU, memoria)
- **Nivel:** DEBUG+
- **Ejemplo:** `2025-11-14_performance.log`

### Logs de Conectividad
- **Patrón:** `YYYY-MM-DD_connectivity.log` (dentro de performance/)
- **Contenido:** Estados de conexión a servidores
- **Nivel:** INFO+
- **Ejemplo:** `2025-11-14_connectivity.log`

### Logs de Configuración
- **Patrón:** `YYYY-MM-DD_config.log`
- **Contenido:** Parámetros de ejecución, configuración de benchmarks
- **Nivel:** INFO+
- **Ejemplo:** `2025-11-14_config.log`

## Política de Retención

- **Logs activos:** Últimos 7 días en directorios activos
- **Logs antiguos:** Comprimidos automáticamente a `.logs/archive/`
- **Compresión:** Archivos de más de 7 días se comprimen con gzip (50-80% reducción)
- **Limpieza manual:** Ver script `cleanup_logs.py`

## Campos de Log Estándar

```
TIMESTAMP | LOGGER_NAME | LEVEL | MESSAGE
YYYY-MM-DD HH:MM:SS | benchmark.general | INFO | Iniciando prueba...
```

## Análisis de Logs

### Ver logs en tiempo real
```bash
# Logs generales
tail -f .logs/daily/$(date +%Y-%m-%d).log

# Errores recientes
tail -f .logs/errors/$(date +%Y-%m-%d)_errors.log

# Rendimiento actual
tail -f .logs/performance/$(date +%Y-%m-%d)_performance.log
```

### Buscar eventos específicos
```bash
# Buscar todos los errores de hoy
grep ERROR .logs/errors/$(date +%Y-%m-%d)_errors.log

# Buscar resultados de un endpoint
grep "Heavy Computation" .logs/performance/$(date +%Y-%m-%d)_performance.log

# Buscar problemas de conexión
grep "FAIL\|ERROR" .logs/performance/$(date +%Y-%m-%d)_connectivity.log
```

## Volumen Estimado (4 semanas)

Por ejecución diaria con 30 pruebas:
- **Logs generales:** ~2-5 MB/día
- **Logs de errores:** ~100-500 KB/día (si hay problemas)
- **Logs de rendimiento:** ~3-8 MB/día
- **Total diario:** ~5-13 MB
- **Total 4 semanas:** ~140-360 MB
- **Comprimido en archive:** ~30-80 MB

## Monitoreo de Logs

Se recomienda monitorear diariamente:

1. **Errores críticos:** Ver `.logs/errors/` cada día
2. **Tendencias de rendimiento:** Analizar `.logs/performance/performance.log`
3. **Resultados consolidados:** Usar `analyze_logs.py` para reportes semanales

## Script de Análisis

```bash
# Generar reporte de últimos 7 días
python analyze_logs.py --days 7

# Limpiar logs antiguos (comprimidos)
python cleanup_logs.py --archive-after 7

# Exportar logs a formato CSV para análisis
python export_logs.py --format csv --output reports/
```

---

**Última actualización:** 2025-11-14
**Versión:** 1.0
"""
        
        if not readme_path.exists():
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
    
    # ========================================================================
    # MÉTODOS DE LOGGING PRINCIPALES
    # ========================================================================
    
    def log_info(self, msg: str, category: str = "general") -> None:
        """Registrar información general"""
        if category == "general":
            self.benchmark_logger.info(msg)
        elif category in self.loggers:
            self.loggers[category].info(msg)
        else:
            self.benchmark_logger.info(f"[{category}] {msg}")
    
    def log_warning(self, msg: str, category: str = "general") -> None:
        """Registrar advertencia"""
        if category == "general":
            self.error_logger.warning(msg)
        elif category in self.loggers:
            self.loggers[category].warning(msg)
        else:
            self.error_logger.warning(f"[{category}] {msg}")
    
    def log_error(self, msg: str, exc_info: bool = True) -> None:
        """Registrar error con información de excepción opcional"""
        if exc_info:
            self.error_logger.exception(msg)
        else:
            self.error_logger.error(msg)
    
    def log_connectivity_test(self, environment: str, url: str, success: bool, response_time_ms: float = 0) -> None:
        """Registrar resultado de prueba de conectividad"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        
        if success:
            msg = f"{status} | {environment} | {url} | {response_time_ms:.2f}ms"
            self.connectivity_logger.info(msg)
        else:
            msg = f"{status} | {environment} | {url} | TIMEOUT/ERROR"
            self.connectivity_logger.warning(msg)
            self.error_logger.warning(f"Connectivity failed: {environment} -> {url}")
    
    def log_endpoint_result(self, data_dict: Dict[str, Any]) -> None:
        """Registrar resultado completo de endpoint"""
        # Log de request/respuesta
        endpoint = data_dict.get('endpoint_name', 'Unknown')
        environment = data_dict.get('environment', 'Unknown')
        rps = data_dict.get('requests_per_second', 0)
        latency = data_dict.get('avg_latency_ms', 0)
        errors = data_dict.get('error_rate', 0)
        
        self.request_logger.info(
            f"ENDPOINT | {endpoint} | {environment} | "
            f"RPS: {rps:.2f} | Latency: {latency:.2f}ms | Errors: {errors:.2f}%"
        )
        
        # Log de métricas del sistema si están disponibles
        if any(key in data_dict for key in ['cpu_usage_percent', 'memory_usage_mb']):
            cpu = data_dict.get('cpu_usage_percent', 0)
            memory = data_dict.get('memory_usage_mb', 0)
            self.system_logger.debug(
                f"METRICS | {endpoint} | CPU: {cpu:.1f}% | Memory: {memory:.1f}MB"
            )
        
        # Log de errores si los hay
        if errors > 0:
            failed = data_dict.get('failed_requests', 0)
            total = data_dict.get('total_requests', 0)
            self.error_logger.warning(
                f"ENDPOINT_ERRORS | {endpoint} | {failed}/{total} requests failed"
            )
    
    def log_benchmark_start(self, config_dict: Dict[str, Any]) -> None:
        """Registrar inicio de benchmark con configuración"""
        self.benchmark_logger.info("=" * 80)
        self.benchmark_logger.info("🚀 BENCHMARK STARTED")
        self.benchmark_logger.info("=" * 80)
        
        # Log de configuración
        for key, value in config_dict.items():
            if key == 'environments' and isinstance(value, list):
                self.benchmark_logger.info(f"Config | {key}: {len(value)} environments")
                for env in value:
                    if isinstance(env, dict):
                        name = env.get('name', 'Unknown')
                        label = env.get('label', 'Unknown')
                        self.benchmark_logger.info(f"  - {name}: {label}")
            else:
                self.benchmark_logger.info(f"Config | {key}: {value}")
    
    def log_benchmark_end(self, total_seconds: float, total_results: int) -> None:
        """Registrar fin de benchmark con estadísticas"""
        self.benchmark_logger.info("=" * 80)
        self.benchmark_logger.info("✅ BENCHMARK COMPLETED")
        self.benchmark_logger.info("=" * 80)
        self.benchmark_logger.info(f"Total time: {total_seconds:.2f} seconds ({total_seconds/60:.2f} minutes)")
        self.benchmark_logger.info(f"Total results: {total_results}")
        self.benchmark_logger.info("=" * 80)
    
    def get_log_files_summary(self) -> Dict[str, List[str]]:
        """Obtener lista de archivos de log por categoría"""
        summary = {}
        
        for category, dir_path in [
            ('errors', self.errors_dir),
            ('requests', self.requests_dir), 
            ('system', self.system_dir),
            ('benchmark', self.benchmark_dir),
            ('connectivity', self.connectivity_dir)
        ]:
            if dir_path.exists():
                summary[category] = sorted([f.name for f in dir_path.glob('*.log')])
            else:
                summary[category] = []
        
        return summary
    
    def export_daily_summary_json(self) -> Dict:
        """Exportar resumen diario en formato JSON para análisis"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        summary = {
            'date': today,
            'timestamp': datetime.now().isoformat(),
            'log_files': self.get_log_files_summary(),
            'log_directory': str(self.log_root),
            'directory_structure': {
                'errors': str(self.errors_dir),
                'requests': str(self.requests_dir),
                'system': str(self.system_dir), 
                'benchmark': str(self.benchmark_dir),
                'connectivity': str(self.connectivity_dir)
            }
        }
        
        return summary


# ============================================================================
# UTILITIES
# ============================================================================

def ensure_log_directories(log_root: Optional[str] = None) -> Path:
    """Asegurar que los directorios de log existan INMEDIATAMENTE"""
    if log_root is None:
        log_root = Path(__file__).parent.parent.resolve() / "logs"
    else:
        log_root = Path(log_root).resolve()
    
    # Crear estructura de directorios requerida
    directories = [
        log_root / "errors",
        log_root / "requests", 
        log_root / "system",
        log_root / "benchmark",
        log_root / "connectivity"
    ]
    
    created_count = 0
    for dir_path in directories:
        try:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                created_count += 1
                print(f"📁 Directorio creado: {dir_path}")
            # No imprimir si ya existe para evitar spam
        except PermissionError:
            print(f"⚠️ Sin permisos para crear: {dir_path}")
        except Exception as e:
            print(f"⚠️ Error creando {dir_path}: {e}")
    
    # Crear README solo si no existe
    readme_path = log_root / "README.md"
    if not readme_path.exists():
        _create_readme_immediate(log_root)
        print(f"📝 README creado: {readme_path}")
    
    if created_count > 0:
        print(f"✅ {created_count} directorios nuevos creados en: {log_root}")
    else:
        print(f"✅ Estructura de logging verificada en: {log_root}")
    
    return log_root

def get_log_manager(log_root: Optional[str] = None) -> BenchmarkLogManager:
    """Factory function para obtener instancia singleton de LogManager"""
    # Asegurar directorios ANTES de crear el LogManager
    ensure_log_directories(log_root)
    return BenchmarkLogManager(log_root)


def _create_readme_immediate(log_root: Path) -> None:
    """Crear archivo README inmediatamente en el directorio de logs"""
    readme_path = log_root / "README.md"
    
    readme_content = """# Sistema de Logging - FastAPI Performance Benchmark

## Estructura de Directorios

```
logs/
├── errors/          # Logs de errores y advertencias
├── requests/        # Logs de requests HTTP y respuestas  
├── system/          # Logs de monitoreo sistema (CPU, RAM, etc.)
├── benchmark/       # Logs de eventos principales del benchmark
├── connectivity/    # Logs de pruebas de conectividad
└── README.md        # Este archivo
```

## Patrones de Archivos

### Logs de Errores
- **Patrón:** `error_YYYY-MM-DD.log`
- **Contenido:** Errores y advertencias del sistema
- **Ejemplo:** `error_2025-11-15.log`

### Logs de Requests
- **Patrón:** `requests_YYYY-MM-DD.log` 
- **Contenido:** Requests HTTP, respuestas, métricas de endpoints
- **Ejemplo:** `requests_2025-11-15.log`

### Logs de Sistema
- **Patrón:** `system_YYYY-MM-DD.log`
- **Contenido:** CPU, RAM, red, disco - monitoreo del sistema
- **Ejemplo:** `system_2025-11-15.log`

### Logs de Benchmark
- **Patrón:** `benchmark_YYYY-MM-DD.log`
- **Contenido:** Inicio/fin de tests, configuración, resúmenes
- **Ejemplo:** `benchmark_2025-11-15.log`

### Logs de Conectividad
- **Patrón:** `connectivity_YYYY-MM-DD.log`
- **Contenido:** Pruebas de conectividad, timeouts, latencia
- **Ejemplo:** `connectivity_2025-11-15.log`

## Ver logs en tiempo real

```bash
# Logs de benchmark hoy
tail -f logs/benchmark/benchmark_$(date +%Y-%m-%d).log

# Errores de hoy  
tail -f logs/errors/error_$(date +%Y-%m-%d).log

# Requests de hoy
tail -f logs/requests/requests_$(date +%Y-%m-%d).log

# Sistema de hoy
tail -f logs/system/system_$(date +%Y-%m-%d).log

# Conectividad de hoy
tail -f logs/connectivity/connectivity_$(date +%Y-%m-%d).log
```

## Buscar eventos específicos

```bash
# Buscar errores
grep -i error logs/errors/error_$(date +%Y-%m-%d).log

# Buscar resultados de endpoint específico
grep "Heavy Computation" logs/requests/requests_$(date +%Y-%m-%d).log

# Buscar picos de CPU
grep "CPU:" logs/system/system_$(date +%Y-%m-%d).log | grep -E "9[0-9]|100"
```

---
**Creado automáticamente:** """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

def cleanup_old_logs(days_to_keep: int = 7, compress_after: int = 3) -> None:
    """Limpiar y comprimir logs antiguos"""
    log_root = Path(__file__).parent.parent.resolve() / "logs"
    
    if not log_root.exists():
        return
    
    now = datetime.now()
    
    # Directorios a limpiar
    log_directories = [
        log_root / "errors",
        log_root / "requests", 
        log_root / "system",
        log_root / "benchmark",
        log_root / "connectivity"
    ]
    
    for log_dir in log_directories:
        if not log_dir.exists():
            continue
        
        for log_file in log_dir.glob("*.log"):
            try:
                file_age = now - datetime.fromtimestamp(log_file.stat().st_mtime)
                
                # Eliminar si es más viejo que days_to_keep
                if file_age.days >= days_to_keep:
                    log_file.unlink()
                    print(f"🗑️ Eliminado: {log_file.name}")
                    
            except Exception as e:
                print(f"⚠️ Error procesando {log_file}: {e}")


# ============================================================================
# INICIALIZACIÓN AUTOMÁTICA
# ============================================================================

# Variable global para evitar inicialización múltiple
_initialized = False

def initialize_logging_system():
    """Inicializar sistema de logging una sola vez"""
    global _initialized
    if not _initialized:
        print("🚀 Inicializando sistema de logging...")
        _default_log_root = ensure_log_directories()
        print("✅ Sistema de logging listo para usar")
        print()
        _initialized = True
    return _initialized

# Inicializar automáticamente solo al importar por primera vez
initialize_logging_system()

if __name__ == "__main__":
    # Test del sistema de logging
    print("🧪 Probando LogManager...")
    
    # Obtener instancia (directorios ya creados)
    log_manager = get_log_manager()
    
    # Probar diferentes tipos de logs
    log_manager.log_info("✅ Test de log general")
    log_manager.log_warning("⚠️ Test de advertencia")
    log_manager.log_error("❌ Test de error", exc_info=False)
    
    config = {
        'num_tests': 10,
        'default_requests': 500,
        'default_connections': 100,
        'results_dir': 'benchmark_escalado',
        'environments': [
            {'name': 'local_docker', 'label': 'Docker Local'},
        ]
    }
    
    log_manager.log_benchmark_start(config)
    
    # Simular prueba de conectividad
    log_manager.log_connectivity_test('local_docker', 'http://localhost:8000', True, 45.3)
    
    # Simular resultado de endpoint
    result = {
        'endpoint_name': 'Root Endpoint',
        'environment': 'local_docker',
        'requests_per_second': 682.79,
        'avg_latency_ms': 534.14,
        'p95_latency_ms': 612.95,
        'p99_latency_ms': 631.43,
        'error_rate': 0.0,
        'cpu_usage_percent': 48.66,
        'memory_usage_mb': 489.01,
        'failed_requests': 0,
        'total_requests': 500
    }
    
    log_manager.log_endpoint_result(result)
    log_manager.log_benchmark_end(125.45, 50)
    
    # Mostrar resumen de archivos creados
    summary = log_manager.get_log_files_summary()
    print("\n📁 Archivos de log creados:")
    for category, files in summary.items():
        if files:
            print(f"  {category}: {len(files)} archivo(s)")
            for file in files:
                print(f"    - {file}")
    
    print("\n✅ Prueba completada - Revisar directorio logs/ para ver los resultados")
