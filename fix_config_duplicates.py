#!/usr/bin/env python3
"""
Eliminar nombres de empresas duplicados del NASDAQ 100 en la sección 'other'
"""

from config import MARKET_STOCKS

# Nombres de empresas del NASDAQ 100 que deben eliminarse de 'other'
NASDAQ_COMPANY_NAMES = [
    'Nvidia', 'Microsoft', 'Apple Inc.', 'Amazon', 'Meta Platforms',
    'Broadcom Inc.', 'Alphabet Inc. (Class A)', 'Alphabet Inc. (Class C)', 'Tesla, Inc.', 'Netflix',
    'Costco', 'Palantir Technologies', 'ASML Holding', 'Cisco', 'T-Mobile US',
    'Advanced Micro Devices Inc.', 'AstraZeneca', 'Linde plc', 'Intuit', 'Texas Instruments',
    'Booking Holdings', 'Intuitive Surgical', 'PepsiCo', 'Qualcomm', 'Applied Materials',
    'Amgen', 'Arm Holdings', 'Adobe Inc.', 'Honeywell', 'Shopify',
    'PDD Holdings', 'Gilead Sciences', 'Micron Technology', 'Comcast', 'Lam Research',
    'Palo Alto Networks', 'MicroStrategy Inc.', 'KLA Corporation', 'Vertex Pharmaceuticals', 'Analog Devices',
    'MercadoLibre', 'CrowdStrike', 'Applovin Corp', 'Starbucks', 'Intel',
    'Constellation Energy', 'DoorDash', 'Mondelez International', 'Cadence Design Systems', 'Cintas',
    'Synopsys', 'Airbnb', 'O\'Reilly Automotive', 'Fortinet', 'Marriott International',
    'PayPal', 'Marvell Technology', 'CSX Corporation', 'Autodesk', 'Regeneron Pharmaceuticals',
    'Workday, Inc.', 'Roper Technologies', 'Axon Enterprise Inc.', 'Monster Beverage', 'NXP Semiconductors',
    'American Electric Power', 'Charter Communications', 'Fastenal', 'Paychex', 'Atlassian',
    'Paccar', 'Datadog', 'Copart', 'Zscaler', 'Keurig Dr Pepper',
    'Coca-Cola Europacific Partners', 'Exelon', 'Take-Two Interactive', 'Verisk', 'Ross Stores',
    'Idexx Laboratories', 'Trade Desk (The)', 'Diamondback Energy', 'Microchip Technology', 'Xcel Energy',
    'Baker Hughes', 'Electronic Arts', 'Cognizant', 'CoStar Group', 'Old Dominion Freight Line',
    'GE HealthCare', 'Ansys', 'DexCom', 'Kraft Heinz', 'Warner Bros. Discovery',
    'Lululemon Athletica', 'Onsemi', 'CDW Corporation', 'GlobalFoundries', 'Biogen'
]

def analyze_duplicates():
    """Analizar duplicados en config actual"""
    print("🔍 ANÁLISIS DE DUPLICADOS EN CONFIG")
    print("="*50)
    
    # Obtener la sección 'other'
    other_symbols = MARKET_STOCKS.get('other', [])
    nasdaq_symbols = MARKET_STOCKS.get('us_nasdaq100', [])
    
    print(f"📊 Símbolos en 'other': {len(other_symbols)}")
    print(f"📊 Símbolos en 'us_nasdaq100': {len(nasdaq_symbols)}")
    
    # Buscar nombres de empresas del NASDAQ en 'other'
    duplicates_found = []
    
    for company_name in NASDAQ_COMPANY_NAMES:
        if company_name in other_symbols:
            duplicates_found.append(company_name)
    
    print(f"\n🚨 DUPLICADOS ENCONTRADOS: {len(duplicates_found)}")
    if duplicates_found:
        print("   Nombres a eliminar de 'other':")
        for i, name in enumerate(duplicates_found, 1):
            print(f"   {i:2d}. {name}")
    
    return duplicates_found

def generate_clean_other_section():
    """Generar la sección 'other' limpia sin duplicados"""
    print(f"\n🧹 GENERANDO SECCIÓN 'OTHER' LIMPIA")
    print("="*50)
    
    other_symbols = MARKET_STOCKS.get('other', [])
    
    # Filtrar duplicados
    clean_other = []
    removed_count = 0
    
    for symbol in other_symbols:
        if symbol not in NASDAQ_COMPANY_NAMES:
            clean_other.append(symbol)
        else:
            removed_count += 1
    
    print(f"📊 Símbolos originales en 'other': {len(other_symbols)}")
    print(f"📊 Símbolos eliminados: {removed_count}")
    print(f"📊 Símbolos finales en 'other': {len(clean_other)}")
    
    # Generar código Python
    print(f"\n🔧 CÓDIGO PARA config.py (sección 'other'):")
    print("="*50)
    print("    'other': [")
    
    # Dividir en líneas de ~6 símbolos cada una para legibilidad
    for i in range(0, len(clean_other), 6):
        chunk = clean_other[i:i+6]
        symbols_str = "', '".join(chunk)
        print(f"        '{symbols_str}',")
    
    print("    ],")
    
    return clean_other

def verify_no_duplicates():
    """Verificar que no hay duplicados después de la limpieza"""
    print(f"\n✅ VERIFICACIÓN DE DUPLICADOS POST-LIMPIEZA")
    print("="*50)
    
    from config import get_all_symbols
    all_symbols = get_all_symbols()
    
    # Contar duplicados
    symbol_counts = {}
    for symbol in all_symbols:
        symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
    
    duplicates = {symbol: count for symbol, count in symbol_counts.items() if count > 1}
    
    print(f"📊 Total símbolos únicos: {len(set(all_symbols))}")
    print(f"📊 Total símbolos con repeticiones: {len(all_symbols)}")
    print(f"📊 Duplicados encontrados: {len(duplicates)}")
    
    if duplicates:
        print(f"\n⚠️  DUPLICADOS RESTANTES:")
        for symbol, count in duplicates.items():
            print(f"   • {symbol}: {count} veces")
    else:
        print(f"\n✅ ¡Sin duplicados! Configuración limpia")

if __name__ == "__main__":
    print("🧹 CORRECCIÓN DE DUPLICADOS EN CONFIG.PY")
    print("="*50)
    
    duplicates = analyze_duplicates()
    
    if duplicates:
        clean_other = generate_clean_other_section()
        print(f"\n⚠️  IMPORTANTE: Aplica el código generado manualmente en config.py")
        print(f"   Reemplaza la sección 'other' completa con el código mostrado")
    else:
        print(f"\n✅ No se encontraron duplicados que corregir")
    
    verify_no_duplicates()
