#!/usr/bin/env python3
"""
Script para corregir los símbolos del NASDAQ 100 
Mapea nombres de empresas a símbolos de trading correctos
"""

import re
from config import MARKET_STOCKS

# Mapeo manual de nombres de empresas a símbolos del NASDAQ 100
NASDAQ_NAME_TO_SYMBOL = {
    'Nvidia': 'NVDA',
    'Microsoft': 'MSFT', 
    'Apple Inc.': 'AAPL',
    'Amazon': 'AMZN',
    'Meta Platforms': 'META',
    'Broadcom Inc.': 'AVGO',
    'Alphabet Inc. (Class A)': 'GOOGL',
    'Alphabet Inc. (Class C)': 'GOOG',
    'Tesla, Inc.': 'TSLA',
    'Netflix': 'NFLX',
    'Costco': 'COST',
    'Palantir Technologies': 'PLTR',
    'ASML Holding': 'ASML',
    'Cisco': 'CSCO',
    'T-Mobile US': 'TMUS',
    'Advanced Micro Devices Inc.': 'AMD',
    'AstraZeneca': 'AZN',
    'Linde plc': 'LIN',
    'Intuit': 'INTU',
    'Texas Instruments': 'TXN',
    'Booking Holdings': 'BKNG',
    'Intuitive Surgical': 'ISRG',
    'PepsiCo': 'PEP',
    'Qualcomm': 'QCOM',
    'Applied Materials': 'AMAT',
    'Amgen': 'AMGN',
    'Arm Holdings': 'ARM',
    'Adobe Inc.': 'ADBE',
    'Honeywell': 'HON',
    'Shopify': 'SHOP',
    'PDD Holdings': 'PDD',
    'Gilead Sciences': 'GILD',
    'Micron Technology': 'MU',
    'Comcast': 'CMCSA',
    'Lam Research': 'LRCX',
    'Palo Alto Networks': 'PANW',
    'MicroStrategy Inc.': 'MSTR',
    'KLA Corporation': 'KLAC',
    'Vertex Pharmaceuticals': 'VRTX',
    'Analog Devices': 'ADI',
    'MercadoLibre': 'MELI',
    'CrowdStrike': 'CRWD',
    'Applovin Corp': 'APP',
    'Starbucks': 'SBUX',
    'Intel': 'INTC',
    'Constellation Energy': 'CEG',
    'DoorDash': 'DASH',
    'Mondelez International': 'MDLZ',
    'Cadence Design Systems': 'CDNS',
    'Cintas': 'CTAS',
    'Synopsys': 'SNPS',
    'Airbnb': 'ABNB',
    'O\'Reilly Automotive': 'ORLY',
    'Fortinet': 'FTNT',
    'Marriott International': 'MAR',
    'PayPal': 'PYPL',
    'Marvell Technology': 'MRVL',
    'CSX Corporation': 'CSX',
    'Autodesk': 'ADSK',
    'Regeneron Pharmaceuticals': 'REGN',
    'Workday, Inc.': 'WDAY',
    'Roper Technologies': 'ROP',
    'Axon Enterprise Inc.': 'AXON',
    'Monster Beverage': 'MNST',
    'NXP Semiconductors': 'NXPI',
    'American Electric Power': 'AEP',
    'Charter Communications': 'CHTR',
    'Fastenal': 'FAST',
    'Paychex': 'PAYX',
    'Atlassian': 'TEAM',
    'Paccar': 'PCAR',
    'Datadog': 'DDOG',
    'Copart': 'CPRT',
    'Zscaler': 'ZS',
    'Keurig Dr Pepper': 'KDP',
    'Coca-Cola Europacific Partners': 'CCEP',
    'Exelon': 'EXC',
    'Take-Two Interactive': 'TTWO',
    'Verisk': 'VRSK',
    'Ross Stores': 'ROST',
    'Idexx Laboratories': 'IDXX',
    'Trade Desk (The)': 'TTD',
    'Diamondback Energy': 'FANG',
    'Microchip Technology': 'MCHP',
    'Xcel Energy': 'XEL',
    'Baker Hughes': 'BKR',
    'Electronic Arts': 'EA',
    'Cognizant': 'CTSH',
    'CoStar Group': 'CSGP',
    'Old Dominion Freight Line': 'ODFL',
    'GE HealthCare': 'GEHC',
    'Ansys': 'ANSS',
    'DexCom': 'DXCM',
    'Kraft Heinz': 'KHC',
    'Warner Bros. Discovery': 'WBD',
    'Lululemon Athletica': 'LULU',
    'Onsemi': 'ON',
    'CDW Corporation': 'CDW',
    'GlobalFoundries': 'GFS',
    'Biogen': 'BIIB'
}

def test_symbols():
    """Probar algunos símbolos para verificar que funcionan"""
    print("🧪 PROBANDO SÍMBOLOS CONVERTIDOS:")
    print("="*50)
    
    import yfinance as yf
    
    # Probar una muestra de símbolos
    test_cases = [
        ('Nvidia', 'NVDA'),
        ('Apple Inc.', 'AAPL'),
        ('Microsoft', 'MSFT'),
        ('Amazon', 'AMZN'),
        ('Tesla, Inc.', 'TSLA')
    ]
    
    for company_name, symbol in test_cases:
        print(f"\n🔍 {company_name} → {symbol}")
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if info and 'longName' in info:
                print(f"   ✅ Válido: {info.get('longName', 'N/A')}")
            else:
                print(f"   ⚠️  Info limitada")
                
            # Probar datos recientes
            data = ticker.history(period="5d")
            if not data.empty:
                print(f"   ✅ Datos: {len(data)} registros recientes")
            else:
                print(f"   ❌ Sin datos")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def fix_nasdaq_symbols():
    """Generar la configuración corregida"""
    print("🔧 CORRIGIENDO SÍMBOLOS DEL NASDAQ 100:")
    print("="*50)
    
    current_nasdaq = MARKET_STOCKS['us_nasdaq100']
    print(f"📊 Nombres actuales: {len(current_nasdaq)}")
    
    # Convertir nombres a símbolos
    converted_symbols = []
    not_found = []
    
    for company_name in current_nasdaq:
        if company_name in NASDAQ_NAME_TO_SYMBOL:
            symbol = NASDAQ_NAME_TO_SYMBOL[company_name]
            converted_symbols.append(symbol)
            print(f"✅ {company_name} → {symbol}")
        else:
            not_found.append(company_name)
            print(f"❌ NO ENCONTRADO: {company_name}")
    
    print(f"\n📊 RESULTADOS:")
    print(f"   • Convertidos: {len(converted_symbols)}")
    print(f"   • No encontrados: {len(not_found)}")
    
    if not_found:
        print(f"\n⚠️  SÍMBOLOS NO MAPEADOS:")
        for name in not_found:
            print(f"   • {name}")
    
    # Generar código Python para config.py
    print(f"\n🔧 CÓDIGO PARA config.py:")
    print("="*50)
    print("    'us_nasdaq100': [")
    
    # Dividir en líneas de ~10 símbolos cada una
    for i in range(0, len(converted_symbols), 10):
        chunk = converted_symbols[i:i+10]
        symbols_str = "', '".join(chunk)
        print(f"        '{symbols_str}',")
    
    print("    ],")
    
    return converted_symbols

if __name__ == "__main__":
    print("📈 CORRECCIÓN DE SÍMBOLOS NASDAQ 100")
    print("="*50)
    
    # Probar algunos símbolos
    test_symbols()
    
    print("\n" + "="*50)
    
    # Generar la configuración corregida
    symbols = fix_nasdaq_symbols()
    
    print(f"\n✅ PROCESO COMPLETADO")
    print(f"   • {len(symbols)} símbolos convertidos")
    print(f"   • Listo para actualizar config.py")
