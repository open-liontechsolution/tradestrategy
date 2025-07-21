import axios from 'axios';

// Configuración base de la API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejo de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // El servidor respondió con un código de error
      throw new Error(error.response.data?.error || `Error ${error.response.status}: ${error.response.statusText}`);
    } else if (error.request) {
      // La petición se hizo pero no hubo respuesta
      throw new Error('No se pudo conectar con el servidor. Verifica que la API esté ejecutándose.');
    } else {
      // Error en la configuración de la petición
      throw new Error('Error en la petición: ' + error.message);
    }
  }
);

/**
 * Verifica el estado de la API
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Obtiene la lista de todos los símbolos disponibles
 */
export const fetchSymbols = async () => {
  try {
    const response = await api.get('/symbols');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Obtiene datos OHLCV para un símbolo específico
 * @param {string} symbol - Símbolo de la acción
 * @param {Object} params - Parámetros opcionales (start_date, end_date, limit)
 */
export const fetchSymbolData = async (symbol, params = {}) => {
  try {
    const response = await api.get(`/data/${symbol}`, { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Obtiene el último precio disponible para un símbolo
 * @param {string} symbol - Símbolo de la acción
 */
export const fetchLatestPrice = async (symbol) => {
  try {
    const response = await api.get(`/data/${symbol}/latest`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Busca símbolos que coincidan con la consulta
 * @param {string} query - Término de búsqueda
 */
export const searchSymbols = async (query) => {
  try {
    const response = await api.get(`/search/${query}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Formatea los datos para el gráfico
 * @param {Array} data - Datos OHLCV del API
 */
export const formatChartData = (data) => {
  return data.map(item => ({
    time: new Date(item.date).getTime() / 1000, // Convertir a timestamp Unix
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
    volume: item.volume
  }));
};

/**
 * Calcula indicadores técnicos básicos
 */
export const calculateIndicators = {
  /**
   * Media Móvil Simple (SMA)
   * @param {Array} data - Datos de precios
   * @param {number} period - Período de la media
   */
  sma: (data, period = 20) => {
    const sma = [];
    for (let i = period - 1; i < data.length; i++) {
      const sum = data.slice(i - period + 1, i + 1).reduce((acc, val) => acc + val.close, 0);
      sma.push({
        time: data[i].time,
        value: sum / period
      });
    }
    return sma;
  },

  /**
   * Media Móvil Exponencial (EMA)
   * @param {Array} data - Datos de precios
   * @param {number} period - Período de la media
   */
  ema: (data, period = 20) => {
    const ema = [];
    const multiplier = 2 / (period + 1);
    
    // Primera EMA es la SMA
    let sum = 0;
    for (let i = 0; i < period; i++) {
      sum += data[i].close;
    }
    let previousEMA = sum / period;
    ema.push({
      time: data[period - 1].time,
      value: previousEMA
    });

    // Calcular EMA para el resto de los datos
    for (let i = period; i < data.length; i++) {
      const currentEMA = (data[i].close - previousEMA) * multiplier + previousEMA;
      ema.push({
        time: data[i].time,
        value: currentEMA
      });
      previousEMA = currentEMA;
    }
    
    return ema;
  },

  /**
   * RSI (Relative Strength Index)
   * @param {Array} data - Datos de precios
   * @param {number} period - Período del RSI (típicamente 14)
   */
  rsi: (data, period = 14) => {
    const rsi = [];
    const gains = [];
    const losses = [];

    // Calcular cambios de precio
    for (let i = 1; i < data.length; i++) {
      const change = data[i].close - data[i - 1].close;
      gains.push(change > 0 ? change : 0);
      losses.push(change < 0 ? Math.abs(change) : 0);
    }

    // Calcular RSI
    for (let i = period - 1; i < gains.length; i++) {
      const avgGain = gains.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) / period;
      const avgLoss = losses.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) / period;
      
      const rs = avgGain / avgLoss;
      const rsiValue = 100 - (100 / (1 + rs));
      
      rsi.push({
        time: data[i + 1].time,
        value: rsiValue
      });
    }

    return rsi;
  },

  /**
   * Bandas de Bollinger
   * @param {Array} data - Datos de precios
   * @param {number} period - Período de la media (típicamente 20)
   * @param {number} stdDev - Desviaciones estándar (típicamente 2)
   */
  bollinger: (data, period = 20, stdDev = 2) => {
    const bands = { upper: [], middle: [], lower: [] };
    
    for (let i = period - 1; i < data.length; i++) {
      const slice = data.slice(i - period + 1, i + 1);
      const sma = slice.reduce((acc, val) => acc + val.close, 0) / period;
      
      const variance = slice.reduce((acc, val) => acc + Math.pow(val.close - sma, 2), 0) / period;
      const standardDeviation = Math.sqrt(variance);
      
      bands.middle.push({ time: data[i].time, value: sma });
      bands.upper.push({ time: data[i].time, value: sma + (standardDeviation * stdDev) });
      bands.lower.push({ time: data[i].time, value: sma - (standardDeviation * stdDev) });
    }
    
    return bands;
  }
};

export default api;
