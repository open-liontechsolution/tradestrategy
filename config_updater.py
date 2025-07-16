#!/usr/bin/env python3
"""
Script para actualizar config.py con las acciones obtenidas dinámicamente
"""

import json
import os
from collections import defaultdict
from typing import Dict, List

def load_dynamic_stocks() -> List[Dict]:
    """Cargar las acciones obtenidas dinámicamente"""
    
    # Buscar el archivo más reciente de acciones mejoradas
    data_dir = "data"
    improved_files = [f for f in os.listdir(data_dir) if f.startswith("improved_stocks_") and f.endswith(".json")]
    
    if not improved_files:
        raise FileNotFoundError("No se encontraron archivos de acciones mejoradas")
    
    # Usar el archivo más reciente
    latest_file = sorted(improved_files)[-1]
    file_path = os.path.join(data_dir, latest_file)
    
    print(f"🔍 Cargando acciones desde: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        stocks = json.load(f)
    
    print(f"✅ Cargadas {len(stocks)} acciones")
    return stocks

def organize_stocks_by_market(stocks: List[Dict]) -> Dict[str, List[str]]:
    """Organizar acciones por mercado"""
    
    market_stocks = defaultdict(list)
    
    for stock in stocks:
        market = stock['market']
        symbol = stock['symbol']
        market_stocks[market].append(symbol)
    
    return dict(market_stocks)

def organize_stocks_by_sector(stocks: List[Dict]) -> Dict[str, List[str]]:
    """Organizar acciones por sector (usando sector cuando esté disponible)"""
    
    sector_stocks = defaultdict(list)
    
    for stock in stocks:
        sector = stock.get('sector', 'Unknown').lower()
        symbol = stock['symbol']
        
        # Mapear sectores conocidos
        if 'technology' in sector or 'information technology' in sector:
            sector_stocks['technology'].append(symbol)
        elif 'financials' in sector or 'financial' in sector:
            sector_stocks['finance'].append(symbol)
        elif 'health' in sector or 'healthcare' in sector:
            sector_stocks['healthcare'].append(symbol)
        elif 'consumer' in sector:
            sector_stocks['consumer'].append(symbol)
        elif 'energy' in sector:
            sector_stocks['energy'].append(symbol)
        elif 'industrial' in sector:
            sector_stocks['industrial'].append(symbol)
        elif 'utilities' in sector:
            sector_stocks['utilities'].append(symbol)
        elif 'materials' in sector:
            sector_stocks['materials'].append(symbol)
        elif 'real estate' in sector:
            sector_stocks['real_estate'].append(symbol)
        elif 'communication' in sector:
            sector_stocks['communication'].append(symbol)
        else:
            sector_stocks['other'].append(symbol)
    
    return dict(sector_stocks)

def escape_quotes(text: str) -> str:
    """Escapar comillas simples en texto para evitar errores de sintaxis"""
    if isinstance(text, str):
        return text.replace("'", "\\'")
    return text

def create_updated_config(stocks: List[Dict]) -> str:
    """Crear la configuración actualizada como string"""
    
    market_stocks = organize_stocks_by_market(stocks)
    sector_stocks = organize_stocks_by_sector(stocks)
    
    config_content = '''"""
Configuración actualizada para el analizador de trading
Incluye acciones obtenidas dinámicamente de múltiples mercados
"""

import json
import os

# Configuración de APIs
YFINANCE_CONFIG = {
    'default_period': '1y',
    'default_interval': '1wk',
    'timeout': 10,
    'max_workers': 10,  # Para descargas paralelas
    'retry_attempts': 3
}

# Configuración de gráficos
PLOT_CONFIG = {
    'figure_size': (15, 10),
    'dpi': 300,
    'style': 'seaborn-v0_8',
    'color_palette': ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
}

# Configuración de estrategias
STRATEGY_CONFIG = {
    'short_ma_period': 4,   # Media móvil corta (4 semanas)
    'long_ma_period': 12,   # Media móvil larga (12 semanas)
    'volatility_window': 4, # Ventana para cálculo de volatilidad
    'rsi_period': 14,       # Período para RSI
    'bollinger_period': 20, # Período para Bandas de Bollinger
    'bollinger_std': 2      # Desviaciones estándar para Bandas de Bollinger
}

# Configuración de mercados
MARKET_CONFIG = {
    'trading_hours': {
        'pre_market': '04:00',
        'market_open': '09:30',
        'market_close': '16:00',
        'after_hours': '20:00'
    },
    'timezone': 'America/New_York',
    'currency': 'USD',
    'european_timezone': 'Europe/Madrid'
}

'''
    
    # Agregar acciones por mercado
    config_content += "# Acciones por mercado (obtenidas dinámicamente)\n"
    config_content += "MARKET_STOCKS = {\n"
    
    for market, symbols in market_stocks.items():
        config_content += f"    '{market.lower()}': [\n"
        # Dividir en líneas de máximo 5 símbolos para mejor legibilidad
        for i in range(0, len(symbols), 5):
            chunk = symbols[i:i+5]
            # Escapar comillas simples en los símbolos
            escaped_chunk = [escape_quotes(symbol) for symbol in chunk]
            symbols_str = "', '".join(escaped_chunk)
            if i + 5 >= len(symbols):
                config_content += f"        '{symbols_str}'\n"
            else:
                config_content += f"        '{symbols_str}',\n"
        config_content += "    ],\n"
    
    config_content += "}\n\n"
    
    # Agregar acciones por sector (versión actualizada)
    config_content += "# Acciones por sectores (combinando datos estáticos y dinámicos)\n"
    config_content += "SECTOR_STOCKS = {\n"
    
    # Mantener algunos sectores conocidos y agregar los nuevos
    known_sectors = {
        'technology': [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 
            'CRM', 'ORCL', 'ADBE', 'NFLX', 'PYPL', 'INTC', 'AMD'
        ],
        'finance': [
            'JPM', 'BAC', 'WFC', 'GS', 'C', 'MS', 'AXP', 'V', 'MA',
            'USB', 'TFC', 'PNC', 'SCHW'
        ],
        'healthcare': [
            'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT', 'DHR',
            'BMY', 'AMGN', 'GILD', 'CVS', 'CI', 'HUM'
        ],
        'consumer': [
            'PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'NKE', 'COST', 'SBUX',
            'TGT', 'LOW', 'TJX', 'MDLZ', 'CL', 'KMB'
        ],
        'energy': [
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'OXY', 'KMI',
            'WMB', 'MPC', 'HES', 'DVN', 'HAL', 'BKR'
        ],
        'industrial': [
            'GE', 'BA', 'CAT', 'HON', 'MMM', 'UPS', 'LMT', 'RTX', 'DE', 'FDX',
            'WM', 'EMR', 'ETN', 'ITW', 'CSX'
        ]
    }
    
    # Combinar sectores conocidos con los dinámicos
    all_sectors = known_sectors.copy()
    
    for sector, symbols in sector_stocks.items():
        if sector in all_sectors:
            # Combinar sin duplicados
            combined = list(set(all_sectors[sector] + symbols))
            all_sectors[sector] = sorted(combined)
        else:
            all_sectors[sector] = sorted(symbols)
    
    for sector, symbols in all_sectors.items():
        if symbols:  # Solo incluir sectores con acciones
            config_content += f"    '{sector}': [\n"
            # Dividir en líneas de máximo 6 símbolos para mejor legibilidad
            for i in range(0, len(symbols), 6):
                chunk = symbols[i:i+6]
                # Escapar comillas simples en los símbolos
                escaped_chunk = [escape_quotes(symbol) for symbol in chunk]
                symbols_str = "', '".join(escaped_chunk)
                if i + 6 >= len(symbols):
                    config_content += f"        '{symbols_str}'\n"
                else:
                    config_content += f"        '{symbols_str}',\n"
            config_content += "    ],\n"
    
    config_content += "}\n\n"
    
    # Agregar función para cargar datos dinámicos
    config_content += '''
def load_dynamic_stocks_data():
    """
    Cargar datos completos de acciones obtenidas dinámicamente
    """
    try:
        data_dir = "data"
        improved_files = [f for f in os.listdir(data_dir) if f.startswith("improved_stocks_") and f.endswith(".json")]
        
        if not improved_files:
            return []
        
        latest_file = sorted(improved_files)[-1]
        file_path = os.path.join(data_dir, latest_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando datos dinámicos: {e}")
        return []

def get_all_symbols():
    """
    Obtener todos los símbolos disponibles
    """
    all_symbols = set()
    
    # Símbolos por mercado
    for symbols in MARKET_STOCKS.values():
        all_symbols.update(symbols)
    
    # Símbolos por sector
    for symbols in SECTOR_STOCKS.values():
        all_symbols.update(symbols)
    
    return sorted(list(all_symbols))

def get_symbols_by_country(country_code: str):
    """
    Obtener símbolos filtrados por país
    """
    dynamic_data = load_dynamic_stocks_data()
    
    if not dynamic_data:
        return []
    
    return [stock['symbol'] for stock in dynamic_data if stock.get('country', '').upper() == country_code.upper()]

# Resumen de datos
STOCK_DATA_SUMMARY = {
'''
    
    config_content += f"    'total_stocks': {len(stocks)},\n"
    config_content += f"    'markets': {list(market_stocks.keys())},\n"
    config_content += f"    'sectors': {list(sector_stocks.keys())},\n"
    
    # Contar por mercado
    config_content += "    'by_market': {\n"
    for market, symbols in market_stocks.items():
        config_content += f"        '{market}': {len(symbols)},\n"
    config_content += "    },\n"
    
    # Contar por sector
    config_content += "    'by_sector': {\n"
    for sector, symbols in sector_stocks.items():
        config_content += f"        '{sector}': {len(symbols)},\n"
    config_content += "    }\n"
    
    config_content += "}\n"
    
    return config_content

def main():
    """Función principal"""
    print("🔄 Actualizando configuración con acciones dinámicas...")
    
    try:
        # Cargar acciones dinámicas
        stocks = load_dynamic_stocks()
        
        # Crear configuración actualizada
        updated_config = create_updated_config(stocks)
        
        # Hacer backup del config actual
        if os.path.exists("config.py"):
            backup_path = f"config_backup_{int(os.path.getctime('config.py'))}.py"
            os.rename("config.py", backup_path)
            print(f"✅ Backup creado: {backup_path}")
        
        # Escribir nueva configuración
        with open("config.py", 'w', encoding='utf-8') as f:
            f.write(updated_config)
        
        print("✅ Configuración actualizada exitosamente")
        print(f"📊 Total de acciones integradas: {len(stocks)}")
        
        # Mostrar resumen
        market_stocks = organize_stocks_by_market(stocks)
        sector_stocks = organize_stocks_by_sector(stocks)
        
        print("\n📈 Acciones por mercado:")
        for market, symbols in market_stocks.items():
            print(f"  {market}: {len(symbols)} acciones")
        
        print("\n🏷️ Acciones por sector:")
        for sector, symbols in sector_stocks.items():
            print(f"  {sector}: {len(symbols)} acciones")
        
    except Exception as e:
        print(f"❌ Error actualizando configuración: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
