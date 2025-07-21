#!/usr/bin/env python3
"""
Breakout Strategy Analyzer
=========================

Script para analizar datos históricos de todos los símbolos y identificar
candidatos para la estrategia de ruptura de resistencia.

Criterios de la estrategia:
1. La acción debe tener un mínimo de 2 años de datos históricos
2. Debe tener al menos un máximo histórico
3. Después del máximo, debe haber un mínimo (no necesariamente histórico)
4. El precio actual debe estar próximo a romper la resistencia del máximo histórico anterior

Si cumple todas las condiciones, se marca como válida en la base de datos
con la fecha de última revisión para evitar análisis repetitivos.

Autor: TradeStrategy Team
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text, Column, String, Float, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from tqdm import tqdm

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("breakout_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BreakoutAnalyzer')

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'stockdata',
    'user': 'postgres',
    'password': 'postgres'
}

# Parámetros de la estrategia
MIN_YEARS_DATA = 2  # Mínimo de años de datos históricos
RESISTANCE_PROXIMITY_PERCENT = 5.0  # Porcentaje de proximidad al máximo histórico
REVIEW_INTERVAL_DAYS = 7  # Días antes de volver a revisar un símbolo

# Definir modelos SQLAlchemy
Base = declarative_base()

class StockPrice(Base):
    """Modelo para datos mensuales de acciones."""
    __tablename__ = 'stock_prices_monthly'
    
    symbol = Column(String, primary_key=True)
    date = Column(DateTime, primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

class StrategyCandidate(Base):
    """Modelo para candidatos de estrategia de ruptura."""
    __tablename__ = 'strategy_candidates'
    
    symbol = Column(String, primary_key=True)
    is_valid = Column(Boolean, default=False)
    last_review_date = Column(DateTime)
    historical_high = Column(Float)
    historical_high_date = Column(DateTime)
    subsequent_low = Column(Float)
    subsequent_low_date = Column(DateTime)
    current_price = Column(Float)
    resistance_distance_percent = Column(Float)
    years_of_data = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BreakoutAnalyzer:
    """Analizador de estrategia de ruptura de resistencia."""
    
    def __init__(self):
        """Inicializa el analizador."""
        self.engine = None
        self.session_maker = None
        self.symbols = []
        self.analysis_stats = {
            'total_symbols': 0,
            'analyzed_symbols': 0,
            'valid_candidates': 0,
            'skipped_recent_review': 0,
            'insufficient_data': 0,
            'no_pattern_found': 0,
            'errors': 0
        }
    
    def connect_to_database(self) -> bool:
        """Establece conexión con la base de datos."""
        try:
            connection_string = (
                f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
                f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            )
            
            self.engine = create_engine(connection_string, echo=False)
            self.session_maker = sessionmaker(bind=self.engine)
            
            # Probar la conexión
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Conexión a base de datos establecida exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a la base de datos: {e}")
            return False
    
    def create_strategy_table(self):
        """Crea la tabla de candidatos de estrategia si no existe."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Tabla strategy_candidates creada/verificada exitosamente")
        except Exception as e:
            logger.error(f"Error creando tabla strategy_candidates: {e}")
            raise
    
    def get_all_symbols(self) -> List[str]:
        """Obtiene todos los símbolos disponibles en la base de datos."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT DISTINCT symbol 
                    FROM stock_prices_monthly 
                    ORDER BY symbol
                """))
                symbols = [row[0] for row in result]
            
            logger.info(f"Encontrados {len(symbols)} símbolos en la base de datos")
            return symbols
            
        except Exception as e:
            logger.error(f"Error obteniendo símbolos: {e}")
            return []
    
    def should_analyze_symbol(self, symbol: str) -> bool:
        """Verifica si un símbolo debe ser analizado (no revisado recientemente)."""
        try:
            session = self.session_maker()
            
            candidate = session.query(StrategyCandidate).filter_by(symbol=symbol).first()
            
            if candidate is None:
                return True  # Nunca ha sido analizado
            
            # Verificar si ha pasado suficiente tiempo desde la última revisión
            if candidate.last_review_date:
                days_since_review = (datetime.utcnow() - candidate.last_review_date).days
                if days_since_review < REVIEW_INTERVAL_DAYS:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando si analizar símbolo {symbol}: {e}")
            return True
        finally:
            session.close()
    
    def get_symbol_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Obtiene datos históricos de un símbolo."""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT symbol, date, open, high, low, close, volume
                    FROM stock_prices_monthly
                    WHERE symbol = :symbol
                    ORDER BY date ASC
                """)
                
                df = pd.read_sql(query, conn, params={'symbol': symbol})
                
                if df.empty:
                    return None
                
                df['date'] = pd.to_datetime(df['date'])
                return df
                
        except Exception as e:
            logger.error(f"Error obteniendo datos para {symbol}: {e}")
            return None
    
    def analyze_symbol_pattern(self, symbol: str, df: pd.DataFrame) -> Optional[Dict]:
        """Analiza el patrón de ruptura para un símbolo específico."""
        try:
            # Verificar que tenga al menos 2 años de datos
            date_range = df['date'].max() - df['date'].min()
            years_of_data = date_range.days / 365.25
            
            if years_of_data < MIN_YEARS_DATA:
                return None
            
            # Encontrar el máximo histórico
            max_idx = df['high'].idxmax()
            historical_high = df.loc[max_idx, 'high']
            historical_high_date = df.loc[max_idx, 'date']
            
            # Buscar datos después del máximo histórico
            after_high_df = df[df['date'] > historical_high_date].copy()
            
            if after_high_df.empty:
                return None  # No hay datos después del máximo
            
            # Encontrar el mínimo después del máximo histórico
            min_after_high_idx = after_high_df['low'].idxmin()
            subsequent_low = after_high_df.loc[min_after_high_idx, 'low']
            subsequent_low_date = after_high_df.loc[min_after_high_idx, 'date']
            
            # Obtener el precio actual (último precio disponible)
            current_price = df.iloc[-1]['close']
            
            # Calcular la distancia porcentual al máximo histórico
            resistance_distance_percent = ((historical_high - current_price) / historical_high) * 100
            
            # Verificar si está próximo a romper la resistencia
            is_near_resistance = resistance_distance_percent <= RESISTANCE_PROXIMITY_PERCENT
            
            return {
                'symbol': symbol,
                'years_of_data': float(years_of_data),
                'historical_high': float(historical_high),
                'historical_high_date': historical_high_date,
                'subsequent_low': float(subsequent_low),
                'subsequent_low_date': subsequent_low_date,
                'current_price': float(current_price),
                'resistance_distance_percent': float(resistance_distance_percent),
                'is_valid_candidate': is_near_resistance,
                'pattern_found': True
            }
            
        except Exception as e:
            logger.error(f"Error analizando patrón para {symbol}: {e}")
            return None
    
    def save_analysis_result(self, analysis_result: Dict):
        """Guarda el resultado del análisis en la base de datos."""
        try:
            session = self.session_maker()
            
            # Buscar si ya existe el registro
            candidate = session.query(StrategyCandidate).filter_by(
                symbol=analysis_result['symbol']
            ).first()
            
            if candidate:
                # Actualizar registro existente
                candidate.is_valid = analysis_result['is_valid_candidate']
                candidate.last_review_date = datetime.utcnow()
                candidate.historical_high = analysis_result['historical_high']
                candidate.historical_high_date = analysis_result['historical_high_date']
                candidate.subsequent_low = analysis_result['subsequent_low']
                candidate.subsequent_low_date = analysis_result['subsequent_low_date']
                candidate.current_price = analysis_result['current_price']
                candidate.resistance_distance_percent = analysis_result['resistance_distance_percent']
                candidate.years_of_data = analysis_result['years_of_data']
                candidate.updated_at = datetime.utcnow()
            else:
                # Crear nuevo registro
                candidate = StrategyCandidate(
                    symbol=analysis_result['symbol'],
                    is_valid=analysis_result['is_valid_candidate'],
                    last_review_date=datetime.utcnow(),
                    historical_high=analysis_result['historical_high'],
                    historical_high_date=analysis_result['historical_high_date'],
                    subsequent_low=analysis_result['subsequent_low'],
                    subsequent_low_date=analysis_result['subsequent_low_date'],
                    current_price=analysis_result['current_price'],
                    resistance_distance_percent=analysis_result['resistance_distance_percent'],
                    years_of_data=analysis_result['years_of_data']
                )
                session.add(candidate)
            
            session.commit()
            logger.debug(f"Resultado guardado para {analysis_result['symbol']}")
            
        except Exception as e:
            logger.error(f"Error guardando resultado para {analysis_result['symbol']}: {e}")
            session.rollback()
        finally:
            session.close()
    
    def analyze_all_symbols(self):
        """Analiza todos los símbolos disponibles."""
        logger.info("Iniciando análisis de todos los símbolos...")
        
        self.symbols = self.get_all_symbols()
        self.analysis_stats['total_symbols'] = len(self.symbols)
        
        if not self.symbols:
            logger.error("No se encontraron símbolos para analizar")
            return
        
        # Procesar cada símbolo
        with tqdm(total=len(self.symbols), desc="Analizando símbolos") as pbar:
            for symbol in self.symbols:
                try:
                    pbar.set_description(f"Analizando {symbol}")
                    
                    # Verificar si debe ser analizado
                    if not self.should_analyze_symbol(symbol):
                        self.analysis_stats['skipped_recent_review'] += 1
                        pbar.update(1)
                        continue
                    
                    # Obtener datos del símbolo
                    df = self.get_symbol_data(symbol)
                    if df is None or df.empty:
                        self.analysis_stats['insufficient_data'] += 1
                        pbar.update(1)
                        continue
                    
                    # Analizar patrón
                    analysis_result = self.analyze_symbol_pattern(symbol, df)
                    
                    if analysis_result is None:
                        self.analysis_stats['insufficient_data'] += 1
                        pbar.update(1)
                        continue
                    
                    if not analysis_result.get('pattern_found', False):
                        self.analysis_stats['no_pattern_found'] += 1
                        pbar.update(1)
                        continue
                    
                    # Guardar resultado
                    self.save_analysis_result(analysis_result)
                    
                    self.analysis_stats['analyzed_symbols'] += 1
                    if analysis_result['is_valid_candidate']:
                        self.analysis_stats['valid_candidates'] += 1
                        logger.info(f"✓ Candidato válido encontrado: {symbol} "
                                  f"(distancia: {analysis_result['resistance_distance_percent']:.2f}%)")
                    
                except Exception as e:
                    logger.error(f"Error procesando símbolo {symbol}: {e}")
                    self.analysis_stats['errors'] += 1
                
                pbar.update(1)
    
    def print_summary(self):
        """Imprime un resumen del análisis."""
        logger.info("\n" + "="*50)
        logger.info("RESUMEN DEL ANÁLISIS DE RUPTURA")
        logger.info("="*50)
        logger.info(f"Total de símbolos: {self.analysis_stats['total_symbols']}")
        logger.info(f"Símbolos analizados: {self.analysis_stats['analyzed_symbols']}")
        logger.info(f"Candidatos válidos: {self.analysis_stats['valid_candidates']}")
        logger.info(f"Omitidos (revisión reciente): {self.analysis_stats['skipped_recent_review']}")
        logger.info(f"Datos insuficientes: {self.analysis_stats['insufficient_data']}")
        logger.info(f"Sin patrón encontrado: {self.analysis_stats['no_pattern_found']}")
        logger.info(f"Errores: {self.analysis_stats['errors']}")
        logger.info("="*50)
        
        # Guardar estadísticas en archivo JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_file = f"breakout_analysis_stats_{timestamp}.json"
        
        with open(stats_file, 'w') as f:
            json.dump(self.analysis_stats, f, indent=2, default=str)
        
        logger.info(f"Estadísticas guardadas en: {stats_file}")
    
    def get_valid_candidates(self) -> List[Dict]:
        """Obtiene todos los candidatos válidos de la base de datos."""
        try:
            session = self.session_maker()
            
            candidates = session.query(StrategyCandidate).filter_by(is_valid=True).all()
            
            result = []
            for candidate in candidates:
                result.append({
                    'symbol': candidate.symbol,
                    'historical_high': candidate.historical_high,
                    'current_price': candidate.current_price,
                    'resistance_distance_percent': candidate.resistance_distance_percent,
                    'last_review_date': candidate.last_review_date,
                    'years_of_data': candidate.years_of_data
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo candidatos válidos: {e}")
            return []
        finally:
            session.close()
    
    def run_analysis(self):
        """Ejecuta el análisis completo."""
        logger.info("Iniciando Breakout Strategy Analyzer...")
        
        # Conectar a base de datos
        if not self.connect_to_database():
            logger.error("No se pudo conectar a la base de datos. Terminando...")
            return False
        
        # Crear tabla de candidatos
        self.create_strategy_table()
        
        # Analizar todos los símbolos
        self.analyze_all_symbols()
        
        # Mostrar resumen
        self.print_summary()
        
        # Mostrar candidatos válidos
        valid_candidates = self.get_valid_candidates()
        if valid_candidates:
            logger.info(f"\nCANDIDATOS VÁLIDOS ACTUALES ({len(valid_candidates)}):")
            logger.info("-" * 80)
            for candidate in sorted(valid_candidates, key=lambda x: x['resistance_distance_percent']):
                logger.info(f"{candidate['symbol']:8} | "
                          f"Máximo: ${candidate['historical_high']:8.2f} | "
                          f"Actual: ${candidate['current_price']:8.2f} | "
                          f"Distancia: {candidate['resistance_distance_percent']:6.2f}%")
        
        logger.info("Análisis completado exitosamente")
        return True


def main():
    """Función principal."""
    analyzer = BreakoutAnalyzer()
    
    try:
        success = analyzer.run_analysis()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Análisis interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
