import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import styled from 'styled-components';

const Container = styled.div`
  position: relative;
  width: 100%;
  height: 500px;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const ChartWrapper = styled.div`
  width: 100%;
  height: 100%;
`;

const ChartControls = styled.div`
  position: absolute;
  top: 15px;
  right: 15px;
  display: flex;
  gap: 8px;
  z-index: 1000;
  flex-wrap: wrap;
  max-width: 280px;
  justify-content: flex-end;
  margin-right: 60px;
`;

const DrawingControls = styled.div`
  position: absolute;
  top: 80px;
  left: 15px;
  display: flex;
  gap: 8px;
  z-index: 1000;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 8px;
  padding: 8px;
  backdrop-filter: blur(10px);
`;

const ControlButton = styled.button`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.4);
  }
  
  &.active {
    background: rgba(74, 144, 226, 0.8);
    border-color: rgba(74, 144, 226, 1);
  }
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.1rem;
  z-index: 20;
`;

const DrawingStatus = styled.div`
  position: absolute;
  bottom: 15px;
  left: 15px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  z-index: 1000;
  backdrop-filter: blur(10px);
`;

const ChartContainer = ({ data, symbol, indicators, timeframe, onTimeframeChange }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef();
  const candlestickSeriesRef = useRef();
  const volumeSeriesRef = useRef();
  const indicatorSeriesRef = useRef({});
  
  const [chartType, setChartType] = useState('candlestick');
  const [loading, setLoading] = useState(false);
  const [showVolume, setShowVolume] = useState(true);
  const [drawingMode, setDrawingMode] = useState(null);
  const [drawnLines, setDrawnLines] = useState([]);
  const [measurementPoints, setMeasurementPoints] = useState([]);
  const [isInitializing, setIsInitializing] = useState(false);

  // Inicializar el gráfico
  useEffect(() => {
    if (!chartContainerRef.current || !data || data.length === 0 || isInitializing) {
      return;
    }
    
    setIsInitializing(true);

    // Limpiar el gráfico anterior si existe
    if (chartRef.current) {
      try {
        chartRef.current.remove();
      } catch (e) {
        console.log('Error al limpiar gráfico:', e);
      } finally {
        chartRef.current = null;
        candlestickSeriesRef.current = null;
        volumeSeriesRef.current = null;
      }
    }
    
    try {
      // Validar que el contenedor tenga dimensiones
      const containerWidth = chartContainerRef.current.clientWidth;
      const containerHeight = chartContainerRef.current.clientHeight;
      
      if (containerWidth === 0 || containerHeight === 0) {
        // Retry after a short delay if container has no dimensions
        setTimeout(() => {
          if (chartContainerRef.current && 
              chartContainerRef.current.clientWidth > 0 && 
              chartContainerRef.current.clientHeight > 0) {
            // Trigger re-render by updating a state
            setLoading(prev => !prev);
          }
        }, 100);
        return;
      }

      const chart = createChart(chartContainerRef.current, {
          layout: {
            background: { color: 'transparent' },
            textColor: '#d1d4dc',
          },
          grid: {
            vertLines: { color: 'rgba(42, 46, 57, 0.6)' },
            horzLines: { color: 'rgba(255, 255, 255, 0.1)' },
          },
          timeScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
            timeVisible: true,
          },
          crosshair: {
            mode: 1,
          },
          rightPriceScale: {
            borderColor: 'rgba(255, 255, 255, 0.3)',
          },
          width: containerWidth,
          height: containerHeight,
        });

        chartRef.current = chart;

        // Configurar series de velas/línea
        let mainSeries;
        if (chartType === 'candlestick') {
          mainSeries = chart.addCandlestickSeries({
            upColor: '#4ade80',
            downColor: '#f87171',
            borderUpColor: '#4ade80',
            borderDownColor: '#f87171',
            wickUpColor: '#4ade80',
            wickDownColor: '#f87171',
          });
        } else {
          mainSeries = chart.addLineSeries({
            color: '#4ade80',
            lineWidth: 2,
          });
        }

        candlestickSeriesRef.current = mainSeries;

        // Agregar serie de volumen solo si está activada
        let volumeSeries = null;
        if (showVolume) {
          volumeSeries = chart.addHistogramSeries({
            color: 'rgba(74, 144, 226, 0.5)',
            priceFormat: {
              type: 'volume',
            },
            priceScaleId: '',
            scaleMargins: {
              top: 0.7,
              bottom: 0,
            },
          });
          volumeSeriesRef.current = volumeSeries;
        }

        // Configurar datos - convertir formato de fecha si es necesario
        const chartData = data.map(item => {
          let time = item.time || item.date;
          
          // Convertir fecha a timestamp si es string
          if (typeof time === 'string') {
            time = new Date(time).getTime() / 1000;
          } else if (time instanceof Date) {
            time = time.getTime() / 1000;
          }
          
          return {
            time: time,
            open: parseFloat(item.open),
            high: parseFloat(item.high),
            low: parseFloat(item.low),
            close: parseFloat(item.close),
          };
        }).filter(item => 
          !isNaN(item.time) && 
          !isNaN(item.open) && 
          !isNaN(item.high) && 
          !isNaN(item.low) && 
          !isNaN(item.close)
        ).sort((a, b) => a.time - b.time);

        if (chartData.length === 0) {
          console.warn('No valid chart data after processing');
          return;
        }

        mainSeries.setData(chartData);

        if (volumeSeries) {
          const volumeData = chartData.map(item => {
            const originalItem = data.find(d => {
              let time = d.time || d.date;
              if (typeof time === 'string') {
                time = new Date(time).getTime() / 1000;
              } else if (time instanceof Date) {
                time = time.getTime() / 1000;
              }
              return Math.abs(time - item.time) < 1; // Allow 1 second tolerance
            });
            
            return {
              time: item.time,
              value: parseFloat(originalItem?.volume || 0),
              color: item.close >= item.open ? 'rgba(76, 175, 80, 0.5)' : 'rgba(244, 67, 54, 0.5)',
            };
          }).filter(item => !isNaN(item.value) && item.value > 0);
          
          // Volume data processed successfully
          volumeSeries.setData(volumeData);
        }

        // Manejar redimensionamiento
        const handleResize = () => {
          if (chartContainerRef.current && chart) {
            chart.applyOptions({
              width: chartContainerRef.current.clientWidth,
              height: chartContainerRef.current.clientHeight,
            });
          }
        };

        window.addEventListener('resize', handleResize);

        // Añadir escala de tiempo y ajustar contenido
        try {
          chart.timeScale().fitContent();
        } catch (error) {
          console.warn('Error al ajustar escala de tiempo:', error);
        }

        // Store chart reference for drawing tools
        chartRef.current = chart;
        
        // Add click handler for drawing tools
        const handleChartClick = (param) => {
          if (!param.point || !param.time || !candlestickSeriesRef.current) return;
          
          const price = candlestickSeriesRef.current.coordinateToPrice(param.point.y);
          
          // Get current drawing mode from state
          const currentDrawingMode = drawingMode;
          
          if (currentDrawingMode === 'horizontal-line') {
            // Create horizontal line immediately
            if (candlestickSeriesRef.current) {
              const priceLine = candlestickSeriesRef.current.createPriceLine({
                price: price,
                color: '#2196F3',
                lineWidth: 2,
                lineStyle: 0,
                axisLabelVisible: true,
                title: `Línea: $${price.toFixed(2)}`,
              });
              setDrawnLines(prev => [...prev, priceLine]);
            }
          } else if (currentDrawingMode === 'ruler') {
              const newPoint = { time: param.time, price: price };
              
              if (measurementPoints.length === 0) {
                setMeasurementPoints([newPoint]);
              } else if (measurementPoints.length === 1) {
                const measurement = calculateMeasurement(measurementPoints[0], newPoint);
                
                // Create a temporary price line to show the measurement
                const measurementLine = candlestickSeriesRef.current.createPriceLine({
                  price: (measurementPoints[0].price + newPoint.price) / 2,
                  color: '#FF9800',
                  lineWidth: 1,
                  lineStyle: 1, // Dashed line
                  axisLabelVisible: true,
                  title: `Δ ${measurement.percentChange}% ($${measurement.priceDiff})`,
                });
                
                // Show measurement in a more professional way
                const measurementText = `📐 MEDICIÓN COMPLETADA\n\n` +
                  `💰 Diferencia de precio: $${measurement.priceDiff}\n` +
                  `📈 Cambio porcentual: ${measurement.percentChange}%\n` +
                  `📅 Tiempo transcurrido: ${measurement.timeDiff} días\n\n` +
                  `Punto 1: $${measurementPoints[0].price.toFixed(2)}\n` +
                  `Punto 2: $${newPoint.price.toFixed(2)}`;
                
                alert(measurementText);
                
                // Remove the measurement line after 5 seconds
                setTimeout(() => {
                  if (candlestickSeriesRef.current) {
                    candlestickSeriesRef.current.removePriceLine(measurementLine);
                  }
                }, 5000);
                
                setMeasurementPoints([]);
              }
            }
          };


        // Cleanup function
        return () => {
          window.removeEventListener('resize', handleResize);
          if (chart && chartRef.current) {
            try {
              chart.remove();
            } catch (error) {
              console.warn('Error removing chart in cleanup:', error);
            } finally {
              chartRef.current = null;
              candlestickSeriesRef.current = null;
              volumeSeriesRef.current = null;
              setDrawnLines([]);
              
              // Limpiar todas las series de indicadores
              Object.keys(indicatorSeriesRef.current).forEach(key => {
                indicatorSeriesRef.current[key] = null;
              });
            }
          }
        };
      } catch (error) {
        console.error('Error al inicializar el gráfico:', error.message || error);
        // Solo mostrar el error si es significativo
        if (error.message && !error.message.includes('disposed')) {
          console.warn('Chart initialization failed:', error.message);
        }
      } finally {
        setIsInitializing(false);
      }
  }, [data, chartType, showVolume]);

  // Separate useEffect for drawing tools to avoid re-initializing the entire chart
  useEffect(() => {
    if (!chartRef.current || !candlestickSeriesRef.current) return;

    const chart = chartRef.current;
    
    const handleChartClick = (param) => {
      if (!param.point || !param.time || !candlestickSeriesRef.current) return;
      
      const price = candlestickSeriesRef.current.coordinateToPrice(param.point.y);
      
      if (drawingMode === 'horizontal-line') {
        // Create horizontal line immediately
        const priceLine = candlestickSeriesRef.current.createPriceLine({
          price: price,
          color: '#2196F3',
          lineWidth: 2,
          lineStyle: 0,
          axisLabelVisible: true,
          title: `Línea: $${price.toFixed(2)}`,
        });
        setDrawnLines(prev => [...prev, priceLine]);
      } else if (drawingMode === 'ruler') {
        const newPoint = { time: param.time, price: price };
        
        if (measurementPoints.length === 0) {
          setMeasurementPoints([newPoint]);
        } else if (measurementPoints.length === 1) {
          const measurement = calculateMeasurement(measurementPoints[0], newPoint);
          
          // Create a temporary price line to show the measurement
          const measurementLine = candlestickSeriesRef.current.createPriceLine({
            price: (measurementPoints[0].price + newPoint.price) / 2,
            color: '#FF9800',
            lineWidth: 1,
            lineStyle: 1,
            axisLabelVisible: true,
            title: `Δ ${measurement.percentChange}% ($${measurement.priceDiff})`,
          });
          
          // Show measurement
          const measurementText = `📐 MEDICIÓN COMPLETADA\n\n` +
            `💰 Diferencia de precio: $${measurement.priceDiff}\n` +
            `📈 Cambio porcentual: ${measurement.percentChange}%\n` +
            `📅 Tiempo transcurrido: ${measurement.timeDiff} días\n\n` +
            `Punto 1: $${measurementPoints[0].price.toFixed(2)}\n` +
            `Punto 2: $${newPoint.price.toFixed(2)}`;
          
          alert(measurementText);
          
          // Remove the measurement line after 5 seconds
          setTimeout(() => {
            if (candlestickSeriesRef.current) {
              candlestickSeriesRef.current.removePriceLine(measurementLine);
            }
          }, 5000);
          
          setMeasurementPoints([]);
        }
      }
    };

    // Subscribe to click events
    chart.subscribeClick(handleChartClick);

    // Cleanup
    return () => {
      try {
        chart.unsubscribeClick(handleChartClick);
      } catch (e) {
        // Ignore cleanup errors
      }
    };
  }, [drawingMode, measurementPoints]);

  // Actualizar indicadores técnicos
  useEffect(() => {
    if (chartRef.current && candlestickSeriesRef.current && indicators) {
      // Limpiar indicadores anteriores
      Object.values(indicatorSeriesRef.current).forEach(series => {
        if (series) {
          try {
            chartRef.current.removeSeries(series);
          } catch (e) {
            console.warn('Error removing indicator series:', e);
          }
        }
      });
      indicatorSeriesRef.current = {};

      // Agregar nuevos indicadores
      if (indicators.sma && indicators.sma.length > 0) {
        const smaSeries = chartRef.current.addLineSeries({
          color: '#ff6b6b',
          lineWidth: 2,
          title: 'SMA',
        });
        smaSeries.setData(indicators.sma);
        indicatorSeriesRef.current.sma = smaSeries;
      }

      if (indicators.ema && indicators.ema.length > 0) {
        const emaSeries = chartRef.current.addLineSeries({
          color: '#4ecdc4',
          lineWidth: 2,
          title: 'EMA',
        });
        emaSeries.setData(indicators.ema);
        indicatorSeriesRef.current.ema = emaSeries;
      }

      if (indicators.bollinger && indicators.bollinger.upper.length > 0) {
        const upperSeries = chartRef.current.addLineSeries({
          color: '#ffd93d',
          lineWidth: 1,
          title: 'BB Upper',
        });
        upperSeries.setData(indicators.bollinger.upper);
        indicatorSeriesRef.current.bbUpper = upperSeries;

        const lowerSeries = chartRef.current.addLineSeries({
          color: '#ffd93d',
          lineWidth: 1,
          title: 'BB Lower',
        });
        lowerSeries.setData(indicators.bollinger.lower);
        indicatorSeriesRef.current.bbLower = lowerSeries;
      }
    }
  }, [indicators]);

  const handleChartTypeChange = (type) => {
    setChartType(type);
  };

  const handleVolumeToggle = () => {
    setShowVolume(!showVolume);
  };

  // Funciones para herramientas de dibujo
  const handleDrawingModeChange = (mode) => {
    setDrawingMode(drawingMode === mode ? null : mode);
    setMeasurementPoints([]); // Reset measurement points when changing mode
  };

  const clearAllDrawings = () => {
    // Clear horizontal lines
    drawnLines.forEach(line => {
      if (candlestickSeriesRef.current) {
        candlestickSeriesRef.current.removePriceLine(line);
      }
    });
    setDrawnLines([]);
    setMeasurementPoints([]);
  };

  const addHorizontalLine = (price) => {
    if (candlestickSeriesRef.current) {
      const priceLine = candlestickSeriesRef.current.createPriceLine({
        price: price,
        color: '#2196F3',
        lineWidth: 2,
        lineStyle: 0, // Solid line
        axisLabelVisible: true,
        title: `Línea: $${price.toFixed(2)}`,
      });
      setDrawnLines(prev => [...prev, priceLine]);
    }
  };

  const calculateMeasurement = (point1, point2) => {
    const priceDiff = Math.abs(point2.price - point1.price);
    const percentChange = ((point2.price - point1.price) / point1.price) * 100;
    const timeDiff = Math.abs(point2.time - point1.time);
    
    return {
      priceDiff: priceDiff.toFixed(2),
      percentChange: percentChange.toFixed(2),
      timeDiff: Math.round(timeDiff / (24 * 60 * 60)) // Convert to days
    };
  };

  const handleTimeframeChange = (tf) => {
    if (onTimeframeChange) {
      onTimeframeChange(tf);
    }
  };

  if (!data || data.length === 0) {
    return (
      <Container>
        <LoadingOverlay>
          Selecciona un símbolo para ver el gráfico
        </LoadingOverlay>
      </Container>
    );
  }

  return (
    <Container>
      <ChartControls>
        <ControlButton
          className={chartType === 'candlestick' ? 'active' : ''}
          onClick={() => handleChartTypeChange('candlestick')}
        >
          Velas
        </ControlButton>
        <ControlButton
          className={chartType === 'line' ? 'active' : ''}
          onClick={() => handleChartTypeChange('line')}
        >
          Línea
        </ControlButton>
        <ControlButton
          className={showVolume ? 'active' : ''}
          onClick={handleVolumeToggle}
        >
          Volumen
        </ControlButton>

        <ControlButton
          className={timeframe === '1M' ? 'active' : ''}
          onClick={() => handleTimeframeChange('1M')}
        >
          1M
        </ControlButton>
        <ControlButton
          className={timeframe === '3M' ? 'active' : ''}
          onClick={() => handleTimeframeChange('3M')}
        >
          3M
        </ControlButton>
        <ControlButton
          className={timeframe === '6M' ? 'active' : ''}
          onClick={() => handleTimeframeChange('6M')}
        >
          6M
        </ControlButton>
        <ControlButton
          className={timeframe === '1Y' ? 'active' : ''}
          onClick={() => handleTimeframeChange('1Y')}
        >
          1A
        </ControlButton>
        <ControlButton
          className={timeframe === '2Y' ? 'active' : ''}
          onClick={() => handleTimeframeChange('2Y')}
        >
          2A
        </ControlButton>
        <ControlButton
          className={timeframe === '5Y' ? 'active' : ''}
          onClick={() => handleTimeframeChange('5Y')}
        >
          5A
        </ControlButton>
        <ControlButton
          className={timeframe === 'ALL' ? 'active' : ''}
          onClick={() => handleTimeframeChange('ALL')}
        >
          TODO
        </ControlButton>
      </ChartControls>
      
      {loading && (
        <LoadingOverlay>
          Actualizando gráfico...
        </LoadingOverlay>
      )}
      
      {drawingMode && (
        <DrawingStatus>
          {drawingMode === 'horizontal-line' && '📏 Haz clic en el gráfico para dibujar una línea horizontal'}
          {drawingMode === 'ruler' && measurementPoints.length === 0 && '📐 Haz clic en el primer punto para medir'}
          {drawingMode === 'ruler' && measurementPoints.length === 1 && '📐 Haz clic en el segundo punto para completar la medición'}
        </DrawingStatus>
      )}
      
      <DrawingControls>
        <ControlButton
          className={drawingMode === 'horizontal-line' ? 'active' : ''}
          onClick={() => handleDrawingModeChange('horizontal-line')}
          title="Dibujar líneas horizontales"
        >
          📏 Línea
        </ControlButton>
        <ControlButton
          className={drawingMode === 'ruler' ? 'active' : ''}
          onClick={() => handleDrawingModeChange('ruler')}
          title="Herramienta de medición"
        >
          📐 Regla
        </ControlButton>
        <ControlButton
          onClick={clearAllDrawings}
          title="Limpiar dibujos"
        >
          🗑️ Limpiar
        </ControlButton>
      </DrawingControls>
      
      <ChartWrapper ref={chartContainerRef} />
    </Container>
  );
};

export default ChartContainer;
