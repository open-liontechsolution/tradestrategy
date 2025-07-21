# TradeStrategy Frontend

Frontend moderno en React para visualización de datos de mercado y análisis técnico.

## Características

- **Visualización de gráficos profesionales** usando TradingView Lightweight Charts
- **Selección de símbolos** con búsqueda y filtros
- **Indicadores técnicos** (SMA, EMA, Bollinger Bands, RSI)
- **Información de mercado** en tiempo real
- **Diseño responsive** y moderno
- **Integración completa** con API de datos

## Tecnologías Utilizadas

- **React 18** - Framework principal
- **TradingView Lightweight Charts** - Gráficos financieros profesionales
- **Styled Components** - Estilos CSS-in-JS
- **Axios** - Cliente HTTP para API
- **React Select** - Selector de símbolos avanzado
- **Date-fns** - Manipulación de fechas

## Componentes Principales

### App.js
Componente principal que orquesta toda la aplicación:
- Gestión del estado global
- Carga de símbolos y datos
- Coordinación entre componentes

### SymbolSelector
Selector de símbolos con funcionalidades avanzadas:
- Búsqueda en tiempo real
- Información de estadísticas por símbolo
- Interfaz intuitiva con React Select

### ChartContainer
Contenedor principal de gráficos:
- Gráficos de velas y líneas
- Integración con indicadores técnicos
- Controles de timeframe
- Visualización de volumen

### TechnicalIndicators
Panel de indicadores técnicos:
- SMA (Media Móvil Simple)
- EMA (Media Móvil Exponencial)
- Bandas de Bollinger
- RSI (Relative Strength Index)
- Visualización de valores en tiempo real

### MarketInfo
Panel de información de mercado:
- Precio actual y cambios
- Estadísticas del período
- Datos de volumen y volatilidad
- Información histórica

## Instalación y Uso

### Prerrequisitos

1. **Node.js 16+** y npm
2. **API backend ejecutándose** en `http://localhost:5000`
3. **TimescaleDB con datos** cargados

### Instalación

```bash
cd frontend

# Instalar dependencias
npm install
```

### Configuración

El frontend está configurado para conectarse a la API en `http://localhost:5000` por defecto.

Para cambiar la URL de la API, modifica la variable `API_BASE_URL` en `src/services/api.js` o usa la variable de entorno:

```bash
export REACT_APP_API_URL=http://tu-api-url:puerto/api
```

### Ejecución

```bash
# Modo desarrollo
npm start
```

La aplicación estará disponible en `http://localhost:3000`

### Build para producción

```bash
npm run build
```

## Estructura del Proyecto

```
frontend/
├── public/
│   └── index.html          # HTML base
├── src/
│   ├── components/         # Componentes React
│   │   ├── SymbolSelector.js
│   │   ├── ChartContainer.js
│   │   ├── TechnicalIndicators.js
│   │   └── MarketInfo.js
│   ├── services/
│   │   └── api.js          # Cliente API y utilidades
│   ├── App.js              # Componente principal
│   ├── App.css             # Estilos globales
│   ├── index.js            # Punto de entrada
│   └── index.css           # Estilos base
├── package.json            # Configuración y dependencias
└── README.md              # Esta documentación
```

## Funcionalidades

### Selección de Símbolos
- Lista completa de 11,000+ símbolos
- Búsqueda en tiempo real
- Información de estadísticas por símbolo
- Filtros por exchange y tipo

### Visualización de Gráficos
- Gráficos de velas japonesas
- Gráficos de líneas
- Visualización de volumen
- Zoom y navegación temporal
- Crosshair con información detallada

### Indicadores Técnicos
- **SMA (20)**: Media móvil simple
- **EMA (20)**: Media móvil exponencial
- **Bollinger Bands**: Bandas de volatilidad
- **RSI (14)**: Índice de fuerza relativa
- Activación/desactivación individual
- Valores calculados en tiempo real

### Información de Mercado
- Precio actual y cambios
- Estadísticas OHLC
- Volumen y volatilidad
- Máximos y mínimos del período
- Rango de fechas de datos

## Personalización

### Colores y Temas
Los colores se pueden personalizar en los styled-components de cada archivo:
- Colores principales en `App.js`
- Colores de gráfico en `ChartContainer.js`
- Colores de indicadores en `TechnicalIndicators.js`

### Indicadores Adicionales
Para agregar nuevos indicadores:

1. Implementa el cálculo en `services/api.js` en `calculateIndicators`
2. Agrega el toggle en `TechnicalIndicators.js`
3. Integra la visualización en `ChartContainer.js`

### Timeframes
Los timeframes se pueden configurar en `ChartContainer.js`:
- Modificar botones de control
- Implementar lógica de filtrado de datos
- Ajustar consultas a la API

## Desarrollo

### Agregar Componentes
1. Crea el archivo en `src/components/`
2. Usa styled-components para estilos
3. Integra con el estado global en `App.js`
4. Conecta con la API usando `services/api.js`

### Debugging
- Usa React Developer Tools
- Console.log en componentes
- Network tab para debugging de API
- Lighthouse para performance

### Testing
```bash
npm test
```

## Optimización

### Performance
- Lazy loading de componentes
- Memoización con useMemo y useCallback
- Debouncing en búsquedas
- Virtualización para listas grandes

### Bundle Size
- Tree shaking automático
- Code splitting por rutas
- Optimización de imágenes
- Minificación en build

## Integración con API

El frontend consume la API REST con los siguientes endpoints:
- `GET /api/symbols` - Lista de símbolos
- `GET /api/data/{symbol}` - Datos OHLCV
- `GET /api/search/{query}` - Búsqueda de símbolos
- `GET /api/health` - Estado de la API

## Responsive Design

La aplicación es completamente responsive:
- **Desktop**: Layout de 3 columnas
- **Tablet**: Layout apilado
- **Mobile**: Navegación optimizada

## Próximas Funcionalidades

- [ ] Alertas de precio
- [ ] Comparación de múltiples símbolos
- [ ] Exportación de gráficos
- [ ] Más indicadores técnicos (MACD, Stochastic)
- [ ] Análisis de patrones
- [ ] Portfolio tracking
