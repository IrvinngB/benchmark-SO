# FastAPI Performance Benchmark Report
**Fecha de ejecución:** 20251103_020918

## Resumen Ejecutivo

### VPS_NO_DOCKER
- **RPS Promedio:** 399.77
- **Latencia Promedio:** 3272.87 ms
- **CPU Promedio:** 48.66%

### VPS_DOCKER
- **RPS Promedio:** 336.89
- **Latencia Promedio:** 4824.86 ms
- **CPU Promedio:** 42.70%

## Análisis por Endpoint

### Root Endpoint (Baseline)
| environment   |   ('requests_per_second', 'mean') |   ('requests_per_second', 'std') |   ('avg_latency_ms', 'mean') |   ('avg_latency_ms', 'std') |   ('error_rate', 'mean') |
|:--------------|----------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|-------------------------:|
| vps_docker    |                            618.26 |                            46.92 |                       603.48 |                       61.92 |                        0 |
| vps_no_docker |                            682.79 |                            40.71 |                       534.14 |                       24.04 |                        0 |

### Health Check
| environment   |   ('requests_per_second', 'mean') |   ('requests_per_second', 'std') |   ('avg_latency_ms', 'mean') |   ('avg_latency_ms', 'std') |   ('error_rate', 'mean') |
|:--------------|----------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|-------------------------:|
| vps_docker    |                            483.19 |                            11.52 |                       809.45 |                       41.61 |                        0 |
| vps_no_docker |                            561.49 |                            24.73 |                       658.35 |                       19.7  |                        0 |

### Async Light
| environment   |   ('requests_per_second', 'mean') |   ('requests_per_second', 'std') |   ('avg_latency_ms', 'mean') |   ('avg_latency_ms', 'std') |   ('error_rate', 'mean') |
|:--------------|----------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|-------------------------:|
| vps_docker    |                            337.58 |                            19.28 |                      1330.01 |                       49.28 |                        0 |
| vps_no_docker |                            380.8  |                            12.21 |                      1178.55 |                       27.41 |                        0 |

### Heavy Computation
| environment   |   ('requests_per_second', 'mean') |   ('requests_per_second', 'std') |   ('avg_latency_ms', 'mean') |   ('avg_latency_ms', 'std') |   ('error_rate', 'mean') |
|:--------------|----------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|-------------------------:|
| vps_docker    |                            155.33 |                             5.43 |                      7124.9  |                      288.14 |                        0 |
| vps_no_docker |                            235.72 |                             6.54 |                      4805.65 |                      114.63 |                        0 |

### Large JSON Response
| environment   |   ('requests_per_second', 'mean') |   ('requests_per_second', 'std') |   ('avg_latency_ms', 'mean') |   ('avg_latency_ms', 'std') |   ('error_rate', 'mean') |
|:--------------|----------------------------------:|---------------------------------:|-----------------------------:|----------------------------:|-------------------------:|
| vps_docker    |                             90.1  |                             4.1  |                     14256.5  |                      628.93 |                        0 |
| vps_no_docker |                            138.07 |                             3.66 |                      9187.66 |                      282.27 |                        0 |

## Análisis de Estabilidad

### VPS_NO_DOCKER
- **Coeficiente de Variación RPS:** 51.40%
- **Coeficiente de Variación Latencia:** 104.13%

### VPS_DOCKER
- **Coeficiente de Variación RPS:** 59.89%
- **Coeficiente de Variación Latencia:** 111.87%
