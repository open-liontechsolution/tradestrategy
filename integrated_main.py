#!/usr/bin/env python3
"""
Script principal integrado para el sistema de análisis de trading mejorado
Incluye todas las funcionalidades del sistema actualizado
"""

import sys
import os
from datetime import datetime
from typing import Optional

# Importar nuestros módulos
from stock_analyzer import StockAnalyzer
from data_loader import DataLoader
from config import get_all_symbols, MARKET_STOCKS, SECTOR_STOCKS, STOCK_DATA_SUMMARY

def show_system_info():
    """Mostrar información del sistema"""
    print("="*60)
    print("🚀 SISTEMA DE ANÁLISIS DE TRADING MEJORADO")
    print("="*60)
    print(f"📊 Total de acciones disponibles: {STOCK_DATA_SUMMARY['total_stocks']}")
    print(f"🌍 Mercados: {', '.join(STOCK_DATA_SUMMARY['markets'])}")
    print(f"🏷️  Sectores: {len(STOCK_DATA_SUMMARY['sectors'])}")
    
    print("\n📈 Acciones por mercado:")
    for market, count in STOCK_DATA_SUMMARY['by_market'].items():
        print(f"  {market}: {count} acciones")
    
    print("\n🏷️ Acciones por sector (principales):")
    for sector, count in STOCK_DATA_SUMMARY['by_sector'].items():
        if count > 20:  # Solo mostrar sectores grandes
            print(f"  {sector}: {count} acciones")
    
    print("="*60)

def analyze_stock_example():
    """Ejecutar análisis de ejemplo con una acción"""
    print("\n🔍 EJEMPLO: Análisis de AAPL")
    print("-" * 40)
    
    analyzer = StockAnalyzer()
    
    try:
        # Analizar AAPL
        analyzer.fetch_stock_data('AAPL', period='1y', interval='1wk')
        
        # Mostrar estadísticas básicas
        stats = analyzer.get_basic_stats()
        print(f"📊 Estadísticas básicas de AAPL:")
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        # Crear gráfico
        analyzer.plot_price_and_volume(save_plot=True, filename='integrated_example_aapl.png')
        print(f"📈 Gráfico guardado: integrated_example_aapl.png")
        
        print("✅ Análisis de ejemplo completado")
        
    except Exception as e:
        print(f"❌ Error en análisis de ejemplo: {e}")

def load_historical_data_menu():
    """Menú para cargar datos históricos"""
    loader = DataLoader()
    
    # Mostrar configuración actual del filtro
    print(f"\n⚙️ CONFIGURACIÓN DE FILTRADO ACTUAL:")
    print(f"📅 Años mínimos: {loader.min_years} (Variable: MIN_STOCK_YEARS={os.getenv('MIN_STOCK_YEARS', 'No definida')})")
    print(f"📊 Fecha mínima: {loader.min_date.strftime('%Y-%m-%d')}")
    
    print("\n📊 OPCIONES DE CARGA DE DATOS HISTÓRICOS:")
    print("1. Carga básica (primeras 20 acciones, período 1 año)")
    print("2. Carga completa CON filtro (644 acciones disponibles, 5+ años mínimo)")
    print("3. Carga completa SIN filtro (TODAS las 644 acciones, sin restricción)")
    print("4. Carga personalizada (configuración manual)")
    print("5. Configuración personalizada")
    print("0. Volver al menú principal")
    
    choice = input("\nSelecciona una opción: ").strip()
    
    if choice == "1":
        print("🧪 Cargando datos de prueba con filtrado...")
        data_dict, combined_file = loader.load_all_historical_data(
            period="max", interval="1wk", max_stocks=20, filter_by_years=True
        )
    elif choice == "2":
        print("🚀 Cargando TODAS las acciones con filtrado de 5+ años...")
        print("⏳ Esto puede tomar varios minutos. Progreso se mostrará en tiempo real.")
        data_dict, combined_file = loader.load_all_historical_data(
            period="max", interval="1wk", max_stocks=None, filter_by_years=True
        )
    elif choice == "3":
        print("⚠️  Cargando TODAS las 644 acciones SIN filtro de años...")
        print("⚠️  Esto incluirá acciones con menos de {} años de historia".format(loader.min_years))
        print("⏳ Proceso muy largo. Se recomienda usar opción 2 con filtrado.")
        confirm = input("¿Continuar? (s/N): ").strip().lower()
        if confirm == 's':
            data_dict, combined_file = loader.load_all_historical_data(
                period="max", interval="1wk", max_stocks=None, filter_by_years=False
            )
        else:
            print("❌ Operación cancelada")
            return
    elif choice == "4":
        print("\n🔧 CONFIGURACIÓN PERSONALIZADA:")
        period = input("Período (1y/2y/5y/max) [max]: ").strip() or "max"
        interval = input("Intervalo (1d/1wk/1mo) [1wk]: ").strip() or "1wk"
        max_stocks_input = input("Máximo acciones (Enter=todas): ").strip()
        max_stocks = int(max_stocks_input) if max_stocks_input.isdigit() else None
        filter_input = input("Aplicar filtro de años? (s/N) [s]: ").strip().lower()
        filter_by_years = filter_input != 'n'
        
        print(f"\n📈 Configuración: período={period}, intervalo={interval}")
        print(f"📀 Acciones: {'Todas (644)' if max_stocks is None else max_stocks}")
        print(f"📅 Filtro: {'Activado (' + str(loader.min_years) + '+ años)' if filter_by_years else 'Desactivado'}")
        
        confirm = input("¿Continuar? (s/N): ").strip().lower()
        if confirm == 's':
            data_dict, combined_file = loader.load_all_historical_data(
                period=period, interval=interval, max_stocks=max_stocks, filter_by_years=filter_by_years
            )
        else:
            print("❌ Operación cancelada")
            return
    elif choice == "5":
        # Configuración del filtro
        print("\n⚙️ CONFIGURACIÓN DEL FILTRO:")
        print(f"Actual: {loader.min_years} años mínimo")
        new_years = input("Nuevo valor (Enter=mantener actual): ").strip()
        if new_years.isdigit():
            import os
            os.environ['MIN_STOCK_YEARS'] = new_years
            print(f"✅ Filtro actualizado: {new_years} años mínimo")
        else:
            print("📌 Filtro mantenido")
        return
    elif choice == "0":
        return
    else:
        print("❌ Opción no válida")
        return
    
    if data_dict:
        print(f"\n✅ Carga completada: {len(data_dict)} acciones")
        print(f"📄 Archivo combinado: {combined_file}")

def analyze_market_sector():
    """Analizar acciones por mercado o sector"""
    print("\n📊 ANÁLISIS POR MERCADO/SECTOR")
    print("-" * 40)
    print("1. Analizar por mercado")
    print("2. Analizar por sector")
    print("0. Volver al menú principal")
    
    choice = input("\nSelecciona una opción: ").strip()
    
    if choice == "1":
        print("\n🌍 Mercados disponibles:")
        for i, market in enumerate(MARKET_STOCKS.keys(), 1):
            count = len(MARKET_STOCKS[market])
            print(f"  {i}. {market.upper()} ({count} acciones)")
        
        try:
            market_idx = int(input("\nSelecciona mercado: ")) - 1
            market_name = list(MARKET_STOCKS.keys())[market_idx]
            symbols = MARKET_STOCKS[market_name][:10]  # Limitar a 10 para ejemplo
            
            print(f"\n🔍 Analizando primeras 10 acciones de {market_name.upper()}:")
            analyzer = StockAnalyzer()
            
            for symbol in symbols:
                try:
                    analyzer.fetch_stock_data(symbol, period='3mo', interval='1wk')
                    stats = analyzer.get_basic_stats()
                    print(f"  {symbol}: Precio actual: ${stats['current_price']:.2f}, Retorno: {stats['total_return']:.1f}%")
                except Exception as e:
                    print(f"  {symbol}: Error - {e}")
                    
        except (ValueError, IndexError):
            print("❌ Selección inválida")
    
    elif choice == "2":
        print("\n🏷️ Sectores disponibles:")
        for i, (sector, symbols) in enumerate(SECTOR_STOCKS.items(), 1):
            if len(symbols) > 10:  # Solo mostrar sectores grandes
                print(f"  {i}. {sector.title()} ({len(symbols)} acciones)")
        
        sector_name = input("\nIngresa nombre del sector: ").strip().lower()
        
        if sector_name in SECTOR_STOCKS:
            symbols = SECTOR_STOCKS[sector_name][:10]  # Limitar a 10 para ejemplo
            
            print(f"\n🔍 Analizando primeras 10 acciones de {sector_name.title()}:")
            analyzer = StockAnalyzer()
            
            for symbol in symbols:
                try:
                    analyzer.fetch_stock_data(symbol, period='3mo', interval='1wk')
                    stats = analyzer.get_basic_stats()
                    print(f"  {symbol}: Precio actual: ${stats['current_price']:.2f}, Retorno: {stats['total_return']:.1f}%")
                except Exception as e:
                    print(f"  {symbol}: Error - {e}")
        else:
            print("❌ Sector no encontrado")
    
    elif choice == "0":
        return
    else:
        print("❌ Opción inválida")

def main_menu():
    """Menú principal del sistema"""
    while True:
        print("\n" + "="*60)
        print("🚀 SISTEMA DE ANÁLISIS DE TRADING MEJORADO")
        print("="*60)
        print("1. Mostrar información del sistema")
        print("2. Ejecutar análisis de ejemplo (AAPL)")
        print("3. Cargar datos históricos")
        print("4. Analizar por mercado/sector")
        print("5. Análisis personalizado de una acción")
        print("6. Comparar múltiples acciones")
        print("0. Salir")
        
        choice = input("\nSelecciona una opción: ").strip()
        
        if choice == "1":
            show_system_info()
        elif choice == "2":
            analyze_stock_example()
        elif choice == "3":
            load_historical_data_menu()
        elif choice == "4":
            analyze_market_sector()
        elif choice == "5":
            symbol = input("\nIngresa el símbolo de la acción: ").strip().upper()
            if symbol:
                try:
                    analyzer = StockAnalyzer()
                    analyzer.fetch_stock_data(symbol, period='1y', interval='1wk')
                    
                    # Análisis completo
                    stats = analyzer.get_basic_stats()
                    print(f"\n📊 Análisis de {symbol}:")
                    for key, value in stats.items():
                        if isinstance(value, float):
                            print(f"  {key}: {value:.2f}")
                        else:
                            print(f"  {key}: {value}")
                    
                    # Crear gráfico
                    filename = f"analysis_{symbol.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    analyzer.plot_price_and_volume(save_plot=True, filename=filename)
                    print(f"📈 Gráfico guardado: {filename}")
                    
                except Exception as e:
                    print(f"❌ Error analizando {symbol}: {e}")
        elif choice == "6":
            symbols_input = input("\nIngresa símbolos separados por comas: ").strip()
            if symbols_input:
                symbols = [s.strip().upper() for s in symbols_input.split(',')]
                try:
                    analyzer = StockAnalyzer()
                    comparison_data = {}
                    
                    for symbol in symbols:
                        analyzer.fetch_stock_data(symbol, period='1y', interval='1wk')
                        comparison_data[symbol] = analyzer.data.copy()
                    
                    # Crear gráfico de comparación
                    filename = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    analyzer.compare_stocks(list(comparison_data.keys()), save_plot=True, filename=filename)
                    print(f"📈 Gráfico de comparación guardado: {filename}")
                    
                except Exception as e:
                    print(f"❌ Error en comparación: {e}")
        elif choice == "0":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

def main():
    """Función principal"""
    print("🔧 Inicializando sistema...")
    
    # Verificar que tenemos datos
    try:
        total_symbols = len(get_all_symbols())
        if total_symbols == 0:
            print("⚠️  No hay datos de acciones disponibles")
            print("🔄 Ejecuta primero 'improved_stock_fetcher.py' para obtener las acciones")
            return
        
        print(f"✅ Sistema listo con {total_symbols} acciones disponibles")
        main_menu()
        
    except Exception as e:
        print(f"❌ Error inicializando sistema: {e}")

if __name__ == "__main__":
    main()
