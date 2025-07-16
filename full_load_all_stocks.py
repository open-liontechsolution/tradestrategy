#!/usr/bin/env python3
"""
Carga completa de todas las 644 acciones con filtro aplicado
"""

import os
import sys
from pathlib import Path

# Configurar el filtro para 5 años mínimo
os.environ['MIN_STOCK_YEARS'] = '5'

# Importar DataLoader
from data_loader import DataLoader

def main():
    """Ejecutar carga completa de todas las acciones"""
    print("🚀 CARGA COMPLETA DE TODAS LAS ACCIONES")
    print("="*60)
    
    # Inicializar DataLoader
    print("🔧 Inicializando DataLoader...")
    loader = DataLoader()
    
    from config import get_all_symbols
    all_symbols = get_all_symbols()
    print(f"📊 Total de acciones disponibles: {len(all_symbols)}")
    print(f"📅 Filtro activo: {loader.min_years} años mínimo")
    print(f"📈 Fecha mínima requerida: {loader.min_date.strftime('%Y-%m-%d')}")
    
    print("\n🚀 Iniciando carga de datos históricos completos...")
    print("⚠️  Este proceso puede tomar 15-30 minutos")
    print("⏳ Se mostrará progreso en tiempo real")
    
    # Confirmar ejecución
    print("\n¿Desea continuar con la carga completa?")
    print("Esto descargará datos históricos para todas las 644 acciones")
    print("aplicando el filtro de 5+ años de historia mínima.")
    
    # Para ejecución automática, removemos la confirmación manual
    print("✅ Iniciando carga automática...")
    
    try:
        # Ejecutar carga completa
        data_dict, combined_file = loader.load_all_historical_data(
            period="max",
            interval="1wk", 
            max_stocks=None,  # Todas las acciones
            filter_by_years=True  # Con filtro activo
        )
        
        if data_dict:
            print(f"\n🎉 ¡CARGA COMPLETADA EXITOSAMENTE!")
            print(f"✅ Acciones procesadas: {len(data_dict)}")
            print(f"📁 Archivo combinado: {combined_file}")
            
            # Mostrar estadísticas
            if combined_file:
                print(f"\n📊 ESTADÍSTICAS DEL DATASET:")
                import pandas as pd
                df = pd.read_csv(combined_file)
                print(f"   • Total de registros: {len(df):,}")
                print(f"   • Acciones únicas: {df['Symbol'].nunique()}")
                print(f"   • Rango temporal: {df['Date'].min()} a {df['Date'].max()}")
                
                # Top 10 por cantidad de registros
                top_stocks = df.groupby('Symbol').size().sort_values(ascending=False).head(10)
                print(f"\n📈 TOP 10 ACCIONES POR REGISTROS HISTÓRICOS:")
                for i, (symbol, count) in enumerate(top_stocks.items(), 1):
                    years = count / 52  # Aproximado semanal
                    print(f"   {i:2}. {symbol}: {count:,} registros (~{years:.1f} años)")
            
            print(f"\n🚀 SIGUIENTES PASOS:")
            print("   1. Ejecutar quick_analysis.py para análisis completo")
            print("   2. Usar launcher.py para análisis interactivo")
            print("   3. Crear estrategias de trading específicas")
            
        else:
            print("❌ No se pudieron cargar datos")
            
    except KeyboardInterrupt:
        print("\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la carga: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
