import React, { useState, useMemo } from 'react';
import Select from 'react-select';
import styled from 'styled-components';

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

  // Filtrar y formatear símbolos para react-select
  const symbolOptions = useMemo(() => {
    let filtered = symbols;
    
    if (searchTerm) {
      filtered = symbols.filter(symbol => 
        symbol.symbol.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return filtered
      .slice(0, 100) // Limitar a 100 resultados para performance
      .map(symbol => ({
        value: symbol.symbol,
        label: `${symbol.symbol} (${symbol.data_points} puntos)`,
        symbol: symbol
      }));
  }, [symbols, searchTerm]);

  const handleSymbolSelect = (selectedOption) => {
    onSymbolChange(selectedOption);
  };

  const formatOptionLabel = ({ symbol }) => (
    <div>
      <div style={{ fontWeight: 'bold', fontSize: '0.95rem' }}>
        {symbol.symbol}
      </div>
      <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>
        {symbol.data_points} puntos de datos
        {symbol.last_date && (
          <span> • Último: {new Date(symbol.last_date).toLocaleDateString()}</span>
        )}
      </div>
    </div>
  );

  return (
    <Container>
      <Title>Seleccionar Símbolo</Title>
      
      <SearchInput
        type="text"
        placeholder="Buscar símbolo..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      
      <Select
        options={symbolOptions}
        value={selectedSymbol}
        onChange={handleSymbolSelect}
        placeholder={loading ? "Cargando símbolos..." : "Selecciona un símbolo"}
        isLoading={loading}
        isDisabled={loading}
        styles={customSelectStyles}
        formatOptionLabel={formatOptionLabel}
        isSearchable
        isClearable
        noOptionsMessage={() => "No se encontraron símbolos"}
        loadingMessage={() => "Cargando..."}
      />
      
      {symbols.length > 0 && (
        <StatsContainer>
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
        </StatsContainer>
      )}
    </Container>
  );
};

export default SymbolSelector;
