import pandas as pd

class Strategy:
    """
    Base strategy class. All custom strategies should inherit from this.
    """
    def __init__(self, data):
        self.data = data
        
    def init(self):
        """
        Initialize indicators and setup before the simulation starts.
        You can securely add new columns to self.data here.
        """
        pass
        
    def next(self, i, current_bar):
        """
        Called on every bar in the dataset.
        i: integer index of current bar
        current_bar: pandas Series of the current row (accessed by column names, e.g. current_bar['Close'])
        
        Return:
         1 to Buy/Go Long
        -1 to Sell/Go Short
         0 to Hold/Do Nothing
        """
        return 0

class MovingAverageCrossStrategy(Strategy):
    """
    A simple Moving Average Crossover strategy.
    Buys when the fast MA crosses above the slow MA.
    Sells when the fast MA crosses below the slow MA.
    """
    def init(self):
        # Calculate Moving Averages on the entire dataset upfront (efficient)
        self.data['SMA_fast'] = self.data['Close'].rolling(window=10).mean()
        self.data['SMA_slow'] = self.data['Close'].rolling(window=30).mean()
        
    def next(self, i, current_bar):
        # Need enough data for the slow MA, else hold
        if i < 30:
            return 0
            
        # Check for crossover
        prev_fast = self.data['SMA_fast'].iloc[i-1]
        prev_slow = self.data['SMA_slow'].iloc[i-1]
        curr_fast = self.data['SMA_fast'].iloc[i]
        curr_slow = self.data['SMA_slow'].iloc[i]
        
        if prev_fast <= prev_slow and curr_fast > curr_slow:
            return 1 # Buy signal
            
        elif prev_fast >= prev_slow and curr_fast < curr_slow:
            return -1 # Sell signal
            
        return 0

class MultiTimeframeStrategy(Strategy):
    """
    MTF Strategy example: 
    Buy when 5m SMA crosses up AND the 1h AND 1d candles are bullish.
    Sell when 5m SMA crosses down AND the 1h AND 1d candles are bearish.
    """
    def __init__(self, data, sma_fast_len=20, sma_slow_len=50, sl_usd=10, tp_usd=20, position_size=10000):
        super().__init__(data)
        self.sma_fast_len = sma_fast_len
        self.sma_slow_len = sma_slow_len
        self.sl_usd = sl_usd
        self.tp_usd = tp_usd
        self.position_size = position_size
        
        # Calculate exactly how many pips represent the desired $ Risk for the given starting Lot Size
        # (If lot trades dynamically scale later, these PIP distances stay mathematically identical)
        self.sl_distance_price = sl_usd / position_size
        self.tp_distance_price = tp_usd / position_size

    def init(self):
        # We slow down the moving averages to reduce "whipsaw" false signals
        self.data['SMA_fast'] = self.data['Close'].rolling(window=self.sma_fast_len).mean()
        self.data['SMA_slow'] = self.data['Close'].rolling(window=self.sma_slow_len).mean()
        
    def next(self, i, current_bar):
        if i < 50:
            return 0
            
        # We ensure no NaN values trick our logic safely by checking if it exists
        if pd.isna(current_bar['Close_1h']) or pd.isna(current_bar['Close_1d']):
            return 0
            
        # 1-hour trend 
        is_1h_bullish = current_bar['Close_1h'] > current_bar['Open_1h']
        is_1h_bearish = current_bar['Close_1h'] < current_bar['Open_1h']
        
        # 1-day trend
        is_1d_bullish = current_bar['Close_1d'] > current_bar['Open_1d']
        is_1d_bearish = current_bar['Close_1d'] < current_bar['Open_1d']
        
        # 5m crossover
        prev_fast = self.data['SMA_fast'].iloc[i-1]
        prev_slow = self.data['SMA_slow'].iloc[i-1]
        curr_fast = self.data['SMA_fast'].iloc[i]
        curr_slow = self.data['SMA_slow'].iloc[i]
        
        cross_up = prev_fast <= prev_slow and curr_fast > curr_slow
        cross_down = prev_fast >= prev_slow and curr_fast < curr_slow
        
        # Strict confluence required for entry
        if cross_up and is_1h_bullish and is_1d_bullish:
            sl = current_bar['Close'] - self.sl_distance_price
            tp = current_bar['Close'] + self.tp_distance_price
            return 1, sl, tp
            
        elif cross_down and is_1h_bearish and is_1d_bearish:
            sl = current_bar['Close'] + self.sl_distance_price
            tp = current_bar['Close'] - self.tp_distance_price
            return -1, sl, tp
            
        return 0, None, None

class DynamicSMAStrategy(Strategy):
    """
    Moving Average Crossover Strategy (Reverted Request)
    Entry: Fast SMA crosses Slow SMA
    Trend Filtering: Dynamic Multi-Timeframe EMA validation natively mapped
    """
    def __init__(self, data, sma_fast_len=5, sma_slow_len=30, sl_usd=10, tp_usd=20, position_size=10000, ema_config=None, **kwargs):
        super().__init__(data)
        self.sma_fast_len = sma_fast_len
        self.sma_slow_len = sma_slow_len
        self.sl_distance_price = sl_usd / position_size
        self.tp_distance_price = tp_usd / position_size
        self.ema_config = ema_config or {}
        
    def init(self):
        self.data['SMA_fast'] = self.data['Close'].rolling(window=self.sma_fast_len).mean()
        self.data['SMA_slow'] = self.data['Close'].rolling(window=self.sma_slow_len).mean()
        
    def next(self, i, current_bar):
        if i < max(self.sma_fast_len, self.sma_slow_len) + 1:
            return 0, None, None
            
        # Fast & Slow SMA evaluation mapped iteratively
        prev_fast = self.data['SMA_fast'].iloc[i-1]
        prev_slow = self.data['SMA_slow'].iloc[i-1]
        curr_fast = self.data['SMA_fast'].iloc[i]
        curr_slow = self.data['SMA_slow'].iloc[i]
        
        cross_up = prev_fast <= prev_slow and curr_fast > curr_slow
        cross_down = prev_fast >= prev_slow and curr_fast < curr_slow
        
        if not cross_up and not cross_down:
            return 0, None, None
            
        # Dynamic Trend Evaluation explicitly configured via user dashboard states
        is_bullish = True
        is_bearish = True
        
        for tf in ['5m', '15m', '30m', '1h', '1d']:
            config = self.ema_config.get(tf, {})
            if config.get('enabled', False):
                close_val = current_bar.get(f'Close_{tf}') if tf != '5m' else current_bar['Close']
                ema_val = current_bar.get(f'EMA_{tf}')
                
                # If data is missing or trend contradicts, invalidate direction completely
                if pd.isna(close_val) or pd.isna(ema_val):
                    is_bullish = False
                    is_bearish = False
                    break
                    
                if close_val <= ema_val:
                    is_bullish = False
                if close_val >= ema_val:
                    is_bearish = False
                    
        # Continuous Breakout Evaluation logic: Evaluates any boundary crossing until a valid trade executes
        if cross_up and is_bullish:
            sl = current_bar['Close'] - self.sl_distance_price
            tp = current_bar['Close'] + self.tp_distance_price
            return 1, sl, tp
            
        elif cross_down and is_bearish:
            sl = current_bar['Close'] + self.sl_distance_price
            tp = current_bar['Close'] - self.tp_distance_price
            return -1, sl, tp
            
        return 0, None, None

class ORBStrategy(Strategy):
    """
    Opening Range Breakout Strategy (17:30 IST / 14:00 MT5)
    Trend Filtering: Dynamic Multi-Timeframe EMA validation natively mapped
    """
    def __init__(self, data, sl_usd=10, tp_usd=20, position_size=10000, ema_config=None, **kwargs):
        super().__init__(data)
        self.sl_distance_price = sl_usd / position_size
        self.tp_distance_price = tp_usd / position_size
        self.ema_config = ema_config or {}
        
        self.orb_high = None
        self.orb_low = None
        self.current_day = None
        
    def init(self):
        pass # HTF indicators securely pre-computed by Backtester 
        
    def next(self, i, current_bar):
        bar_time = current_bar.name
        bar_date = bar_time.date()
        
        if self.current_day != bar_date:
            self.current_day = bar_date
            self.orb_high = None
            self.orb_low = None
            
        if bar_time.hour == 14 and bar_time.minute == 0:
            self.orb_high = current_bar['High']
            self.orb_low = current_bar['Low']
            return 0, None, None
            
        if self.orb_high is None or self.orb_low is None:
            return 0, None, None
            
        is_bullish, is_bearish = True, True
        
        for tf in ['5m', '15m', '30m', '1h', '1d']:
            config = self.ema_config.get(tf, {})
            if config.get('enabled', False):
                close_val = current_bar.get(f'Close_{tf}') if tf != '5m' else current_bar['Close']
                ema_val = current_bar.get(f'EMA_{tf}')
                if pd.isna(close_val) or pd.isna(ema_val):
                    is_bullish, is_bearish = False, False
                    break
                if close_val <= ema_val: is_bullish = False
                if close_val >= ema_val: is_bearish = False
                    
        if current_bar['Close'] > self.orb_high and is_bullish:
            sl = current_bar['Close'] - self.sl_distance_price
            tp = current_bar['Close'] + self.tp_distance_price
            return 1, sl, tp
            
        elif current_bar['Close'] < self.orb_low and is_bearish:
            sl = current_bar['Close'] + self.sl_distance_price
            tp = current_bar['Close'] - self.tp_distance_price
            return -1, sl, tp
            
        return 0, None, None

class RSIReversalStrategy(Strategy):
    def __init__(self, data, rsi_period=14, rsi_upper=70, rsi_lower=30, sl_usd=10, tp_usd=20, position_size=10000, ema_config=None, **kwargs):
        super().__init__(data)
        self.rsi_period = int(rsi_period)
        self.rsi_upper = float(rsi_upper)
        self.rsi_lower = float(rsi_lower)
        self.sl_distance_price = sl_usd / position_size
        self.tp_distance_price = tp_usd / position_size
        self.ema_config = ema_config or {}
        
    def init(self):
        import pandas_ta as ta
        self.data['RSI'] = ta.rsi(self.data['Close'], length=self.rsi_period)
        
    def next(self, i, current_bar):
        if i < self.rsi_period + 1 or 'RSI' not in self.data.columns: return 0, None, None
        
        prev_rsi = self.data['RSI'].iloc[i-1]
        curr_rsi = self.data['RSI'].iloc[i]
        
        cross_up = prev_rsi <= self.rsi_lower and curr_rsi > self.rsi_lower
        cross_down = prev_rsi >= self.rsi_upper and curr_rsi < self.rsi_upper
        
        if not cross_up and not cross_down: return 0, None, None
            
        is_bullish, is_bearish = True, True
        for tf in ['5m', '15m', '30m', '1h', '1d']:
            config = self.ema_config.get(tf, {})
            if config.get('enabled', False):
                close_val = current_bar.get(f'Close_{tf}') if tf != '5m' else current_bar['Close']
                ema_val = current_bar.get(f'EMA_{tf}')
                if pd.isna(close_val) or pd.isna(ema_val):
                    is_bullish, is_bearish = False, False; break
                if close_val <= ema_val: is_bullish = False
                if close_val >= ema_val: is_bearish = False

        if cross_up and is_bullish:
            return 1, current_bar['Close'] - self.sl_distance_price, current_bar['Close'] + self.tp_distance_price
        elif cross_down and is_bearish:
            return -1, current_bar['Close'] + self.sl_distance_price, current_bar['Close'] - self.tp_distance_price
        return 0, None, None

class MACDTrendStrategy(Strategy):
    def __init__(self, data, macd_fast=12, macd_slow=26, macd_sig=9, sl_usd=10, tp_usd=20, position_size=10000, ema_config=None, **kwargs):
        super().__init__(data)
        self.macd_fast = int(macd_fast)
        self.macd_slow = int(macd_slow)
        self.macd_sig = int(macd_sig)
        self.sl_distance_price = sl_usd / position_size
        self.tp_distance_price = tp_usd / position_size
        self.ema_config = ema_config or {}
        
    def init(self):
        import pandas_ta as ta
        macd = ta.macd(self.data['Close'], fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_sig)
        if macd is not None:
            self.data['MACD_Line'] = macd.iloc[:, 0]
            self.data['MACD_Signal'] = macd.iloc[:, 2]
            
    def next(self, i, current_bar):
        if i < self.macd_slow + 1 or 'MACD_Line' not in self.data.columns: return 0, None, None
        
        prev_line = self.data['MACD_Line'].iloc[i-1]
        prev_sig = self.data['MACD_Signal'].iloc[i-1]
        curr_line = self.data['MACD_Line'].iloc[i]
        curr_sig = self.data['MACD_Signal'].iloc[i]
        
        cross_up = prev_line <= prev_sig and curr_line > curr_sig
        cross_down = prev_line >= prev_sig and curr_line < curr_sig
        
        if not cross_up and not cross_down: return 0, None, None
            
        is_bullish, is_bearish = True, True
        for tf in ['5m', '15m', '30m', '1h', '1d']:
            config = self.ema_config.get(tf, {})
            if config.get('enabled', False):
                close_val = current_bar.get(f'Close_{tf}') if tf != '5m' else current_bar['Close']
                ema_val = current_bar.get(f'EMA_{tf}')
                if pd.isna(close_val) or pd.isna(ema_val):
                    is_bullish, is_bearish = False, False; break
                if close_val <= ema_val: is_bullish = False
                if close_val >= ema_val: is_bearish = False

        if cross_up and is_bullish:
            return 1, current_bar['Close'] - self.sl_distance_price, current_bar['Close'] + self.tp_distance_price
        elif cross_down and is_bearish:
            return -1, current_bar['Close'] + self.sl_distance_price, current_bar['Close'] - self.tp_distance_price
        return 0, None, None

class BollingerBreakoutStrategy(Strategy):
    def __init__(self, data, bb_length=20, bb_std=2.0, sl_usd=10, tp_usd=20, position_size=10000, ema_config=None, **kwargs):
        super().__init__(data)
        self.bb_length = int(bb_length)
        self.bb_std = float(bb_std)
        self.sl_distance_price = sl_usd / position_size
        self.tp_distance_price = tp_usd / position_size
        self.ema_config = ema_config or {}
        
    def init(self):
        import pandas_ta as ta
        bb = ta.bbands(self.data['Close'], length=self.bb_length, std=self.bb_std)
        if bb is not None:
            self.data['BB_Lower'] = bb.iloc[:, 0]
            self.data['BB_Upper'] = bb.iloc[:, 2]
            
    def next(self, i, current_bar):
        if i < self.bb_length + 1 or 'BB_Upper' not in self.data.columns: return 0, None, None
        
        curr_close = current_bar['Close']
        bb_up = self.data['BB_Upper'].iloc[i]
        bb_low = self.data['BB_Lower'].iloc[i]
        
        cross_up = curr_close > bb_up
        cross_down = curr_close < bb_low
        
        if not cross_up and not cross_down: return 0, None, None
            
        is_bullish, is_bearish = True, True
        for tf in ['5m', '15m', '30m', '1h', '1d']:
            config = self.ema_config.get(tf, {})
            if config.get('enabled', False):
                close_val = current_bar.get(f'Close_{tf}') if tf != '5m' else current_bar['Close']
                ema_val = current_bar.get(f'EMA_{tf}')
                if pd.isna(close_val) or pd.isna(ema_val):
                    is_bullish, is_bearish = False, False; break
                if close_val <= ema_val: is_bullish = False
                if close_val >= ema_val: is_bearish = False

        if cross_up and is_bullish:
            return 1, current_bar['Close'] - self.sl_distance_price, current_bar['Close'] + self.tp_distance_price
        elif cross_down and is_bearish:
            return -1, current_bar['Close'] + self.sl_distance_price, current_bar['Close'] - self.tp_distance_price
        return 0, None, None

class BuilderStrategy(Strategy):
    """
    Dynamically executes a ParsedStrategyConfig generated by the strategy parser.
    """
    def __init__(self, data, config, sl_usd=10, tp_usd=20, position_size=10000, ema_config=None):
        super().__init__(data)
        self.config = config
        self.sl_distance_price = sl_usd / position_size
        self.tp_distance_price = tp_usd / position_size
        
    def init(self):
        # Compute indicators
        import pandas_ta as ta
        for name, ind in self.config.indicators.items():
            tf = ind['tf']
            close_col = 'Close' if tf == '5m' else f'Close_{tf}'
            open_col = 'Open' if tf == '5m' else f'Open_{tf}'
            high_col = 'High' if tf == '5m' else f'High_{tf}'
            low_col = 'Low' if tf == '5m' else f'Low_{tf}'
            
            if ind['type'] == 'ema':
                val = self.data[close_col].ewm(span=ind['period'], adjust=False).mean()
                self.data[name] = (self.data[close_col] > val).astype(int) if ind.get('is_bool') else val
            elif ind['type'] == 'sma':
                val = self.data[close_col].rolling(window=ind['period']).mean()
                self.data[name] = (self.data[close_col] > val).astype(int) if ind.get('is_bool') else val
            elif ind['type'] == 'rsi':
                val = ta.rsi(self.data[close_col], length=ind['period'])
                self.data[name] = (val > 50).astype(int) if ind.get('is_bool') else val
            elif ind['type'] == 'atr':
                val = ta.atr(self.data[high_col], self.data[low_col], self.data[close_col], length=ind['period'])
                # For ATR, boolean means ATR is increasing (volatility rising)
                self.data[name] = (val > val.shift(1)).astype(int) if ind.get('is_bool') else val
            elif ind['type'] == 'macd_line':
                macd = ta.macd(self.data[close_col], fast=ind['fast'], slow=ind['slow'], signal=ind['sig'])
                if macd is not None:
                    val = macd.iloc[:, 0]
                    sig = macd.iloc[:, 2]
                    self.data[name] = (val > sig).astype(int) if ind.get('is_bool') else val
            elif ind['type'] == 'macd_signal':
                macd = ta.macd(self.data[close_col], fast=ind['fast'], slow=ind['slow'], signal=ind['sig'])
                if macd is not None:
                    val = macd.iloc[:, 2]
                    line = macd.iloc[:, 0]
                    self.data[name] = (line > val).astype(int) if ind.get('is_bool') else val
            elif ind['type'] == 'bb_upper':
                bb = ta.bbands(self.data[close_col], length=ind['p1'], std=ind['p2'])
                if bb is not None:
                    val = bb.iloc[:, 2]
                    self.data[name] = (self.data[close_col] > val).astype(int) if ind.get('is_bool') else val
            elif ind['type'] == 'bb_lower':
                bb = ta.bbands(self.data[close_col], length=ind['p1'], std=ind['p2'])
                if bb is not None:
                    val = bb.iloc[:, 0]
                    self.data[name] = (self.data[close_col] < val).astype(int) if ind.get('is_bool') else val

        # Precompute Conditions securely using pandas vectorization
        for name, cond in self.config.conditions.items():
            if cond['type'] == 'cross_up':
                ind1, ind2 = cond['args']
                self.data[name] = (self.data[ind1].shift(1) <= self.data[ind2].shift(1)) & (self.data[ind1] > self.data[ind2])
                
            elif cond['type'] == 'cross_down':
                ind1, ind2 = cond['args']
                self.data[name] = (self.data[ind1].shift(1) >= self.data[ind2].shift(1)) & (self.data[ind1] < self.data[ind2])
                
            elif cond['type'] == 'trend_up':
                tf = cond['tf']
                close_col = 'Close' if tf == '5m' else f'Close_{tf}'
                open_col = 'Open' if tf == '5m' else f'Open_{tf}'
                self.data[name] = (self.data[close_col] > self.data[open_col])
                    
            elif cond['type'] == 'trend_down':
                tf = cond['tf']
                close_col = 'Close' if tf == '5m' else f'Close_{tf}'
                open_col = 'Open' if tf == '5m' else f'Open_{tf}'
                self.data[name] = (self.data[close_col] < self.data[open_col])

        # Precompute Comparisons securely
        for name, comp in self.config.comparisons.items():
            left_val = self.data[comp['left']]
            right_val = self.data[comp['right']] if isinstance(comp['right'], str) else comp['right']
            
            op = comp['op']
            if op == '>': self.data[name] = left_val > right_val
            elif op == '<': self.data[name] = left_val < right_val
            elif op == '>=': self.data[name] = left_val >= right_val
            elif op == '<=': self.data[name] = left_val <= right_val
            elif op == '==': self.data[name] = (left_val == right_val)
            
        # Precompute Final Execution Flags directly across logical paths
        self.data['CUSTOM_BUY_SIGNAL'] = False
        for rule_set in self.config.buy_rules:
            # Join rules logically avoiding empty missing vectors
            rule_vector = self.data[rule_set[0]] if len(rule_set) > 0 else pd.Series(False, index=self.data.index)
            for cond_name in rule_set[1:]:
                rule_vector = rule_vector & self.data[cond_name]
            self.data['CUSTOM_BUY_SIGNAL'] = self.data['CUSTOM_BUY_SIGNAL'] | rule_vector

        self.data['CUSTOM_SELL_SIGNAL'] = False
        for rule_set in self.config.sell_rules:
            rule_vector = self.data[rule_set[0]] if len(rule_set) > 0 else pd.Series(False, index=self.data.index)
            for cond_name in rule_set[1:]:
                rule_vector = rule_vector & self.data[cond_name]
            self.data['CUSTOM_SELL_SIGNAL'] = self.data['CUSTOM_SELL_SIGNAL'] | rule_vector
                
    def next(self, i, current_bar):
        # Determine max period comprehensively preventing boundary indexing clashes
        max_period = max([ind['period'] for ind in self.config.indicators.values()] + [50])
        if i < max_period + 1:
            return 0, None, None
            
        if current_bar['CUSTOM_BUY_SIGNAL']:
            sl = current_bar['Close'] - self.sl_distance_price
            tp = current_bar['Close'] + self.tp_distance_price
            return 1, sl, tp
            
        elif current_bar['CUSTOM_SELL_SIGNAL']:
            sl = current_bar['Close'] + self.sl_distance_price
            tp = current_bar['Close'] - self.tp_distance_price
            return -1, sl, tp
            
        return 0, None, None
