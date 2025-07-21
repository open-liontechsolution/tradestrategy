#!/usr/bin/env python3
"""
Stock Data Loader
================

Script para descargar datos mensuales históricos de acciones y almacenarlos
en TimescaleDB para su análisis posterior.

Características:
- Lectura de símbolos desde el archivo generado por symbol_fetcher
- Descarga de datos OHLCV mensuales desde Yahoo Finance
- Almacenamiento eficiente en TimescaleDB
- Procesamiento en paralelo y gestión de errores
- Registro detallado del proceso

Autor: TradeStrategy Team
"""

import os
import sys
import time
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dateutil.relativedelta import relativedelta
import traceback

import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, text, Column, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm
from dateutil.relativedelta import relativedelta

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stock_data_loader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('StockDataLoader')

# Rutas de archivos
SCRIPT_DIR = Path(__file__).parent.resolve()
SYMBOLS_FILE = SCRIPT_DIR.parent.joinpath('market_data_tools', 'market_data', 'market_symbols.txt')
MAX_WORKERS = 3  # Número máximo de hilos para descarga en paralelo (reducido para evitar rate limit)
DEFAULT_START_DATE = "2000-01-01"  # Fecha de inicio por defecto para descarga
BATCH_SIZE = 10  # Tamaño del lote para inserciones en DB (reducido para testing)
RETRY_ATTEMPTS = 3  # Intentos de reintentos para llamadas a API
REQUEST_DELAY = 1.0  # Tiempo de espera entre solicitudes (en segundos)
SEQUENTIAL_MODE = False  # Si es True, procesa símbolos secuencialmente sin concurrencia
TEST_MODE = False  # Si es True, limita el número de símbolos a procesar
TEST_SYMBOLS_COUNT = 3  # Número de símbolos a procesar en modo prueba

# Configuración de conexión a TimescaleDB
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "stockdata",
    "user": "postgres",
    "password": "postgres"
}

# Definir el modelo SQLAlchemy para los datos de acciones
Base = declarative_base()

class StockPrice(Base):
    """Modelo para datos mensuales de acciones."""
    __tablename__ = 'stock_prices_monthly'

    # Columnas de datos
    symbol = Column(String, primary_key=True)
    date = Column(DateTime, primary_key=True)  # Será una hypertable en TimescaleDB
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    
    def __repr__(self):
        return f"<StockPrice(symbol='{self.symbol}', date='{self.date}')>"


class StockDataLoader:
    """Clase para cargar datos históricos mensuales de acciones en TimescaleDB."""
    
    def __init__(self):
        """Inicializa el cargador de datos de acciones."""
        self.engine = None
        self.session_maker = None
        self.symbols = []
        self.stats = {
            "total_symbols": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "total_records": 0,
            "start_time": datetime.now(),
            "end_time": None,
            "duration_seconds": 0
        }
    
    def connect_db(self):
        """Establece conexión con TimescaleDB."""
        try:
            # Crear cadena de conexión
            conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            
            # Crear engine SQLAlchemy
            self.engine = create_engine(conn_string)
            
            # Crear tablas si no existen
            Base.metadata.create_all(self.engine)
            
            # Configurar TimescaleDB hypertable
            with self.engine.connect() as conn:
                # Verificar si la extensión TimescaleDB está instalada
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
                conn.commit()
                
                # Crear la tabla si no existe (no borrar los datos existentes)
                Base.metadata.create_all(self.engine)
                
                # Verificar si la tabla es una hypertable y convertirla si no lo es
                try:
                    conn.execute(text("""
                        SELECT create_hypertable('stock_prices_monthly', 'date', 
                                                if_not_exists => TRUE);
                    """))
                    conn.commit()  # Confirmar la creación de la hypertable
                except SQLAlchemyError as e:
                    logger.warning(f"Error al crear hypertable: {e}")
                    conn.rollback()  # Revertir en caso de error
                
                # Crear índices para mejorar rendimiento
                try:
                    conn.execute(text(
                        "CREATE INDEX IF NOT EXISTS idx_stock_symbol ON stock_prices_monthly (symbol);"
                    ))
                    conn.commit()  # Confirmar la creación de índices
                except SQLAlchemyError as e:
                    logger.warning(f"Error al crear índice: {e}")
                    conn.rollback()  # Revertir en caso de error
                
                conn.commit()
            
            # Crear session maker
            self.session_maker = sessionmaker(bind=self.engine)
            logger.info("Conexión a TimescaleDB establecida correctamente")
            return True
        
        except Exception as e:
            logger.error(f"Error al conectar con TimescaleDB: {e}")
            return False
    
    def load_symbols(self):
        """Carga los símbolos desde el archivo generado por symbol_fetcher."""
        try:
            if not SYMBOLS_FILE.exists():
                logger.error(f"Archivo de símbolos no encontrado: {SYMBOLS_FILE}")
                return False
            
            # Leer símbolos del archivo de texto
            with open(SYMBOLS_FILE, "r") as f:
                self.symbols = [line.strip() for line in f if line.strip()]
                
            # Si estamos en modo prueba, limitamos a un pequeño conjunto de símbolos
            if TEST_MODE:
                self.symbols = self.symbols[:TEST_SYMBOLS_COUNT]
            
            self.stats["total_symbols"] = len(self.symbols)
            logger.info(f"Cargados {len(self.symbols)} símbolos desde {SYMBOLS_FILE}")
            return True
        
        except Exception as e:
            logger.error(f"Error al cargar símbolos: {e}")
            return False
    
    @retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_exponential(multiplier=1, min=4, max=60))
    def download_stock_data(self, symbol):
        """Descarga datos históricos mensuales para un símbolo."""
        try:
            # Obtener la última fecha disponible para este símbolo y si necesita actualización
            date_info = self.get_last_date_for_symbol(symbol)
            
            # Si no necesita actualización, salir rápidamente
            if not date_info['need_update']:
                # Ya está registrado el log en get_last_date_for_symbol
                return symbol, None
            
            # Obtener la fecha de inicio para la descarga
            start_date = date_info['start_date']
            
            # Añadir sleep para evitar rate limits
            time.sleep(REQUEST_DELAY)
            
            # Obtener ticker de Yahoo Finance
            ticker = yf.Ticker(symbol)
            
            # Descargar datos mensuales desde la fecha de inicio 
            df = ticker.history(start=start_date, interval="1mo")
            
            # Verificar si hay datos
            if df.empty:
                logger.warning(f"No se encontraron datos para {symbol}")
                return symbol, None
            
            # Depuración: mostrar columnas disponibles
            logger.info(f"Columnas disponibles para {symbol}: {list(df.columns)}")
            
            # Resetear el índice para tener la fecha como columna
            df = df.reset_index()
            
            # Añadir columna de símbolo
            df['Symbol'] = symbol
            
            # Renombrar columnas directamente (simplificado)
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
                'Symbol': 'symbol'
            })
            
            # Seleccionar y ordenar columnas relevantes
            columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
            df = df[columns].copy()
            
            # Ordenar por fecha
            df = df.sort_values('date')
            
            logger.debug(f"Descargados {len(df)} registros para {symbol}")
            return symbol, df
        
        except Exception as e:
            logger.error(f"Error descargando datos para {symbol}: {e}")
            return symbol, None
    
    def get_last_date_for_symbol(self, symbol):
        """Obtiene la última fecha disponible para un símbolo.
        
        Retorna un diccionario con:
        - need_update: True si necesita actualizar, False si ya está al día
        - start_date: La fecha desde la que se deberían descargar nuevos datos
        - last_date: La última fecha disponible en la base de datos
        """
        try:
            # Crear sesión
            session = self.session_maker()
            
            # Consultar la última fecha para este símbolo
            result = session.query(func.max(StockPrice.date))\
                    .filter(StockPrice.symbol == symbol)\
                    .scalar()
            
            # Verificar si ya tenemos datos actualizados (hasta el mes actual o el anterior)
            current_date = datetime.now()
            current_month_start = datetime(current_date.year, current_date.month, 1)
            previous_month = current_date.month - 1 if current_date.month > 1 else 12
            previous_year = current_date.year if current_date.month > 1 else current_date.year - 1
            previous_month_start = datetime(previous_year, previous_month, 1)
            
            # Si hay datos, verificar si están actualizados
            if result:
                # Si los datos son del mes actual o anterior, están actualizados
                if ((result.year == current_date.year and result.month == current_date.month) or
                    (result.year == previous_year and result.month == previous_month)):
                    logger.info(f"Datos para {symbol} ya actualizados hasta {result.strftime('%Y-%m-%d')}, no es necesario descargar")
                    return {'need_update': False, 'start_date': None, 'last_date': result}
                else:
                    # Si no están actualizados, descargar desde el mes siguiente al último dato
                    next_date = result + relativedelta(months=1)
                    logger.info(f"Datos existentes para {symbol} hasta {result}, continuando desde {next_date}")
                    return {'need_update': True, 'start_date': next_date, 'last_date': result}
            else:
                # Si no hay datos previos, descargar desde el inicio
                logger.info(f"No hay datos previos para {symbol}, descargando desde el inicio")
                return {'need_update': True, 'start_date': DEFAULT_START_DATE, 'last_date': None}
                
        except Exception as e:
            logger.error(f"Error al obtener la última fecha para {symbol}: {e}")
            return {'need_update': True, 'start_date': DEFAULT_START_DATE, 'last_date': None}
        finally:
            session.close()
    
    def save_to_db(self, dataframes):
        """Guarda los datos en la base de datos TimescaleDB."""
        if not dataframes:
            logger.warning("No hay datos para guardar en la base de datos")
            return 0
        
        try:
            # Concatenar todos los dataframes
            combined_df = pd.concat(dataframes, ignore_index=True)
            
            # Asegurar que no hay filas duplicadas (misma fecha y símbolo)
            combined_df = combined_df.drop_duplicates(subset=["symbol", "date"])
            
            records_saved = 0
            
            # Crear sesión de base de datos
            session = self.session_maker()
            
            try:
                # Usar inserción masiva para mejor rendimiento
                total_rows = len(combined_df)
                
                for i in range(0, total_rows, BATCH_SIZE):
                    batch = combined_df.iloc[i:i+BATCH_SIZE]
                    
                    # Ejecutar consulta directamente para upsert (actualizar o insertar)
                    values = []
                    for _, row in batch.iterrows():
                        values.append({
                            'symbol': row['symbol'],
                            'date': row['date'],
                            'open': row['open'],
                            'high': row['high'],
                            'low': row['low'],
                            'close': row['close'],
                            'volume': row['volume']
                        })
                    
                    # Usar SQLAlchemy para el upsert
                    insert_stmt = text("""
                        INSERT INTO stock_prices_monthly 
                        (symbol, date, open, high, low, close, volume)
                        VALUES (:symbol, :date, :open, :high, :low, :close, :volume)
                        ON CONFLICT (symbol, date) DO UPDATE SET
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume
                    """)
                    
                    session.execute(insert_stmt, values)
                    session.commit()
                    
                    records_saved += len(batch)
                    logger.debug(f"Guardados {records_saved}/{total_rows} registros en la base de datos")
            
            except Exception as e:
                session.rollback()
                logger.error(f"Error al guardar datos en la base de datos: {e}")
                raise
            
            finally:
                session.close()
            
            logger.info(f"Guardados {records_saved} registros en total en la base de datos")
            return records_saved
        
        except Exception as e:
            logger.error(f"Error en save_to_db: {e}")
            return 0
    
    def process_symbols_parallel(self, symbols):
        """Procesa varios símbolos en paralelo o secuencialmente."""
        successful = 0
        failed = 0
        dataframes = []
        
        # Mostrar progreso
        with tqdm(total=len(symbols), desc="Descargando datos") as pbar:
            # Modo secuencial (para mitigar problemas de rate limit)
            if SEQUENTIAL_MODE:
                for symbol in symbols:
                    try:
                        symbol, df = self.download_stock_data(symbol)
                        
                        if df is not None and not df.empty:
                            dataframes.append(df)
                            successful += 1
                        else:
                            failed += 1
                    
                    except Exception as e:
                        logger.error(f"Error procesando {symbol}: {e}")
                        failed += 1
                    
                    finally:
                        pbar.update(1)
            
            # Modo paralelo (con menos trabajadores para mitigar rate limit)
            else:
                # Usar ThreadPoolExecutor para procesar en paralelo
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    future_to_symbol = {executor.submit(self.download_stock_data, symbol): symbol for symbol in symbols}
                    
                    # Procesar resultados a medida que se completan
                    for future in as_completed(future_to_symbol):
                        symbol = future_to_symbol[future]
                        try:
                            symbol, df = future.result()
                            
                            if df is not None and not df.empty:
                                dataframes.append(df)
                                successful += 1
                            else:
                                failed += 1
                        
                        except Exception as e:
                            logger.error(f"Error procesando {symbol}: {e}")
                            failed += 1
                        
                        finally:
                            pbar.update(1)
        
        # Actualizar estadísticas
        self.stats["successful_downloads"] += successful
        self.stats["failed_downloads"] += failed
        
        # Guardar lote en la base de datos
        if dataframes:
            records_saved = self.save_to_db(dataframes)
            self.stats["total_records"] += records_saved
        
        return successful, failed
    
    def process_all_symbols(self):
        """Procesa todos los símbolos en lotes para gestión de memoria."""
        total_symbols = len(self.symbols)
        logger.info(f"Iniciando procesamiento de {total_symbols} símbolos en lotes de {BATCH_SIZE}")
        
        # Procesar en lotes para evitar problemas de memoria
        for i in range(0, total_symbols, BATCH_SIZE):
            batch = self.symbols[i:i+BATCH_SIZE]
            logger.info(f"Procesando lote {i//BATCH_SIZE + 1}/{(total_symbols-1)//BATCH_SIZE + 1} ({len(batch)} símbolos)")
            
            successful, failed = self.process_symbols_parallel(batch)
            logger.info(f"Lote completado. Éxito: {successful}, Fallos: {failed}")
    
    def save_stats(self):
        """Guarda estadísticas de la ejecución en un archivo JSON."""
        self.stats["end_time"] = datetime.now()
        self.stats["duration_seconds"] = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        # Convertir datetime a string para JSON
        self.stats["start_time"] = self.stats["start_time"].isoformat()
        self.stats["end_time"] = self.stats["end_time"].isoformat()
        
        # Guardar en archivo JSON
        stats_file = f"stock_data_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)
        
        logger.info(f"Estadísticas guardadas en {stats_file}")
    
    def run(self):
        """Ejecuta el proceso completo de carga de datos."""
        logger.info("Iniciando proceso de carga de datos históricos de acciones")
        
        # 1. Conectar a la base de datos
        if not self.connect_db():
            logger.error("No se pudo conectar a la base de datos. Abortando.")
            return False
        
        # 2. Cargar símbolos
        if not self.load_symbols():
            logger.error("No se pudieron cargar los símbolos. Abortando.")
            return False
        
        # 3. Procesar todos los símbolos
        try:
            self.process_all_symbols()
            
            # 4. Guardar estadísticas
            self.save_stats()
            
            logger.info("Proceso de carga de datos completado")
            return True
        
        except Exception as e:
            logger.error(f"Error en el proceso de carga: {e}")
            traceback.print_exc()
            return False


def check_timescale_db():
    """Verifica si TimescaleDB está accesible."""
    from sqlalchemy import inspect
    
    try:
        # Crear cadena de conexión
        conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        
        # Intentar conectar
        engine = create_engine(conn_string)
        inspector = inspect(engine)
        
        # Verificar extensión TimescaleDB
        with engine.connect() as conn:
            result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'timescaledb';"))
            if not result.fetchone():
                logger.warning("La extensión TimescaleDB no está instalada en la base de datos")
                return False
            
            logger.info("Conexión exitosa a TimescaleDB")
            return True
    
    except Exception as e:
        logger.error(f"Error al verificar TimescaleDB: {e}")
        logger.error("Asegúrese de que el contenedor Docker de TimescaleDB esté en ejecución:")
        logger.error("  docker-compose up -d")
        return False


def print_summary(stats):
    """Imprime un resumen de la ejecución."""
    print("\n" + "=" * 60)
    print("RESUMEN DE CARGA DE DATOS")
    print("=" * 60)
    
    # Calcular estadísticas adicionales
    success_rate = stats["successful_downloads"] / stats["total_symbols"] * 100 if stats["total_symbols"] > 0 else 0
    
    print(f"Total de símbolos procesados: {stats['total_symbols']}")
    print(f"Descargas exitosas: {stats['successful_downloads']} ({success_rate:.1f}%)")
    print(f"Descargas fallidas: {stats['failed_downloads']}")
    print(f"Total de registros guardados: {stats['total_records']:,}")
    
    # Calcular duración
    if isinstance(stats["duration_seconds"], (int, float)):
        minutes, seconds = divmod(stats["duration_seconds"], 60)
        hours, minutes = divmod(minutes, 60)
        print(f"Duración total: {int(hours)}h {int(minutes)}m {int(seconds)}s")
    
    print("=" * 60)


def main():
    """Función principal."""
    print("=" * 60)
    print("CARGADOR DE DATOS HISTÓRICOS DE ACCIONES")
    print("=" * 60)
    print("Este script descarga datos mensuales históricos para todos los símbolos")
    print("y los almacena en una base de datos TimescaleDB.")
    print()
    
    # Verificar TimescaleDB antes de proceder
    print("Verificando conexión a TimescaleDB...")
    if not check_timescale_db():
        print("\n⚠️  TimescaleDB no está disponible.")
        print("Asegúrese de que el contenedor Docker esté en ejecución:")
        print("  docker-compose up -d")
        sys.exit(1)
    
    print("\nProcesando datos históricos mensuales...")
    loader = StockDataLoader()
    success = loader.run()
    
    if success:
        print_summary(loader.stats)
    else:
        print("\n❌ El proceso de carga de datos falló. Revise los logs para más detalles.")
        sys.exit(1)


if __name__ == "__main__":
    main()
