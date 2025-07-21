# Strategy Analysis - Breakout Analyzer

Este módulo implementa un analizador de estrategia de ruptura de resistencia que identifica candidatos potenciales para trading basado en patrones técnicos específicos.

## Estrategia Implementada

### Criterios de Selección
1. **Mínimo 2 años de datos**: La acción debe tener al menos 2 años de datos históricos
2. **Máximo histórico**: Debe existir al menos un máximo histórico identificable
3. **Mínimo posterior**: Después del máximo histórico, debe haber un mínimo (no necesariamente el mínimo histórico)
4. **Proximidad a resistencia**: El precio actual debe estar próximo a romper la resistencia del máximo histórico anterior (dentro del 5% por defecto)

### Funcionalidades
- ✅ Análisis automático de todos los símbolos en la base de datos
- ✅ Identificación de patrones de ruptura de resistencia
- ✅ Almacenamiento de candidatos válidos en base de datos
- ✅ Control de revisiones (evita re-analizar símbolos revisados recientemente)
- ✅ Logging detallado y estadísticas de análisis
- ✅ Configuración flexible de parámetros

## Estructura de Archivos

```
strategy_analysis/
├── breakout_analyzer.py    # Script principal de análisis
├── test_analyzer.py        # Script de verificación y pruebas
├── requirements.txt        # Dependencias Python
├── README.md              # Esta documentación
├── venv/                   # Entorno virtual Python
├── breakout_analyzer.log   # Log detallado del análisis
└── breakout_analysis_stats_*.json  # Estadísticas del análisis
```

## Base de Datos

### Nueva Tabla: `strategy_candidates`
```sql
CREATE TABLE strategy_candidates (
    symbol VARCHAR PRIMARY KEY,
    is_valid BOOLEAN DEFAULT FALSE,
    last_review_date TIMESTAMP,
    historical_high FLOAT,
    historical_high_date TIMESTAMP,
    subsequent_low FLOAT,
    subsequent_low_date TIMESTAMP,
    current_price FLOAT,
    resistance_distance_percent FLOAT,
    years_of_data FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Configuración

### Parámetros Principales
- `MIN_YEARS_DATA = 2`: Mínimo de años de datos históricos requeridos
- `RESISTANCE_PROXIMITY_PERCENT = 5.0`: Porcentaje máximo de distancia al máximo histórico
- `REVIEW_INTERVAL_DAYS = 7`: Días antes de volver a revisar un símbolo

### Base de Datos
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'stockdata',
    'user': 'postgres',
    'password': 'postgres'
}
```

## Instalación y Uso

### 1. Instalar Dependencias
```bash
cd strategy_analysis
pip install -r requirements.txt
```

### 2. Ejecutar Análisis
```bash
python breakout_analyzer.py
```

### 3. Revisar Resultados
El script genera:
- Logs detallados en `breakout_analyzer.log`
- Estadísticas en formato JSON `breakout_analysis_stats_YYYYMMDD_HHMMSS.json`
- Candidatos válidos almacenados en la tabla `strategy_candidates`

## Resultados del Último Análisis (21 Julio 2025)

### Estadísticas Reales
```
==================================================
RESUMEN DEL ANÁLISIS DE RUPTURA
==================================================
Total de símbolos: 2039
Símbolos analizados: 1251
Candidatos válidos: 104
Omitidos (revisión reciente): 0
Datos insuficientes: 788
Sin patrón encontrado: 0
Errores: 0
==================================================
```

### Top 10 Candidatos Más Próximos a Ruptura
```
CANDIDATOS VÁLIDOS ACTUALES (104 total):
--------------------------------------------------------------------------------
AGZ      | Máximo: $   111.60 | Actual: $   109.12 | Distancia:   2.23%
ARDC     | Máximo: $    15.01 | Actual: $    14.57 | Distancia:   2.93%
BKIV     | Máximo: $    38.55 | Actual: $    37.41 | Distancia:   2.97%
CBON     | Máximo: $    23.02 | Actual: $    22.33 | Distancia:   2.98%
CLSE     | Máximo: $    24.23 | Actual: $    23.50 | Distancia:   3.01%
AGNG     | Máximo: $    33.33 | Actual: $    32.30 | Distancia:   3.09%
BSX      | Máximo: $   107.53 | Actual: $   104.09 | Distancia:   3.20%
BR       | Máximo: $   246.11 | Actual: $   238.02 | Distancia:   3.29%
CHSCM    | Máximo: $    24.82 | Actual: $    24.00 | Distancia:   3.31%
ARGD     | Máximo: $    21.79 | Actual: $    21.06 | Distancia:   3.34%
```

## Optimización de Rendimiento

- **Control de revisiones**: Evita re-analizar símbolos revisados en los últimos 7 días
- **Logging eficiente**: Diferentes niveles de logging para desarrollo y producción
- **Manejo de errores**: Continúa el análisis aunque fallen símbolos individuales
- **Estadísticas detalladas**: Tracking completo del proceso de análisis

## Integración con el Sistema

Este módulo se integra perfectamente con:
- **TimescaleDB**: Utiliza la misma base de datos que el resto del sistema
- **Market Data API**: Puede consumir datos a través de la API existente
- **Frontend**: Los candidatos pueden ser mostrados en la interfaz web

## Próximas Mejoras

- [ ] Análisis de múltiples timeframes (semanal, diario)
- [ ] Integración con indicadores técnicos adicionales
- [ ] Alertas automáticas cuando nuevos candidatos son identificados
- [ ] Dashboard web para visualizar candidatos
- [ ] Backtesting de la estrategia
