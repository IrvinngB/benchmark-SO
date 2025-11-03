# FastAPI Performance Benchmark Report
**Fecha de ejecución:** 20251103_015035

## Resumen Ejecutivo

### VPS_NO_DOCKER
- **RPS Promedio:** 277.98
- **Latencia Promedio:** 1434.37 ms
- **CPU Promedio:** 38.03%

### VPS_DOCKER
- **RPS Promedio:** 227.38
- **Latencia Promedio:** 2323.16 ms
- **CPU Promedio:** 33.02%

## Análisis por Endpoint

### Root Endpoint (Baseline)
| environment   |   ('requests_per_second', 'mean') |   ('requests_per_second', 'std') |   ('avg_latency_ms', 'mean') |   ('avg_latency_ms', 'std') |   ('error_rate', 'mean') |
|:--------------|----------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|-------------------------:|
| vps_docker    |                            389.79 |                            85.57 |                       221.64 |                       43.38 |                        0 |
| vps_no_docker |                            399.52 |                            88.57 |                       219.52 |                       47.02 |                        0 |

### Health Check
| environment   |   ('requests_per_second', 'mean') |   ('requests_per_second', 'std') |   ('avg_latency_ms', 'mean') |   ('avg_latency_ms', 'std') |   ('error_rate', 'mean') |
|:--------------|----------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|-------------------------:|
| vps_docker    |                            317.17 |                            48.23 |                       250.14 |                       31.77 |                        0 |
| vps_no_docker |                            348.09 |                            60.84 |                       234.87 |                       38.24 |                        0 |

### Async Light
| environment   |   ('requests_per_second', 'mean') |   ('requests_per_second', 'std') |   ('avg_latency_ms', 'mean') |   ('avg_latency_ms', 'std') |   ('error_rate', 'mean') |
|:--------------|----------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|-------------------------:|
| vps_docker    |                            158.11 |                            24.26 |                       433.66 |                       25.49 |                        0 |
| vps_no_docker |                            188.3  |                            19.64 |                       393.79 |                       32.82 |                        0 |

### Heavy Computation
| environment   |   ('requests_per_second', 'mean') |   ('requests_per_second', 'std') |   ('avg_latency_ms', 'mean') |   ('avg_latency_ms', 'std') |   ('error_rate', 'mean') |
|:--------------|----------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|-------------------------:|
| vps_docker    |                            157.98 |                             7.11 |                      3340.11 |                      103.19 |                        0 |
| vps_no_docker |                            259.88 |                             9.57 |                      2050.76 |                       56.19 |                        0 |

### Large JSON Response
| environment   |   ('requests_per_second', 'mean') |   ('requests_per_second', 'std') |   ('avg_latency_ms', 'mean') |   ('avg_latency_ms', 'std') |   ('error_rate', 'mean') |
|:--------------|----------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|-------------------------:|
| vps_docker    |                            113.85 |                             6.05 |                      7370.26 |                      363.43 |                        0 |
| vps_no_docker |                            194.1  |                             5.91 |                      4272.88 |                      154.6  |                        0 |

## Análisis de Estabilidad

### VPS_NO_DOCKER
- **Coeficiente de Variación RPS:** 34.77%
- **Coeficiente de Variación Latencia:** 111.94%

### VPS_DOCKER
- **Coeficiente de Variación RPS:** 51.22%
- **Coeficiente de Variación Latencia:** 122.14%
