"""
Technical indicators calculation module
Implements various technical analysis indicators for cryptocurrency markets
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Tuple, List
import pandas_ta as ta


class TechnicalIndicators:
    """Calculate technical indicators for cryptocurrency price analysis"""
    
    def __init__(self):
        """Initialize the technical indicators calculator"""
        self.logger = logging.getLogger(__name__)
    
    def validate_data(self, df: pd.DataFrame, min_periods: int = 2) -> bool:
        """
        Validate input DataFrame for indicator calculations
        
        Args:
            df: Price data DataFrame
            min_periods: Minimum number of periods required
            
        Returns:
            True if data is valid for calculations
        """
        if df is None or df.empty:
            self.logger.warning("DataFrame is None or empty")
            return False
        
        if len(df) < min_periods:
            self.logger.warning(f"Insufficient data: {len(df)} periods, need at least {min_periods}")
            return False
        
        required_columns = ['close']
        for col in required_columns:
            if col not in df.columns:
                self.logger.error(f"Missing required column: {col}")
                return False
        
        return True
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> Optional[pd.Series]:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            df: DataFrame with 'close' column
            period: RSI calculation period
            
        Returns:
            RSI values as pandas Series or None if calculation fails
        """
        if not self.validate_data(df, period + 1):
            return None
        
        try:
            rsi = ta.rsi(df['close'], length=period)
            return rsi
        except Exception as e:
            self.logger.error(f"RSI calculation failed: {e}")
            return None
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[Dict[str, pd.Series]]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame with 'close' column
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line EMA period
            
        Returns:
            Dictionary with MACD line, signal line, and histogram or None if calculation fails
        """
        if not self.validate_data(df, slow + signal):
            return None
        
        try:
            macd_data = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
            
            return {
                'macd': macd_data[f'MACD_{fast}_{slow}_{signal}'],
                'signal': macd_data[f'MACDs_{fast}_{slow}_{signal}'],
                'histogram': macd_data[f'MACDh_{fast}_{slow}_{signal}']
            }
        except Exception as e:
            self.logger.error(f"MACD calculation failed: {e}")
            return None
    
    def calculate_moving_averages(self, df: pd.DataFrame, short_period: int = 50, long_period: int = 200) -> Optional[Dict[str, pd.Series]]:
        """
        Calculate Simple Moving Averages
        
        Args:
            df: DataFrame with 'close' column
            short_period: Short MA period
            long_period: Long MA period
            
        Returns:
            Dictionary with short and long moving averages or None if calculation fails
        """
        if not self.validate_data(df, long_period):
            return None
        
        try:
            short_ma = ta.sma(df['close'], length=short_period)
            long_ma = ta.sma(df['close'], length=long_period)
            
            return {
                'ma_short': short_ma,
                'ma_long': long_ma
            }
        except Exception as e:
            self.logger.error(f"Moving average calculation failed: {e}")
            return None
    
    def calculate_ema(self, df: pd.DataFrame, periods: List[int] = [20, 50, 200]) -> Optional[Dict[str, pd.Series]]:
        """
        Calculate Exponential Moving Averages
        
        Args:
            df: DataFrame with 'close' column
            periods: List of EMA periods to calculate
            
        Returns:
            Dictionary with EMAs for each period or None if calculation fails
        """
        if not self.validate_data(df, max(periods)):
            return None
        
        try:
            emas = {}
            for period in periods:
                emas[f'ema_{period}'] = ta.ema(df['close'], length=period)
            
            return emas
        except Exception as e:
            self.logger.error(f"EMA calculation failed: {e}")
            return None
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> Optional[Dict[str, pd.Series]]:
        """
        Calculate Bollinger Bands
        
        Args:
            df: DataFrame with 'close' column
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Dictionary with upper, middle, and lower bands or None if calculation fails
        """
        if not self.validate_data(df, period):
            return None
        
        try:
            bb_data = ta.bbands(df['close'], length=period, std=std_dev)
            
            return {
                'upper': bb_data[f'BBU_{period}_{std_dev}'],
                'middle': bb_data[f'BBM_{period}_{std_dev}'],
                'lower': bb_data[f'BBL_{period}_{std_dev}']
            }
        except Exception as e:
            self.logger.error(f"Bollinger Bands calculation failed: {e}")
            return None
    
    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Optional[Dict[str, pd.Series]]:
        """
        Calculate Stochastic Oscillator
        
        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            k_period: %K period
            d_period: %D period (smoothing)
            
        Returns:
            Dictionary with %K and %D values or None if calculation fails
        """
        required_columns = ['high', 'low', 'close']
        for col in required_columns:
            if col not in df.columns:
                self.logger.error(f"Missing required column for Stochastic: {col}")
                return None
        
        if not self.validate_data(df, k_period + d_period):
            return None
        
        try:
            stoch_data = ta.stoch(df['high'], df['low'], df['close'], k=k_period, d=d_period)
            
            return {
                'k': stoch_data[f'STOCHk_{k_period}_{d_period}_{d_period}'],
                'd': stoch_data[f'STOCHd_{k_period}_{d_period}_{d_period}']
            }
        except Exception as e:
            self.logger.error(f"Stochastic calculation failed: {e}")
            return None
    
    def calculate_volume_indicators(self, df: pd.DataFrame) -> Optional[Dict[str, pd.Series]]:
        """
        Calculate volume-based indicators
        
        Args:
            df: DataFrame with 'close' and 'volume' columns
            
        Returns:
            Dictionary with volume indicators or None if calculation fails
        """
        if 'volume' not in df.columns:
            self.logger.warning("Volume data not available")
            return None
        
        if not self.validate_data(df, 20):
            return None
        
        try:
            return {
                'volume_sma': ta.sma(df['volume'], length=20),
                'ad': ta.ad(df['high'], df['low'], df['close'], df['volume']) if all(col in df.columns for col in ['high', 'low']) else None,
                'obv': ta.obv(df['close'], df['volume'])
            }
        except Exception as e:
            self.logger.error(f"Volume indicators calculation failed: {e}")
            return None
    
    def get_latest_indicator_values(self, df: pd.DataFrame, config: Dict) -> Dict[str, float]:
        """
        Get the latest values of all configured indicators
        
        Args:
            df: Price data DataFrame
            config: Indicator configuration
            
        Returns:
            Dictionary with latest indicator values
        """
        results = {}
        
        try:
            # RSI
            rsi = self.calculate_rsi(df, config.get('rsi_period', 14))
            if rsi is not None and not rsi.empty:
                results['rsi'] = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
            
            # MACD
            macd_data = self.calculate_macd(
                df, 
                config.get('macd_fast', 12),
                config.get('macd_slow', 26),
                config.get('macd_signal', 9)
            )
            if macd_data:
                for key, series in macd_data.items():
                    if series is not None and not series.empty:
                        results[f'macd_{key}'] = float(series.iloc[-1]) if not pd.isna(series.iloc[-1]) else None
            
            # Moving Averages
            ma_data = self.calculate_moving_averages(
                df,
                config.get('ma_short', 50),
                config.get('ma_long', 200)
            )
            if ma_data:
                for key, series in ma_data.items():
                    if series is not None and not series.empty:
                        results[key] = float(series.iloc[-1]) if not pd.isna(series.iloc[-1]) else None
            
            # Current price
            if 'close' in df.columns and not df['close'].empty:
                results['current_price'] = float(df['close'].iloc[-1])
            
        except Exception as e:
            self.logger.error(f"Error calculating latest indicator values: {e}")
        
        return results
    
    def detect_crossovers(self, series1: pd.Series, series2: pd.Series, periods_back: int = 2) -> Dict[str, bool]:
        """
        Detect crossovers between two series (e.g., MACD crossover, MA crossover)
        
        Args:
            series1: First series (e.g., MACD line)
            series2: Second series (e.g., Signal line)
            periods_back: Number of periods to look back for crossover detection
            
        Returns:
            Dictionary with bullish and bearish crossover flags
        """
        if len(series1) < periods_back or len(series2) < periods_back:
            return {'bullish_crossover': False, 'bearish_crossover': False}
        
        try:
            # Recent values
            recent1 = series1.iloc[-periods_back:].values
            recent2 = series2.iloc[-periods_back:].values
            
            # Check for bullish crossover (series1 crosses above series2)
            bullish_crossover = bool((recent1[-2] <= recent2[-2]) and (recent1[-1] > recent2[-1]))
            
            # Check for bearish crossover (series1 crosses below series2)
            bearish_crossover = bool((recent1[-2] >= recent2[-2]) and (recent1[-1] < recent2[-1]))
            
            return {
                'bullish_crossover': bullish_crossover,
                'bearish_crossover': bearish_crossover
            }
        except Exception as e:
            self.logger.error(f"Crossover detection failed: {e}")
            return {'bullish_crossover': False, 'bearish_crossover': False}
    
    def calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict[str, float]:
        """
        Calculate basic support and resistance levels
        
        Args:
            df: DataFrame with 'high' and 'low' columns
            window: Window size for calculation
            
        Returns:
            Dictionary with support and resistance levels
        """
        if not all(col in df.columns for col in ['high', 'low']):
            return {'support': None, 'resistance': None}
        
        if len(df) < window:
            return {'support': None, 'resistance': None}
        
        try:
            recent_data = df.iloc[-window:]
            support = float(recent_data['low'].min())
            resistance = float(recent_data['high'].max())
            
            return {'support': support, 'resistance': resistance}
        except Exception as e:
            self.logger.error(f"Support/Resistance calculation failed: {e}")
            return {'support': None, 'resistance': None}
