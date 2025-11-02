# Reporte de Comparación: Docker vs Bare Metal

## Información del Test

**Fecha del Test:** YYYY-MM-DD
**Duración:** 60 segundos por endpoint
**Conexiones Concurrentes:** 100
**Threads:** 4
**Herramienta:** wrk

## Configuración de Droplets

### Droplet Bare Metal
- **IP:** `XXX.XXX.XXX.XXX`
- **Plan:** $12/month (2GB RAM, 1 vCPU)
- **SO:** Ubuntu 22.04 LTS
- **Python:** 3.10.12
- **Workers:** 3
- **Dependencias:** requirements-linux.txt (con uvloop)

### Droplet Docker
- **IP:** `YYY.YYY.YYY.YYY`
- **Plan:** $12/month (2GB RAM, 1 vCPU)
- **SO:** Ubuntu 22.04 LTS
- **Docker:** Versión más reciente
- **Python:** 3.10 (en contenedor)
- **Workers:** 3
- **Dependencias:** requirements-linux.txt (con uvloop)

## Resultados por Endpoint

### Endpoint Ligero (`/`)

#### Bare Metal
```
Running 1m test @ http://XXX.XXX.XXX.XXX:8000/
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.34ms    1.12ms  45.67ms   88.45%
    Req/Sec     1.23k   234.56     2.34k    78.90%
  294015 requests in 1.00m, 45.67MB read
Requests/sec:   4900.25
Transfer/sec:    780.45MB
```

#### Docker
```
Running 1m test @ http://YYY.YYY.YYY.YYY:8000/
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.56ms    1.23ms  47.89ms   87.34%
    Req/Sec     1.18k   245.67     2.28k    77.45%
  283456 requests in 1.00m, 44.23MB read
Requests/sec:   4724.27
Transfer/sec:    753.72MB
```

#### Comparación
- **RPS Bare Metal:** 4900.25 req/s
- **RPS Docker:** 4724.27 req/s
- **Overhead Docker:** 3.6% más lento
- **Latencia Bare Metal:** 2.34ms (avg)
- **Latencia Docker:** 2.56ms (avg)

### Endpoint Pesado (`/heavy`)

#### Bare Metal
```
[Pegar resultados aquí]
```

#### Docker
```
[Pegar resultados aquí]
```

#### Comparación
- **RPS Bare Metal:** XXX req/s
- **RPS Docker:** XXX req/s
- **Overhead Docker:** X% más lento

### Endpoint JSON Grande (`/json-large`)

#### Bare Metal
```
[Pegar resultados aquí]
```

#### Docker
```
[Pegar resultados aquí]
```

#### Comparación
- **RPS Bare Metal:** XXX req/s
- **RPS Docker:** XXX req/s
- **Overhead Docker:** X% más lento

## Monitoreo de Recursos

### Bare Metal - Uso Promedio
- **CPU:** XX%
- **RAM:** XXX MB
- **Network I/O:** XXX Mbps

### Docker - Uso Promedio
- **CPU:** XX%
- **RAM:** XXX MB
- **Network I/O:** XXX Mbps

## Conclusiones

### Overhead de Containerización
- **Promedio:** X% más lento en Docker
- **Variación por endpoint:** Ligero (X%), Pesado (X%), JSON (X%)

### Recomendaciones
- Para **alto rendimiento crítico**: Bare Metal
- Para **microservicios/orquestación**: Docker
- Para **desarrollo/portabilidad**: Docker

### Observaciones
- [Agregar cualquier observación relevante sobre estabilidad, errores, etc.]

## Próximos Pasos
- [ ] Optimizar endpoint `/json-large` (streaming/paginación)
- [ ] Probar con diferentes tamaños de droplet
- [ ] Implementar rate limiting
- [ ] Agregar métricas de aplicación (Prometheus)