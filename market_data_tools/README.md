# Market Data Tools

Este directorio contiene scripts para obtener y procesar datos de mercado para el proyecto TradeStrategy.

## Symbol Fetcher

El script `symbol_fetcher.py` descarga automáticamente los símbolos (tickers) de acciones de los principales mercados mundiales utilizando fuentes gratuitas y los almacena en un archivo de texto.

### Características:

- Obtiene símbolos de múltiples fuentes (Yahoo Finance, NASDAQ, Financial Modeling Prep)
- Valida y corrige los símbolos automáticamente
- Almacena el resultado en un archivo de texto, sobrescribiendo los datos anteriores
- Genera un informe JSON detallado con información por mercado

### Requisitos:

Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

### Uso:

```bash
python3 symbol_fetcher.py
```

### Archivos generados:

- `market_data/market_symbols.txt`: Lista completa de símbolos válidos (un símbolo por línea)
- `market_data/market_symbols_by_exchange.json`: Informe detallado con símbolos por mercado

## Estructura de directorios:

```
market_data_tools/
├── symbol_fetcher.py  # Script para obtener símbolos de mercado
├── requirements.txt   # Dependencias necesarias
├── README.md          # Este archivo
└── market_data/       # Directorio creado automáticamente para almacenar datos
    ├── market_symbols.txt              # Archivo de símbolos (principal)
    └── market_symbols_by_exchange.json # Desglose por mercado
```
