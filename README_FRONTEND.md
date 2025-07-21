# TradeStrategy - Frontend de Visualización de Datos de Mercado

## Nuevo Módulo: Frontend Web

Se ha agregado un frontend completo para visualizar y analizar los datos de mercado almacenados en TimescaleDB.

### Estructura Actualizada del Proyecto

```
TradeStrategy/
├── market_data_symbols/        # Módulo de obtención de símbolos
├── stock_data_loader/          # Módulo de carga de datos históricos
├── market_data_api/           # 🆕 API REST para servir datos
│   ├── app.py                 # Servidor Flask
│   ├── requirements.txt       # Dependencias de la API
│   └── README.md             # Documentación de la API
├── frontend/                  # 🆕 Frontend React
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   ├── services/         # Cliente API
│   │   └── App.js            # Aplicación principal
│   ├── package.json          # Configuración React
│   └── README.md            # Documentación del frontend
├── docker-compose.yml         # TimescaleDB
└── README.md                 # Documentación principal
```

## Características del Frontend

### 🎯 Funcionalidades Principales

- **Visualización profesional de gráficos** con TradingView Lightweight Charts
- **Selección inteligente de símbolos** con búsqueda y filtros
- **Análisis técnico completo** con indicadores populares
- **Información de mercado detallada** y estadísticas
- **Diseño moderno y responsive** para todos los dispositivos

### 📊 Indicadores Técnicos Incluidos

- **SMA (Simple Moving Average)** - Media móvil simple de 20 períodos
- **EMA (Exponential Moving Average)** - Media móvil exponencial de 20 períodos
- **Bollinger Bands** - Bandas de volatilidad (20, 2)
- **RSI (Relative Strength Index)** - Índice de fuerza relativa de 14 períodos
- **Volumen** - Visualización integrada en el gráfico

### 🛠 Tecnologías Utilizadas

- **Backend API**: Flask + SQLAlchemy + TimescaleDB
- **Frontend**: React 18 + TradingView Lightweight Charts
- **Estilos**: Styled Components con diseño glassmorphism
- **Datos**: 11,000+ símbolos con datos históricos mensuales

## Instalación Rápida

### 1. Iniciar TimescaleDB

```bash
# Desde la raíz del proyecto
docker-compose up -d
```

### 2. Cargar Datos (si no están cargados)

```bash
# Obtener símbolos
cd market_data_symbols
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python symbol_fetcher.py

# Cargar datos históricos
cd ../stock_data_loader
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python stock_data_loader.py
```

### 3. Iniciar API Backend

```bash
cd market_data_api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```

La API estará disponible en `http://localhost:5000`

### 4. Iniciar Frontend

```bash
cd frontend
npm install
npm start
```

El frontend estará disponible en `http://localhost:3000`

## Uso del Frontend

### Selección de Símbolos
1. Usa el buscador para encontrar símbolos específicos
2. Selecciona de la lista desplegable con información de estadísticas
3. Los datos se cargan automáticamente al seleccionar

### Análisis de Gráficos
- **Tipos de gráfico**: Cambia entre velas japonesas y líneas
- **Timeframes**: Selecciona diferentes períodos de visualización
- **Zoom y navegación**: Usa el mouse para hacer zoom y desplazarte
- **Crosshair**: Hover sobre el gráfico para ver datos detallados

### Indicadores Técnicos
- Activa/desactiva indicadores usando los toggles del panel derecho
- Los valores se calculan y muestran en tiempo real
- Los indicadores se superponen directamente en el gráfico

### Información de Mercado
- Panel izquierdo muestra estadísticas detalladas del símbolo seleccionado
- Incluye precios, volúmenes, volatilidad y rangos históricos
- Se actualiza automáticamente al cambiar de símbolo

## Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   Flask API     │    │   TimescaleDB   │
│                 │    │                 │    │                 │
│ - Symbol Select │◄──►│ - REST Endpoints│◄──►│ - OHLCV Data    │
│ - Charts        │    │ - Data Queries  │    │ - Time Series   │
│ - Indicators    │    │ - JSON Response │    │ - 11K+ Symbols  │
│ - Market Info   │    │ - CORS Enabled  │    │ - Monthly Data  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## API Endpoints

- `GET /api/health` - Estado del sistema
- `GET /api/symbols` - Lista completa de símbolos
- `GET /api/data/{symbol}` - Datos OHLCV históricos
- `GET /api/data/{symbol}/latest` - Último precio
- `GET /api/search/{query}` - Búsqueda de símbolos

## Ventajas del Nuevo Sistema

### ✅ Completamente Gratuito
- Todas las librerías son open source
- Sin costos de licencias o suscripciones
- Hosting local o en servidor propio

### ✅ Profesional y Moderno
- Gráficos de calidad institucional
- Interfaz intuitiva y responsive
- Análisis técnico completo

### ✅ Escalable y Mantenible
- Arquitectura modular
- API REST estándar
- Código bien documentado

### ✅ Integración Perfecta
- Usa los datos existentes de TimescaleDB
- Compatible con el flujo de trabajo actual
- Sin necesidad de migrar datos

## Desarrollo y Personalización

### Agregar Nuevos Indicadores
1. Implementa el cálculo en `frontend/src/services/api.js`
2. Agrega el toggle en `TechnicalIndicators.js`
3. Integra la visualización en `ChartContainer.js`

### Personalizar Estilos
- Modifica los styled-components en cada archivo
- Cambia colores, fuentes y layouts
- Totalmente personalizable

### Extender la API
- Agrega nuevos endpoints en `market_data_api/app.py`
- Implementa nuevas consultas a TimescaleDB
- Mantén la compatibilidad con el frontend

## Próximos Pasos

1. **Prueba el sistema** con diferentes símbolos
2. **Personaliza los colores** y estilos según tus preferencias
3. **Agrega más indicadores** según tus necesidades
4. **Implementa alertas** de precio si lo deseas
5. **Despliega en producción** cuando esté listo

## Soporte y Documentación

- **API**: Ver `market_data_api/README.md`
- **Frontend**: Ver `frontend/README.md`
- **Base de datos**: Ver documentación de TimescaleDB
- **Gráficos**: Ver documentación de TradingView Lightweight Charts

¡Disfruta analizando los mercados con tu nueva herramienta profesional de trading! 📈
