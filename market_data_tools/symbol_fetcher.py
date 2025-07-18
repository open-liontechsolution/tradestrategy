#!/usr/bin/env python3
"""
Market Symbol Fetcher
====================

Script for fetching stock symbols from major markets worldwide.
Features:
- Retrieves symbols from multiple free data sources
- Validates and corrects symbols
- Saves to a text file, overwriting previous data
- Handles different markets (NYSE, NASDAQ, etc.)

Author: TradeStrategy Team
"""

import os
import json
import time
import logging
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('SymbolFetcher')

# Define constants
OUTPUT_DIR = Path("market_data")
OUTPUT_FILE = OUTPUT_DIR / "market_symbols.txt"
MAX_WORKERS = 5  # For parallel processing
MARKETS = {
    "NYSE": "New York Stock Exchange",
    "NASDAQ": "NASDAQ",
    "AMEX": "American Stock Exchange",
    "TSX": "Toronto Stock Exchange",
    "LSE": "London Stock Exchange",
    "EURONEXT": "Euronext",
    "HKEX": "Hong Kong Stock Exchange"
}

class SymbolFetcher:
    """Class for fetching, validating and storing market symbols."""
    
    def __init__(self):
        """Initialize the SymbolFetcher."""
        self.symbols_by_market = {}
        self.all_symbols = set()
        self.invalid_symbols = set()
        
        # Create output directory if it doesn't exist
        OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    
    def fetch_nasdaq_symbols(self):
        """Fetch symbols from NASDAQ website."""
        logger.info("Fetching NASDAQ symbols...")
        
        try:
            # NASDAQ, NYSE and AMEX listings
            nasdaq_url = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
            other_url = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"
            
            # Read NASDAQ listings
            nasdaq_df = pd.read_csv(nasdaq_url, sep="|", skipfooter=1, engine="python")
            nasdaq_symbols = nasdaq_df["Symbol"].tolist()
            self.symbols_by_market["NASDAQ"] = nasdaq_symbols
            logger.info(f"Found {len(nasdaq_symbols)} NASDAQ symbols")
            
            # Read NYSE and other listings
            other_df = pd.read_csv(other_url, sep="|", skipfooter=1, engine="python")
            
            # Group by exchange
            for exchange, group in other_df.groupby("Exchange"):
                exchange_name = exchange
                if exchange == "N":
                    exchange_name = "NYSE"
                elif exchange == "A":
                    exchange_name = "AMEX"
                
                exchange_symbols = group["ACT Symbol"].tolist()
                self.symbols_by_market[exchange_name] = exchange_symbols
                logger.info(f"Found {len(exchange_symbols)} {exchange_name} symbols")
                
            return True
        except Exception as e:
            logger.error(f"Error fetching NASDAQ symbols: {e}")
            return False
    
    def fetch_yahoo_finance_symbols(self):
        """Fetch symbols from Yahoo Finance."""
        logger.info("Fetching symbols from Yahoo Finance...")
        
        try:
            # Get S&P 500 components
            sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            sp500_table = pd.read_html(sp500_url)
            sp500_df = sp500_table[0]
            sp500_symbols = sp500_df["Symbol"].tolist()
            self.symbols_by_market["S&P500"] = sp500_symbols
            logger.info(f"Found {len(sp500_symbols)} S&P 500 symbols")
            
            # Get major indices components using yfinance
            indices = ['^DJI', '^GSPC', '^IXIC', '^FTSE', '^N225', '^GDAXI']
            
            for index in indices:
                try:
                    index_ticker = yf.Ticker(index)
                    if hasattr(index_ticker, 'components'):
                        components = list(index_ticker.components)
                        index_name = {
                            '^DJI': 'Dow Jones',
                            '^GSPC': 'S&P 500',
                            '^IXIC': 'NASDAQ Composite',
                            '^FTSE': 'FTSE 100',
                            '^N225': 'Nikkei 225',
                            '^GDAXI': 'DAX'
                        }.get(index, index)
                        
                        self.symbols_by_market[index_name] = components
                        logger.info(f"Found {len(components)} {index_name} symbols")
                except Exception as e:
                    logger.warning(f"Could not fetch components for {index}: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance symbols: {e}")
            return False
    
    def fetch_fmp_symbols(self):
        """Fetch symbols from Financial Modeling Prep (free API)."""
        logger.info("Fetching symbols from Financial Modeling Prep...")
        
        try:
            # FMP provides a free endpoint for stock symbols
            url = "https://financialmodelingprep.com/api/v3/stock/list"
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                
                # Group by exchange
                exchanges = {}
                for item in data:
                    if "symbol" in item and "exchange" in item:
                        symbol = item["symbol"]
                        exchange = item["exchange"]
                        
                        if exchange not in exchanges:
                            exchanges[exchange] = []
                        
                        exchanges[exchange].append(symbol)
                
                # Add to markets dictionary
                for exchange, symbols in exchanges.items():
                    if exchange and exchange != "":
                        self.symbols_by_market[exchange] = symbols
                        logger.info(f"Found {len(symbols)} {exchange} symbols from FMP")
                
                return True
            else:
                logger.warning(f"FMP API returned status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error fetching FMP symbols: {e}")
            return False
    
    def validate_symbols(self):
        """Validate symbols and filter out invalid ones."""
        logger.info("Validating symbols...")
        
        # Combine all symbols from all markets
        all_symbols = []
        for market, symbols in self.symbols_by_market.items():
            all_symbols.extend(symbols)
        
        # Remove duplicates
        unique_symbols = list(set(all_symbols))
        logger.info(f"Total unique symbols before validation: {len(unique_symbols)}")
        
        valid_symbols = []
        invalid_symbols = []
        
        # Sample a few symbols to validate with yfinance
        sample_size = min(100, len(unique_symbols))
        sample_symbols = unique_symbols[:sample_size]
        
        def validate_symbol(symbol):
            try:
                ticker = yf.Ticker(symbol)
                # Try to get basic info to validate
                info = ticker.info
                if info and "symbol" in info:
                    return (symbol, True)
                return (symbol, False)
            except:
                return (symbol, False)
        
        # Validate sample in parallel
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(validate_symbol, sample_symbols))
        
        # Count valid symbols in sample
        valid_in_sample = sum(1 for _, valid in results if valid)
        logger.info(f"Validation sample: {valid_in_sample}/{sample_size} valid symbols")
        
        # Apply basic validation rules to all symbols
        for symbol in unique_symbols:
            # Basic validation: no spaces, reasonable length, valid characters
            if (symbol and isinstance(symbol, str) and 
                1 <= len(symbol) <= 10 and
                " " not in symbol and
                all(c.isalnum() or c in ".-_^" for c in symbol)):
                valid_symbols.append(symbol)
            else:
                invalid_symbols.append(symbol)
        
        self.all_symbols = set(valid_symbols)
        self.invalid_symbols = set(invalid_symbols)
        
        logger.info(f"Validation complete. Valid: {len(self.all_symbols)}, Invalid: {len(self.invalid_symbols)}")
    
    def save_to_file(self):
        """Save fetched symbols to output file."""
        logger.info(f"Saving {len(self.all_symbols)} symbols to {OUTPUT_FILE}")
        
        try:
            # Save as plain text file, one symbol per line
            with open(OUTPUT_FILE, "w") as f:
                # Convert all symbols to strings before sorting to avoid type comparison issues
                string_symbols = [str(symbol) for symbol in self.all_symbols]
                for symbol in sorted(string_symbols):
                    f.write(f"{symbol}\n")
            
            # Also save market-wise breakdown as JSON for reference
            market_file = OUTPUT_DIR / "market_symbols_by_exchange.json"
            
            # Convert markets and invalid symbols to strings to avoid sorting errors
            markets_str = {}
            for market, symbols in self.symbols_by_market.items():
                markets_str[market] = [str(s) for s in symbols]
            
            invalid_str = [str(s) for s in self.invalid_symbols]
            
            market_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "markets": {k: sorted(v) for k, v in markets_str.items()},
                "invalid_symbols": sorted(invalid_str),
                "summary": {
                    "total_valid": len(self.all_symbols),
                    "total_invalid": len(self.invalid_symbols),
                    "markets": {k: len(v) for k, v in self.symbols_by_market.items()}
                }
            }
            
            with open(market_file, "w") as f:
                json.dump(market_data, f, indent=2)
            
            logger.info(f"Successfully saved symbols to {OUTPUT_FILE}")
            logger.info(f"Market breakdown saved to {market_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving symbols to file: {e}")
            return False
    
    def run(self):
        """Run the complete symbol fetching process."""
        logger.info("Starting symbol fetching process...")
        
        # Fetch from multiple sources
        self.fetch_nasdaq_symbols()
        self.fetch_yahoo_finance_symbols()
        self.fetch_fmp_symbols()
        
        # Validate symbols
        self.validate_symbols()
        
        # Save to file
        self.save_to_file()
        
        logger.info("Symbol fetching process completed")
        return len(self.all_symbols)

def main():
    """Main function."""
    print("=" * 60)
    print("MARKET SYMBOL FETCHER")
    print("=" * 60)
    print("This script fetches stock symbols from major markets worldwide")
    print("and saves them to a text file.")
    print()
    
    fetcher = SymbolFetcher()
    total_symbols = fetcher.run()
    
    print()
    print("=" * 60)
    print(f"FETCHING COMPLETE: {total_symbols} valid symbols")
    print(f"Output file: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
