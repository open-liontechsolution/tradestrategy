# Stock Data Loader

Este módulo descarga datos históricos mensuales de acciones a partir de los símbolos obtenidos por el `symbol_fetcher` y los almacena en una base de datos TimescaleDB optimizada para series temporales.

## Características

- Lectura de símbolos desde el archivo generado por el script `symbol_fetcher`
- Descarga en paralelo de datos OHLCV mensuales desde Yahoo Finance
- Almacenamiento eficiente en TimescaleDB (optimizada para series temporales)
- Manejo de errores y reintentos automáticos
- Procesamiento por lotes para evitar problemas de memoria
- Registro detallado del proceso y estadísticas

## Requisitos

- Python 3.6+
- Docker y docker-compose para TimescaleDB
- Dependencias Python:
  ```bash
  pip install -r requirements.txt
  ```

## Configuración de la base de datos

El proyecto incluye un archivo `docker-compose.yml` en la raíz que configura TimescaleDB:

```bash
# En la raíz del proyecto
docker-compose up -d
```

Esto iniciará un contenedor TimescaleDB con la siguiente configuración:
- Puerto: 5432
- Base de datos: stockdata
- Usuario: postgres
- Contraseña: postgres

## Uso

```bash
cd stock_data_loader
python stock_data_loader.py
```

El script:
1. Verifica la conexión a TimescaleDB
2. Carga los símbolos desde `market_data_tools/market_data/market_symbols.txt`
3. Descarga datos históricos mensuales para cada símbolo desde Yahoo Finance
4. Almacena los datos en la tabla `stock_prices_monthly` en TimescaleDB
5. Genera estadísticas de la ejecución

## Estructura de la base de datos

La tabla principal `stock_prices_monthly` es una hypertable de TimescaleDB con la siguiente estructura:

| Columna    | Tipo    | Descripción                             |
|------------|---------|----------------------------------------|
| symbol     | String  | Símbolo de la acción (clave primaria)  |
| date       | DateTime| Fecha del registro (clave primaria)    |
| open       | Float   | Precio de apertura                     |
| high       | Float   | Precio más alto del período            |
| low        | Float   | Precio más bajo del período            |
| close      | Float   | Precio de cierre                       |
| adj_close  | Float   | Precio de cierre ajustado              |
| volume     | Float   | Volumen de operaciones                 |

## Archivo de estadísticas

Después de la ejecución, el script genera un archivo JSON con estadísticas detalladas:

```json
{
  "total_symbols": 11194,
  "successful_downloads": 10345,
  "failed_downloads": 849,
  "total_records": 1234567,
  "start_time": "2025-07-18T11:57:23.123456",
  "end_time": "2025-07-18T12:45:12.345678",
  "duration_seconds": 2869.222222
}
```

## Personalización

Puedes modificar las siguientes constantes en el script para ajustar su comportamiento:

- `MAX_WORKERS`: Número de hilos para descargas en paralelo (default: 10)
- `DEFAULT_START_DATE`: Fecha de inicio para datos históricos (default: "2000-01-01")
- `BATCH_SIZE`: Tamaño de lote para inserciones en la base de datos (default: 100)
- `RETRY_ATTEMPTS`: Intentos de reintentos para llamadas a la API (default: 3)
