"""
Configuración actualizada para el analizador de trading
Incluye acciones obtenidas dinámicamente de múltiples mercados
"""

import json
import os

# Configuración de APIs
YFINANCE_CONFIG = {
    'default_period': '1y',
    'default_interval': '1wk',
    'timeout': 10,
    'max_workers': 10,  # Para descargas paralelas
    'retry_attempts': 3
}

# Configuración de gráficos
PLOT_CONFIG = {
    'figure_size': (15, 10),
    'dpi': 300,
    'style': 'seaborn-v0_8',
    'color_palette': ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
}

# Configuración de estrategias
STRATEGY_CONFIG = {
    'short_ma_period': 4,   # Media móvil corta (4 semanas)
    'long_ma_period': 12,   # Media móvil larga (12 semanas)
    'volatility_window': 4, # Ventana para cálculo de volatilidad
    'rsi_period': 14,       # Período para RSI
    'bollinger_period': 20, # Período para Bandas de Bollinger
    'bollinger_std': 2      # Desviaciones estándar para Bandas de Bollinger
}

# Configuración de mercados
MARKET_CONFIG = {
    'trading_hours': {
        'pre_market': '04:00',
        'market_open': '09:30',
        'market_close': '16:00',
        'after_hours': '20:00'
    },
    'timezone': 'America/New_York',
    'currency': 'USD',
    'european_timezone': 'Europe/Madrid'
}

# Acciones por mercado (obtenidas dinámicamente)
MARKET_STOCKS = {
    'us_sp500': [
        'MMM', 'AOS', 'ABT', 'ABBV', 'ACN',
        'ADBE', 'AMD', 'AES', 'AFL', 'A',
        'APD', 'ABNB', 'AKAM', 'ALB', 'ARE',
        'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL',
        'GOOG', 'MO', 'AMZN', 'AMCR', 'AEE',
        'AEP', 'AXP', 'AIG', 'AMT', 'AWK',
        'AMP', 'AME', 'AMGN', 'APH', 'ADI',
        'ANSS', 'AON', 'APA', 'APO', 'AAPL',
        'AMAT', 'APTV', 'ACGL', 'ADM', 'ANET',
        'AJG', 'AIZ', 'T', 'ATO', 'ADSK',
        'ADP', 'AZO', 'AVB', 'AVY', 'AXON',
        'BKR', 'BALL', 'BAC', 'BAX', 'BDX',
        'BRK.B', 'BBY', 'TECH', 'BIIB', 'BLK',
        'BX', 'BK', 'BA', 'BKNG', 'BSX',
        'BMY', 'AVGO', 'BR', 'BRO', 'BF.B',
        'BLDR', 'BG', 'BXP', 'CHRW', 'CDNS',
        'CZR', 'CPT', 'CPB', 'COF', 'CAH',
        'KMX', 'CCL', 'CARR', 'CAT', 'CBOE',
        'CBRE', 'CDW', 'COR', 'CNC', 'CNP',
        'CF', 'CRL', 'SCHW', 'CHTR', 'CVX',
        'CMG', 'CB', 'CHD', 'CI', 'CINF',
        'CTAS', 'CSCO', 'C', 'CFG', 'CLX',
        'CME', 'CMS', 'KO', 'CTSH', 'COIN',
        'CL', 'CMCSA', 'CAG', 'COP', 'ED',
        'STZ', 'CEG', 'COO', 'CPRT', 'GLW',
        'CPAY', 'CTVA', 'CSGP', 'COST', 'CTRA',
        'CRWD', 'CCI', 'CSX', 'CMI', 'CVS',
        'DHR', 'DRI', 'DDOG', 'DVA', 'DAY',
        'DECK', 'DE', 'DELL', 'DAL', 'DVN',
        'DXCM', 'FANG', 'DLR', 'DG', 'DLTR',
        'D', 'DPZ', 'DASH', 'DOV', 'DOW',
        'DHI', 'DTE', 'DUK', 'DD', 'EMN',
        'ETN', 'EBAY', 'ECL', 'EIX', 'EW',
        'EA', 'ELV', 'EMR', 'ENPH', 'ETR',
        'EOG', 'EPAM', 'EQT', 'EFX', 'EQIX',
        'EQR', 'ERIE', 'ESS', 'EL', 'EG',
        'EVRG', 'ES', 'EXC', 'EXE', 'EXPE',
        'EXPD', 'EXR', 'XOM', 'FFIV', 'FDS',
        'FICO', 'FAST', 'FRT', 'FDX', 'FIS',
        'FITB', 'FSLR', 'FE', 'FI', 'F',
        'FTNT', 'FTV', 'FOXA', 'FOX', 'BEN',
        'FCX', 'GRMN', 'IT', 'GE', 'GEHC',
        'GEV', 'GEN', 'GNRC', 'GD', 'GIS',
        'GM', 'GPC', 'GILD', 'GPN', 'GL',
        'GDDY', 'GS', 'HAL', 'HIG', 'HAS',
        'HCA', 'DOC', 'HSIC', 'HSY', 'HES',
        'HPE', 'HLT', 'HOLX', 'HD', 'HON',
        'HRL', 'HST', 'HWM', 'HPQ', 'HUBB',
        'HUM', 'HBAN', 'HII', 'IBM', 'IEX',
        'IDXX', 'ITW', 'INCY', 'IR', 'PODD',
        'INTC', 'ICE', 'IFF', 'IP', 'IPG',
        'INTU', 'ISRG', 'IVZ', 'INVH', 'IQV',
        'IRM', 'JBHT', 'JBL', 'JKHY', 'J',
        'JNJ', 'JCI', 'JPM', 'K', 'KVUE',
        'KDP', 'KEY', 'KEYS', 'KMB', 'KIM',
        'KMI', 'KKR', 'KLAC', 'KHC', 'KR',
        'LHX', 'LH', 'LRCX', 'LW', 'LVS',
        'LDOS', 'LEN', 'LII', 'LLY', 'LIN',
        'LYV', 'LKQ', 'LMT', 'L', 'LOW',
        'LULU', 'LYB', 'MTB', 'MPC', 'MKTX',
        'MAR', 'MMC', 'MLM', 'MAS', 'MA',
        'MTCH', 'MKC', 'MCD', 'MCK', 'MDT',
        'MRK', 'META', 'MET', 'MTD', 'MGM',
        'MCHP', 'MU', 'MSFT', 'MAA', 'MRNA',
        'MHK', 'MOH', 'TAP', 'MDLZ', 'MPWR',
        'MNST', 'MCO', 'MS', 'MOS', 'MSI',
        'MSCI', 'NDAQ', 'NTAP', 'NFLX', 'NEM',
        'NWSA', 'NWS', 'NEE', 'NKE', 'NI',
        'NDSN', 'NSC', 'NTRS', 'NOC', 'NCLH',
        'NRG', 'NUE', 'NVDA', 'NVR', 'NXPI',
        'ORLY', 'OXY', 'ODFL', 'OMC', 'ON',
        'OKE', 'ORCL', 'OTIS', 'PCAR', 'PKG',
        'PLTR', 'PANW', 'PARA', 'PH', 'PAYX',
        'PAYC', 'PYPL', 'PNR', 'PEP', 'PFE',
        'PCG', 'PM', 'PSX', 'PNW', 'PNC',
        'POOL', 'PPG', 'PPL', 'PFG', 'PG',
        'PGR', 'PLD', 'PRU', 'PEG', 'PTC',
        'PSA', 'PHM', 'PWR', 'QCOM', 'DGX',
        'RL', 'RJF', 'RTX', 'O', 'REG',
        'REGN', 'RF', 'RSG', 'RMD', 'RVTY',
        'ROK', 'ROL', 'ROP', 'ROST', 'RCL',
        'SPGI', 'CRM', 'SBAC', 'SLB', 'STX',
        'SRE', 'NOW', 'SHW', 'SPG', 'SWKS',
        'SJM', 'SW', 'SNA', 'SOLV', 'SO',
        'LUV', 'SWK', 'SBUX', 'STT', 'STLD',
        'STE', 'SYK', 'SMCI', 'SYF', 'SNPS',
        'SYY', 'TMUS', 'TROW', 'TTWO', 'TPR',
        'TRGP', 'TGT', 'TEL', 'TDY', 'TER',
        'TSLA', 'TXN', 'TPL', 'TXT', 'TMO',
        'TJX', 'TKO', 'TSCO', 'TT', 'TDG',
        'TRV', 'TRMB', 'TFC', 'TYL', 'TSN',
        'USB', 'UBER', 'UDR', 'ULTA', 'UNP',
        'UAL', 'UPS', 'URI', 'UNH', 'UHS',
        'VLO', 'VTR', 'VLTO', 'VRSN', 'VRSK',
        'VZ', 'VRTX', 'VTRS', 'VICI', 'V',
        'VST', 'VMC', 'WRB', 'GWW', 'WAB',
        'WBA', 'WMT', 'DIS', 'WBD', 'WM',
        'WAT', 'WEC', 'WFC', 'WELL', 'WST',
        'WDC', 'WY', 'WSM', 'WMB', 'WTW',
        'WDAY', 'WYNN', 'XEL', 'XYL', 'YUM',
        'ZBRA', 'ZBH', 'ZTS'
    ],
    'us_nasdaq100': [
        'NVDA', 'MSFT', 'AAPL', 'AMZN', 'META', 'AVGO', 'GOOGL', 'GOOG', 'TSLA', 'NFLX',
        'COST', 'PLTR', 'ASML', 'CSCO', 'TMUS', 'AMD', 'AZN', 'LIN', 'INTU', 'TXN',
        'BKNG', 'ISRG', 'PEP', 'QCOM', 'AMAT', 'AMGN', 'ARM', 'ADBE', 'HON', 'SHOP',
        'PDD', 'GILD', 'MU', 'CMCSA', 'LRCX', 'PANW', 'MSTR', 'KLAC', 'VRTX', 'ADI',
        'MELI', 'CRWD', 'APP', 'SBUX', 'INTC', 'CEG', 'DASH', 'MDLZ', 'CDNS', 'CTAS',
        'SNPS', 'ABNB', 'ORLY', 'FTNT', 'MAR', 'PYPL', 'MRVL', 'CSX', 'ADSK', 'REGN',
        'WDAY', 'ROP', 'AXON', 'MNST', 'NXPI', 'AEP', 'CHTR', 'FAST', 'PAYX', 'TEAM',
        'PCAR', 'DDOG', 'CPRT', 'ZS', 'KDP', 'CCEP', 'EXC', 'TTWO', 'VRSK', 'ROST',
        'IDXX', 'TTD', 'FANG', 'MCHP', 'XEL', 'BKR', 'EA', 'CTSH', 'CSGP', 'ODFL',
        'GEHC', 'ANSS', 'DXCM', 'KHC', 'WBD', 'LULU', 'ON', 'CDW', 'GFS', 'BIIB'
    ],
    'es_ibex35': [
        'EVO.MC', 'PAS.MC', 'OPE.MC', 'BOL.MC', 'CRE.MC',
        'BAS.MC', 'COM.MC', 'ISI.MC', 'SIT.MC', 'REL.MC',
        'EDI.MC'
    ],
    'de_dax40': [
        'SAP.DE', 'ASME.DE', 'SIE.DE', 'DTE.DE', 'ALV.DE',
        'MUV2.DE', 'ADS.DE', 'BAS.DE', 'VOW3.DE', 'BMW.DE'
    ],
    'fr_cac40': [
        'MC.PA', 'OR.PA', 'ASML.AS', 'TTE.PA', 'SAN.PA',
        'BNP.PA', 'AIR.PA', 'EL.PA', 'RMS.PA', 'CDI.PA'
    ],
    'uk_ftse100': [
        'SHEL.L', 'AZN.L', 'ULVR.L', 'BP.L', 'LLOY.L',
        'VOD.L', 'GLEN.L', 'BARC.L', 'HSBA.L', 'BT-A.L'
    ],
}

# Acciones por sectores (combinando datos estáticos y dinámicos)
SECTOR_STOCKS = {
    'technology': [
        'AAPL', 'ACN', 'ADBE', 'ADI', 'ADSK', 'AKAM',
        'AMAT', 'AMD', 'AMZN', 'ANET', 'ANSS', 'APH',
        'AVGO', 'CDNS', 'CDW', 'CRM', 'CRWD', 'CSCO',
        'CTSH', 'DDOG', 'DELL', 'ENPH', 'EPAM', 'FFIV',
        'FICO', 'FSLR', 'FTNT', 'GDDY', 'GEN', 'GLW',
        'GOOG', 'GOOGL', 'HPE', 'HPQ', 'IBM', 'INTC',
        'INTU', 'IT', 'JBL', 'KEYS', 'KLAC', 'LRCX',
        'MCHP', 'META', 'MPWR', 'MSFT', 'MSI', 'MU',
        'NFLX', 'NOW', 'NTAP', 'NVDA', 'NXPI', 'ON',
        'ORCL', 'PANW', 'PLTR', 'PTC', 'PYPL', 'QCOM',
        'ROP', 'SMCI', 'SNPS', 'STX', 'SWKS', 'TDY',
        'TEL', 'TER', 'TRMB', 'TSLA', 'TXN', 'TYL',
        'VRSN', 'WDAY', 'WDC', 'ZBRA'
    ],
    'finance': [
        'ACGL', 'AFL', 'AIG', 'AIZ', 'AJG', 'ALL',
        'AMP', 'AON', 'APO', 'AXP', 'BAC', 'BEN',
        'BK', 'BLK', 'BRK.B', 'BRO', 'BX', 'C',
        'CB', 'CBOE', 'CFG', 'CINF', 'CME', 'COF',
        'COIN', 'CPAY', 'EG', 'ERIE', 'FDS', 'FI',
        'FIS', 'FITB', 'GL', 'GPN', 'GS', 'HBAN',
        'HIG', 'ICE', 'IVZ', 'JKHY', 'JPM', 'KEY',
        'KKR', 'L', 'MA', 'MCO', 'MET', 'MKTX',
        'MMC', 'MS', 'MSCI', 'MTB', 'NDAQ', 'NTRS',
        'PFG', 'PGR', 'PNC', 'PRU', 'PYPL', 'RF',
        'RJF', 'SCHW', 'SPGI', 'STT', 'SYF', 'TFC',
        'TROW', 'TRV', 'USB', 'V', 'WFC', 'WRB',
        'WTW'
    ],
    'healthcare': [
        'A', 'ABBV', 'ABT', 'ALGN', 'AMGN', 'BAX',
        'BDX', 'BIIB', 'BMY', 'BSX', 'CAH', 'CI',
        'CNC', 'COO', 'COR', 'CRL', 'CVS', 'DGX',
        'DHR', 'DVA', 'DXCM', 'ELV', 'EW', 'GEHC',
        'GILD', 'HCA', 'HOLX', 'HSIC', 'HUM', 'IDXX',
        'INCY', 'IQV', 'ISRG', 'JNJ', 'LH', 'LLY',
        'MCK', 'MDT', 'MOH', 'MRK', 'MRNA', 'MTD',
        'PFE', 'PODD', 'REGN', 'RMD', 'RVTY', 'SOLV',
        'STE', 'SYK', 'TECH', 'TMO', 'UHS', 'UNH',
        'VRTX', 'VTRS', 'WAT', 'WST', 'ZBH', 'ZTS'
    ],
    'consumer': [
        'ABNB', 'ADM', 'AMZN', 'APTV', 'AZO', 'BBY',
        'BF.B', 'BG', 'BKNG', 'CAG', 'CCL', 'CHD',
        'CL', 'CLX', 'CMG', 'COST', 'CPB', 'CZR',
        'DASH', 'DECK', 'DG', 'DHI', 'DLTR', 'DPZ',
        'DRI', 'EBAY', 'EL', 'EXPE', 'F', 'GIS',
        'GM', 'GPC', 'GRMN', 'HAS', 'HD', 'HLT',
        'HRL', 'HSY', 'K', 'KDP', 'KHC', 'KMB',
        'KMX', 'KO', 'KR', 'KVUE', 'LEN', 'LKQ',
        'LOW', 'LULU', 'LVS', 'LW', 'MAR', 'MCD',
        'MDLZ', 'MGM', 'MHK', 'MKC', 'MNST', 'MO',
        'NCLH', 'NKE', 'NVR', 'ORLY', 'PEP', 'PG',
        'PHM', 'PM', 'POOL', 'RCL', 'RL', 'ROST',
        'SBUX', 'SJM', 'STZ', 'SYY', 'TAP', 'TGT',
        'TJX', 'TPR', 'TSCO', 'TSLA', 'TSN', 'ULTA',
        'WBA', 'WMT', 'WSM', 'WYNN', 'YUM'
    ],
    'energy': [
        'APA', 'BKR', 'COP', 'CTRA', 'CVX', 'DVN',
        'EOG', 'EQT', 'EXE', 'FANG', 'HAL', 'HES',
        'KMI', 'MPC', 'OKE', 'OXY', 'PSX', 'SLB',
        'TPL', 'TRGP', 'VLO', 'WMB', 'XOM'
    ],
    'industrial': [
        'ADP', 'ALLE', 'AME', 'AOS', 'AXON', 'BA',
        'BLDR', 'BR', 'CARR', 'CAT', 'CHRW', 'CMI',
        'CPRT', 'CSX', 'CTAS', 'DAL', 'DAY', 'DE',
        'DOV', 'EFX', 'EMR', 'ETN', 'EXPD', 'FAST',
        'FDX', 'FTV', 'GD', 'GE', 'GEV', 'GNRC',
        'GWW', 'HII', 'HON', 'HUBB', 'HWM', 'IEX',
        'IR', 'ITW', 'J', 'JBHT', 'JCI', 'LDOS',
        'LHX', 'LII', 'LMT', 'LUV', 'MAS', 'MMM',
        'NDSN', 'NOC', 'NSC', 'ODFL', 'OTIS', 'PAYC',
        'PAYX', 'PCAR', 'PH', 'PNR', 'PWR', 'ROK',
        'ROL', 'RSG', 'RTX', 'SNA', 'SWK', 'TDG',
        'TT', 'TXT', 'UAL', 'UBER', 'UNP', 'UPS',
        'URI', 'VLTO', 'VRSK', 'WAB', 'WM', 'XYL'
    ],
    'utilities': [
        'AEE', 'AEP', 'AES', 'ATO', 'AWK', 'CEG',
        'CMS', 'CNP', 'D', 'DTE', 'DUK', 'ED',
        'EIX', 'ES', 'ETR', 'EVRG', 'EXC', 'FE',
        'LNT', 'NEE', 'NI', 'NRG', 'PCG', 'PEG',
        'PNW', 'PPL', 'SO', 'SRE', 'VST', 'WEC',
        'XEL'
    ],
    'materials': [
        'ALB', 'AMCR', 'APD', 'AVY', 'BALL', 'CF',
        'CTVA', 'DD', 'DOW', 'ECL', 'EMN', 'FCX',
        'IFF', 'IP', 'LIN', 'LYB', 'MLM', 'MOS',
        'NEM', 'NUE', 'PKG', 'PPG', 'SHW', 'STLD',
        'SW', 'VMC'
    ],
    'real_estate': [
        'AMT', 'ARE', 'AVB', 'BXP', 'CBRE', 'CCI',
        'CPT', 'CSGP', 'DLR', 'DOC', 'EQIX', 'EQR',
        'ESS', 'EXR', 'FRT', 'HST', 'INVH', 'IRM',
        'KIM', 'MAA', 'O', 'PLD', 'PSA', 'REG',
        'SBAC', 'SPG', 'UDR', 'VICI', 'VTR', 'WELL',
        'WY'
    ],
    'communication': [
        'CHTR', 'CMCSA', 'DIS', 'EA', 'FOX', 'FOXA',
        'GOOG', 'GOOGL', 'IPG', 'LYV', 'META', 'MTCH',
        'NFLX', 'NWS', 'NWSA', 'OMC', 'PARA', 'T',
        'TKO', 'TMUS', 'TTWO', 'VZ', 'WBD'
    ],
    'other': [
        'ADS.DE', 'AIR.PA', 'ALV.DE', 'ASME.DE', 'ASML.AS',
        'AZN.L', 'BARC.L', 'BAS.DE', 'BAS.MC', 'BMW.DE', 'BNP.PA',
        'BOL.MC', 'BP.L', 'BT-A.L', 'CDI.PA', 'COM.MC', 'CRE.MC',
        'DTE.DE', 'EDI.MC', 'EL.PA', 'EVO.MC', 'GLEN.L', 'HSBA.L',
        'ISI.MC', 'LLOY.L', 'MC.PA', 'MUV2.DE', 'OPE.MC', 'OR.PA',
        'PAS.MC', 'REL.MC', 'RMS.PA', 'SAN.PA', 'SAP.DE', 'SHEL.L',
        'SIE.DE', 'SIT.MC', 'TTE.PA', 'ULVR.L', 'VOD.L', 'VOW3.DE'
    ],
}


def load_dynamic_stocks_data():
    """
    Cargar datos completos de acciones obtenidas dinámicamente
    """
    try:
        data_dir = "data"
        improved_files = [f for f in os.listdir(data_dir) if f.startswith("improved_stocks_") and f.endswith(".json")]
        
        if not improved_files:
            return []
        
        latest_file = sorted(improved_files)[-1]
        file_path = os.path.join(data_dir, latest_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando datos dinámicos: {e}")
        return []

def get_all_symbols():
    """
    Obtener todos los símbolos disponibles
    """
    all_symbols = set()
    
    # Símbolos por mercado
    for symbols in MARKET_STOCKS.values():
        all_symbols.update(symbols)
    
    # Símbolos por sector
    for symbols in SECTOR_STOCKS.values():
        all_symbols.update(symbols)
    
    return sorted(list(all_symbols))

def get_symbols_by_country(country_code: str):
    """
    Obtener símbolos filtrados por país
    """
    dynamic_data = load_dynamic_stocks_data()
    
    if not dynamic_data:
        return []
    
    return [stock['symbol'] for stock in dynamic_data if stock.get('country', '').upper() == country_code.upper()]

# Resumen de datos
STOCK_DATA_SUMMARY = {
    'total_stocks': 644,
    'markets': ['US_SP500', 'US_NASDAQ100', 'ES_IBEX35', 'DE_DAX40', 'FR_CAC40', 'UK_FTSE100'],
    'sectors': ['industrial', 'healthcare', 'technology', 'utilities', 'finance', 'materials', 'consumer', 'real_estate', 'communication', 'energy', 'other'],
    'by_market': {
        'US_SP500': 503,
        'US_NASDAQ100': 100,
        'ES_IBEX35': 11,
        'DE_DAX40': 10,
        'FR_CAC40': 10,
        'UK_FTSE100': 10,
    },
    'by_sector': {
        'industrial': 78,
        'healthcare': 60,
        'technology': 69,
        'utilities': 31,
        'finance': 73,
        'materials': 26,
        'consumer': 89,
        'real_estate': 31,
        'communication': 23,
        'energy': 23,
        'other': 141,
    }
}
