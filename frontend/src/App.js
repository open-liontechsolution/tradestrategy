import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import SymbolSelector from './components/SymbolSelector';
import ChartContainer from './components/ChartContainer';
import TechnicalIndicators from './components/TechnicalIndicators';
import MarketInfo from './components/MarketInfo';
import { fetchSymbols, fetchSymbolData } from './services/api';
import './App.css';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
`;

const Header = styled.header`
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem 2rem;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const Title = styled.h1`
  margin: 0;
  font-size: 2rem;
  font-weight: 300;
  text-align: center;
  background: linear-gradient(45deg, #fff, #e0e0e0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const MainContent = styled.main`
  display: grid;
  grid-template-columns: 300px 1fr 300px;
  grid-template-rows: auto 1fr;
  gap: 1rem;
  padding: 1rem;
  height: calc(100vh - 100px);
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto 1fr auto;
    height: auto;
  }
`;

const LeftPanel = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  
  @media (max-width: 1200px) {
    grid-column: 1;
    grid-row: 1;
  }
`;

const ChartArea = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  
  @media (max-width: 1200px) {
    grid-column: 1;
    grid-row: 3;
    min-height: 500px;
  }
`;

const RightPanel = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  
  @media (max-width: 1200px) {
    grid-column: 1;
    grid-row: 4;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 1.2rem;
  
  &::after {
    content: '';
    width: 40px;
    height: 40px;
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top: 4px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-left: 1rem;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid rgba(255, 0, 0, 0.5);
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
  text-align: center;
`;

function App() {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [indicators, setIndicators] = useState({
    sma: false,
    ema: false,
    bollinger: false,
    rsi: false,
    macd: false
  });
  const [timeframe, setTimeframe] = useState('2Y'); // Nuevo estado para timeframe

  // Cargar símbolos al iniciar la aplicación
  useEffect(() => {
    const loadSymbols = async () => {
      try {
        setLoading(true);
        const symbolsData = await fetchSymbols();
        setSymbols(symbolsData.symbols || []);
        setError(null);
      } catch (err) {
        setError('Error cargando símbolos: ' + err.message);
        console.error('Error loading symbols:', err);
      } finally {
        setLoading(false);
      }
    };

    loadSymbols();
  }, []);

  // Cargar datos cuando se selecciona un símbolo o cambia el timeframe
  useEffect(() => {
    if (selectedSymbol) {
      loadChartData(selectedSymbol.value);
    }
  }, [selectedSymbol, timeframe]);

  const loadChartData = async (symbol, selectedTimeframe = timeframe) => {
    try {
      setLoading(true);
      setError(null);
      
      // Calcular fechas según el timeframe seleccionado
      const endDate = new Date();
      const startDate = new Date();
      
      switch (selectedTimeframe) {
        case '1M':
          startDate.setMonth(endDate.getMonth() - 1);
          break;
        case '3M':
          startDate.setMonth(endDate.getMonth() - 3);
          break;
        case '6M':
          startDate.setMonth(endDate.getMonth() - 6);
          break;
        case '1Y':
          startDate.setFullYear(endDate.getFullYear() - 1);
          break;
        case '2Y':
          startDate.setFullYear(endDate.getFullYear() - 2);
          break;
        case '5Y':
          startDate.setFullYear(endDate.getFullYear() - 5);
          break;
        case 'ALL':
          startDate.setFullYear(2000); // Desde el año 2000
          break;
        default:
          startDate.setFullYear(endDate.getFullYear() - 2);
      }
      
      const data = await fetchSymbolData(symbol, {
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
      });
      
      setChartData(data.data || []);
    } catch (err) {
      setError('Error cargando datos del gráfico: ' + err.message);
      console.error('Error loading chart data:', err);
      setChartData([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSymbolChange = (symbol) => {
    setSelectedSymbol(symbol);
  };

  const handleIndicatorToggle = (indicator) => {
    setIndicators(prev => ({
      ...prev,
      [indicator]: !prev[indicator]
    }));
  };

  const handleTimeframeChange = (newTimeframe) => {
    setTimeframe(newTimeframe);
  };

  return (
    <AppContainer>
      <Header>
        <Title>TradeStrategy - Market Data Visualization</Title>
      </Header>
      
      <MainContent>
        <LeftPanel>
          <SymbolSelector
            symbols={symbols}
            selectedSymbol={selectedSymbol}
            onSymbolChange={handleSymbolChange}
            loading={loading}
          />
          
          {selectedSymbol && (
            <MarketInfo
              symbol={selectedSymbol.value}
              data={chartData}
            />
          )}
        </LeftPanel>
        
        <ChartArea>
          {error && <ErrorMessage>{error}</ErrorMessage>}
          
          {loading && !chartData.length ? (
            <LoadingSpinner>Cargando datos...</LoadingSpinner>
          ) : chartData.length > 0 ? (
            <ChartContainer
              data={chartData}
              symbol={selectedSymbol?.value}
              indicators={indicators}
              timeframe={timeframe}
              onTimeframeChange={handleTimeframeChange}
            />
          ) : (
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '100%',
              fontSize: '1.2rem',
              opacity: 0.7 
            }}>
              Selecciona un símbolo para ver el gráfico
            </div>
          )}
        </ChartArea>
        
        <RightPanel>
          <TechnicalIndicators
            indicators={indicators}
            onIndicatorToggle={handleIndicatorToggle}
            data={chartData}
            symbol={selectedSymbol?.value}
          />
        </RightPanel>
      </MainContent>
    </AppContainer>
  );
}

export default App;
