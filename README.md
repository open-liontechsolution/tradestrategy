# TradeStrategy - Sistema Modular de Análisis de Trading

## Proyecto estructurado en módulos independientes

Este proyecto está organizado en módulos especializados, cada uno con su propio entorno virtual y funcionalidad específica, permitiendo un desarrollo más mantenible y escalable.

## Estructura del Proyecto

### Módulos Principales

#### [market_data_symbols](./market_data_symbols)
- **Función**: Obtención de símbolos (tickers) de los principales mercados mundiales
- **Herramienta principal**: `symbol_fetcher.py`
- **Características**: 
  - Obtiene símbolos de múltiples fuentes
  - Valida y corrige símbolos automáticamente
  - Almacena resultados en formato texto y JSON

#### [stock_data_loader](./stock_data_loader)
- **Función**: Descarga y almacenamiento de datos históricos
- **Herramienta principal**: `stock_data_loader.py`
- **Características**:
  - Descarga en paralelo de datos OHLCV mensuales
  - Almacenamiento en TimescaleDB
  - Procesamiento por lotes y gestión de errores

### Directorios de Datos

- **data/**: Archivos de configuración y listados
- **historical_data/**: Datos históricos descargados

### Archivos de Soporte

- **docker-compose.yml**: Configuración para TimescaleDB
- **requirements.txt**: Dependencias globales mínimas

## Configuración de Base de Datos

El proyecto utiliza TimescaleDB para el almacenamiento eficiente de series temporales:

```bash
# Iniciar la base de datos
docker-compose up -d
```

## Uso del Sistema

Cada módulo debe utilizarse desde su propio directorio con su entorno virtual correspondiente.

### 1. Obtención de Símbolos de Mercado

```bash
cd market_data_symbols

# Crear y activar entorno virtual si no existe
python -m venv venv
source venv/bin/activate  # En Linux/Mac

# Instalar dependencias del módulo
pip install -r requirements.txt

# Ejecutar el fetcher de símbolos
python symbol_fetcher.py
```

### 2. Carga de Datos Históricos

```bash
cd stock_data_loader

# Crear y activar entorno virtual si no existe
python -m venv venv
source venv/bin/activate  # En Linux/Mac

# Instalar dependencias del módulo
pip install -r requirements.txt

# Ejecutar el cargador de datos
python stock_data_loader.py
```

## Documentación Detallada

Cada módulo contiene su propia documentación en su archivo README.md correspondiente.

## Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.
