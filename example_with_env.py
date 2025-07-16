#!/usr/bin/env python3
"""
Ejemplo de uso del sistema con variables de entorno para filtrado por años mínimos
"""

import os
from data_loader import DataLoader

def example_with_different_min_years():
    """Ejemplo mostrando diferentes configuraciones de años mínimos"""
    
    print("🎯 EJEMPLOS DE CONFIGURACIÓN POR AÑOS MÍNIMOS")
    print("=" * 60)
    
    # Ejemplo 1: 3 años mínimos
    print("\n📈 EJEMPLO 1: Acciones con mínimo 3 años")
    os.environ['MIN_STOCK_YEARS'] = '3'
    loader1 = DataLoader()
    print(f"Configuración: {loader1.min_years} años mínimos")
    print(f"Fecha mínima: {loader1.min_date.strftime('%Y-%m-%d')}")
    
    # Ejemplo 2: 10 años mínimos (más conservador)
    print("\n📈 EJEMPLO 2: Acciones con mínimo 10 años (conservador)")
    os.environ['MIN_STOCK_YEARS'] = '10'
    loader2 = DataLoader()
    print(f"Configuración: {loader2.min_years} años mínimos")
    print(f"Fecha mínima: {loader2.min_date.strftime('%Y-%m-%d')}")
    
    # Ejemplo 3: 1 año mínimo (menos restrictivo)
    print("\n📈 EJEMPLO 3: Acciones con mínimo 1 año (menos restrictivo)")
    os.environ['MIN_STOCK_YEARS'] = '1'
    loader3 = DataLoader()
    print(f"Configuración: {loader3.min_years} años mínimos")
    print(f"Fecha mínima: {loader3.min_date.strftime('%Y-%m-%d')}")

def run_filtered_example():
    """Ejecutar un ejemplo práctico con filtrado"""
    
    print("\n🚀 EJECUTANDO EJEMPLO PRÁCTICO CON FILTRADO")
    print("=" * 60)
    
    # Configurar para 3 años mínimos para este ejemplo
    os.environ['MIN_STOCK_YEARS'] = '3'
    
    loader = DataLoader()
    
    print(f"⚙️ Configuración activa:")
    print(f"   📅 Años mínimos: {loader.min_years}")
    print(f"   📊 Fecha mínima: {loader.min_date.strftime('%Y-%m-%d')}")
    print(f"   🔧 Variable: MIN_STOCK_YEARS={os.getenv('MIN_STOCK_YEARS')}")
    
    # Ejecutar carga de prueba con filtrado
    print(f"\n🧪 Cargando datos de prueba (5 acciones, histórico completo, filtro activado)...")
    
    data_dict, combined_file = loader.load_all_historical_data(
        period="max",           # Histórico completo
        interval="1wk",         # Datos semanales
        max_stocks=5,          # Solo 5 acciones para ejemplo rápido
        filter_by_years=True   # Activar filtro
    )
    
    if data_dict:
        print(f"\n✅ Ejemplo completado exitosamente!")
        print(f"📊 Acciones procesadas: {len(data_dict)}")
        print(f"📁 Archivo combinado: {combined_file}")
        
        # Mostrar información de las primeras acciones
        for symbol, df in list(data_dict.items())[:3]:
            if not df.empty:
                oldest_date = df.index.min().strftime('%Y-%m-%d')
                newest_date = df.index.max().strftime('%Y-%m-%d')
                print(f"   📈 {symbol}: {oldest_date} → {newest_date} ({len(df)} registros)")
    else:
        print("❌ No se pudieron cargar datos en el ejemplo")

if __name__ == "__main__":
    print("🎯 EJEMPLOS DE USO CON FILTRADO POR AÑOS MÍNIMOS")
    print("=" * 70)
    
    # Mostrar ejemplos de configuración
    example_with_different_min_years()
    
    # Ejecutar ejemplo práctico
    run_filtered_example()
    
    print("\n" + "=" * 70)
    print("📝 INSTRUCCIONES DE USO:")
    print("   • Para cambiar años mínimos: export MIN_STOCK_YEARS=5")
    print("   • Para usar el sistema: python integrated_main.py")
    print("   • Para datos sin filtro: Seleccionar opción 4 en el menú")
    print("   • Valores recomendados: 1-3 años (menos restrictivo), 5-10 años (más conservador)")
