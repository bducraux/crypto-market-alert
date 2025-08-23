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
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            df: DataFrame with 'close' column
            period: RSI calculation period
            
        Returns:
            Latest RSI value as float or None if calculation fails
        """
        if not self.validate_data(df, period + 1):
            return None
        
        try:
            rsi = ta.rsi(df['close'], length=period)
            if rsi is not None and not rsi.empty:
                latest_rsi = rsi.iloc[-1]
                return float(latest_rsi) if not pd.isna(latest_rsi) else None
            return None
        except Exception as e:
            self.logger.error(f"RSI calculation failed: {e}")
            return None
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Optional[pd.Series]]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame with 'close' column
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line EMA period
            
        Returns:
            Dictionary with MACD line, signal line, and histogram (None values if calculation fails)
        """
        if not self.validate_data(df, slow + signal):
            return {
                'macd': None,
                'signal': None,
                'histogram': None
            }
        
        try:
            macd_data = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
            
            return {
                'macd': macd_data[f'MACD_{fast}_{slow}_{signal}'],
                'signal': macd_data[f'MACDs_{fast}_{slow}_{signal}'],
                'histogram': macd_data[f'MACDh_{fast}_{slow}_{signal}']
            }
        except Exception as e:
            self.logger.error(f"MACD calculation failed: {e}")
            return {
                'macd': None,
                'signal': None,
                'histogram': None
            }
    
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
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> Dict[str, Optional[pd.Series]]:
        """
        Calculate Bollinger Bands
        
        Args:
            df: DataFrame with 'close' column
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Dictionary with upper, middle, and lower bands (None values if calculation fails)
        """
        if not self.validate_data(df, period):
            return {
                'bb_upper': None,
                'bb_middle': None,
                'bb_lower': None
            }
        
        try:
            bb_data = ta.bbands(df['close'], length=period, std=std_dev)
            
            return {
                'bb_upper': bb_data[f'BBU_{period}_{std_dev}'],
                'bb_middle': bb_data[f'BBM_{period}_{std_dev}'],
                'bb_lower': bb_data[f'BBL_{period}_{std_dev}']
            }
        except Exception as e:
            self.logger.error(f"Bollinger Bands calculation failed: {e}")
            return {
                'bb_upper': None,
                'bb_middle': None,
                'bb_lower': None
            }
    
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
    
    def get_latest_indicator_values(self, df: pd.DataFrame, config: Dict, coin_symbol: str = None) -> Dict[str, float]:
        """
        Get the latest values of all configured indicators
        
        Args:
            df: Price data DataFrame
            config: Indicator configuration
            coin_symbol: Symbol of the coin being analyzed (for Pi Cycle Top Bitcoin-only logic)
            
        Returns:
            Dictionary with latest indicator values
        """
        results = {}

        try:
            # RSI
            rsi = self.calculate_rsi(df, config.get('rsi_period', 14))
            if rsi is not None:
                results['rsi'] = rsi

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

            # Pi Cycle Top Indicator (ONLY for Bitcoin - BTC cycle top detection)
            if config.get('enable_pi_cycle', False) and coin_symbol and coin_symbol.lower() == 'bitcoin':
                self.logger.info("Calculating Pi Cycle Top indicator for Bitcoin (market cycle analysis)")
                pi_cycle_data = self.calculate_pi_cycle_top(df)
                results.update(pi_cycle_data)
            elif config.get('enable_pi_cycle', False) and coin_symbol and coin_symbol.lower() != 'bitcoin':
                self.logger.debug(f"Skipping Pi Cycle Top for {coin_symbol} - indicator is Bitcoin-specific for market cycle detection")

            # 3-Line RCI (Rank Correlation Index)
            if config.get('enable_rci', False):
                rci_data = self.calculate_rci_3lines(df, config.get('rci_periods', [9, 26, 52]))
                if 'error' not in rci_data:
                    results['rci_3lines'] = rci_data
                else:
                    self.logger.warning(f"RCI calculation failed: {rci_data['error']}")

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

    def calculate_pi_cycle_top(self, df: pd.DataFrame, short_period: int = 111, long_period: int = 350) -> Dict[str, any]:
        """
        Calculate Pi Cycle Top Indicator for Bitcoin cycle analysis
        
        The Pi Cycle Top Indicator uses the 111-day moving average and 2x the 350-day moving average.
        When the 111-day MA crosses above the 2x 350-day MA, it historically indicates a market top.
        
        Args:
            df: DataFrame with 'close' column
            short_period: Short MA period (default 111)
            long_period: Long MA period (default 350)
            
        Returns:
            Dictionary with Pi Cycle data and signals
        """
        if not self.validate_data(df, long_period):
            return {'pi_cycle_signal': False, 'ma_111': None, 'ma_350_2x': None, 'distance': None}
        
        try:
            # Calculate the moving averages
            ma_111 = ta.sma(df['close'], length=short_period)
            ma_350 = ta.sma(df['close'], length=long_period)
            
            if ma_111 is None or ma_350 is None or ma_111.empty or ma_350.empty:
                return {'pi_cycle_signal': False, 'ma_111': None, 'ma_350_2x': None, 'distance': None}
            
            # Pi Cycle uses 2x the 350-day MA
            ma_350_2x = ma_350 * 2
            
            # Get latest values
            latest_111 = float(ma_111.iloc[-1]) if not pd.isna(ma_111.iloc[-1]) else None
            latest_350_2x = float(ma_350_2x.iloc[-1]) if not pd.isna(ma_350_2x.iloc[-1]) else None
            
            if latest_111 is None or latest_350_2x is None:
                return {'pi_cycle_signal': False, 'ma_111': None, 'ma_350_2x': None, 'distance': None}
            
            # Check for crossover signal
            pi_cycle_signal = latest_111 >= latest_350_2x
            
            # Calculate distance between lines (as percentage)
            distance = ((latest_111 / latest_350_2x) - 1) * 100
            
            # Detect recent crossover
            crossover_detected = False
            if len(ma_111) >= 2 and len(ma_350_2x) >= 2:
                prev_111 = ma_111.iloc[-2]
                prev_350_2x = ma_350_2x.iloc[-2]
                
                if not pd.isna(prev_111) and not pd.isna(prev_350_2x):
                    # Bullish crossover: 111 MA crosses above 2x 350 MA
                    crossover_detected = (prev_111 < prev_350_2x) and (latest_111 >= latest_350_2x)
            
            return {
                'pi_cycle_signal': pi_cycle_signal,
                'ma_111': latest_111,
                'ma_350_2x': latest_350_2x,
                'distance': round(distance, 2),
                'crossover_detected': crossover_detected,
                'risk_level': 'HIGH' if pi_cycle_signal else 'LOW'
            }
            
        except Exception as e:
            self.logger.error(f"Pi Cycle Top calculation failed: {e}")
            return {'pi_cycle_signal': False, 'ma_111': None, 'ma_350_2x': None, 'distance': None}

    def calculate_rci_3_line(self, df: pd.DataFrame, periods: List[int] = [9, 26, 52]) -> Dict[str, any]:
        """
        Calculate 3-Line RCI (Rank Correlation Index) for trend analysis
        
        RCI measures the correlation between price rank and time rank.
        Three periods provide short, medium, and long-term trend analysis.
        
        Args:
            df: DataFrame with 'close' column
            periods: List of periods for RCI calculation [short, medium, long]
            
        Returns:
            Dictionary with RCI values and signals
        """
        if not self.validate_data(df, max(periods)):
            return {'rci_short': None, 'rci_medium': None, 'rci_long': None, 'signal': 'NEUTRAL'}
        
        try:
            results = {}
            rci_values = {}
            
            for i, period in enumerate(periods):
                rci_name = ['short', 'medium', 'long'][i]
                rci_values[rci_name] = self._calculate_single_rci(df, period)
                results[f'rci_{rci_name}'] = rci_values[rci_name]
            
            # Generate trading signal based on RCI convergence/divergence
            signal = self._analyze_rci_signals(rci_values)
            results['signal'] = signal
            
            # Add overbought/oversold levels
            results['overbought_level'] = 80
            results['oversold_level'] = -80
            
            return results
            
        except Exception as e:
            self.logger.error(f"3-Line RCI calculation failed: {e}")
            return {'rci_short': None, 'rci_medium': None, 'rci_long': None, 'signal': 'NEUTRAL'}

    def _calculate_single_rci(self, df: pd.DataFrame, period: int) -> Optional[float]:
        """
        Calculate RCI for a single period
        
        RCI = (1 - 6 * Σ(Rank_Price - Rank_Time)² / (period * (period² - 1))) * 100
        """
        if len(df) < period:
            return None
        
        try:
            # Get the last 'period' values
            recent_data = df['close'].tail(period).values
            
            # Create time ranks (1 to period)
            time_ranks = list(range(1, period + 1))
            
            # Create price ranks (1 = lowest price, period = highest price)
            price_ranks = pd.Series(recent_data).rank(method='min').tolist()
            
            # Calculate rank differences squared
            rank_diff_squared = sum((p_rank - t_rank) ** 2 for p_rank, t_rank in zip(price_ranks, time_ranks))
            
            # RCI formula
            rci = (1 - (6 * rank_diff_squared) / (period * (period ** 2 - 1))) * 100
            
            return float(rci)
            
        except Exception as e:
            self.logger.error(f"Single RCI calculation failed for period {period}: {e}")
            return None

    def _analyze_rci_signals(self, rci_values: Dict[str, Optional[float]]) -> str:
        """
        Analyze RCI signals to determine market trend
        
        Returns:
            Signal string: 'STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL'
        """
        short = rci_values.get('short')
        medium = rci_values.get('medium')
        long_term = rci_values.get('long')
        
        if any(v is None for v in [short, medium, long_term]):
            return 'NEUTRAL'
        
        # Count how many RCI lines are in bullish/bearish territory
        bullish_count = sum(1 for rci in [short, medium, long_term] if rci > 0)
        bearish_count = sum(1 for rci in [short, medium, long_term] if rci < 0)
        
        # Strong signals when all three align
        if bullish_count == 3 and short > 50:
            return 'STRONG_BUY'
        elif bearish_count == 3 and short < -50:
            return 'STRONG_SELL'
        
        # Medium signals when majority align
        elif bullish_count >= 2 and short > 0:
            return 'BUY'
        elif bearish_count >= 2 and short < 0:
            return 'SELL'
        
        return 'NEUTRAL'

    def calculate_rci_3lines(self, df: pd.DataFrame, periods: List[int] = [9, 26, 52]) -> Dict:
        """
        Calculate RCI 3-Lines (Rank Correlation Index)
        
        The RCI is superior to RSI for crypto markets as it measures the correlation
        between price rank and time rank, making it more sensitive to trend changes.
        
        Args:
            df: DataFrame with OHLCV data
            periods: List of periods for short, medium, long RCI [9, 26, 52]
            
        Returns:
            Dictionary containing RCI values and analysis
        """
        try:
            if not self.validate_data(df, min_periods=max(periods)):
                return {'error': 'Insufficient data for RCI calculation'}
            
            rci_values = {}
            close_prices = df['close'].values
            
            for period in periods:
                if len(close_prices) >= period:
                    rci_series = []
                    
                    # Calculate RCI for each window
                    for i in range(period - 1, len(close_prices)):
                        window_prices = close_prices[i - period + 1:i + 1]
                        
                        # Create rank arrays
                        price_ranks = pd.Series(window_prices).rank(method='min').values
                        time_ranks = np.arange(1, period + 1)
                        
                        # Calculate Spearman correlation coefficient
                        n = len(price_ranks)
                        d_squared_sum = np.sum((price_ranks - time_ranks) ** 2)
                        
                        # RCI formula: (1 - 6 * Σd² / (n³ - n)) * 100
                        rci = (1 - (6 * d_squared_sum) / (n ** 3 - n)) * 100
                        rci_series.append(rci)
                    
                    # Pad with NaN for earlier periods
                    full_series = [np.nan] * (period - 1) + rci_series
                    rci_values[f'rci_{period}'] = full_series[-1] if rci_series else np.nan
                else:
                    rci_values[f'rci_{period}'] = np.nan
            
            # Analyze RCI signals
            analysis = self._analyze_rci_3_line_signals(rci_values)
            
            return {
                'values': rci_values,
                'analysis': analysis,
                'current': {
                    'short': rci_values.get('rci_9', np.nan),
                    'medium': rci_values.get('rci_26', np.nan),
                    'long': rci_values.get('rci_52', np.nan)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating RCI 3-Lines: {e}")
            return {'error': f'RCI calculation failed: {str(e)}'}

    def _analyze_rci_3_line_signals(self, rci_values: Dict, overbought: float = 80, oversold: float = -80) -> Dict:
        """
        Analyze RCI signals for market conditions
        
        Args:
            rci_values: Dictionary with RCI values for different periods
            overbought: Overbought threshold (default: 80)
            oversold: Oversold threshold (default: -80)
            
        Returns:
            Dictionary with signal analysis
        """
        try:
            rci_9 = rci_values.get('rci_9', 0)
            rci_26 = rci_values.get('rci_26', 0)
            rci_52 = rci_values.get('rci_52', 0)
            
            # Handle NaN values
            valid_rcis = [rci for rci in [rci_9, rci_26, rci_52] if not pd.isna(rci)]
            
            if not valid_rcis:
                return {
                    'condition': 'INSUFFICIENT_DATA',
                    'signal': '⚪ NO SIGNAL',
                    'risk_score': 50,
                    'strength': 'WEAK',
                    'details': 'Insufficient data for RCI analysis'
                }
            
            # Count lines in different zones
            overbought_count = sum(1 for rci in valid_rcis if rci > overbought)
            oversold_count = sum(1 for rci in valid_rcis if rci < oversold)
            neutral_high = sum(1 for rci in valid_rcis if 50 <= rci <= overbought)
            neutral_low = sum(1 for rci in valid_rcis if oversold <= rci <= -50)
            
            # Determine market condition based on RCI alignment
            total_lines = len(valid_rcis)
            
            if overbought_count == total_lines:
                condition = "EXTREME_OVERBOUGHT"
                signal = "🔴 SELL SIGNAL"
                risk_score = 95
                strength = "VERY_STRONG"
            elif overbought_count >= 2:
                condition = "OVERBOUGHT" 
                signal = "🟡 CAUTION - Consider taking profits"
                risk_score = 75
                strength = "STRONG"
            elif oversold_count == total_lines:
                condition = "EXTREME_OVERSOLD"
                signal = "🟢 BUY SIGNAL"
                risk_score = 5
                strength = "VERY_STRONG"
            elif oversold_count >= 2:
                condition = "OVERSOLD"
                signal = "🟢 ACCUMULATE - Good buying opportunity"
                risk_score = 20
                strength = "STRONG"
            elif neutral_high >= 2:
                condition = "BULLISH_MOMENTUM"
                signal = "💚 BULLISH - Uptrend continues"
                risk_score = 35
                strength = "MEDIUM"
            elif neutral_low >= 2:
                condition = "BEARISH_MOMENTUM"
                signal = "🔻 BEARISH - Downtrend continues"
                risk_score = 65
                strength = "MEDIUM"
            else:
                condition = "NEUTRAL"
                signal = "⚪ HOLD - Mixed signals"
                risk_score = 50
                strength = "WEAK"
            
            return {
                'condition': condition,
                'signal': signal,
                'risk_score': risk_score,
                'strength': strength,
                'overbought_lines': overbought_count,
                'oversold_lines': oversold_count,
                'total_lines': total_lines,
                'details': {
                    'rci_short': rci_9,
                    'rci_medium': rci_26,
                    'rci_long': rci_52,
                    'alignment_score': max(overbought_count, oversold_count) / total_lines * 100
                }
            }
            
        except Exception as e:
            return {
                'condition': 'ERROR',
                'signal': '⚠️ ERROR',
                'risk_score': 50,
                'strength': 'WEAK',
                'details': f'Analysis error: {str(e)}'
            }
