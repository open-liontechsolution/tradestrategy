#!/usr/bin/env python3
"""
Market Data API
===============

REST API para servir datos de mercado desde TimescaleDB al frontend.

Endpoints:
- GET /api/symbols - Lista todos los símbolos disponibles
- GET /api/data/{symbol} - Datos OHLCV para un símbolo específico
- GET /api/data/{symbol}/latest - Último precio para un símbolo
- GET /api/health - Estado de la API y base de datos

Autor: TradeStrategy Team
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MarketDataAPI')

# Configuración de la aplicación Flask
app = Flask(__name__)
CORS(app)  # Permitir CORS para el frontend

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'stockdata',
    'user': 'postgres',
    'password': 'postgres'
}

# Motor de base de datos global
engine = None

def init_db():
    """Inicializa la conexión a la base de datos."""
    global engine
    try:
        connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        engine = create_engine(connection_string, pool_size=10, max_overflow=20)
        
        # Probar la conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        logger.info("Conexión a TimescaleDB establecida correctamente")
        return True
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud de la API."""
    try:
        if engine is None:
            return jsonify({
                'status': 'error',
                'message': 'Base de datos no inicializada'
            }), 500
        
        # Probar conexión a la base de datos
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM stock_prices_monthly LIMIT 1"))
            count = result.fetchone()[0]
        
        return jsonify({
            'status': 'ok',
            'message': 'API funcionando correctamente',
            'database': 'connected',
            'total_records': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/symbols', methods=['GET'])
def get_symbols():
    """Obtiene la lista de todos los símbolos disponibles."""
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT DISTINCT symbol, 
                       COUNT(*) as data_points,
                       MIN(date) as first_date,
                       MAX(date) as last_date
                FROM stock_prices_monthly 
                GROUP BY symbol 
                ORDER BY symbol
            """)
            result = conn.execute(query)
            
            symbols = []
            for row in result:
                symbols.append({
                    'symbol': row[0],
                    'data_points': row[1],
                    'first_date': row[2].isoformat() if row[2] else None,
                    'last_date': row[3].isoformat() if row[3] else None
                })
        
        return jsonify({
            'symbols': symbols,
            'total': len(symbols)
        })
    except Exception as e:
        logger.error(f"Error obteniendo símbolos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/<symbol>', methods=['GET'])
def get_symbol_data(symbol):
    """Obtiene datos OHLCV para un símbolo específico."""
    try:
        # Parámetros de consulta opcionales
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', type=int)
        
        # Construir consulta base
        query_parts = [
            "SELECT date, open, high, low, close, volume",
            "FROM stock_prices_monthly",
            "WHERE symbol = :symbol"
        ]
        
        params = {'symbol': symbol.upper()}
        
        # Agregar filtros de fecha si se proporcionan
        if start_date:
            query_parts.append("AND date >= :start_date")
            params['start_date'] = start_date
        
        if end_date:
            query_parts.append("AND date <= :end_date")
            params['end_date'] = end_date
        
        query_parts.append("ORDER BY date ASC")
        
        # Agregar límite si se proporciona
        if limit:
            query_parts.append("LIMIT :limit")
            params['limit'] = limit
        
        query = text(" ".join(query_parts))
        
        with engine.connect() as conn:
            result = conn.execute(query, params)
            
            data = []
            for row in result:
                data.append({
                    'date': row[0].isoformat(),
                    'open': float(row[1]) if row[1] else None,
                    'high': float(row[2]) if row[2] else None,
                    'low': float(row[3]) if row[3] else None,
                    'close': float(row[4]) if row[4] else None,
                    'adj_close': float(row[4]) if row[4] else None,  # Use close as adj_close
                    'volume': float(row[5]) if row[5] else None
                })
        
        if not data:
            return jsonify({
                'error': f'No se encontraron datos para el símbolo {symbol}'
            }), 404
        
        return jsonify({
            'symbol': symbol.upper(),
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo datos para {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/<symbol>/latest', methods=['GET'])
def get_latest_price(symbol):
    """Obtiene el último precio disponible para un símbolo."""
    try:
        query = text("""
            SELECT date, open, high, low, close, volume
            FROM stock_prices_monthly
            WHERE symbol = :symbol
            ORDER BY date DESC
            LIMIT 1
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {'symbol': symbol.upper()})
            row = result.fetchone()
            
            if not row:
                return jsonify({
                    'error': f'No se encontraron datos para el símbolo {symbol}'
                }), 404
            
            return jsonify({
                'symbol': symbol.upper(),
                'latest': {
                    'date': row[0].isoformat(),
                    'open': float(row[1]) if row[1] else None,
                    'high': float(row[2]) if row[2] else None,
                    'low': float(row[3]) if row[3] else None,
                    'close': float(row[4]) if row[4] else None,
                    'adj_close': float(row[4]) if row[4] else None,  # Use close as adj_close
                    'volume': float(row[5]) if row[5] else None
                }
            })
            
    except Exception as e:
        logger.error(f"Error obteniendo último precio para {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/<query>', methods=['GET'])
def search_symbols(query):
    """Busca símbolos que coincidan con la consulta."""
    try:
        search_query = text("""
            SELECT DISTINCT symbol,
                   COUNT(*) as data_points,
                   MAX(date) as last_date
            FROM stock_prices_monthly 
            WHERE symbol ILIKE :query
            GROUP BY symbol 
            ORDER BY symbol
            LIMIT 50
        """)
        
        with engine.connect() as conn:
            result = conn.execute(search_query, {'query': f'%{query.upper()}%'})
            
            symbols = []
            for row in result:
                symbols.append({
                    'symbol': row[0],
                    'data_points': row[1],
                    'last_date': row[2].isoformat() if row[2] else None
                })
        
        return jsonify({
            'query': query,
            'symbols': symbols,
            'count': len(symbols)
        })
        
    except Exception as e:
        logger.error(f"Error buscando símbolos: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Inicializar base de datos
    if not init_db():
        logger.error("No se pudo inicializar la base de datos. Saliendo...")
        exit(1)
    
    # Ejecutar la aplicación
    logger.info("Iniciando Market Data API...")
    app.run(host='0.0.0.0', port=5000, debug=True)
