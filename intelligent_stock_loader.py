#!/usr/bin/env python3
"""
Intelligent Stock Loader - Carga Inteligente con Symbol Resolver
===============================================================

Sistema profesional que combina:
- Symbol Resolver para limpieza automática de símbolos
- Carga masiva optimizada de datos históricos  
- Integración con configuración dinámica
- Reportes profesionales detallados
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from symbol_resolver import SymbolResolver
from data_loader import DataLoader
from config import MARKET_STOCKS, SECTOR_STOCKS

def get_all_symbols_from_config():
    """Obtener todos los símbolos de la configuración actual"""
    all_symbols = []
    
    # Obtener símbolos de MARKET_STOCKS
    for market_name, symbols_list in MARKET_STOCKS.items():
        if isinstance(symbols_list, list):
            all_symbols.extend(symbols_list)
        elif isinstance(symbols_list, dict):
            for subsection, subsymbols in symbols_list.items():
                if isinstance(subsymbols, list):
                    all_symbols.extend(subsymbols)
    
    # Obtener símbolos de SECTOR_STOCKS  
    for sector_name, symbols_list in SECTOR_STOCKS.items():
        if isinstance(symbols_list, list):
            all_symbols.extend(symbols_list)
    
    return list(set(all_symbols))  # Eliminar duplicados

def get_dynamic_symbols():
    """Obtener símbolos de archivos JSON dinámicos"""
    import json
    
    dynamic_symbols = []
    data_dir = Path("data")
    
    if data_dir.exists():
        # Buscar archivos JSON de stocks
        json_files = list(data_dir.glob("improved_stocks_*.json"))
        if json_files:
            # Usar el más reciente
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for stock in data:
                        if isinstance(stock, dict) and 'symbol' in stock:
                            dynamic_symbols.append(stock['symbol'])
                        elif isinstance(stock, dict) and 'name' in stock:
                            # Si solo tiene nombre, añadirlo para resolución
                            dynamic_symbols.append(stock['name'])
                        elif isinstance(stock, str):
                            dynamic_symbols.append(stock)
            except Exception as e:
                print(f"⚠️ Error leyendo {latest_file}: {e}")
    
    return dynamic_symbols

def intelligent_stock_load():
    """Función principal de carga inteligente"""
    print("🚀 INTELLIGENT STOCK LOADER V1.0")
    print("="*60)
    print("Sistema profesional con resolución automática de símbolos")
    print()
    
    # 1. Recopilar todos los símbolos/nombres
    print("📚 Recopilando símbolos de todas las fuentes...")
    config_symbols = get_all_symbols_from_config()
    dynamic_symbols = get_dynamic_symbols()
    
    print(f"   • Config.py: {len(config_symbols)} elementos")
    print(f"   • Archivos dinámicos: {len(dynamic_symbols)} elementos")
    
    # Combinar y eliminar duplicados
    all_inputs = list(set(config_symbols + dynamic_symbols))
    print(f"   • Total único: {len(all_inputs)} elementos")
    print()
    
    # 2. Aplicar Symbol Resolver
    print("🧠 Aplicando Symbol Resolver Inteligente...")
    resolver = SymbolResolver()
    clean_symbols, resolution_report = resolver.batch_resolve(all_inputs)
    print()
    
    # 3. Generar reporte de resolución
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"resolution_report_{timestamp}.json"
    resolver.generate_detailed_report(resolution_report, report_file)
    print(f"💾 Reporte de resolución guardado: {report_file}")
    print()
    
    # 4. Confirmar con usuario antes de carga masiva
    print(f"✅ SÍMBOLOS LISTOS PARA CARGA:")
    print(f"   • Símbolos válidos: {len(clean_symbols)}")
    print(f"   • Conversiones realizadas: {resolution_report['names_resolved']}")
    print(f"   • Elementos descartados: {resolution_report['failed_resolutions']}")
    print()
    
    response = input("¿Proceder con la carga masiva de datos históricos? [s/N]: ").strip().lower()
    if response not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Carga cancelada por el usuario.")
        return clean_symbols, resolution_report
    
    # 5. Carga masiva con símbolos limpios
    print()
    print("📈 INICIANDO CARGA MASIVA DE DATOS HISTÓRICOS")
    print("="*60)
    
    # Configurar filtro de años mínimos
    min_years = int(os.getenv('MIN_STOCK_YEARS', '5'))
    print(f"🔧 Configuración: Mínimo {min_years} años de historial")
    print()
    
    # Ejecutar carga
    loader = DataLoader()
    result = loader.load_all_historical_data(clean_symbols, min_years=min_years)
    
    # 6. Generar reporte combinado final
    final_report = {
        'timestamp': timestamp,
        'symbol_resolution': resolution_report,
        'data_loading': result,
        'summary': {
            'input_elements': len(all_inputs),
            'resolved_symbols': len(clean_symbols),
            'successfully_loaded': result.get('successful_downloads', 0),
            'failed_loads': result.get('failed_downloads', 0),
            'final_dataset_records': result.get('total_records', 0)
        }
    }
    
    final_report_file = f"intelligent_load_report_{timestamp}.json"
    import json
    with open(final_report_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print()
    print("🎉 CARGA INTELIGENTE COMPLETADA")
    print("="*40)
    print(f"📊 RESUMEN FINAL:")
    print(f"   • Elementos de entrada: {final_report['summary']['input_elements']}")
    print(f"   • Símbolos resueltos: {final_report['summary']['resolved_symbols']}")
    print(f"   • Cargas exitosas: {final_report['summary']['successfully_loaded']}")  
    print(f"   • Registros generados: {final_report['summary']['final_dataset_records']:,}")
    print(f"📁 Reporte completo: {final_report_file}")
    
    return clean_symbols, final_report

def quick_test_mode():
    """Modo de prueba rápida - solo resolución sin carga"""
    print("🧪 MODO PRUEBA - Solo Symbol Resolution")
    print("="*50)
    
    # Test con muestra pequeña
    test_symbols = [
        'AAPL', 'Microsoft', 'Tesla, Inc.', 'NVDA',
        'Apple Inc.', 'Meta Platforms', 'INVALID_SYMBOL',
        'Amazon', 'Alphabet Inc. (Class A)'
    ]
    
    resolver = SymbolResolver()
    clean_symbols, report = resolver.batch_resolve(test_symbols)
    resolver.generate_detailed_report(report, "test_resolution.json")
    
    print(f"\n✅ Test completado:")
    print(f"   • Input: {len(test_symbols)} elementos")
    print(f"   • Output: {len(clean_symbols)} símbolos válidos")
    print(f"   • Símbolos finales: {clean_symbols}")
    
    return clean_symbols, report

if __name__ == "__main__":
    # Determinar modo de ejecución
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        quick_test_mode()
    else:
        intelligent_stock_load()
