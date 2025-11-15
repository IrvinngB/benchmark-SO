#!/usr/bin/env python3
"""
Logging Manager para FastAPI Performance Benchmark
===================================================
Sistema avanzado de logging con:
- Rotación automática diaria
- Múltiples niveles de severidad
- Separación de logs por categoría
- Compresión de logs antiguos
- Análisis y reportes automáticos

Estructura de Carpetas:
.logs/
├── daily/              # Logs generales diarios (YYYY-MM-DD.log)
├── errors/             # Logs de errores filtrados (YYYY-MM-DD_errors.log)
├── performance/        # Métricas de rendimiento (YYYY-MM-DD_performance.log)
├── archive/            # Logs comprimidos de más de 7 días
└── README.md           # Documentación del sistema de logging
"""

import logging
import logging.handlers
import os
import sys
import gzip
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import threading
import traceback


class DailyRotatingFileHandler(logging.FileHandler):
    """Handler personalizado con rotación diaria automática"""
    
    def __init__(self, log_dir: Path, prefix: str = ""):
        self.log_dir = Path(log_dir)
        self.prefix = prefix
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear nombre de archivo con fecha actual
        self.current_date = datetime.now().date()
        filename = self._get_filename()
        
        super().__init__(str(filename))
        
    def _get_filename(self) -> Path:
        """Genera nombre de archivo basado en fecha actual"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        if self.prefix:
            filename = f"{date_str}_{self.prefix}.log"
        else:
            filename = f"{date_str}.log"
        
        return self.log_dir / filename
    
    def emit(self, record: logging.LogRecord) -> None:
        """Override para verificar rotación diaria"""
        # Verificar si cambió la fecha
        current_date = datetime.now().date()
        if current_date != self.current_date:
            # Rotar archivo
            self._rotate_file()
            self.current_date = current_date
            
            # Crear nuevo archivo
            new_filename = self._get_filename()
            self.close()
            self.stream = self._open()
            self.baseFilename = str(new_filename)
        
        super().emit(record)
    
    def _rotate_file(self) -> None:
        """Comprime el archivo anterior"""
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            if self.prefix:
                old_filename = self.log_dir / f"{yesterday}_{self.prefix}.log"
            else:
                old_filename = self.log_dir / f"{yesterday}.log"
            
            if old_filename.exists() and (datetime.now().time().hour >= 1):  # Rotar después de medianoche
                # Comprimir archivo antiguo si es más de 7 días
                file_age = datetime.now() - datetime.fromtimestamp(old_filename.stat().st_mtime)
                if file_age.days > 7:
                    self._compress_and_archive(old_filename)
        
        except Exception as e:
            # No fallar si hay error en rotación
            print(f"Error durante rotación de logs: {e}", file=sys.stderr)
    
    def _compress_and_archive(self, filepath: Path) -> None:
        """Comprime y mueve archivo antiguo al directorio de archivo"""
        try:
            archive_dir = self.log_dir.parent / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            # Crear archivo comprimido
            gzip_path = archive_dir / f"{filepath.name}.gz"
            
            with open(filepath, 'rb') as f_in:
                with gzip.open(gzip_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Eliminar original
            filepath.unlink()
            
        except Exception as e:
            print(f"Error comprimiendo archivo: {e}", file=sys.stderr)


class BenchmarkLogManager:
    """Gestor centralizado de logging para benchmarking"""
    
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
        """Inicializar LogManager con estructura de directorios"""
        if self._initialized:
            return
        
        # Usar directorio proporcionado o usar default
        if log_root is None:
            log_root = Path(__file__).parent / ".logs"
        else:
            log_root = Path(log_root)
        
        self.log_root = log_root
        self.daily_dir = log_root / "daily"
        self.error_dir = log_root / "errors"
        self.performance_dir = log_root / "performance"
        self.archive_dir = log_root / "archive"
        
        # Crear directorios
        for dir_path in [self.daily_dir, self.error_dir, self.performance_dir, self.archive_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar loggers
        self.loggers = {}
        self._setup_loggers()
        
        # Crear README
        self._create_readme()
        
        self._initialized = True
    
    def _setup_loggers(self) -> None:
        """Configurar múltiples loggers especializados"""
        
        # 1. Logger General (STDOUT + FILE)
        self.general_logger = self._create_logger(
            name="benchmark.general",
            handlers=[
                ('console', logging.StreamHandler(sys.stdout), logging.INFO),
                ('file', DailyRotatingFileHandler(self.daily_dir), logging.DEBUG),
            ]
        )
        
        # 2. Logger de Errores (STDERR + FILE)
        self.error_logger = self._create_logger(
            name="benchmark.errors",
            handlers=[
                ('console', logging.StreamHandler(sys.stderr), logging.ERROR),
                ('file', DailyRotatingFileHandler(self.error_dir, "errors"), logging.WARNING),
            ]
        )
        
        # 3. Logger de Rendimiento (FILE ONLY)
        self.performance_logger = self._create_logger(
            name="benchmark.performance",
            handlers=[
                ('file', DailyRotatingFileHandler(self.performance_dir, "performance"), logging.DEBUG),
            ]
        )
        
        # 4. Logger de Conectividad (FILE ONLY)
        self.connectivity_logger = self._create_logger(
            name="benchmark.connectivity",
            handlers=[
                ('file', DailyRotatingFileHandler(self.performance_dir, "connectivity"), logging.INFO),
            ]
        )
        
        # 5. Logger de Configuración (FILE ONLY)
        self.config_logger = self._create_logger(
            name="benchmark.config",
            handlers=[
                ('file', DailyRotatingFileHandler(self.daily_dir, "config"), logging.INFO),
            ]
        )
        
        self.loggers = {
            'general': self.general_logger,
            'error': self.error_logger,
            'performance': self.performance_logger,
            'connectivity': self.connectivity_logger,
            'config': self.config_logger,
        }
    
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
    # MÉTODOS DE LOGGING
    # ========================================================================
    
    def log_benchmark_start(self, config: Dict) -> None:
        """Registrar inicio de ejecución de benchmark"""
        self.general_logger.info("=" * 80)
        self.general_logger.info("🚀 INICIO DE BENCHMARK")
        self.general_logger.info("=" * 80)
        
        self.config_logger.info(f"Número de pruebas: {config.get('num_tests', 'N/A')}")
        self.config_logger.info(f"Requests por test: {config.get('default_requests', 'N/A')}")
        self.config_logger.info(f"Conexiones concurrentes: {config.get('default_connections', 'N/A')}")
        self.config_logger.info(f"Directorio de resultados: {config.get('results_dir', 'N/A')}")
        
        # Log de entornos
        if 'environments' in config:
            self.config_logger.info(f"Entornos a probar: {len(config['environments'])}")
            for env in config['environments']:
                self.config_logger.info(f"  - {env.get('name')}: {env.get('label')}")
    
    def log_benchmark_end(self, total_time_seconds: float, results_count: int) -> None:
        """Registrar fin de ejecución de benchmark"""
        self.general_logger.info("=" * 80)
        self.general_logger.info("✅ BENCHMARK COMPLETADO")
        self.general_logger.info("=" * 80)
        self.general_logger.info(f"Tiempo total: {total_time_seconds:.2f} segundos ({total_time_seconds/60:.2f} minutos)")
        self.general_logger.info(f"Resultados procesados: {results_count}")
        self.general_logger.info("")
    
    def log_environment_start(self, environment: Dict) -> None:
        """Registrar inicio de pruebas en un entorno"""
        self.general_logger.info(f"\n{'─' * 60}")
        self.general_logger.info(f"🌍 INICIANDO PRUEBAS: {environment.get('label')}")
        self.general_logger.info(f"{'─' * 60}")
        
        self.connectivity_logger.info(f"Comenzando pruebas en {environment.get('name')} ({environment.get('label')})")
    
    def log_environment_end(self, environment: str, success: bool) -> None:
        """Registrar fin de pruebas en un entorno"""
        status = "✅ EXITOSAS" if success else "❌ FALLIDAS"
        self.general_logger.info(f"Pruebas en {environment}: {status}")
    
    def log_connectivity_test(self, environment: str, url: str, success: bool, response_time_ms: float = 0) -> None:
        """Registrar resultado de prueba de conectividad"""
        status = "✅" if success else "❌"
        level = logging.INFO if success else logging.WARNING
        
        if success:
            self.connectivity_logger.log(level, f"{status} Conectividad OK: {url} ({response_time_ms:.2f}ms)")
        else:
            self.connectivity_logger.log(level, f"{status} Error de conectividad: {url}")
            self.error_logger.warning(f"Fallo de conectividad: {url}")
    
    def log_test_execution(self, test_number: int, total_tests: int) -> None:
        """Registrar ejecución de un test específico"""
        progress = (test_number / total_tests) * 100
        self.general_logger.debug(f"  [{progress:5.1f}%] Ejecutando test {test_number}/{total_tests}")
    
    def log_endpoint_result(self, result: Dict) -> None:
        """Registrar resultado de benchmark de endpoint"""
        # Log general
        self.general_logger.info(
            f"  ✅ {result.get('endpoint_name')}: "
            f"{result.get('requests_per_second', 0):.2f} RPS, "
            f"{result.get('avg_latency_ms', 0):.2f}ms, "
            f"{result.get('error_rate', 0):.2f}% errors"
        )
        
        # Log detallado de rendimiento
        self.performance_logger.debug(
            f"Endpoint: {result.get('endpoint_name')} | "
            f"Environment: {result.get('environment')} | "
            f"RPS: {result.get('requests_per_second', 0):.2f} | "
            f"Latency: {result.get('avg_latency_ms', 0):.2f}ms | "
            f"P95: {result.get('p95_latency_ms', 0):.2f}ms | "
            f"P99: {result.get('p99_latency_ms', 0):.2f}ms | "
            f"CPU: {result.get('cpu_usage_percent', 0):.1f}% | "
            f"Memory: {result.get('memory_usage_mb', 0):.1f}MB | "
            f"Errors: {result.get('failed_requests', 0)}/{result.get('total_requests', 0)}"
        )
        
        # Si hay errores, loguear en error log
        if result.get('error_rate', 0) > 0:
            self.error_logger.warning(
                f"Errores detectados en {result.get('endpoint_name')}: "
                f"{result.get('failed_requests')}/{result.get('total_requests')} requests"
            )
    
    def log_error(self, message: str, exc_info: bool = False) -> None:
        """Registrar error con traceback opcional"""
        if exc_info:
            self.error_logger.exception(message)
        else:
            self.error_logger.error(message)
    
    def log_warning(self, message: str) -> None:
        """Registrar advertencia"""
        self.error_logger.warning(message)
    
    def log_info(self, message: str, category: str = "general") -> None:
        """Registrar información"""
        logger = self.loggers.get(category, self.general_logger)
        logger.info(message)
    
    def log_debug(self, message: str, category: str = "general") -> None:
        """Registrar información de debug"""
        logger = self.loggers.get(category, self.general_logger)
        logger.debug(message)
    
    def log_system_metrics(self, metrics: Dict) -> None:
        """Registrar métricas del sistema durante ejecución"""
        self.performance_logger.debug(
            f"System Metrics - CPU: {metrics.get('cpu_percent', 0):.1f}% | "
            f"Memory: {metrics.get('memory_mb', 0):.1f}MB | "
            f"Network TX: {metrics.get('network_sent', 0)} bytes | "
            f"Network RX: {metrics.get('network_recv', 0)} bytes"
        )
    
    def log_summary(self, summary: Dict) -> None:
        """Registrar resumen de ejecución"""
        self.general_logger.info("\n" + "=" * 80)
        self.general_logger.info("📊 RESUMEN DE EJECUCIÓN")
        self.general_logger.info("=" * 80)
        
        for key, value in summary.items():
            if isinstance(value, float):
                self.general_logger.info(f"{key}: {value:.2f}")
            else:
                self.general_logger.info(f"{key}: {value}")
        
        self.general_logger.info("=" * 80 + "\n")
    
    def get_log_files_summary(self) -> Dict[str, List[str]]:
        """Obtener lista de archivos de log por categoría"""
        summary = {
            'daily': sorted([f.name for f in self.daily_dir.glob('*.log')]),
            'errors': sorted([f.name for f in self.error_dir.glob('*.log')]),
            'performance': sorted([f.name for f in self.performance_dir.glob('*.log')]),
            'archived': sorted([f.name for f in self.archive_dir.glob('*.gz')]),
        }
        return summary
    
    def export_daily_summary_json(self) -> Dict:
        """Exportar resumen diario en formato JSON para análisis"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        summary = {
            'date': today,
            'timestamp': datetime.now().isoformat(),
            'log_files': self.get_log_files_summary(),
            'log_directory': str(self.log_root),
        }
        
        return summary


# ============================================================================
# UTILITIES
# ============================================================================

def ensure_log_directories(log_root: Optional[str] = None) -> Path:
    """Asegurar que los directorios de log existan INMEDIATAMENTE"""
    if log_root is None:
        log_root = Path(__file__).parent / ".logs"
    else:
        log_root = Path(log_root)
    
    # Crear directorios inmediatamente
    directories = [
        log_root / "daily",
        log_root / "errors", 
        log_root / "performance",
        log_root / "archive"
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio creado/verificado: {dir_path}")
    
    # Crear README inmediatamente
    readme_path = log_root / "README.md"
    if not readme_path.exists():
        _create_readme_immediate(log_root)
        print(f"📝 README creado: {readme_path}")
    
    print(f"✅ Estructura de logging lista en: {log_root}")
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
.logs/
├── daily/           # Logs generales por día
├── errors/          # Logs de errores y advertencias  
├── performance/     # Logs de métricas de rendimiento
├── archive/         # Logs comprimidos (>7 días)
└── README.md        # Este archivo
```

## Uso

### Logs Diarios
- **Patrón:** `YYYY-MM-DD.log`
- **Contenido:** Logs generales, inicio/fin de tests

### Logs de Errores
- **Patrón:** `YYYY-MM-DD_errors.log` 
- **Contenido:** Errores y advertencias

### Logs de Rendimiento
- **Patrón:** `YYYY-MM-DD_performance.log`
- **Contenido:** Métricas (RPS, latencia, CPU, memoria)

### Ver logs en tiempo real
```bash
# Logs de hoy
tail -f .logs/daily/$(date +%Y-%m-%d).log

# Errores de hoy  
tail -f .logs/errors/$(date +%Y-%m-%d)_errors.log

# Rendimiento de hoy
tail -f .logs/performance/$(date +%Y-%m-%d)_performance.log
```

---
**Creado automáticamente:** """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

def cleanup_old_logs(days_to_keep: int = 7, compress_after: int = 3) -> None:
    """Limpiar y comprimir logs antiguos"""
    log_root = Path(__file__).parent / ".logs"
    
    if not log_root.exists():
        return
    
    now = datetime.now()
    
    for log_dir in [log_root / "daily", log_root / "errors", log_root / "performance"]:
        if not log_dir.exists():
            continue
        
        for log_file in log_dir.glob("*.log"):
            file_age = now - datetime.fromtimestamp(log_file.stat().st_mtime)
            
            # Comprimir si es más viejo que compress_after días
            if file_age.days >= compress_after and file_age.days < days_to_keep:
                try:
                    archive_dir = log_root / "archive"
                    archive_dir.mkdir(exist_ok=True)
                    
                    gzip_path = archive_dir / f"{log_file.name}.gz"
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(gzip_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    log_file.unlink()
                    print(f"Comprimido: {log_file.name} -> {gzip_path.name}")
                
                except Exception as e:
                    print(f"Error comprimiendo {log_file}: {e}")
            
            # Eliminar si es más viejo que days_to_keep
            elif file_age.days >= days_to_keep:
                try:
                    log_file.unlink()
                    print(f"Eliminado: {log_file.name}")
                except Exception as e:
                    print(f"Error eliminando {log_file}: {e}")


# ============================================================================
# INICIALIZACIÓN AUTOMÁTICA
# ============================================================================

# Crear directorios inmediatamente al importar este módulo
print("🚀 Inicializando sistema de logging...")
_default_log_root = ensure_log_directories()
print("✅ Sistema de logging listo para usar")
print()

if __name__ == "__main__":
    # Test del sistema de logging
    print("🧪 Probando LogManager...")
    
    # Obtener instancia (directorios ya creados)
    log_manager = get_log_manager()
    
    # Probar diferentes tipos de logs
    log_manager.general_logger.info("✅ Test de log general")
    log_manager.error_logger.warning("⚠️ Test de advertencia")
    log_manager.performance_logger.debug("📊 Test de métrica de rendimiento")
    
    config = {
        'num_tests': 10,
        'default_requests': 500,
        'default_connections': 100,
        'results_dir': 'benchmark_escalado',
        'environments': [
            {'name': 'vps_no_docker', 'label': 'VPS Sin Docker'},
            {'name': 'vps_docker', 'label': 'VPS Con Docker'}
        ]
    }
    
    log_manager.log_benchmark_start(config)
    
    # Simular prueba
    log_manager.log_environment_start({'name': 'test', 'label': 'Test Environment'})
    log_manager.log_connectivity_test('test', 'http://localhost:8000', True, 45.3)
    
    result = {
        'endpoint_name': 'Root Endpoint',
        'environment': 'vps_no_docker',
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
    
    print("\n✅ Prueba completada - Revisar .logs/daily/ para ver los resultados")
