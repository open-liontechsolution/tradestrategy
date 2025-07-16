#!/usr/bin/env python3
"""
Script para cargar datos históricos de todas las acciones obtenidas dinámicamente
"""

import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import Dict, List, Optional, Tuple
import warnings
from config import load_dynamic_stocks_data, YFINANCE_CONFIG

warnings.filterwarnings('ignore')

class DataLoader:
    """
    Cargador de datos históricos para acciones obtenidas dinámicamente
    """
    
    def __init__(self, data_dir: str = "historical_data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Configuración
        self.max_workers = YFINANCE_CONFIG.get('max_workers', 10)
        self.retry_attempts = YFINANCE_CONFIG.get('retry_attempts', 3)
        self.timeout = YFINANCE_CONFIG.get('timeout', 10)
        
        # Configuración de filtro por años mínimos
        self.min_years = int(os.getenv('MIN_STOCK_YEARS', '5'))  # Por defecto 5 años
        self.min_date = datetime.now() - timedelta(days=self.min_years * 365)
        
        # Estadísticas
        self.stats = {
            'successful': 0,
            'failed': 0,
            'errors': [],
            'start_time': None,
            'end_time': None
        }
    
    def ensure_data_directory(self):
        """Crear directorio de datos históricos si no existe"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def check_stock_min_history(self, symbol: str) -> bool:
        """Verificar si una acción tiene el histórico mínimo requerido"""
        try:
            ticker = yf.Ticker(symbol)
            # Obtener solo los últimos 30 días para verificación rápida
            recent_data = ticker.history(period="1mo", timeout=5)
            
            if recent_data.empty:
                return False
            
            # Obtener información básica de la acción
            info = ticker.info
            
            # Verificar fecha de primer trading (si está disponible)
            first_trade_date = info.get('firstTradeDateEpochUtc')
            if first_trade_date:
                first_date = datetime.fromtimestamp(first_trade_date)
                return first_date <= self.min_date
            
            # Si no hay info de primera fecha, intentar obtener datos históricos
            # para verificar si tiene suficiente historia
            test_period = f"{self.min_years}y"
            test_data = ticker.history(period=test_period, timeout=5)
            
            if not test_data.empty:
                # Convertir a datetime naive para comparación
                oldest_date = test_data.index.min()
                if hasattr(oldest_date, 'tz_localize'):
                    oldest_date = oldest_date.tz_localize(None)
                elif hasattr(oldest_date, 'replace'):
                    oldest_date = oldest_date.replace(tzinfo=None)
                
                oldest_date = oldest_date.to_pydatetime() if hasattr(oldest_date, 'to_pydatetime') else oldest_date
                required_date = datetime.now() - timedelta(days=self.min_years * 365)
                return oldest_date <= required_date
            
            return False
            
        except Exception as e:
            print(f"  ⚠️ Error verificando histórico de {symbol}: {e}")
            return False
    
    def download_stock_data(self, symbol: str, period: str = "max", interval: str = "1wk") -> Optional[pd.DataFrame]:
        """
        Descargar datos históricos para una acción específica
        Por defecto usa 'max' para obtener todo el histórico disponible
        """
        for attempt in range(self.retry_attempts):
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period, interval=interval, timeout=self.timeout)
                
                if not data.empty:
                    # Agregar información del símbolo
                    data['Symbol'] = symbol
                    return data
                
            except Exception as e:
                if attempt == self.retry_attempts - 1:  # Último intento
                    error_msg = f"Error descargando {symbol}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"  ❌ {error_msg}")
                else:
                    time.sleep(1)  # Pausa antes del retry
        
        return None
    
    def download_batch_data(self, symbols: List[str], period: str = "max", interval: str = "1wk", filter_by_years: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Descargar datos de múltiples acciones en paralelo
        """
        print(f"📊 Descargando datos históricos para {len(symbols)} acciones...")
        print(f"🔧 Configuración: período={period}, intervalo={interval}, workers={self.max_workers}")
        
        if filter_by_years:
            print(f"⚙️ Filtrando acciones con mínimo {self.min_years} años de historia...")
            
            # Filtrar acciones por años mínimos
            filtered_symbols = []
            print(f"🔍 Verificando historial de {len(symbols)} acciones...")
            
            for i, symbol in enumerate(symbols, 1):
                if self.check_stock_min_history(symbol):
                    filtered_symbols.append(symbol)
                    print(f"  ✅ {symbol} - Histórico válido ({i}/{len(symbols)})")
                else:
                    print(f"  ❌ {symbol} - Histórico insuficiente ({i}/{len(symbols)})")
                
                # Mostrar progreso cada 20 acciones
                if i % 20 == 0:
                    print(f"  📈 Progreso verificación: {i}/{len(symbols)} ({len(filtered_symbols)} válidas)")
            
            symbols = filtered_symbols
            print(f"✅ Filtrado completado: {len(symbols)} acciones válidas de {len(symbols)} originales")
            
            if not symbols:
                print("❌ No hay acciones que cumplan el criterio de años mínimos")
                return {}
        
        self.stats['start_time'] = datetime.now()
        successful_data = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Enviar todas las tareas
            future_to_symbol = {
                executor.submit(self.download_stock_data, symbol, period, interval): symbol 
                for symbol in symbols
            }
            
            # Procesar resultados
            for i, future in enumerate(as_completed(future_to_symbol), 1):
                symbol = future_to_symbol[future]
                
                try:
                    data = future.result()
                    
                    if data is not None:
                        successful_data[symbol] = data
                        self.stats['successful'] += 1
                        print(f"  ✅ {symbol} ({i}/{len(symbols)})")
                    else:
                        self.stats['failed'] += 1
                        print(f"  ⚠️ {symbol} - Sin datos ({i}/{len(symbols)})")
                        
                except Exception as e:
                    self.stats['failed'] += 1
                    error_msg = f"Error procesando {symbol}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"  ❌ {symbol} - {error_msg} ({i}/{len(symbols)})")
                
                # Mostrar progreso cada 50 acciones
                if i % 50 == 0:
                    success_rate = (self.stats['successful'] / i) * 100
                    print(f"  📈 Progreso: {i}/{len(symbols)} ({success_rate:.1f}% éxito)")
        
        self.stats['end_time'] = datetime.now()
        return successful_data
    
    def save_individual_data(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """
        Guardar datos individuales de cada acción
        """
        print(f"\n💾 Guardando datos individuales...")
        
        individual_dir = os.path.join(self.data_dir, "individual")
        if not os.path.exists(individual_dir):
            os.makedirs(individual_dir)
        
        saved_files = {}
        
        for symbol, data in data_dict.items():
            try:
                # Limpiar símbolo para nombre de archivo
                clean_symbol = symbol.replace('.', '_').replace('^', '').replace('/', '_')
                filename = f"{clean_symbol}_{self.timestamp}.csv"
                filepath = os.path.join(individual_dir, filename)
                
                data.to_csv(filepath)
                saved_files[symbol] = filepath
                
            except Exception as e:
                print(f"  ❌ Error guardando {symbol}: {e}")
        
        print(f"  ✅ Guardados {len(saved_files)} archivos individuales")
        return saved_files
    
    def create_combined_dataset(self, data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Crear dataset combinado con todas las acciones
        """
        print(f"\n🔗 Creando dataset combinado...")
        
        all_data = []
        
        for symbol, data in data_dict.items():
            # Agregar información adicional
            data_copy = data.copy()
            data_copy['Symbol'] = symbol
            data_copy['Date'] = data_copy.index
            
            # Obtener información adicional del stock
            stock_info = self.get_stock_info(symbol)
            if stock_info:
                for key, value in stock_info.items():
                    data_copy[key] = value
            
            all_data.append(data_copy)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"  ✅ Dataset combinado creado: {len(combined_df)} registros")
            return combined_df
        
        return pd.DataFrame()
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Obtener información adicional de una acción desde los datos dinámicos
        """
        try:
            dynamic_data = load_dynamic_stocks_data()
            
            for stock in dynamic_data:
                if stock['symbol'] == symbol:
                    return {
                        'Market': stock.get('market', 'Unknown'),
                        'Sector': stock.get('sector', 'Unknown'),
                        'Industry': stock.get('industry', 'Unknown'),
                        'Country': stock.get('country', 'Unknown'),
                        'Exchange': stock.get('exchange', 'Unknown'),
                        'Source': stock.get('source', 'Unknown')
                    }
        except Exception:
            pass
        
        return None
    
    def save_combined_data(self, combined_df: pd.DataFrame) -> str:
        """
        Guardar dataset combinado
        """
        if combined_df.empty:
            return ""
        
        filename = f"combined_historical_data_{self.timestamp}.csv"
        filepath = os.path.join(self.data_dir, filename)
        
        combined_df.to_csv(filepath, index=False)
        print(f"  ✅ Dataset combinado guardado: {filepath}")
        
        return filepath
    
    def generate_summary_report(self, data_dict: Dict[str, pd.DataFrame]) -> str:
        """
        Generar reporte resumen
        """
        print(f"\n📋 Generando reporte resumen...")
        
        duration = self.stats['end_time'] - self.stats['start_time'] if self.stats['end_time'] else timedelta(0)
        
        report = f"""
REPORTE DE CARGA DE DATOS HISTÓRICOS
====================================

Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duración: {duration}

ESTADÍSTICAS:
- Acciones procesadas: {self.stats['successful'] + self.stats['failed']}
- Descargas exitosas: {self.stats['successful']}
- Descargas fallidas: {self.stats['failed']}
- Tasa de éxito: {(self.stats['successful'] / (self.stats['successful'] + self.stats['failed']) * 100):.1f}%

ANÁLISIS DE DATOS:
"""
        
        if data_dict:
            # Estadísticas por mercado
            market_stats = {}
            sector_stats = {}
            
            for symbol in data_dict.keys():
                stock_info = self.get_stock_info(symbol)
                if stock_info:
                    market = stock_info.get('Market', 'Unknown')
                    sector = stock_info.get('Sector', 'Unknown')
                    
                    market_stats[market] = market_stats.get(market, 0) + 1
                    sector_stats[sector] = sector_stats.get(sector, 0) + 1
            
            report += "\nAcciones exitosas por mercado:\n"
            for market, count in sorted(market_stats.items()):
                report += f"- {market}: {count} acciones\n"
            
            report += "\nAcciones exitosas por sector:\n"
            for sector, count in sorted(sector_stats.items()):
                if count > 5:  # Solo mostrar sectores con más de 5 acciones
                    report += f"- {sector}: {count} acciones\n"
        
        if self.stats['errors']:
            report += f"\nERRORES ({len(self.stats['errors'])}):\n"
            for error in self.stats['errors'][:10]:  # Mostrar solo los primeros 10 errores
                report += f"- {error}\n"
            
            if len(self.stats['errors']) > 10:
                report += f"... y {len(self.stats['errors']) - 10} errores más\n"
        
        report += "\n" + "="*50 + "\n"
        
        # Guardar reporte
        report_file = os.path.join(self.data_dir, f"load_report_{self.timestamp}.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"📄 Reporte guardado: {report_file}")
        
        return report_file
    
    def load_all_historical_data(self, period: str = "max", interval: str = "1wk", max_stocks: Optional[int] = None, filter_by_years: bool = True) -> Tuple[Dict[str, pd.DataFrame], str]:
        """
        Cargar datos históricos de todas las acciones disponibles
        
        Args:
            period: Período de datos ('max' para todo el histórico)
            interval: Intervalo de datos ('1d', '1wk', '1mo')
            max_stocks: Límite máximo de acciones (None para todas)
            filter_by_years: Si filtrar por años mínimos de historia
        """
        print("🚀 Iniciando carga masiva de datos históricos...")
        print("📊 Obteniendo listado de acciones dinámicas...\n")
        
        # Cargar listado de acciones
        dynamic_stocks = load_dynamic_stocks_data()
        if not dynamic_stocks:
            print("❌ No se pudieron cargar las acciones dinámicas")
            return {}, ""
        
        symbols = [stock['symbol'] for stock in dynamic_stocks]
        
        if max_stocks:
            symbols = symbols[:max_stocks]
            print(f"🔢 Limitando a {max_stocks} acciones para prueba")
        
        print(f"📈 Total de acciones a procesar: {len(symbols)}")
        
        # Mostrar configuración de filtrado
        if filter_by_years:
            print(f"⚙️ Filtro activado: Mínimo {self.min_years} años de historia")
            print(f"📅 Fecha mínima requerida: {self.min_date.strftime('%Y-%m-%d')}")
        else:
            print("⚠️ Filtro desactivado: Se procesarán todas las acciones")
        
        # Descargar datos
        data_dict = self.download_batch_data(symbols, period, interval, filter_by_years)
        
        if not data_dict:
            print("❌ No se pudieron descargar datos")
            return {}, ""
        
        # Guardar datos individuales
        self.save_individual_data(data_dict)
        
        # Crear y guardar dataset combinado
        combined_df = self.create_combined_dataset(data_dict)
        combined_file = self.save_combined_data(combined_df)
        
        # Generar reporte
        report_file = self.generate_summary_report(data_dict)
        
        print(f"\n🎉 ¡Carga completada!")
        print(f"✅ Datos descargados: {len(data_dict)} acciones")
        print(f"💾 Archivos generados en: {self.data_dir}/")
        
        return data_dict, combined_file


def main():
    """Función principal"""
    
    loader = DataLoader()
    
    # Mostrar configuración actual
    print("⚙️ CONFIGURACIÓN ACTUAL:")
    print(f"📅 Años mínimos requeridos: {loader.min_years}")
    print(f"📊 Fecha mínima: {loader.min_date.strftime('%Y-%m-%d')}")
    print(f"🔧 Variable de entorno MIN_STOCK_YEARS: {os.getenv('MIN_STOCK_YEARS', 'No definida (usa 5 por defecto)')}")
    print()
    
    # Realizar una carga de prueba con filtrado
    print("🧪 Realizando carga de prueba con histórico completo y filtrado...")
    data_dict, combined_file = loader.load_all_historical_data(
        period="max",       # Histórico completo
        interval="1wk",     # Datos semanales
        max_stocks=20,      # Límite para prueba rápida
        filter_by_years=True # Activar filtro
    )
    
    if data_dict:
        print(f"\n✅ Prueba exitosa: {len(data_dict)} acciones cargadas")
        print(f"📄 Archivo combinado: {combined_file}")
        print("\n🚀 Para cargar TODAS las acciones, ejecuta:")
        print("loader.load_all_historical_data(period='1y', interval='1wk', max_stocks=None)")
    else:
        print("❌ Error en la carga de prueba")


if __name__ == "__main__":
    main()
