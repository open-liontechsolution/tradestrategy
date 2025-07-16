#!/usr/bin/env python3
"""
Ejemplo de uso del analizador de acciones para estrategias de trading
"""

from stock_analyzer import StockAnalyzer
import time

def main():
    """
    Función principal para demostrar el uso del analizador
    """
    print("=== Trading Strategy Analyzer ===")
    print("Iniciando análisis de acciones...\n")
    
    # Crear instancia del analizador
    analyzer = StockAnalyzer()
    
    # 1. Mostrar lista de acciones populares
    print("1. Acciones populares disponibles:")
    popular_stocks = analyzer.get_popular_stocks()
    print(f"Total de acciones: {len(popular_stocks)}")
    print("Primeras 20 acciones:", popular_stocks[:20])
    print()
    
    # 2. Obtener información de algunas acciones específicas
    print("2. Información de acciones específicas:")
    test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    
    for symbol in test_symbols:
        info = analyzer.get_stock_info(symbol)
        if info:
            print(f"{symbol}: {info['name']} | Sector: {info['sector']} | Precio: ${info['current_price']}")
        time.sleep(0.5)  # Pausa para evitar límites de API
    
    print()
    
    # 3. Obtener datos históricos y generar gráficos
    print("3. Análisis de datos históricos:")
    
    # Análisis de Apple (AAPL)
    symbol = "AAPL"
    print(f"Analizando {symbol}...")
    
    # Obtener datos semanales del último año
    data = analyzer.get_stock_data(symbol, period="1y", interval="1wk")
    
    if data is not None:
        # Mostrar estadísticas básicas
        stats = analyzer.get_basic_stats(symbol, data)
        analyzer.print_stats(stats)
        
        # Generar gráfico estático
        print(f"\nGenerando gráfico para {symbol}...")
        analyzer.plot_stock_data(symbol, data, save_path=f"{symbol}_analysis.png")
        
        # Generar gráfico interactivo
        print(f"Generando gráfico interactivo para {symbol}...")
        analyzer.plot_interactive_chart(symbol, data)
    
    print()
    
    # 4. Comparación de múltiples acciones
    print("4. Comparación de acciones tecnológicas:")
    tech_stocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    analyzer.compare_stocks(tech_stocks, period="6mo", interval="1wk")
    
    print()
    
    # 5. Análisis mensual para estrategias de largo plazo
    print("5. Análisis mensual (datos más estables):")
    monthly_data = analyzer.get_stock_data("AAPL", period="2y", interval="1mo")
    
    if monthly_data is not None:
        monthly_stats = analyzer.get_basic_stats("AAPL", monthly_data)
        analyzer.print_stats(monthly_stats)
        
        print("\nGenerando gráfico mensual...")
        analyzer.plot_stock_data("AAPL", monthly_data, save_path="AAPL_monthly.png")
    
    print("\n=== Análisis completado ===")
    print("Los gráficos han sido guardados como archivos PNG")
    print("Para ver gráficos interactivos, ejecuta el script en un entorno con soporte para Plotly")

if __name__ == "__main__":
    main()
