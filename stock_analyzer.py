import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import warnings

warnings.filterwarnings('ignore')

class StockAnalyzer:
    """
    Analizador de acciones para estrategias de trading
    """
    
    def __init__(self):
        """Inicializar el analizador"""
        self.popular_stocks = self._get_popular_stocks_list()
        
    def _get_popular_stocks_list(self) -> List[str]:
        """
        Lista de acciones populares para trading
        """
        return [
            # Tecnología
            "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "TSLA", "NVDA", "CRM", "ORCL",
            # Financiero
            "JPM", "BAC", "WFC", "GS", "C", "MS", "AXP", "V", "MA", "PYPL",
            # Salud
            "JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "TMO", "ABT", "DHR", "BMY",
            # Consumo
            "PG", "KO", "PEP", "WMT", "HD", "MCD", "NKE", "COST", "SBUX", "TGT",
            # Energía
            "XOM", "CVX", "COP", "EOG", "SLB", "PSX", "VLO", "OXY", "KMI", "WMB",
            # Industriales
            "GE", "BA", "CAT", "HON", "MMM", "UPS", "LMT", "RTX", "DE", "FDX",
            # Telecomunicaciones
            "T", "VZ", "TMUS", "CHTR", "CMCSA", "DIS", "NFLX", "ROKU", "SPOT", "TWTR",
            # Retail
            "AMZN", "BABA", "JD", "SHOP", "ETSY", "EBAY", "MELI", "SE", "PINS", "SNAP"
        ]
    
    def get_popular_stocks(self) -> List[str]:
        """
        Obtener lista de acciones populares para trading
        """
        return self.popular_stocks
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        Obtener información básica de una acción
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'current_price': info.get('currentPrice', 'N/A'),
                'currency': info.get('currency', 'USD')
            }
        except Exception as e:
            print(f"Error obteniendo información de {symbol}: {e}")
            return None
    
    def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1wk") -> pd.DataFrame:
        """
        Obtener datos históricos de una acción
        
        Args:
            symbol: Símbolo de la acción (ej: "AAPL")
            period: Período de tiempo ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
            interval: Intervalo de datos ("1d", "1wk", "1mo")
        """
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval=interval)
            
            if data.empty:
                print(f"No se encontraron datos para {symbol}")
                return None
                
            # Agregar columnas útiles
            data['Symbol'] = symbol
            data['Returns'] = data['Close'].pct_change()
            data['Volatility'] = data['Returns'].rolling(window=4).std()
            data['MA_4'] = data['Close'].rolling(window=4).mean()
            data['MA_12'] = data['Close'].rolling(window=12).mean()
            
            return data
            
        except Exception as e:
            print(f"Error obteniendo datos de {symbol}: {e}")
            return None
    
    def get_multiple_stocks_data(self, symbols: List[str], period: str = "1y", interval: str = "1wk") -> Dict[str, pd.DataFrame]:
        """
        Obtener datos de múltiples acciones
        """
        results = {}
        for symbol in symbols:
            data = self.get_stock_data(symbol, period, interval)
            if data is not None:
                results[symbol] = data
            else:
                print(f"No se pudieron obtener datos para {symbol}")
        return results
    
    def plot_stock_data(self, symbol: str, data: pd.DataFrame, save_path: Optional[str] = None):
        """
        Graficar datos de una acción usando matplotlib
        """
        if data is None or data.empty:
            print(f"No hay datos para graficar de {symbol}")
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Análisis de {symbol}', fontsize=16)
        
        # Gráfico de precio
        axes[0, 0].plot(data.index, data['Close'], label='Precio de Cierre', color='blue')
        axes[0, 0].plot(data.index, data['MA_4'], label='MA 4 períodos', color='red', alpha=0.7)
        axes[0, 0].plot(data.index, data['MA_12'], label='MA 12 períodos', color='green', alpha=0.7)
        axes[0, 0].set_title('Precio de Cierre y Medias Móviles')
        axes[0, 0].legend()
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Gráfico de volumen
        axes[0, 1].bar(data.index, data['Volume'], alpha=0.7, color='orange')
        axes[0, 1].set_title('Volumen de Transacciones')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Gráfico de retornos
        axes[1, 0].plot(data.index, data['Returns'], label='Retornos', color='purple', alpha=0.7)
        axes[1, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[1, 0].set_title('Retornos Semanales')
        axes[1, 0].legend()
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Gráfico de volatilidad
        axes[1, 1].plot(data.index, data['Volatility'], label='Volatilidad', color='red')
        axes[1, 1].set_title('Volatilidad (4 períodos)')
        axes[1, 1].legend()
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_interactive_chart(self, symbol: str, data: pd.DataFrame):
        """
        Crear gráfico interactivo con Plotly
        """
        if data is None or data.empty:
            print(f"No hay datos para graficar de {symbol}")
            return
            
        fig = go.Figure()
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=f'{symbol} Precio'
        ))
        
        # Medias móviles
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MA_4'],
            mode='lines',
            name='MA 4 períodos',
            line=dict(color='red', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MA_12'],
            mode='lines',
            name='MA 12 períodos',
            line=dict(color='blue', width=1)
        ))
        
        fig.update_layout(
            title=f'Análisis Interactivo de {symbol}',
            xaxis_title='Fecha',
            yaxis_title='Precio ($)',
            xaxis_rangeslider_visible=False,
            height=600
        )
        
        fig.show()
    
    def compare_stocks(self, symbols: List[str], period: str = "1y", interval: str = "1wk"):
        """
        Comparar múltiples acciones
        """
        data_dict = self.get_multiple_stocks_data(symbols, period, interval)
        
        if not data_dict:
            print("No se pudieron obtener datos para comparar")
            return
        
        plt.figure(figsize=(12, 8))
        
        for symbol, data in data_dict.items():
            if data is not None and not data.empty:
                # Normalizar precios para comparación
                normalized_price = (data['Close'] / data['Close'].iloc[0]) * 100
                plt.plot(data.index, normalized_price, label=symbol, linewidth=2)
        
        plt.title('Comparación de Rendimiento de Acciones (Normalizado)')
        plt.xlabel('Fecha')
        plt.ylabel('Rendimiento Normalizado (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def get_basic_stats(self, symbol: str, data: pd.DataFrame) -> Dict:
        """
        Obtener estadísticas básicas de una acción
        """
        if data is None or data.empty:
            return None
            
        stats = {
            'symbol': symbol,
            'period_start': data.index[0].strftime('%Y-%m-%d'),
            'period_end': data.index[-1].strftime('%Y-%m-%d'),
            'initial_price': round(data['Close'].iloc[0], 2),
            'final_price': round(data['Close'].iloc[-1], 2),
            'total_return': round(((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100, 2),
            'max_price': round(data['Close'].max(), 2),
            'min_price': round(data['Close'].min(), 2),
            'average_price': round(data['Close'].mean(), 2),
            'volatility': round(data['Returns'].std() * 100, 2),
            'average_volume': int(data['Volume'].mean())
        }
        
        return stats
    
    def print_stats(self, stats: Dict):
        """
        Imprimir estadísticas de forma legible
        """
        if stats is None:
            print("No hay estadísticas disponibles")
            return
            
        print(f"\n=== Estadísticas de {stats['symbol']} ===")
        print(f"Período: {stats['period_start']} a {stats['period_end']}")
        print(f"Precio inicial: ${stats['initial_price']}")
        print(f"Precio final: ${stats['final_price']}")
        print(f"Retorno total: {stats['total_return']}%")
        print(f"Precio máximo: ${stats['max_price']}")
        print(f"Precio mínimo: ${stats['min_price']}")
        print(f"Precio promedio: ${stats['average_price']}")
        print(f"Volatilidad: {stats['volatility']}%")
        print(f"Volumen promedio: {stats['average_volume']:,}")
