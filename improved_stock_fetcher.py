#!/usr/bin/env python3
"""
Script MEJORADO que obtiene listados de acciones usando múltiples fuentes confiables
Combina web scraping con APIs confiables como yfinance
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os
from typing import List, Dict, Optional
import re
import warnings
import yfinance as yf

warnings.filterwarnings('ignore')

class ImprovedStockFetcher:
    """
    Obtiene listados de acciones usando fuentes múltiples y confiables
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Configurar session con headers realistas
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Símbolos conocidos para obtener componentes via yfinance
        self.known_indices = {
            'S&P500': '^GSPC',
            'NASDAQ100': '^NDX', 
            'IBEX35': '^IBEX',
            'DAX': '^GDAXI',
            'CAC40': '^FCHI',
            'FTSE100': '^FTSE'
        }
    
    def ensure_data_directory(self):
        """Crear directorio de datos si no existe"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def fetch_sp500_dynamic(self) -> List[Dict]:
        """
        Obtener S&P 500 dinámicamente desde Wikipedia (funciona bien)
        """
        print("🔍 Consultando S&P 500 dinámicamente desde Wikipedia...")
        
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # Usar pandas para leer las tablas de Wikipedia
                tables = pd.read_html(response.content)
                
                if tables and len(tables) > 0:
                    df = tables[0]  # Primera tabla contiene las compañías
                    
                    stocks = []
                    print(f"  📊 Procesando {len(df)} filas de la tabla...")
                    
                    for _, row in df.iterrows():
                        try:
                            symbol = str(row.get('Symbol', '')).strip()
                            name = str(row.get('Security', '')).strip()
                            sector = str(row.get('GICS Sector', '')).strip()
                            industry = str(row.get('GICS Sub-Industry', '')).strip()
                            
                            if symbol and name and symbol != 'nan':
                                stocks.append({
                                    'symbol': symbol,
                                    'name': name,
                                    'sector': sector if sector != 'nan' else 'Unknown',
                                    'industry': industry if industry != 'nan' else 'Unknown',
                                    'market': 'US_SP500',
                                    'exchange': 'NYSE/NASDAQ',
                                    'country': 'US',
                                    'source': 'Wikipedia_Dynamic'
                                })
                        except Exception:
                            continue
                    
                    print(f"  ✅ Obtenidas {len(stocks)} acciones del S&P 500")
                    return stocks
                    
        except Exception as e:
            print(f"  ❌ Error obteniendo S&P 500: {e}")
        
        return []
    
    def fetch_nasdaq100_dynamic(self) -> List[Dict]:
        """
        Obtener NASDAQ 100 usando múltiples fuentes
        """
        print("🔍 Consultando NASDAQ 100 dinámicamente...")
        
        # Método 1: Intentar web scraping
        stocks = self._try_slickcharts_nasdaq()
        if stocks:
            return stocks
        
        # Método 2: Lista conocida de NASDAQ 100 como fallback
        return self._get_nasdaq100_fallback()
    
    def _try_slickcharts_nasdaq(self) -> List[Dict]:
        """Intentar obtener NASDAQ 100 desde SlickCharts"""
        try:
            print("  🔍 Intentando SlickCharts...")
            url = "https://www.slickcharts.com/nasdaq100"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar tabla con datos
                table = soup.find('table')
                if table:
                    stocks = []
                    rows = table.find_all('tr')[1:]  # Saltar header
                    
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 3:
                            try:
                                symbol = cols[1].text.strip()
                                name = cols[2].text.strip()
                                
                                if symbol and name:
                                    stocks.append({
                                        'symbol': symbol,
                                        'name': name,
                                        'sector': 'Unknown',
                                        'industry': 'Unknown',
                                        'market': 'US_NASDAQ100',
                                        'exchange': 'NASDAQ',
                                        'country': 'US',
                                        'source': 'SlickCharts_Dynamic'
                                    })
                            except Exception:
                                continue
                    
                    if stocks:
                        print(f"  ✅ Obtenidas {len(stocks)} acciones desde SlickCharts")
                        return stocks
                        
        except Exception as e:
            print(f"  ⚠ Error con SlickCharts: {e}")
        
        return []
    
    def _get_nasdaq100_fallback(self) -> List[Dict]:
        """Lista de fallback con las principales acciones del NASDAQ 100"""
        print("  🔄 Usando lista de fallback para NASDAQ 100...")
        
        # Top acciones del NASDAQ 100 más conocidas
        nasdaq_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc. Class A'},
            {'symbol': 'GOOG', 'name': 'Alphabet Inc. Class C'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
            {'symbol': 'NFLX', 'name': 'Netflix Inc.'},
            {'symbol': 'ADBE', 'name': 'Adobe Inc.'},
            {'symbol': 'PYPL', 'name': 'PayPal Holdings Inc.'},
            {'symbol': 'INTC', 'name': 'Intel Corporation'},
            {'symbol': 'CMCSA', 'name': 'Comcast Corporation'},
            {'symbol': 'CSCO', 'name': 'Cisco Systems Inc.'},
            {'symbol': 'AVGO', 'name': 'Broadcom Inc.'},
            {'symbol': 'TXN', 'name': 'Texas Instruments Incorporated'},
            {'symbol': 'QCOM', 'name': 'QUALCOMM Incorporated'},
            {'symbol': 'COST', 'name': 'Costco Wholesale Corporation'},
            {'symbol': 'AMGN', 'name': 'Amgen Inc.'},
            {'symbol': 'TMUS', 'name': 'T-Mobile US Inc.'},
        ]
        
        stocks = []
        for stock in nasdaq_stocks:
            stocks.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'sector': 'Technology',
                'industry': 'Unknown',
                'market': 'US_NASDAQ100',
                'exchange': 'NASDAQ',
                'country': 'US',
                'source': 'Fallback_List'
            })
        
        print(f"  ✅ Obtenidas {len(stocks)} acciones desde lista de fallback")
        return stocks
    
    def fetch_ibex35_improved(self) -> List[Dict]:
        """
        Obtener IBEX 35 con métodos mejorados
        """
        print("🔍 Consultando IBEX 35 con métodos mejorados...")
        
        # Método 1: Intentar Wikipedia española
        stocks = self._try_wikipedia_ibex()
        if stocks:
            return stocks
        
        # Método 2: Lista de fallback
        return self._get_ibex35_fallback()
    
    def _try_wikipedia_ibex(self) -> List[Dict]:
        """Intentar obtener IBEX 35 desde Wikipedia en español"""
        try:
            print("  🔍 Intentando Wikipedia española...")
            url = "https://es.wikipedia.org/wiki/IBEX_35"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # Intentar usar pandas para leer tablas
                try:
                    tables = pd.read_html(response.content)
                    
                    for table in tables:
                        if len(table.columns) >= 2:
                            stocks = []
                            
                            for _, row in table.iterrows():
                                try:
                                    # Buscar columnas que contengan nombres de empresas
                                    for col in table.columns:
                                        value = str(row[col]).strip()
                                        
                                        # Si parece un nombre de empresa (contiene letras y espacios)
                                        if len(value) > 3 and any(c.isalpha() for c in value) and value != 'nan':
                                            # Generar símbolo aproximado
                                            symbol = self._generate_spanish_symbol(value)
                                            
                                            if symbol:
                                                stocks.append({
                                                    'symbol': symbol,
                                                    'name': value,
                                                    'sector': 'Unknown',
                                                    'industry': 'Unknown',
                                                    'market': 'ES_IBEX35',
                                                    'exchange': 'BME',
                                                    'country': 'ES',
                                                    'source': 'Wikipedia_ES_Dynamic'
                                                })
                                                break
                                except Exception:
                                    continue
                            
                            if len(stocks) >= 10:  # Si encontramos suficientes acciones
                                print(f"  ✅ Obtenidas {len(stocks)} acciones desde Wikipedia ES")
                                return stocks[:35]  # Limitamos a 35
                                
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"  ⚠ Error con Wikipedia ES: {e}")
        
        return []
    
    def _generate_spanish_symbol(self, company_name: str) -> str:
        """Generar símbolo bursátil aproximado para empresa española"""
        # Mapeo conocido de empresas españolas
        known_symbols = {
            'Banco Santander': 'SAN.MC',
            'BBVA': 'BBVA.MC', 
            'Iberdrola': 'IBE.MC',
            'Telefónica': 'TEF.MC',
            'Inditex': 'ITX.MC',
            'Repsol': 'REP.MC',
            'Banco Sabadell': 'SAB.MC',
            'Endesa': 'ELE.MC',
            'Naturgy': 'NTGY.MC',
            'Ferrovial': 'FER.MC',
            'ACS': 'ACS.MC',
            'CaixaBank': 'CABK.MC',
            'Amadeus': 'AMS.MC',
            'Grifols': 'GRF.MC',
            'IAG': 'IAG.MC'
        }
        
        for company, symbol in known_symbols.items():
            if company.lower() in company_name.lower():
                return symbol
        
        # Si no está en el mapeo, generar símbolo genérico
        clean_name = re.sub(r'[^A-Za-z]', '', company_name)
        if len(clean_name) >= 3:
            return clean_name[:3].upper() + '.MC'
        
        return None
    
    def _get_ibex35_fallback(self) -> List[Dict]:
        """Lista de fallback con las principales acciones del IBEX 35"""
        print("  🔄 Usando lista de fallback para IBEX 35...")
        
        ibex_stocks = [
            {'symbol': 'SAN.MC', 'name': 'Banco Santander S.A.'},
            {'symbol': 'BBVA.MC', 'name': 'Banco Bilbao Vizcaya Argentaria S.A.'},
            {'symbol': 'IBE.MC', 'name': 'Iberdrola S.A.'},
            {'symbol': 'TEF.MC', 'name': 'Telefónica S.A.'},
            {'symbol': 'ITX.MC', 'name': 'Industria de Diseño Textil S.A.'},
            {'symbol': 'REP.MC', 'name': 'Repsol S.A.'},
            {'symbol': 'CABK.MC', 'name': 'CaixaBank S.A.'},
            {'symbol': 'FER.MC', 'name': 'Ferrovial S.A.'},
            {'symbol': 'ACS.MC', 'name': 'Actividades de Construcción y Servicios S.A.'},
            {'symbol': 'ELE.MC', 'name': 'Endesa S.A.'},
            {'symbol': 'NTGY.MC', 'name': 'Naturgy Energy Group S.A.'},
            {'symbol': 'AMS.MC', 'name': 'Amadeus IT Group S.A.'},
            {'symbol': 'SAB.MC', 'name': 'Banco de Sabadell S.A.'},
            {'symbol': 'IAG.MC', 'name': 'International Consolidated Airlines Group S.A.'},
            {'symbol': 'GRF.MC', 'name': 'Grifols S.A.'},
        ]
        
        stocks = []
        for stock in ibex_stocks:
            stocks.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market': 'ES_IBEX35',
                'exchange': 'BME',
                'country': 'ES',
                'source': 'Fallback_List'
            })
        
        print(f"  ✅ Obtenidas {len(stocks)} acciones desde lista de fallback")
        return stocks
    
    def fetch_european_indices(self) -> List[Dict]:
        """
        Obtener índices europeos con listas de fallback confiables
        """
        print("🔍 Consultando índices europeos con listas mejoradas...")
        
        all_stocks = []
        
        # DAX 40 (Alemania)
        dax_stocks = self._get_dax40_fallback()
        all_stocks.extend(dax_stocks)
        
        # CAC 40 (Francia)  
        cac_stocks = self._get_cac40_fallback()
        all_stocks.extend(cac_stocks)
        
        # FTSE 100 (Reino Unido)
        ftse_stocks = self._get_ftse100_fallback()
        all_stocks.extend(ftse_stocks)
        
        return all_stocks
    
    def _get_dax40_fallback(self) -> List[Dict]:
        """Lista de fallback para DAX 40"""
        print("  🔄 Obteniendo DAX 40 desde lista confiable...")
        
        dax_stocks = [
            {'symbol': 'SAP.DE', 'name': 'SAP SE'},
            {'symbol': 'ASME.DE', 'name': 'ASML Holding N.V.'},
            {'symbol': 'SIE.DE', 'name': 'Siemens AG'},
            {'symbol': 'DTE.DE', 'name': 'Deutsche Telekom AG'},
            {'symbol': 'ALV.DE', 'name': 'Allianz SE'},
            {'symbol': 'MUV2.DE', 'name': 'Munich Re'},
            {'symbol': 'ADS.DE', 'name': 'Adidas AG'},
            {'symbol': 'BAS.DE', 'name': 'BASF SE'},
            {'symbol': 'VOW3.DE', 'name': 'Volkswagen AG'},
            {'symbol': 'BMW.DE', 'name': 'Bayerische Motoren Werke AG'},
        ]
        
        stocks = []
        for stock in dax_stocks:
            stocks.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market': 'DE_DAX40',
                'exchange': 'XETRA',
                'country': 'DE',
                'source': 'Fallback_List'
            })
        
        print(f"  ✅ Obtenidas {len(stocks)} acciones del DAX 40")
        return stocks
    
    def _get_cac40_fallback(self) -> List[Dict]:
        """Lista de fallback para CAC 40"""
        print("  🔄 Obteniendo CAC 40 desde lista confiable...")
        
        cac_stocks = [
            {'symbol': 'MC.PA', 'name': 'LVMH Moët Hennessy Louis Vuitton SE'},
            {'symbol': 'OR.PA', 'name': "L'Oréal S.A."},
            {'symbol': 'ASML.AS', 'name': 'ASML Holding N.V.'},
            {'symbol': 'TTE.PA', 'name': 'TotalEnergies SE'},
            {'symbol': 'SAN.PA', 'name': 'Sanofi'},
            {'symbol': 'BNP.PA', 'name': 'BNP Paribas'},
            {'symbol': 'AIR.PA', 'name': 'Airbus SE'},
            {'symbol': 'EL.PA', 'name': 'EssilorLuxottica'},
            {'symbol': 'RMS.PA', 'name': 'Hermès International'},
            {'symbol': 'CDI.PA', 'name': 'Christian Dior SE'},
        ]
        
        stocks = []
        for stock in cac_stocks:
            stocks.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market': 'FR_CAC40',
                'exchange': 'EPA',
                'country': 'FR',
                'source': 'Fallback_List'
            })
        
        print(f"  ✅ Obtenidas {len(stocks)} acciones del CAC 40")
        return stocks
    
    def _get_ftse100_fallback(self) -> List[Dict]:
        """Lista de fallback para FTSE 100"""
        print("  🔄 Obteniendo FTSE 100 desde lista confiable...")
        
        ftse_stocks = [
            {'symbol': 'SHEL.L', 'name': 'Shell plc'},
            {'symbol': 'AZN.L', 'name': 'AstraZeneca PLC'},
            {'symbol': 'ULVR.L', 'name': 'Unilever PLC'},
            {'symbol': 'BP.L', 'name': 'BP p.l.c.'},
            {'symbol': 'LLOY.L', 'name': 'Lloyds Banking Group plc'},
            {'symbol': 'VOD.L', 'name': 'Vodafone Group Plc'},
            {'symbol': 'GLEN.L', 'name': 'Glencore plc'},
            {'symbol': 'BARC.L', 'name': 'Barclays PLC'},
            {'symbol': 'HSBA.L', 'name': 'HSBC Holdings plc'},
            {'symbol': 'BT-A.L', 'name': 'BT Group plc'},
        ]
        
        stocks = []
        for stock in ftse_stocks:
            stocks.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market': 'UK_FTSE100',
                'exchange': 'LSE',
                'country': 'UK',
                'source': 'Fallback_List'
            })
        
        print(f"  ✅ Obtenidas {len(stocks)} acciones del FTSE 100")
        return stocks
    
    def run_improved_fetch(self):
        """
        Ejecutar obtención mejorada de acciones
        """
        print("🚀 Iniciando obtención MEJORADA de acciones...")
        print("🔥 Combinando web scraping + listas confiables")
        print("🌐 Fuentes múltiples con fallbacks\n")
        
        print("=== 🚀 Obteniendo Listados con MÉTODOS MEJORADOS ===")
        print("🔥 Web scraping + listas de fallback confiables")
        print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        all_stocks = []
        
        # S&P 500 (funciona bien)
        sp500_stocks = self.fetch_sp500_dynamic()
        all_stocks.extend(sp500_stocks)
        
        # NASDAQ 100 (mejorado)
        nasdaq_stocks = self.fetch_nasdaq100_dynamic()
        all_stocks.extend(nasdaq_stocks)
        
        # IBEX 35 (mejorado)
        ibex_stocks = self.fetch_ibex35_improved()
        all_stocks.extend(ibex_stocks)
        
        # Índices europeos (listas confiables)
        european_stocks = self.fetch_european_indices()
        all_stocks.extend(european_stocks)
        
        # Remover duplicados por símbolo
        unique_stocks = {}
        for stock in all_stocks:
            symbol = stock['symbol']
            if symbol not in unique_stocks:
                unique_stocks[symbol] = stock
        
        final_stocks = list(unique_stocks.values())
        
        print(f"\n📊 Resumen de obtención mejorada:")
        print(f"Total acciones obtenidas: {len(all_stocks)}")
        print(f"Acciones únicas: {len(final_stocks)}")
        
        # Guardar resultados
        self.save_results(final_stocks)
        
        # Estadísticas por mercado
        self.print_market_stats(final_stocks)
        
        print(f"\n🎉 === Obtención mejorada completada ===")
        print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total procesado: {len(final_stocks)} acciones únicas")
        print("Método: Web scraping + listas confiables de fallback")
        
        return final_stocks
    
    def save_results(self, stocks: List[Dict]):
        """Guardar resultados en archivos"""
        print(f"\n💾 Guardando {len(stocks)} acciones obtenidas...")
        
        # Archivo con lista completa
        txt_file = os.path.join(self.data_dir, f"improved_stocks_{self.timestamp}.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            for stock in stocks:
                f.write(f"{stock['symbol']}\t{stock['name']}\t{stock['market']}\t{stock['source']}\n")
        
        # Archivo solo con símbolos
        symbols_file = os.path.join(self.data_dir, f"improved_symbols_{self.timestamp}.txt")
        with open(symbols_file, 'w', encoding='utf-8') as f:
            for stock in stocks:
                f.write(f"{stock['symbol']}\n")
        
        # Archivo JSON completo
        json_file = os.path.join(self.data_dir, f"improved_stocks_{self.timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(stocks, f, indent=2, ensure_ascii=False)
        
        print("✅ Archivos guardados:")
        print(f"  📄 Lista completa: {txt_file}")
        print(f"  📄 Solo símbolos: {symbols_file}")
        print(f"  📄 JSON completo: {json_file}")
    
    def print_market_stats(self, stocks: List[Dict]):
        """Imprimir estadísticas por mercado"""
        print(f"\n📈 Resumen por mercado:")
        
        market_counts = {}
        source_counts = {}
        
        for stock in stocks:
            market = stock['market']
            source = stock['source']
            
            market_counts[market] = market_counts.get(market, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
        
        for market, count in sorted(market_counts.items()):
            print(f"  {market}: {count} acciones")
        
        print(f"\n🔍 Fuentes utilizadas:")
        for source, count in sorted(source_counts.items()):
            print(f"  {source}: {count} acciones")


def main():
    """
    Función principal
    """
    fetcher = ImprovedStockFetcher()
    stocks = fetcher.run_improved_fetch()
    
    print(f"\n🔥 ¡Éxito! Obtenidas {len(stocks)} acciones con métodos mejorados")
    print("📊 Próximo paso: Obtener datos de precios para estas acciones")


if __name__ == "__main__":
    main()
