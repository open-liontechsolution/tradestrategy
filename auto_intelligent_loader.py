#!/usr/bin/env python3
"""
Auto Intelligent Loader - Ejecución automática sin input interactivo
==================================================================
"""

import os
import json
from datetime import datetime
from intelligent_stock_loader import get_all_symbols_from_config, get_dynamic_symbols
from symbol_resolver import SymbolResolver
from data_loader import DataLoader

def auto_intelligent_load():
    """Carga automática sin interacción del usuario"""
    print("🚀 AUTO INTELLIGENT STOCK LOADER V1.0")
    print("="*60)
    print("Carga automática con símbolos limpios del Symbol Resolver")
    print()
    
    # 1. Recopilar símbolos
    print("📚 Recopilando símbolos...")
    config_symbols = get_all_symbols_from_config()
    dynamic_symbols = get_dynamic_symbols()
    all_inputs = list(set(config_symbols + dynamic_symbols))
    print(f"   • Total elementos únicos: {len(all_inputs)}")
    
    # 2. Aplicar Symbol Resolver
    print("\n🧠 Aplicando Symbol Resolver...")
    resolver = SymbolResolver()
    clean_symbols, resolution_report = resolver.batch_resolve(all_inputs)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    resolver.generate_detailed_report(resolution_report, f"resolution_report_{timestamp}.json")
    
    print(f"\n✅ SÍMBOLOS LISTOS PARA CARGA:")
    print(f"   • Símbolos válidos: {len(clean_symbols)}")
    print(f"   • Conversiones realizadas: {resolution_report['names_resolved']}")
    print(f"   • Elementos descartados: {resolution_report['failed_resolutions']}")
    
    # 3. Carga automática (sin preguntar)
    print("\n🚀 INICIANDO CARGA MASIVA AUTOMÁTICA")
    print("📊 Procesando todos los símbolos válidos...")
    
    # Crear archivo temporal con símbolos válidos para que DataLoader los use
    temp_stocks_data = []
    for symbol in clean_symbols:
        temp_stocks_data.append({
            'symbol': symbol,
            'name': symbol,  # Usar el símbolo como nombre por defecto
            'market': 'Mixed'
        })
    
    # Guardar temporalmente los símbolos válidos
    temp_file = f"data/temp_resolved_stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('data', exist_ok=True)
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(temp_stocks_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Símbolos válidos guardados en: {temp_file}")
    
    # Inicializar DataLoader
    data_loader = DataLoader()
    
    # Cargar datos históricos masivos
    print(f"\n📈 Iniciando descarga masiva con filtro de años activado...")
    data_dict, combined_file = data_loader.load_all_historical_data(
        period="max", 
        interval="1wk",
        filter_by_years=True  # Filtrar por años mínimos (configurado en .env)
    )
    
    # 4. Reporte final
    final_report = {
        'timestamp': timestamp,
        'symbol_resolution': resolution_report,
        'data_loading': data_dict,
        'summary': {
            'input_elements': len(all_inputs),
            'resolved_symbols': len(clean_symbols),
            'successfully_loaded': len(data_dict) if isinstance(data_dict, dict) else 0,
            'combined_file': combined_file
        }
    }
    
    final_report_file = f"intelligent_load_report_{timestamp}.json"
    with open(final_report_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 CARGA INTELIGENTE COMPLETADA")
    print("="*50)
    print(f"📊 RESUMEN FINAL:")
    print(f"   • Elementos de entrada: {final_report['summary']['input_elements']}")
    print(f"   • Símbolos resueltos: {final_report['summary']['resolved_symbols']}")
    print(f"   • Cargas exitosas: {final_report['summary']['successfully_loaded']}")  
    print(f"   • Registros generados: {final_report['summary']['final_dataset_records']:,}")
    print(f"📁 Reporte completo: {final_report_file}")
    
    return clean_symbols, final_report

if __name__ == "__main__":
    auto_intelligent_load()
