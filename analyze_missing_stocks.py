#!/usr/bin/env python3
"""
Análisis de acciones faltantes y errores de descarga
"""

import os
from config import get_all_symbols, MARKET_STOCKS
import pandas as pd
from pathlib import Path

def analyze_missing_stocks():
    """Analizar qué acciones faltaron en la descarga"""
    print("🔍 ANÁLISIS DE ACCIONES FALTANTES")
    print("="*50)
    
    # Obtener todas las acciones disponibles
    all_symbols = get_all_symbols()
    print(f"📊 Total acciones en config: {len(all_symbols)}")
    
    # Verificar qué acciones se descargaron exitosamente
    data_dir = Path("historical_data/individual")
    downloaded_files = list(data_dir.glob("*.csv"))
    
    # Extraer símbolos de los archivos descargados
    downloaded_symbols = set()
    for file in downloaded_files:
        # El formato es SYMBOL_YYYYMMDD_HHMMSS.csv
        symbol = file.stem.split('_')[0]
        downloaded_symbols.add(symbol)
    
    print(f"✅ Acciones descargadas: {len(downloaded_symbols)}")
    
    # Encontrar acciones faltantes
    missing_symbols = set(all_symbols) - downloaded_symbols
    print(f"❌ Acciones faltantes: {len(missing_symbols)}")
    
    if missing_symbols:
        print(f"\n🚨 ACCIONES FALTANTES ({len(missing_symbols)}):")
        
        # Analizar por mercado
        missing_by_market = {}
        for symbol in missing_symbols:
            found_market = None
            for market, stocks in MARKET_STOCKS.items():
                if symbol in stocks:
                    found_market = market
                    break
            
            if found_market:
                if found_market not in missing_by_market:
                    missing_by_market[found_market] = []
                missing_by_market[found_market].append(symbol)
            else:
                if 'UNKNOWN' not in missing_by_market:
                    missing_by_market['UNKNOWN'] = []
                missing_by_market['UNKNOWN'].append(symbol)
        
        # Mostrar por mercado
        for market, symbols in missing_by_market.items():
            print(f"\n📍 {market}: {len(symbols)} acciones")
            for symbol in sorted(symbols):
                print(f"   • {symbol}")
        
        # Análisis de patrones
        print(f"\n🔍 ANÁLISIS DE PATRONES:")
        
        # Verificar sufijos de mercado
        suffixes = {}
        for symbol in missing_symbols:
            if '.' in symbol:
                suffix = symbol.split('.')[-1]
                if suffix not in suffixes:
                    suffixes[suffix] = []
                suffixes[suffix].append(symbol)
        
        if suffixes:
            print(f"   📍 Por sufijo de mercado:")
            for suffix, symbols in suffixes.items():
                print(f"      .{suffix}: {len(symbols)} acciones - {symbols[:5]}{'...' if len(symbols) > 5 else ''}")
        
        # Verificar caracteres especiales
        special_chars = {}
        for symbol in missing_symbols:
            for char in ['-', '/', '=', '+', '^']:
                if char in symbol:
                    if char not in special_chars:
                        special_chars[char] = []
                    special_chars[char].append(symbol)
        
        if special_chars:
            print(f"   📍 Con caracteres especiales:")
            for char, symbols in special_chars.items():
                print(f"      '{char}': {len(symbols)} acciones - {symbols[:3]}{'...' if len(symbols) > 3 else ''}")
    
    else:
        print("\n✅ ¡Todas las acciones fueron descargadas exitosamente!")
    
    # Verificar el dataset combinado
    combined_file = "historical_data/combined_historical_data_20250715_124830.csv"
    if os.path.exists(combined_file):
        print(f"\n📊 ANÁLISIS DEL DATASET COMBINADO:")
        df = pd.read_csv(combined_file)
        unique_symbols = df['Symbol'].unique()
        print(f"   • Símbolos únicos en dataset: {len(unique_symbols)}")
        print(f"   • Total registros: {len(df):,}")
        
        # Verificar consistencia
        if len(unique_symbols) == len(downloaded_symbols):
            print("   ✅ Consistencia: Dataset coincide con archivos individuales")
        else:
            print("   ⚠️  Inconsistencia detectada entre dataset y archivos")
    
    return missing_symbols, downloaded_symbols

def test_problematic_symbols():
    """Probar manualmente algunos símbolos problemáticos"""
    print(f"\n🧪 PRUEBA MANUAL DE SÍMBOLOS PROBLEMÁTICOS:")
    
    # Símbolos que suelen dar problemas
    test_symbols = ['BRK.B', 'BF.B', 'NVR', 'COIN', 'CEG', 'DASH']
    
    import yfinance as yf
    from datetime import datetime, timedelta
    
    for symbol in test_symbols:
        print(f"\n🔍 Probando {symbol}:")
        try:
            ticker = yf.Ticker(symbol)
            
            # Probar información básica
            info = ticker.info
            if info and 'longName' in info:
                print(f"   ✅ Info: {info.get('longName', 'N/A')}")
            else:
                print(f"   ❌ Sin información básica")
            
            # Probar datos históricos recientes
            data = ticker.history(period="1mo")
            if not data.empty:
                print(f"   ✅ Datos recientes: {len(data)} registros (último: {data.index[-1].strftime('%Y-%m-%d')})")
            else:
                print(f"   ❌ Sin datos históricos recientes")
            
            # Probar datos históricos largos
            long_data = ticker.history(period="5y")
            if not long_data.empty:
                years = (long_data.index[-1] - long_data.index[0]).days / 365.25
                print(f"   ✅ Datos 5 años: {len(long_data)} registros ({years:.1f} años)")
            else:
                print(f"   ❌ Sin datos históricos largos")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    missing, downloaded = analyze_missing_stocks()
    
    if missing:
        test_problematic_symbols()
    
    print(f"\n📋 RESUMEN:")
    print(f"   • Total configuradas: {len(get_all_symbols())}")
    print(f"   • Descargadas exitosamente: {len(downloaded)}")
    print(f"   • Faltantes: {len(missing)}")
    print(f"   • Tasa éxito: {len(downloaded)/(len(downloaded)+len(missing))*100:.1f}%")
