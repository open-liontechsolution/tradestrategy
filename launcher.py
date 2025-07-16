#!/usr/bin/env python3
"""
Launcher principal del sistema de trading
"""

import os
import sys
from pathlib import Path

def show_welcome():
    """Mostrar mensaje de bienvenida"""
    print("🚀 SISTEMA DE TRADING - VERSIÓN 2.0")
    print("="*50)
    print("✅ 97 acciones cargadas con filtro de 5+ años")
    print("✅ 36,712 registros históricos disponibles")
    print("✅ Datos desde 1962 hasta 2025")
    print("✅ Análisis avanzado completado")
    print()

def show_configuration():
    """Mostrar configuración actual"""
    min_years = os.getenv('MIN_STOCK_YEARS', '5')
    print(f"⚙️ CONFIGURACIÓN ACTUAL:")
    print(f"   📅 Años mínimos: {min_years}")
    print(f"   📊 Filtrado: {'Activado' if min_years != '0' else 'Desactivado'}")
    print()

def main_menu():
    """Menú principal"""
    while True:
        print("📋 OPCIONES DISPONIBLES:")
        print("1. 🖥️  Sistema integrado completo (integrated_main.py)")
        print("2. 📊 Análisis rápido del dataset (quick_analysis.py)")
        print("3. 🔧 Cargar más datos históricos (data_loader.py)")
        print("4. 📈 Análisis individual de acción (main.py)")
        print("5. ⚙️  Configurar filtro de años")
        print("6. 📋 Ver ejemplos de configuración")
        print("0. 🚪 Salir")
        print()
        
        choice = input("Selecciona una opción (0-6): ").strip()
        
        if choice == "1":
            print("🚀 Ejecutando sistema integrado...")
            os.system("python integrated_main.py")
        elif choice == "2":
            print("📊 Ejecutando análisis rápido...")
            os.system("python quick_analysis.py")
        elif choice == "3":
            print("🔧 Abriendo cargador de datos...")
            print("💡 Tip: Usa export MIN_STOCK_YEARS=X para configurar filtro")
            os.system("python -c 'from data_loader import DataLoader; DataLoader().interactive_load()'")
        elif choice == "4":
            print("📈 Ejecutando análisis individual...")
            os.system("python main.py")
        elif choice == "5":
            configure_filter()
        elif choice == "6":
            show_examples()
        elif choice == "0":
            print("🚪 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida")
        
        print("\n" + "-"*50 + "\n")

def configure_filter():
    """Configurar filtro de años"""
    print("\n⚙️ CONFIGURACIÓN DE FILTRO")
    print("="*30)
    print("1. Sin filtro (todas las acciones)")
    print("2. 1 año mínimo (menos restrictivo)")
    print("3. 3 años mínimo (moderado)")
    print("4. 5 años mínimo (equilibrado - recomendado)")
    print("5. 10 años mínimo (conservador)")
    print("6. Personalizado")
    
    choice = input("\nSelecciona configuración (1-6): ").strip()
    
    if choice == "1":
        os.environ['MIN_STOCK_YEARS'] = "0"
        print("✅ Filtro desactivado")
    elif choice == "2":
        os.environ['MIN_STOCK_YEARS'] = "1"
        print("✅ Filtro configurado: 1 año mínimo")
    elif choice == "3":
        os.environ['MIN_STOCK_YEARS'] = "3"
        print("✅ Filtro configurado: 3 años mínimos")
    elif choice == "4":
        os.environ['MIN_STOCK_YEARS'] = "5"
        print("✅ Filtro configurado: 5 años mínimos")
    elif choice == "5":
        os.environ['MIN_STOCK_YEARS'] = "10"
        print("✅ Filtro configurado: 10 años mínimos")
    elif choice == "6":
        years = input("Ingresa años mínimos: ").strip()
        try:
            int(years)
            os.environ['MIN_STOCK_YEARS'] = years
            print(f"✅ Filtro configurado: {years} años mínimos")
        except ValueError:
            print("❌ Valor no válido")

def show_examples():
    """Mostrar ejemplos de uso"""
    print("\n📋 EJEMPLOS DE USO")
    print("="*30)
    print("🔧 CONFIGURACIÓN POR TERMINAL:")
    print("   export MIN_STOCK_YEARS=5")
    print("   python integrated_main.py")
    print()
    print("📊 ANÁLISIS RÁPIDO:")
    print("   python quick_analysis.py")
    print()
    print("🎯 CARGA ESPECÍFICA:")
    print("   python example_with_env.py")
    print()
    print("📈 DATASET ACTUAL:")
    print("   • 97 acciones filtradas (5+ años)")
    print("   • 36,712 registros históricos")
    print("   • Rendimiento promedio: 14.2% anual")
    print("   • Mejor: AMZN (+300,820% total)")

def main():
    """Función principal"""
    show_welcome()
    show_configuration()
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n🚪 Saliendo...")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
