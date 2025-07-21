import React, { useMemo } from 'react';
import styled from 'styled-components';
import { calculateIndicators } from '../services/api';

const Container = styled.div`
  height: 100%;
  overflow-y: auto;
`;

const Title = styled.h3`
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
`;

const IndicatorGroup = styled.div`
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const IndicatorTitle = styled.h4`
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ToggleSwitch = styled.label`
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  margin-left: auto;
`;

const ToggleSlider = styled.span`
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.2);
  transition: 0.3s;
  border-radius: 24px;
  
  &:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: 0.3s;
    border-radius: 50%;
  }
`;

const ToggleInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;
  
  &:checked + ${ToggleSlider} {
    background-color: #4ade80;
  }
  
  &:checked + ${ToggleSlider}:before {
    transform: translateX(20px);
  }
`;

const IndicatorValue = styled.div`
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 0.5rem;
`;

const ValueRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const ValueLabel = styled.span`
  color: rgba(255, 255, 255, 0.7);
`;

const ValueNumber = styled.span`
  color: ${props => props.color || 'rgba(255, 255, 255, 0.9)'};
  font-weight: 500;
`;

const RSIContainer = styled.div`
  margin-top: 0.5rem;
`;

const RSIBar = styled.div`
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  position: relative;
  margin-top: 0.5rem;
`;

const RSIFill = styled.div`
  height: 100%;
  border-radius: 4px;
  width: ${props => props.value}%;
  background: ${props => 
    props.value > 70 ? '#f87171' : 
    props.value < 30 ? '#4ade80' : 
    '#fbbf24'
  };
  transition: all 0.3s ease;
`;

const RSIZones = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.25rem;
`;

const TechnicalIndicators = ({ indicators, onIndicatorToggle, data, symbol }) => {
  // Calcular valores de indicadores
  const indicatorValues = useMemo(() => {
    if (!data || data.length === 0) return null;

    const formattedData = data.map(item => ({
      time: new Date(item.date).getTime() / 1000,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
      volume: item.volume
    }));

    const values = {};

    // SMA
    if (indicators.sma) {
      const smaData = calculateIndicators.sma(formattedData, 20);
      values.sma = smaData[smaData.length - 1]?.value;
    }

    // EMA
    if (indicators.ema) {
      const emaData = calculateIndicators.ema(formattedData, 20);
      values.ema = emaData[emaData.length - 1]?.value;
    }

    // RSI
    if (indicators.rsi) {
      const rsiData = calculateIndicators.rsi(formattedData, 14);
      values.rsi = rsiData[rsiData.length - 1]?.value;
    }

    // Bandas de Bollinger
    if (indicators.bollinger) {
      const bollingerData = calculateIndicators.bollinger(formattedData, 20, 2);
      values.bollinger = {
        upper: bollingerData.upper[bollingerData.upper.length - 1]?.value,
        middle: bollingerData.middle[bollingerData.middle.length - 1]?.value,
        lower: bollingerData.lower[bollingerData.lower.length - 1]?.value
      };
    }

    // Precio actual
    values.currentPrice = formattedData[formattedData.length - 1]?.close;

    return values;
  }, [data, indicators]);

  const formatPrice = (price) => {
    if (!price) return 'N/A';
    return price.toFixed(2);
  };

  const getRSIColor = (rsi) => {
    if (rsi > 70) return '#f87171'; // Sobrecomprado - rojo
    if (rsi < 30) return '#4ade80'; // Sobrevendido - verde
    return '#fbbf24'; // Neutral - amarillo
  };

  const getRSILabel = (rsi) => {
    if (rsi > 70) return 'Sobrecomprado';
    if (rsi < 30) return 'Sobrevendido';
    return 'Neutral';
  };

  return (
    <Container>
      <Title>Análisis Técnico</Title>
      
      {symbol && (
        <IndicatorGroup>
          <IndicatorTitle>
            {symbol}
            {indicatorValues?.currentPrice && (
              <ValueNumber style={{ marginLeft: 'auto', fontSize: '1.1rem' }}>
                ${formatPrice(indicatorValues.currentPrice)}
              </ValueNumber>
            )}
          </IndicatorTitle>
        </IndicatorGroup>
      )}

      {/* Media Móvil Simple */}
      <IndicatorGroup>
        <IndicatorTitle>
          Media Móvil Simple (20)
          <ToggleSwitch>
            <ToggleInput
              type="checkbox"
              checked={indicators.sma}
              onChange={() => onIndicatorToggle('sma')}
            />
            <ToggleSlider />
          </ToggleSwitch>
        </IndicatorTitle>
        {indicators.sma && indicatorValues?.sma && (
          <IndicatorValue>
            <ValueRow>
              <ValueLabel>SMA (20):</ValueLabel>
              <ValueNumber>${formatPrice(indicatorValues.sma)}</ValueNumber>
            </ValueRow>
            {indicatorValues.currentPrice && (
              <ValueRow>
                <ValueLabel>Diferencia:</ValueLabel>
                <ValueNumber color={
                  indicatorValues.currentPrice > indicatorValues.sma ? '#4ade80' : '#f87171'
                }>
                  {((indicatorValues.currentPrice - indicatorValues.sma) / indicatorValues.sma * 100).toFixed(2)}%
                </ValueNumber>
              </ValueRow>
            )}
          </IndicatorValue>
        )}
      </IndicatorGroup>

      {/* Media Móvil Exponencial */}
      <IndicatorGroup>
        <IndicatorTitle>
          Media Móvil Exponencial (20)
          <ToggleSwitch>
            <ToggleInput
              type="checkbox"
              checked={indicators.ema}
              onChange={() => onIndicatorToggle('ema')}
            />
            <ToggleSlider />
          </ToggleSwitch>
        </IndicatorTitle>
        {indicators.ema && indicatorValues?.ema && (
          <IndicatorValue>
            <ValueRow>
              <ValueLabel>EMA (20):</ValueLabel>
              <ValueNumber>${formatPrice(indicatorValues.ema)}</ValueNumber>
            </ValueRow>
            {indicatorValues.currentPrice && (
              <ValueRow>
                <ValueLabel>Diferencia:</ValueLabel>
                <ValueNumber color={
                  indicatorValues.currentPrice > indicatorValues.ema ? '#4ade80' : '#f87171'
                }>
                  {((indicatorValues.currentPrice - indicatorValues.ema) / indicatorValues.ema * 100).toFixed(2)}%
                </ValueNumber>
              </ValueRow>
            )}
          </IndicatorValue>
        )}
      </IndicatorGroup>

      {/* Bandas de Bollinger */}
      <IndicatorGroup>
        <IndicatorTitle>
          Bandas de Bollinger (20, 2)
          <ToggleSwitch>
            <ToggleInput
              type="checkbox"
              checked={indicators.bollinger}
              onChange={() => onIndicatorToggle('bollinger')}
            />
            <ToggleSlider />
          </ToggleSwitch>
        </IndicatorTitle>
        {indicators.bollinger && indicatorValues?.bollinger && (
          <IndicatorValue>
            <ValueRow>
              <ValueLabel>Banda Superior:</ValueLabel>
              <ValueNumber>${formatPrice(indicatorValues.bollinger.upper)}</ValueNumber>
            </ValueRow>
            <ValueRow>
              <ValueLabel>Banda Media:</ValueLabel>
              <ValueNumber>${formatPrice(indicatorValues.bollinger.middle)}</ValueNumber>
            </ValueRow>
            <ValueRow>
              <ValueLabel>Banda Inferior:</ValueLabel>
              <ValueNumber>${formatPrice(indicatorValues.bollinger.lower)}</ValueNumber>
            </ValueRow>
            {indicatorValues.currentPrice && (
              <ValueRow>
                <ValueLabel>Posición:</ValueLabel>
                <ValueNumber color={
                  indicatorValues.currentPrice > indicatorValues.bollinger.upper ? '#f87171' :
                  indicatorValues.currentPrice < indicatorValues.bollinger.lower ? '#4ade80' :
                  '#fbbf24'
                }>
                  {indicatorValues.currentPrice > indicatorValues.bollinger.upper ? 'Sobre banda superior' :
                   indicatorValues.currentPrice < indicatorValues.bollinger.lower ? 'Bajo banda inferior' :
                   'Dentro de bandas'}
                </ValueNumber>
              </ValueRow>
            )}
          </IndicatorValue>
        )}
      </IndicatorGroup>

      {/* RSI */}
      <IndicatorGroup>
        <IndicatorTitle>
          RSI (14)
          <ToggleSwitch>
            <ToggleInput
              type="checkbox"
              checked={indicators.rsi}
              onChange={() => onIndicatorToggle('rsi')}
            />
            <ToggleSlider />
          </ToggleSwitch>
        </IndicatorTitle>
        {indicators.rsi && indicatorValues?.rsi && (
          <IndicatorValue>
            <ValueRow>
              <ValueLabel>RSI:</ValueLabel>
              <ValueNumber color={getRSIColor(indicatorValues.rsi)}>
                {indicatorValues.rsi.toFixed(2)}
              </ValueNumber>
            </ValueRow>
            <ValueRow>
              <ValueLabel>Estado:</ValueLabel>
              <ValueNumber color={getRSIColor(indicatorValues.rsi)}>
                {getRSILabel(indicatorValues.rsi)}
              </ValueNumber>
            </ValueRow>
            <RSIContainer>
              <RSIBar>
                <RSIFill value={indicatorValues.rsi} />
              </RSIBar>
              <RSIZones>
                <span>0</span>
                <span>30</span>
                <span>70</span>
                <span>100</span>
              </RSIZones>
            </RSIContainer>
          </IndicatorValue>
        )}
      </IndicatorGroup>

      {/* MACD */}
      <IndicatorGroup>
        <IndicatorTitle>
          MACD
          <ToggleSwitch>
            <ToggleInput
              type="checkbox"
              checked={indicators.macd}
              onChange={() => onIndicatorToggle('macd')}
            />
            <ToggleSlider />
          </ToggleSwitch>
        </IndicatorTitle>
        {indicators.macd && (
          <IndicatorValue>
            <ValueRow>
              <ValueLabel>Estado:</ValueLabel>
              <ValueNumber>Próximamente</ValueNumber>
            </ValueRow>
          </IndicatorValue>
        )}
      </IndicatorGroup>

      {!data || data.length === 0 ? (
        <div style={{ 
          textAlign: 'center', 
          color: 'rgba(255, 255, 255, 0.6)',
          padding: '2rem 0',
          fontSize: '0.9rem'
        }}>
          Selecciona un símbolo para ver los indicadores técnicos
        </div>
      ) : null}
    </Container>
  );
};

export default TechnicalIndicators;
