#!/usr/bin/env python3
"""
Symbol Resolver Inteligente - Sistema Profesional de Resolución de Símbolos
===========================================================================

Este módulo proporciona resolución automática e inteligente de nombres de empresas
a símbolos bursátiles, con validación en tiempo real y caché persistente.

Características:
- Detección automática símbolo vs nombre de empresa
- Resolución dinámica usando múltiples estrategias
- Validación con yfinance en tiempo real
- Caché persistente para eficiencia
- Reportes detallados de conversiones
- Escalable para futuros datasets
"""

import re
import json
import yfinance as yf
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timedelta
import warnings

# Suprimir warnings de yfinance
warnings.filterwarnings('ignore')

class SymbolResolver:
    """
    Resuelve automáticamente nombres de empresas a símbolos bursátiles válidos
    """
    
    def __init__(self, cache_file: str = "symbol_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
        self.session_resoluciones = []
        
        # Mapeos conocidos del NASDAQ 100 (seed data)
        self.known_mappings = {
            'Nvidia': 'NVDA', 'Microsoft': 'MSFT', 'Apple Inc.': 'AAPL', 
            'Amazon': 'AMZN', 'Meta Platforms': 'META', 'Broadcom Inc.': 'AVGO',
            'Alphabet Inc. (Class A)': 'GOOGL', 'Alphabet Inc. (Class C)': 'GOOG',
            'Tesla, Inc.': 'TSLA', 'Netflix': 'NFLX', 'Costco': 'COST',
            'Palantir Technologies': 'PLTR', 'ASML Holding': 'ASML', 'Cisco': 'CSCO',
            'T-Mobile US': 'TMUS', 'Advanced Micro Devices Inc.': 'AMD',
            'AstraZeneca': 'AZN', 'Linde plc': 'LIN', 'Intuit': 'INTU',
            'Texas Instruments': 'TXN', 'Booking Holdings': 'BKNG',
            'Intuitive Surgical': 'ISRG', 'PepsiCo': 'PEP', 'Qualcomm': 'QCOM',
            'Applied Materials': 'AMAT', 'Amgen': 'AMGN', 'Arm Holdings': 'ARM',
            'Adobe Inc.': 'ADBE', 'Honeywell': 'HON', 'Shopify': 'SHOP',
            'PDD Holdings': 'PDD', 'Gilead Sciences': 'GILD', 'Micron Technology': 'MU',
            'Comcast': 'CMCSA', 'Lam Research': 'LRCX', 'Palo Alto Networks': 'PANW',
            'MicroStrategy Inc.': 'MSTR', 'KLA Corporation': 'KLAC',
            'Vertex Pharmaceuticals': 'VRTX', 'Analog Devices': 'ADI',
            'MercadoLibre': 'MELI', 'CrowdStrike': 'CRWD', 'Applovin Corp': 'APP',
            'Starbucks': 'SBUX', 'Intel': 'INTC', 'Constellation Energy': 'CEG',
            'DoorDash': 'DASH', 'Mondelez International': 'MDLZ',
            # Añadir más mapeos según necesidad...
        }
        
        # Inicializar caché con mapeos conocidos
        self._seed_cache_with_known_mappings()
    
    def _load_cache(self) -> Dict:
        """Cargar caché desde archivo"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'mappings': {}, 'validations': {}, 'metadata': {}}
        return {'mappings': {}, 'validations': {}, 'metadata': {}}
    
    def _save_cache(self):
        """Guardar caché a archivo"""
        self.cache['metadata']['last_updated'] = datetime.now().isoformat()
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def _seed_cache_with_known_mappings(self):
        """Inicializar caché con mapeos conocidos"""
        for name, symbol in self.known_mappings.items():
            if name not in self.cache['mappings']:
                self.cache['mappings'][name] = symbol
                self.cache['validations'][symbol] = {
                    'valid': True,
                    'last_check': datetime.now().isoformat(),
                    'source': 'known_mapping'
                }
    
    def is_symbol(self, text: str) -> bool:
        """
        Detectar si un texto es un símbolo bursátil o nombre de empresa
        
        Heurísticas:
        - Símbolos: cortos, mayúsculas, pueden tener .XX suffix
        - Nombres: largos, espacios, palabras como Inc., Corp, etc.
        """
        text = text.strip()
        
        # Patrones claros de símbolos
        if re.match(r'^[A-Z]{1,5}(\.[A-Z]{1,3})?$', text):
            return True
        
        # Patrones claros de nombres de empresa  
        company_indicators = ['Inc.', 'Corp', 'Corporation', 'Ltd', 'Limited', 
                             'Holdings', 'Group', 'Company', 'Technologies', 
                             'Systems', 'Solutions', 'Services', 'plc']
        
        if any(indicator in text for indicator in company_indicators):
            return False
        
        # Heurísticas adicionales
        if len(text) <= 5 and text.isupper() and ' ' not in text:
            return True
        
        if len(text) > 10 or ' ' in text:
            return False
        
        # Caso ambiguo - asumir símbolo si es corto y mayúsculas
        return len(text) <= 6 and text.isupper()
    
    def validate_symbol(self, symbol: str, use_cache: bool = True) -> bool:
        """
        Validar que un símbolo funciona con yfinance
        """
        if use_cache and symbol in self.cache['validations']:
            validation = self.cache['validations'][symbol]
            # Si fue validado en las últimas 24 horas, usar caché
            last_check = datetime.fromisoformat(validation['last_check'])
            if datetime.now() - last_check < timedelta(hours=24):
                return validation['valid']
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.history(period="5d")
            valid = len(info) > 0
            
            # Actualizar caché
            self.cache['validations'][symbol] = {
                'valid': valid,
                'last_check': datetime.now().isoformat(),
                'source': 'yfinance_validation'
            }
            
            return valid
        except:
            self.cache['validations'][symbol] = {
                'valid': False,
                'last_check': datetime.now().isoformat(),
                'source': 'yfinance_validation'
            }
            return False
    
    def resolve_name_to_symbol(self, company_name: str) -> Optional[str]:
        """
        Resolver nombre de empresa a símbolo usando múltiples estrategias
        """
        # 1. Consultar caché primero
        if company_name in self.cache['mappings']:
            cached_symbol = self.cache['mappings'][company_name]
            if self.validate_symbol(cached_symbol):
                return cached_symbol
        
        # 2. Estrategias de resolución
        strategies = [
            self._resolve_by_direct_search,
            self._resolve_by_abbreviation,  
            self._resolve_by_keyword_search
        ]
        
        for strategy in strategies:
            try:
                symbol = strategy(company_name)
                if symbol and self.validate_symbol(symbol):
                    # Guardar en caché exitoso
                    self.cache['mappings'][company_name] = symbol
                    return symbol
            except:
                continue
        
        return None
    
    def _resolve_by_direct_search(self, company_name: str) -> Optional[str]:
        """Buscar directamente por nombre de empresa en yfinance"""
        try:
            # Buscar ticker por nombre
            ticker = yf.Ticker(company_name)
            info = ticker.info
            if 'symbol' in info:
                return info['symbol']
        except:
            pass
        return None
    
    def _resolve_by_abbreviation(self, company_name: str) -> Optional[str]:
        """Crear abreviación inteligente del nombre"""
        # Remover palabras comunes
        words = company_name.replace(',', '').split()
        filtered_words = [w for w in words if w not in 
                         ['Inc.', 'Corp', 'Corporation', 'Ltd', 'Limited', 
                          'Holdings', 'Group', 'Company', 'Technologies',
                          'Systems', 'Solutions', 'Services', 'plc']]
        
        if len(filtered_words) == 0:
            return None
        
        # Estrategias de abreviación
        strategies = [
            # Primera letra de cada palabra
            ''.join([w[0].upper() for w in filtered_words[:4]]),
            # Primeras 2 letras de primera palabra + primera de resto
            filtered_words[0][:2].upper() + ''.join([w[0].upper() for w in filtered_words[1:3]]),
            # Primera palabra completa si es corta
            filtered_words[0].upper() if len(filtered_words[0]) <= 4 else None
        ]
        
        for abbrev in strategies:
            if abbrev and len(abbrev) <= 5:
                return abbrev
        
        return None
    
    def _resolve_by_keyword_search(self, company_name: str) -> Optional[str]:
        """Búsqueda por palabras clave importantes"""
        # Esta estrategia se puede expandir con APIs externas
        # Por ahora, retorna None para indicar que no se pudo resolver
        return None
    
    def batch_resolve(self, symbols_and_names: List[str]) -> Tuple[List[str], Dict]:
        """
        Procesar lote de símbolos/nombres mixtos
        
        Returns:
            tuple: (lista_símbolos_válidos, reporte_conversiones)
        """
        print("🧠 INICIANDO SYMBOL RESOLVER INTELIGENTE")
        print("="*60)
        
        resolved_symbols = []
        report = {
            'total_inputs': len(symbols_and_names),
            'symbols_passed_through': 0,
            'names_resolved': 0,
            'failed_resolutions': 0,
            'conversions': [],
            'failures': []
        }
        
        for i, item in enumerate(symbols_and_names, 1):
            print(f"🔍 Procesando ({i}/{len(symbols_and_names)}): {item}")
            
            if self.is_symbol(item):
                # Es un símbolo - validar directamente
                if self.validate_symbol(item):
                    resolved_symbols.append(item)
                    report['symbols_passed_through'] += 1
                    print(f"  ✅ Símbolo válido: {item}")
                else:
                    report['failures'].append({
                        'input': item,
                        'type': 'invalid_symbol',
                        'reason': 'No pasa validación yfinance'
                    })
                    print(f"  ❌ Símbolo inválido: {item}")
            else:
                # Es un nombre - resolver a símbolo
                resolved_symbol = self.resolve_name_to_symbol(item)
                if resolved_symbol:
                    resolved_symbols.append(resolved_symbol)
                    report['names_resolved'] += 1
                    report['conversions'].append({
                        'name': item,
                        'symbol': resolved_symbol
                    })
                    print(f"  🔄 Convertido: {item} → {resolved_symbol}")
                    self.session_resoluciones.append((item, resolved_symbol))
                else:
                    report['failed_resolutions'] += 1
                    report['failures'].append({
                        'input': item,
                        'type': 'unresolved_name', 
                        'reason': 'No se pudo encontrar símbolo válido'
                    })
                    print(f"  ❌ No resuelto: {item}")
        
        # Guardar caché actualizado
        self._save_cache()
        
        print(f"\n📊 RESUMEN DE RESOLUCIÓN:")
        print(f"   • Entradas procesadas: {report['total_inputs']}")
        print(f"   • Símbolos válidos: {report['symbols_passed_through']}")
        print(f"   • Nombres convertidos: {report['names_resolved']}")
        print(f"   • Fallos: {report['failed_resolutions']}")
        print(f"   • Símbolos finales: {len(resolved_symbols)}")
        
        return resolved_symbols, report
    
    def generate_detailed_report(self, report: Dict, output_file: str = None):
        """Generar reporte detallado de la sesión"""
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 REPORTE DETALLADO DE SYMBOL RESOLVER")
        print("="*60)
        
        if report['conversions']:
            print(f"\n🔄 CONVERSIONES EXITOSAS ({len(report['conversions'])}):")
            for conv in report['conversions']:
                print(f"   • {conv['name']} → {conv['symbol']}")
        
        if report['failures']:
            print(f"\n❌ ELEMENTOS NO PROCESADOS ({len(report['failures'])}):")
            for failure in report['failures']:
                print(f"   • {failure['input']} ({failure['reason']})")


def test_symbol_resolver():
    """Función de prueba del Symbol Resolver"""
    resolver = SymbolResolver()
    
    # Test con ejemplos mixtos
    test_data = [
        'AAPL',  # Símbolo válido
        'Apple Inc.',  # Nombre conocido
        'Microsoft',  # Nombre conocido
        'Tesla, Inc.',  # Nombre conocido
        'INVALID',  # Símbolo inválido
        'Empresa Inexistente Corp'  # Nombre no resolvible
    ]
    
    symbols, report = resolver.batch_resolve(test_data)
    resolver.generate_detailed_report(report, "test_resolution_report.json")
    
    return symbols, report


if __name__ == "__main__":
    # Ejecutar test
    print("🧪 TESTING SYMBOL RESOLVER")
    symbols, report = test_symbol_resolver()
    print(f"\n✅ Test completado. Símbolos resueltos: {symbols}")
