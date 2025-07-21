#!/usr/bin/env python3
"""
Test script para verificar la funcionalidad básica del Breakout Analyzer
"""

import sys
from pathlib import Path

# Añadir el directorio actual al path para importar el módulo
sys.path.append(str(Path(__file__).parent))

from breakout_analyzer import BreakoutAnalyzer

def test_database_connection():
    """Prueba la conexión a la base de datos."""
    print("Probando conexión a la base de datos...")
    analyzer = BreakoutAnalyzer()
    
    if analyzer.connect_to_database():
        print("✓ Conexión exitosa")
        return True
    else:
        print("✗ Error de conexión")
        return False

def test_symbol_retrieval():
    """Prueba la obtención de símbolos."""
    print("Probando obtención de símbolos...")
    analyzer = BreakoutAnalyzer()
    
    if not analyzer.connect_to_database():
        print("✗ No se pudo conectar a la base de datos")
        return False
    
    symbols = analyzer.get_all_symbols()
    if symbols:
        print(f"✓ Se encontraron {len(symbols)} símbolos")
        print(f"Primeros 5 símbolos: {symbols[:5]}")
        return True
    else:
        print("✗ No se encontraron símbolos")
        return False

def test_table_creation():
    """Prueba la creación de la tabla de candidatos."""
    print("Probando creación de tabla...")
    analyzer = BreakoutAnalyzer()
    
    if not analyzer.connect_to_database():
        print("✗ No se pudo conectar a la base de datos")
        return False
    
    try:
        analyzer.create_strategy_table()
        print("✓ Tabla strategy_candidates creada/verificada")
        return True
    except Exception as e:
        print(f"✗ Error creando tabla: {e}")
        return False

def test_single_symbol_analysis():
    """Prueba el análisis de un símbolo específico."""
    print("Probando análisis de símbolo individual...")
    analyzer = BreakoutAnalyzer()
    
    if not analyzer.connect_to_database():
        print("✗ No se pudo conectar a la base de datos")
        return False
    
    # Obtener un símbolo para probar
    symbols = analyzer.get_all_symbols()
    if not symbols:
        print("✗ No hay símbolos para probar")
        return False
    
    test_symbol = symbols[0]  # Usar el primer símbolo
    print(f"Probando con símbolo: {test_symbol}")
    
    # Obtener datos del símbolo
    df = analyzer.get_symbol_data(test_symbol)
    if df is None or df.empty:
        print(f"✗ No se pudieron obtener datos para {test_symbol}")
        return False
    
    print(f"✓ Datos obtenidos: {len(df)} registros desde {df['date'].min()} hasta {df['date'].max()}")
    
    # Analizar patrón
    analysis_result = analyzer.analyze_symbol_pattern(test_symbol, df)
    if analysis_result:
        print(f"✓ Análisis completado para {test_symbol}")
        print(f"  - Años de datos: {analysis_result['years_of_data']:.2f}")
        print(f"  - Máximo histórico: ${analysis_result['historical_high']:.2f}")
        print(f"  - Precio actual: ${analysis_result['current_price']:.2f}")
        print(f"  - Distancia a resistencia: {analysis_result['resistance_distance_percent']:.2f}%")
        print(f"  - Es candidato válido: {analysis_result['is_valid_candidate']}")
        return True
    else:
        print(f"✗ No se pudo analizar el patrón para {test_symbol}")
        return False

def main():
    """Ejecuta todas las pruebas."""
    print("="*60)
    print("PRUEBAS DEL BREAKOUT ANALYZER")
    print("="*60)
    
    tests = [
        ("Conexión a base de datos", test_database_connection),
        ("Obtención de símbolos", test_symbol_retrieval),
        ("Creación de tabla", test_table_creation),
        ("Análisis de símbolo", test_single_symbol_analysis),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ Error inesperado: {e}")
    
    print("\n" + "="*60)
    print(f"RESULTADO: {passed}/{total} pruebas pasaron")
    print("="*60)
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El analyzer está listo para usar.")
        return True
    else:
        print("❌ Algunas pruebas fallaron. Revisa la configuración.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
