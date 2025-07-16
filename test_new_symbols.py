#!/usr/bin/env python3
"""
Probar los nuevos símbolos del NASDAQ 100 corregidos
"""

from config import get_all_symbols, MARKET_STOCKS
import yfinance as yf
import os
from datetime import datetime, timedelta

def test_nasdaq_symbols():
    """Probar cuántos símbolos del NASDAQ 100 funcionan ahora"""
    print("🧪 PROBANDO SÍMBOLOS NASDAQ 100 CORREGIDOS")
    print("="*60)
    
    nasdaq_symbols = MARKET_STOCKS['us_nasdaq100']
    print(f"📊 Total símbolos NASDAQ 100: {len(nasdaq_symbols)}")
    
    working_symbols = []
    failed_symbols = []
    
    print(f"\n🔍 Probando símbolos (muestra de 20 para velocidad):")
    
    # Probar solo una muestra para ser rápido
    sample_symbols = nasdaq_symbols[:20]
    
    for i, symbol in enumerate(sample_symbols, 1):
        print(f"   [{i:2d}/20] {symbol}...", end=" ")
        try:
            ticker = yf.Ticker(symbol)
            
            # Probar datos recientes
            data = ticker.history(period="5d")
            if not data.empty:
                working_symbols.append(symbol)
                print("✅")
            else:
                failed_symbols.append(symbol)
                print("❌ Sin datos")
                
        except Exception as e:
            failed_symbols.append(symbol)
            print(f"❌ Error")
    
    print(f"\n📊 RESULTADOS DE LA MUESTRA:")
    print(f"   • Funcionando: {len(working_symbols)}/{len(sample_symbols)} ({len(working_symbols)/len(sample_symbols)*100:.1f}%)")
    print(f"   • Fallando: {len(failed_symbols)}")
    
    if failed_symbols:
        print(f"   • Símbolos problemáticos: {failed_symbols}")
    
    # Extrapolar al total
    success_rate = len(working_symbols) / len(sample_symbols)
    estimated_working = int(len(nasdaq_symbols) * success_rate)
    
    print(f"\n📈 PROYECCIÓN TOTAL:")
    print(f"   • Estimados funcionando: {estimated_working}/{len(nasdaq_symbols)}")
    print(f"   • Mejora estimada: +{estimated_working} acciones del NASDAQ 100")

def test_all_symbols_count():
    """Contar cuántos símbolos tenemos ahora en total"""
    print(f"\n📊 RECUENTO TOTAL DE SÍMBOLOS:")
    print("="*60)
    
    all_symbols = get_all_symbols()
    print(f"📈 Total símbolos configurados: {len(all_symbols)}")
    
    # Por mercado
    for market, symbols in MARKET_STOCKS.items():
        print(f"   • {market}: {len(symbols)} símbolos")
    
    # Verificar duplicados
    unique_symbols = set(all_symbols)
    duplicates = len(all_symbols) - len(unique_symbols)
    
    if duplicates > 0:
        print(f"⚠️  Símbolos duplicados encontrados: {duplicates}")
    else:
        print(f"✅ Sin duplicados - todos los símbolos son únicos")

def check_filtering_impact():
    """Verificar el impacto del filtrado en los nuevos símbolos"""
    print(f"\n🔍 ANÁLISIS DE FILTRADO (5+ AÑOS):")
    print("="*60)
    
    # Verificar algunos símbolos nuevos que antes fallaban
    test_symbols = ['CEG', 'DASH', 'PLTR', 'ARM', 'GEHC']
    
    min_years = int(os.getenv('MIN_STOCK_YEARS', '5'))
    cutoff_date = datetime.now() - timedelta(days=min_years * 365)
    
    print(f"📅 Filtro configurado: {min_years} años mínimos")
    print(f"📅 Fecha límite: {cutoff_date.strftime('%Y-%m-%d')}")
    
    for symbol in test_symbols:
        print(f"\n🔍 {symbol}:")
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="max")
            
            if not data.empty:
                start_date = data.index[0]
                years_of_data = (datetime.now() - start_date.to_pydatetime()).days / 365.25
                
                print(f"   📊 Datos desde: {start_date.strftime('%Y-%m-%d')}")
                print(f"   📊 Años de datos: {years_of_data:.1f}")
                
                if years_of_data >= min_years:
                    print(f"   ✅ Pasa filtro (≥{min_years} años)")
                else:
                    print(f"   ❌ Filtrado (< {min_years} años)")
            else:
                print(f"   ❌ Sin datos históricos")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("📈 VALIDACIÓN DE LA CORRECCIÓN NASDAQ 100")
    print("="*60)
    
    test_nasdaq_symbols()
    test_all_symbols_count()  
    check_filtering_impact()
    
    print(f"\n✅ ANÁLISIS COMPLETADO")
    print(f"🚀 Listo para ejecutar carga completa con símbolos corregidos")
