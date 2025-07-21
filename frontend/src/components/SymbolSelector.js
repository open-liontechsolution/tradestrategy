import React, { useState, useMemo, useEffect } from 'react';
import Select from 'react-select';
import styled from 'styled-components';
import { fetchRecommendedSymbols } from '../services/api';

const Container = styled.div`
  margin-bottom: 2rem;
`;

const Title = styled.h3`
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 0.9rem;
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
  
  &:focus {
    outline: none;
    border-color: rgba(255, 255, 255, 0.4);
    background: rgba(255, 255, 255, 0.15);
  }
`;

const TabContainer = styled.div`
  display: flex;
  margin-bottom: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 0.25rem;
`;

const TabButton = styled.button`
  flex: 1;
  padding: 0.75rem 1rem;
  background: ${props => props.active ? 'rgba(255, 255, 255, 0.2)' : 'transparent'};
  border: none;
  border-radius: 6px;
  color: ${props => props.active ? 'white' : 'rgba(255, 255, 255, 0.7)'};
  font-size: 0.9rem;
  font-weight: ${props => props.active ? '500' : '400'};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }
`;

const RecommendedBadge = styled.span`
  display: inline-block;
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  color: white;
  font-size: 0.7rem;
  font-weight: bold;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  margin-left: 0.5rem;
`;

const DistanceBadge = styled.span`
  display: inline-block;
  background: ${props => {
    const distance = parseFloat(props.distance);
    if (distance < 1) return 'linear-gradient(45deg, #00d2ff, #3a7bd5)';
    if (distance < 3) return 'linear-gradient(45deg, #a8edea, #fed6e3)';
    return 'linear-gradient(45deg, #ffecd2, #fcb69f)';
  }};
  color: ${props => parseFloat(props.distance) < 3 ? 'white' : '#333'};
  font-size: 0.7rem;
  font-weight: bold;
  padding: 0.2rem 0.4rem;
  border-radius: 10px;
  margin-left: 0.5rem;
`;

const StatsContainer = styled.div`
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
`;

const StatRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const customSelectStyles = {
  control: (provided, state) => ({
    ...provided,
    background: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '8px',
    minHeight: '42px',
    boxShadow: state.isFocused ? '0 0 0 1px rgba(255, 255, 255, 0.4)' : 'none',
    '&:hover': {
      borderColor: 'rgba(255, 255, 255, 0.3)'
    }
  }),
  menu: (provided) => ({
    ...provided,
    background: 'rgba(30, 60, 114, 0.95)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '8px',
    zIndex: 1000
  }),
  option: (provided, state) => ({
    ...provided,
    background: state.isFocused 
      ? 'rgba(255, 255, 255, 0.2)' 
      : state.isSelected 
        ? 'rgba(255, 255, 255, 0.3)' 
        : 'transparent',
    color: 'white',
    padding: '12px 16px',
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.2)'
    }
  }),
  singleValue: (provided) => ({
    ...provided,
    color: 'white'
  }),
  placeholder: (provided) => ({
    ...provided,
    color: 'rgba(255, 255, 255, 0.6)'
  }),
  input: (provided) => ({
    ...provided,
    color: 'white'
  }),
  indicatorSeparator: () => ({
    display: 'none'
  }),
  dropdownIndicator: (provided) => ({
    ...provided,
    color: 'rgba(255, 255, 255, 0.6)',
    '&:hover': {
      color: 'rgba(255, 255, 255, 0.8)'
    }
  })
};

const SymbolSelector = ({ symbols, selectedSymbol, onSymbolChange, loading }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('all'); // 'all' o 'recommended'
  const [recommendedSymbols, setRecommendedSymbols] = useState([]);
  const [loadingRecommended, setLoadingRecommended] = useState(false);

  // Cargar candidatos recomendados cuando se selecciona la pestaña
  useEffect(() => {
    if (activeTab === 'recommended' && recommendedSymbols.length === 0) {
      loadRecommendedSymbols();
    }
  }, [activeTab]);

  const loadRecommendedSymbols = async () => {
    try {
      setLoadingRecommended(true);
      const response = await fetchRecommendedSymbols({ limit: 50 });
      setRecommendedSymbols(response.candidates || []);
    } catch (error) {
      console.error('Error cargando candidatos recomendados:', error);
    } finally {
      setLoadingRecommended(false);
    }
  };

  // Filtrar y formatear símbolos para react-select
  const symbolOptions = useMemo(() => {
    let sourceData = activeTab === 'recommended' ? recommendedSymbols : symbols;
    let filtered = sourceData;
    
    if (searchTerm) {
      if (activeTab === 'recommended') {
        filtered = sourceData.filter(candidate => 
          candidate.symbol.toLowerCase().includes(searchTerm.toLowerCase())
        );
      } else {
        filtered = sourceData.filter(symbol => 
          symbol.symbol.toLowerCase().includes(searchTerm.toLowerCase())
        );
      }
    }
    
    if (activeTab === 'recommended') {
      return filtered
        .slice(0, 50)
        .map(candidate => ({
          value: candidate.symbol,
          label: `${candidate.symbol} (${candidate.resistance_distance_percent?.toFixed(2)}% distancia)`,
          symbol: {
            symbol: candidate.symbol,
            data_points: candidate.data_points,
            last_date: candidate.last_data_date,
            // Añadir datos específicos de candidatos
            historical_high: candidate.historical_high,
            current_price: candidate.current_price,
            resistance_distance_percent: candidate.resistance_distance_percent,
            years_of_data: candidate.years_of_data,
            isRecommended: true
          }
        }));
    } else {
      return filtered
        .slice(0, 100) // Limitar a 100 resultados para performance
        .map(symbol => ({
          value: symbol.symbol,
          label: `${symbol.symbol} (${symbol.data_points} puntos)`,
          symbol: symbol
        }));
    }
  }, [symbols, recommendedSymbols, searchTerm, activeTab]);

  const handleSymbolSelect = (selectedOption) => {
    onSymbolChange(selectedOption);
  };

  const formatOptionLabel = ({ symbol }) => (
    <div>
      <div style={{ fontWeight: 'bold', fontSize: '0.95rem', display: 'flex', alignItems: 'center' }}>
        {symbol.symbol}
        {symbol.isRecommended && (
          <RecommendedBadge>RECOMENDADO</RecommendedBadge>
        )}
        {symbol.resistance_distance_percent !== undefined && (
          <DistanceBadge distance={symbol.resistance_distance_percent}>
            {symbol.resistance_distance_percent.toFixed(2)}%
          </DistanceBadge>
        )}
      </div>
      <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>
        {symbol.isRecommended ? (
          <>
            Máximo: ${symbol.historical_high?.toFixed(2)} • Actual: ${symbol.current_price?.toFixed(2)}
            {symbol.last_date && (
              <span> • Último: {new Date(symbol.last_date).toLocaleDateString()}</span>
            )}
          </>
        ) : (
          <>
            {symbol.data_points} puntos de datos
            {symbol.last_date && (
              <span> • Último: {new Date(symbol.last_date).toLocaleDateString()}</span>
            )}
          </>
        )}
      </div>
    </div>
  );

  return (
    <Container>
      <Title>Seleccionar Símbolo</Title>
      
      <TabContainer>
        <TabButton 
          active={activeTab === 'all'} 
          onClick={() => setActiveTab('all')}
        >
          Todos los Símbolos
        </TabButton>
        <TabButton 
          active={activeTab === 'recommended'} 
          onClick={() => setActiveTab('recommended')}
        >
          Recomendados {recommendedSymbols.length > 0 && `(${recommendedSymbols.length})`}
        </TabButton>
      </TabContainer>
      
      <SearchInput
        type="text"
        placeholder={activeTab === 'recommended' ? "Buscar candidato..." : "Buscar símbolo..."}
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      
      <Select
        options={symbolOptions}
        value={selectedSymbol}
        onChange={handleSymbolSelect}
        placeholder={
          loading || loadingRecommended 
            ? "Cargando..." 
            : activeTab === 'recommended' 
              ? "Selecciona un candidato recomendado" 
              : "Selecciona un símbolo"
        }
        isLoading={loading || loadingRecommended}
        isDisabled={loading || loadingRecommended}
        styles={customSelectStyles}
        formatOptionLabel={formatOptionLabel}
        isSearchable
        isClearable
        noOptionsMessage={() => activeTab === 'recommended' ? "No se encontraron candidatos" : "No se encontraron símbolos"}
        loadingMessage={() => "Cargando..."}
      />
      
      {(symbols.length > 0 || recommendedSymbols.length > 0) && (
        <StatsContainer>
          {activeTab === 'recommended' ? (
            <>
              <StatRow>
                <span>Candidatos recomendados:</span>
                <span>{recommendedSymbols.length}</span>
              </StatRow>
              <StatRow>
                <span>Mostrando:</span>
                <span>{Math.min(symbolOptions.length, 50)}</span>
              </StatRow>
              {selectedSymbol && selectedSymbol.symbol.isRecommended && (
                <>
                  <StatRow>
                    <span>Candidato seleccionado:</span>
                    <span>{selectedSymbol.value}</span>
                  </StatRow>
                  <StatRow>
                    <span>Distancia a resistencia:</span>
                    <span style={{ color: selectedSymbol.symbol.resistance_distance_percent < 3 ? '#4ade80' : '#fbbf24' }}>
                      {selectedSymbol.symbol.resistance_distance_percent?.toFixed(2)}%
                    </span>
                  </StatRow>
                  <StatRow>
                    <span>Máximo histórico:</span>
                    <span>${selectedSymbol.symbol.historical_high?.toFixed(2)}</span>
                  </StatRow>
                  <StatRow>
                    <span>Precio actual:</span>
                    <span>${selectedSymbol.symbol.current_price?.toFixed(2)}</span>
                  </StatRow>
                  <StatRow>
                    <span>Años de datos:</span>
                    <span>{selectedSymbol.symbol.years_of_data?.toFixed(1)} años</span>
                  </StatRow>
                </>
              )}
            </>
          ) : (
            <>
              <StatRow>
                <span>Total símbolos:</span>
                <span>{symbols.length.toLocaleString()}</span>
              </StatRow>
              <StatRow>
                <span>Mostrando:</span>
                <span>{Math.min(symbolOptions.length, 100)}</span>
              </StatRow>
              {selectedSymbol && (
                <>
                  <StatRow>
                    <span>Símbolo seleccionado:</span>
                    <span>{selectedSymbol.value}</span>
                  </StatRow>
                  <StatRow>
                    <span>Puntos de datos:</span>
                    <span>{selectedSymbol.symbol.data_points}</span>
                  </StatRow>
                  {selectedSymbol.symbol.first_date && (
                    <StatRow>
                      <span>Desde:</span>
                      <span>{new Date(selectedSymbol.symbol.first_date).toLocaleDateString()}</span>
                    </StatRow>
                  )}
                  {selectedSymbol.symbol.last_date && (
                    <StatRow>
                      <span>Hasta:</span>
                      <span>{new Date(selectedSymbol.symbol.last_date).toLocaleDateString()}</span>
                    </StatRow>
                  )}
                </>
              )}
            </>
          )}
        </StatsContainer>
      )}
    </Container>
  );
};

export default SymbolSelector;
