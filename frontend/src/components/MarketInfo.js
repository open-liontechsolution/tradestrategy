import React, { useMemo } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  margin-top: 1.5rem;
`;

const Title = styled.h3`
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
`;

const InfoCard = styled.div`
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const InfoLabel = styled.span`
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
`;

const InfoValue = styled.span`
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  font-size: 0.9rem;
`;

const PriceChange = styled.span`
  font-weight: 600;
  color: ${props => props.$positive ? '#4ade80' : '#f87171'};
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const StatItem = styled.div`
  text-align: center;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const StatLabel = styled.div`
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.25rem;
`;

const StatValue = styled.div`
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
`;

const MarketInfo = ({ symbol, data }) => {
  const marketStats = useMemo(() => {
    if (!data || data.length === 0) return null;

    const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));
    const latestData = sortedData[sortedData.length - 1];
    const previousData = sortedData[sortedData.length - 2];

    // Calcular estadísticas básicas
    const prices = sortedData.map(d => d.close).filter(p => p !== null);
    const volumes = sortedData.map(d => d.volume).filter(v => v !== null);
    const highs = sortedData.map(d => d.high).filter(h => h !== null);
    const lows = sortedData.map(d => d.low).filter(l => l !== null);

    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    const avgVolume = volumes.reduce((a, b) => a + b, 0) / volumes.length;
    const maxVolume = Math.max(...volumes);

    // Calcular cambio de precio
    let priceChange = 0;
    let priceChangePercent = 0;
    if (latestData && previousData && previousData.close) {
      priceChange = latestData.close - previousData.close;
      priceChangePercent = (priceChange / previousData.close) * 100;
    }

    // Calcular volatilidad (desviación estándar de los retornos)
    const returns = [];
    for (let i = 1; i < sortedData.length; i++) {
      if (sortedData[i].close && sortedData[i-1].close) {
        returns.push((sortedData[i].close - sortedData[i-1].close) / sortedData[i-1].close);
      }
    }
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((acc, ret) => acc + Math.pow(ret - avgReturn, 2), 0) / returns.length;
    const volatility = Math.sqrt(variance) * 100;

    return {
      latest: latestData,
      previous: previousData,
      priceChange,
      priceChangePercent,
      maxPrice,
      minPrice,
      avgVolume,
      maxVolume,
      volatility,
      dataPoints: sortedData.length,
      dateRange: {
        start: sortedData[0].date,
        end: latestData.date
      }
    };
  }, [data]);

  const formatPrice = (price) => {
    if (!price) return 'N/A';
    return `$${price.toFixed(2)}`;
  };

  const formatVolume = (volume) => {
    if (!volume) return 'N/A';
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`;
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`;
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`;
    return volume.toLocaleString();
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (!marketStats) {
    return (
      <Container>
        <Title>Información del Mercado</Title>
        <InfoCard>
          <div style={{ 
            textAlign: 'center', 
            color: 'rgba(255, 255, 255, 0.6)',
            padding: '1rem 0'
          }}>
            No hay datos disponibles
          </div>
        </InfoCard>
      </Container>
    );
  }

  return (
    <Container>
      <Title>Información del Mercado</Title>
      
      {/* Precio actual y cambio */}
      <InfoCard>
        <InfoRow>
          <InfoLabel>Precio Actual:</InfoLabel>
          <InfoValue>{formatPrice(marketStats.latest.close)}</InfoValue>
        </InfoRow>
        
        {marketStats.previous && (
          <>
            <InfoRow>
              <InfoLabel>Cambio:</InfoLabel>
              <PriceChange $positive={marketStats.priceChange >= 0}>
                {marketStats.priceChange >= 0 ? '+' : ''}{formatPrice(Math.abs(marketStats.priceChange))}
              </PriceChange>
            </InfoRow>
            <InfoRow>
              <InfoLabel>Cambio %:</InfoLabel>
              <PriceChange $positive={marketStats.priceChangePercent >= 0}>
                {marketStats.priceChangePercent >= 0 ? '+' : ''}{marketStats.priceChangePercent.toFixed(2)}%
              </PriceChange>
            </InfoRow>
          </>
        )}
        
        <InfoRow>
          <InfoLabel>Última Actualización:</InfoLabel>
          <InfoValue>{formatDate(marketStats.latest.date)}</InfoValue>
        </InfoRow>
      </InfoCard>

      {/* Estadísticas del día */}
      <InfoCard>
        <InfoRow>
          <InfoLabel>Apertura:</InfoLabel>
          <InfoValue>{formatPrice(marketStats.latest.open)}</InfoValue>
        </InfoRow>
        <InfoRow>
          <InfoLabel>Máximo:</InfoLabel>
          <InfoValue>{formatPrice(marketStats.latest.high)}</InfoValue>
        </InfoRow>
        <InfoRow>
          <InfoLabel>Mínimo:</InfoLabel>
          <InfoValue>{formatPrice(marketStats.latest.low)}</InfoValue>
        </InfoRow>
        <InfoRow>
          <InfoLabel>Volumen:</InfoLabel>
          <InfoValue>{formatVolume(marketStats.latest.volume)}</InfoValue>
        </InfoRow>
      </InfoCard>

      {/* Estadísticas del período */}
      <InfoCard>
        <InfoRow style={{ marginBottom: '1rem' }}>
          <InfoLabel>Estadísticas del Período</InfoLabel>
        </InfoRow>
        
        <StatsGrid>
          <StatItem>
            <StatLabel>Máximo Período</StatLabel>
            <StatValue>{formatPrice(marketStats.maxPrice)}</StatValue>
          </StatItem>
          <StatItem>
            <StatLabel>Mínimo Período</StatLabel>
            <StatValue>{formatPrice(marketStats.minPrice)}</StatValue>
          </StatItem>
          <StatItem>
            <StatLabel>Vol. Promedio</StatLabel>
            <StatValue>{formatVolume(marketStats.avgVolume)}</StatValue>
          </StatItem>
          <StatItem>
            <StatLabel>Vol. Máximo</StatLabel>
            <StatValue>{formatVolume(marketStats.maxVolume)}</StatValue>
          </StatItem>
          <StatItem>
            <StatLabel>Volatilidad</StatLabel>
            <StatValue>{marketStats.volatility.toFixed(2)}%</StatValue>
          </StatItem>
          <StatItem>
            <StatLabel>Datos</StatLabel>
            <StatValue>{marketStats.dataPoints}</StatValue>
          </StatItem>
        </StatsGrid>
      </InfoCard>

      {/* Rango de fechas */}
      <InfoCard>
        <InfoRow>
          <InfoLabel>Período:</InfoLabel>
          <InfoValue>
            {formatDate(marketStats.dateRange.start)} - {formatDate(marketStats.dateRange.end)}
          </InfoValue>
        </InfoRow>
      </InfoCard>
    </Container>
  );
};

export default MarketInfo;
