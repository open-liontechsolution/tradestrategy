# TradeStrategy - Sistema Avanzado de Análisis de Trading

## 🚀 Sistema Completo con 644 Acciones y Filtrado Inteligente

Sistema avanzado de análisis de estrategias de trading con datos históricos completos, filtrado por años mínimos y análisis multi-mercado.

### 📊 **Mercados y Acciones Disponibles**

### 🌍 **644 Acciones de 6 Mercados Globales:**
- **🇺🇸 S&P 500**: 503 acciones (Apple, Microsoft, Google, etc.)
- **🇺🇸 NASDAQ 100**: 100 acciones tech (NVIDIA, Tesla, Amazon, etc.)
- **🇪🇸 IBEX 35**: 11 acciones españolas (Telefónica, Santander, etc.)
- **🇩🇪 DAX 40**: 10 acciones alemanas (SAP, Mercedes-Benz, etc.)
- **🇫🇷 CAC 40**: 10 acciones francesas (LVMH, L'Oréal, etc.)
- **🇬🇧 FTSE 100**: 10 acciones británicas (Shell, BP, etc.)

### 📈 **Datos Históricos Disponibles:**
- **Período**: Hasta 40+ años de historia (según la acción)
- **Intervalos**: Diario, semanal, mensual
- **Filtrado**: Por años mínimos de historia (configurable)
- **Formato**: CSV individual y dataset combinado

### 🎆 **NUEVAS FUNCIONALIDADES V2.0:**
- ✅ **644 acciones** de 6 mercados globales  
- ✅ **Filtrado por años mínimos** configurable
- ✅ **Histórico completo** disponible (hasta décadas atrás)
- ✅ **Descarga paralela** optimizada
- ✅ **Sistema integrado** con menú interactivo

## Características

- Obtención de listado de acciones populares para trading
- Consulta de precios históricos (mensuales/semanales)
- Visualización de gráficos de precios
- Análisis de datos para estrategias de trading

## Instalación

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 🚀 Uso Rápido

### 1. **Sistema Principal (Recomendado)**
```bash
# Activar entorno virtual
source venv/bin/activate

# Configurar filtrado (opcional)
export MIN_STOCK_YEARS=5  # 5 años mínimos por defecto

# Ejecutar sistema integrado
python integrated_main.py
```

### 2. **Configuración de Filtrado**
```bash
# Menos restrictivo (1-3 años)
export MIN_STOCK_YEARS=3

# Equilibrado (5 años - por defecto)
export MIN_STOCK_YEARS=5

# Conservador (10+ años)
export MIN_STOCK_YEARS=10
```

### 3. **Ejemplos y Demostraciones**
```bash
# Ver ejemplos de configuración
python example_with_env.py

# Demostración completa de filtrado
python demo_filtering.py

# Análisis individual
python main.py
```

## Uso

```python
from stock_analyzer import StockAnalyzer

# Crear instancia del analizador
analyzer = StockAnalyzer()

# Obtener lista de acciones populares
stocks = analyzer.get_popular_stocks()

# Obtener datos históricos
data = analyzer.get_stock_data("AAPL", period="1y")

# Graficar datos
analyzer.plot_stock_data("AAPL", data)
```

## APIs Utilizadas

- Yahoo Finance (yfinance) - Gratuita para datos históricos
- Sin límites de API key para uso básico
