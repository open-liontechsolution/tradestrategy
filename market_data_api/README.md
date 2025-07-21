# Market Data API

API REST para servir datos de mercado desde TimescaleDB al frontend de TradeStrategy.

## Características

- **Endpoints RESTful** para acceso a datos de mercado
- **Conexión directa a TimescaleDB** para consultas eficientes
- **CORS habilitado** para integración con frontend
- **Búsqueda de símbolos** con filtros y paginación
- **Datos históricos** con filtros de fecha y límites
- **Health check** para monitoreo del sistema

## Endpoints Disponibles

### GET /api/health
Verifica el estado de la API y la conexión a la base de datos.

**Respuesta:**
```json
{
  "status": "ok",
  "message": "API funcionando correctamente",
  "database": "connected",
  "total_records": 1234567,
  "timestamp": "2025-07-21T11:43:52.123456"
}
```

### GET /api/symbols
Obtiene la lista de todos los símbolos disponibles con estadísticas.

**Respuesta:**
```json
{
  "symbols": [
    {
      "symbol": "AAPL",
      "data_points": 240,
      "first_date": "2000-01-01T00:00:00",
      "last_date": "2025-07-21T00:00:00"
    }
  ],
  "total": 11194
}
```

### GET /api/data/{symbol}
Obtiene datos OHLCV para un símbolo específico.

**Parámetros de consulta:**
- `start_date` (opcional): Fecha de inicio (YYYY-MM-DD)
- `end_date` (opcional): Fecha de fin (YYYY-MM-DD)
- `limit` (opcional): Número máximo de registros

**Respuesta:**
```json
{
  "symbol": "AAPL",
  "data": [
    {
      "date": "2025-01-01T00:00:00",
      "open": 150.00,
      "high": 155.00,
      "low": 149.00,
      "close": 154.00,
      "adj_close": 154.00,
      "volume": 50000000
    }
  ],
  "count": 240
}
```

### GET /api/data/{symbol}/latest
Obtiene el último precio disponible para un símbolo.

### GET /api/search/{query}
Busca símbolos que coincidan con la consulta.

## Instalación y Uso

### Prerrequisitos

1. **TimescaleDB ejecutándose** (usar docker-compose desde la raíz del proyecto)
2. **Python 3.8+**
3. **Datos cargados** en la tabla `stock_prices_monthly`

### Instalación

```bash
cd market_data_api

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración

La API se conecta por defecto a:
- **Host:** localhost
- **Puerto:** 5432
- **Base de datos:** stockdata
- **Usuario:** postgres
- **Contraseña:** postgres

Para cambiar la configuración, modifica el diccionario `DB_CONFIG` en `app.py`.

### Ejecución

```bash
python app.py
```

La API estará disponible en `http://localhost:5000`

### Verificación

Verifica que la API funciona correctamente:

```bash
curl http://localhost:5000/api/health
```

## Estructura del Proyecto

```
market_data_api/
├── app.py              # Aplicación principal Flask
├── requirements.txt    # Dependencias Python
└── README.md          # Esta documentación
```

## Dependencias

- **Flask**: Framework web
- **Flask-CORS**: Manejo de CORS
- **SQLAlchemy**: ORM para base de datos
- **psycopg2-binary**: Driver PostgreSQL
- **pandas**: Manipulación de datos
- **python-dateutil**: Utilidades de fecha

## Desarrollo

### Agregar nuevos endpoints

1. Define la función del endpoint en `app.py`
2. Agrega el decorador `@app.route()` apropiado
3. Implementa la lógica de consulta a la base de datos
4. Retorna JSON usando `jsonify()`

### Manejo de errores

La API incluye manejo de errores automático:
- **404**: Endpoint no encontrado
- **500**: Error interno del servidor
- **Errores de base de datos**: Capturados y devueltos como JSON

### Logging

Los logs se escriben a la consola con información sobre:
- Conexiones a la base de datos
- Errores de consulta
- Requests HTTP

## Integración con Frontend

El frontend React está configurado para usar esta API:
- **Proxy configurado** en `package.json` del frontend
- **CORS habilitado** para desarrollo
- **Formato de datos compatible** con componentes React

## Producción

Para producción, considera:
- Usar **Gunicorn** como servidor WSGI
- Configurar **variables de entorno** para credenciales
- Implementar **rate limiting**
- Agregar **autenticación** si es necesario
- Usar **HTTPS**
