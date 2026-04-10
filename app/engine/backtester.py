import pandas as pd
import numpy as np

class Trade:
    def __init__(self, entry_time, entry_price, size, direction, sl_price=None, tp_price=None):
        # Execution occurs at the EXACT complete form moment of the signal candle
        self.entry_time = entry_time + pd.Timedelta(minutes=5)
        self.entry_price = entry_price
        self.size = size
        self.direction = direction # 1 for long, -1 for short
        self.sl_price = sl_price
        self.tp_price = tp_price
        self.exit_time = None
        self.exit_price = None
        self.pnl = 0
        self.moved_to_be = False

    def close(self, exit_time, exit_price):
        # Execution occurs at the exact mathematical threshold
        self.exit_time = exit_time + pd.Timedelta(minutes=5)
        self.exit_price = exit_price
        self.pnl = (self.exit_price - self.entry_price) * self.direction * self.size

class Backtester:
    def __init__(self, data_paths, strategy_class, ema_config=None, primary_tf='5m', start_date=None, end_date=None, cash=10000, leverage=100, position_size=10000, compound=False, session_start=0, session_end=23, spread_pips=0.0, commission=0.0, break_even_trigger=0.0, break_even_lock=0.0, max_trades_per_day=1, max_loss_trades_per_day=50):
        self.data_paths = data_paths
        self.ema_config = ema_config or {}
        self.primary_tf = primary_tf
        self.strategy_class = strategy_class
        self.start_date = start_date
        self.end_date = end_date
        self.initial_cash = cash
        self.cash = cash
        self.leverage = leverage
        self.position_size = position_size
        self.compound = compound
        self.session_start = session_start
        self.session_end = session_end
        self.spread_pips = spread_pips
        self.commission = commission
        self.break_even_trigger = break_even_trigger
        self.break_even_lock = break_even_lock
        self.max_trades_per_day = max_trades_per_day
        self.max_loss_trades_per_day = max_loss_trades_per_day
        self.blown_up = False
        self.data = pd.DataFrame()
        self.trades = []
        self.equity_curve = []
        
    def load_data(self):
        # Load primary timeframe first
        primary_path = self.data_paths[self.primary_tf]
        self.data = self._load_csv(primary_path).sort_index()
        
        # Apply primary timeframe EMA dynamically
        ema_props_primary = self.ema_config.get(self.primary_tf, {})
        if ema_props_primary.get('enabled', False):
            span_val = ema_props_primary.get('span', 50)
            self.data[f'EMA_{self.primary_tf}'] = self.data['Close'].ewm(span=span_val, adjust=False).mean()
        
        # Load and merge higher timeframes
        for tf, path in self.data_paths.items():
            if tf == self.primary_tf:
                continue
                
            df_tf = self._load_csv(path).sort_index()
            
            # Dynamically apply exact Custom EMA span per user interface configurations natively
            ema_props = self.ema_config.get(tf, {})
            if ema_props.get('enabled', False):
                span_val = ema_props.get('span', 50)
                df_tf['EMA'] = df_tf['Close'].ewm(span=span_val, adjust=False).mean()
                
            df_tf = df_tf.add_suffix(f'_{tf}')
            
            self.data = pd.merge_asof(self.data, df_tf, left_index=True, right_index=True, direction='backward')
            
        # Apply date filters if provided
        if self.start_date:
            self.data = self.data[self.data.index >= pd.to_datetime(self.start_date)]
        if self.end_date:
            self.data = self.data[self.data.index <= pd.to_datetime(self.end_date)]
            
    def _load_csv(self, path):
        df = pd.read_csv(path, encoding='utf-16le', names=['DateTime', 'Open', 'High', 'Low', 'Close', 'TickVol', 'Spread'], on_bad_lines='skip')
        df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
        df.dropna(subset=['DateTime'], inplace=True)
        df.set_index('DateTime', inplace=True)
        for col in ['Open', 'High', 'Low', 'Close', 'TickVol', 'Spread']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(inplace=True)
        return df

    def run(self):
        print(f"Loading data from {list(self.data_paths.keys())}...")
        self.load_data()
        print(f"Data loaded successfully. Total candles: {len(self.data)}")
        
        strategy = self.strategy_class(self.data)
        strategy.init()
        
        current_position = 0 # + size for long, - size for short
        open_trade = None
        self.blown_up_date = None
        
        current_day = None
        trades_today = 0
        loss_trades_today = 0
        won_today = False
        previous_trade_count = 0
        
        print("Running backtest strategy...")
        for i in range(len(self.data)):
            current_bar = self.data.iloc[i]
            
            bar_date = current_bar.name.date()
            if current_day != bar_date:
                current_day = bar_date
                trades_today = 0
                loss_trades_today = 0
                won_today = False
                
            # 0. Check Account Blowup
            if self.blown_up:
                self.equity_curve.append(0)
                continue
            
            # Evaluate intra-bar blowout risk based on current open trade floating PNL
            if open_trade:
                unrealized_max_loss = 0
                if open_trade.direction == 1:
                    unrealized_max_loss = (current_bar['Low'] - open_trade.entry_price) * open_trade.size
                elif open_trade.direction == -1:
                    unrealized_max_loss = (open_trade.entry_price - current_bar['High']) * open_trade.size
                
                if self.cash + unrealized_max_loss <= 0:
                    self.blown_up = True
                    open_trade.close(current_bar.name, current_bar['Close']) # Close at destruction
                    self.cash = 0
                    self.trades.append(open_trade)
                    open_trade = None
                    current_position = 0
                    self.equity_curve.append(0)
                    continue

            # 1. Manage active trades automatically based on Stop Loss and Take Profit levels
            if open_trade:
                if open_trade.direction == 1:
                    # Evaluate Smart Trailing Pivot (Break-Even Trigger)
                    if self.break_even_trigger > 0 and getattr(open_trade, 'moved_to_be', False) == False:
                        be_trigger_price = open_trade.entry_price + (self.break_even_trigger / open_trade.size)
                        if current_bar['High'] >= be_trigger_price:
                            # Lock SL exactly to Entry Price + Lock Amount, explicitly offsetting initial spread automatically
                            lock_price_offset = (self.break_even_lock / open_trade.size)
                            open_trade.sl_price = open_trade.entry_price + lock_price_offset + (self.spread_pips * 0.0001)
                            open_trade.moved_to_be = True
                            
                    # Check SL
                    if open_trade.sl_price is not None and current_bar['Low'] <= open_trade.sl_price:
                        open_trade.close(current_bar.name, open_trade.sl_price)
                        self.cash += open_trade.pnl
                        self.trades.append(open_trade)
                        open_trade = None
                        current_position = 0
                    # Check TP
                    elif open_trade.tp_price is not None and current_bar['High'] >= open_trade.tp_price:
                        open_trade.close(current_bar.name, open_trade.tp_price)
                        self.cash += open_trade.pnl
                        self.trades.append(open_trade)
                        open_trade = None
                        current_position = 0
                        
                elif open_trade.direction == -1:
                    # Evaluate Smart Trailing Pivot (Break-Even Trigger)
                    if self.break_even_trigger > 0 and getattr(open_trade, 'moved_to_be', False) == False:
                        be_trigger_price = open_trade.entry_price - (self.break_even_trigger / open_trade.size)
                        if current_bar['Low'] <= be_trigger_price:
                            # Lock SL exactly to Entry Price - Lock Amount, explicitly offsetting initial spread automatically
                            lock_price_offset = (self.break_even_lock / open_trade.size)
                            open_trade.sl_price = open_trade.entry_price - lock_price_offset - (self.spread_pips * 0.0001)
                            open_trade.moved_to_be = True
                            
                    # Check SL
                    if open_trade.sl_price is not None and current_bar['High'] >= open_trade.sl_price:
                        open_trade.close(current_bar.name, open_trade.sl_price)
                        self.cash += open_trade.pnl
                        self.trades.append(open_trade)
                        open_trade = None
                        current_position = 0
                    # Check TP
                    elif open_trade.tp_price is not None and current_bar['Low'] <= open_trade.tp_price:
                        open_trade.close(current_bar.name, open_trade.tp_price)
                        self.cash += open_trade.pnl
                        self.trades.append(open_trade)
                        open_trade = None
                        current_position = 0

            # Evaluate daily trackers based on closed trades
            current_trade_count = len(self.trades)
            if current_trade_count > previous_trade_count:
                for new_trade in self.trades[previous_trade_count:]:
                    if new_trade.pnl is not None:
                        if new_trade.pnl > 0:
                            won_today = True
                        elif new_trade.pnl <= 0:
                            loss_trades_today += 1
                previous_trade_count = current_trade_count

            # 2. Get Strategy Signal (Subject to Session Filters)
            signal = 0
            sl, tp = None, None
            
            is_valid_session = True
            
            # Convert base MT5 (UTC+2) to IST (UTC+5:30) for filtering
            current_bar_ist = current_bar.name + pd.Timedelta(hours=3, minutes=30)
            current_hour = current_bar_ist.hour
            
            if self.session_start <= self.session_end:
                if not (self.session_start <= current_hour <= self.session_end):
                    is_valid_session = False
            else:
                if not (current_hour >= self.session_start or current_hour <= self.session_end):
                    is_valid_session = False
                    
            # Apply user-configurable dynamic daily limits
            if trades_today >= self.max_trades_per_day or loss_trades_today >= self.max_loss_trades_per_day:
                is_valid_session = False
                
            if is_valid_session:
                signal_data = strategy.next(i, current_bar)
                if isinstance(signal_data, tuple):
                    signal, sl, tp = signal_data
                else:
                    signal, sl, tp = signal_data, None, None
            
            # 3. Simple execution logic
            exec_size = self.position_size
            if self.compound and self.cash > 0:
                multiplier = self.cash / self.initial_cash
                exec_size = self.position_size * multiplier
                
            if signal == 1 and current_position <= 0 and not self.blown_up:
                # Close short if open
                if open_trade:
                    open_trade.close(current_bar.name, current_bar['Close'])
                    self.cash += open_trade.pnl
                    self.trades.append(open_trade)
                    open_trade = None
                
                margin_req = (exec_size * current_bar['Close']) / self.leverage
                if self.cash >= margin_req:
                    # Apply explicit spread penalty natively to execution entry price
                    actual_entry = current_bar['Close'] + (self.spread_pips * 0.0001)
                    open_trade = Trade(current_bar.name, actual_entry, exec_size, 1, sl, tp)
                    current_position = 1
                    trades_today += 1
                
            elif signal == -1 and current_position >= 0 and not self.blown_up:
                # Close long if open
                if open_trade:
                    open_trade.close(current_bar.name, current_bar['Close'])
                    self.cash += open_trade.pnl
                    self.trades.append(open_trade)
                    open_trade = None
                
                margin_req = (exec_size * current_bar['Close']) / self.leverage
                if self.cash >= margin_req:
                    # Apply explicit spread penalty natively to execution entry price
                    actual_entry = current_bar['Close'] - (self.spread_pips * 0.0001)
                    open_trade = Trade(current_bar.name, actual_entry, exec_size, -1, sl, tp)
                    current_position = -1
                    trades_today += 1
                
            # Track equity curve
            unrealized_pnl = 0
            if open_trade:
                unrealized_pnl = (current_bar['Close'] - open_trade.entry_price) * open_trade.direction * open_trade.size
            
            current_equity = self.cash + unrealized_pnl
            self.equity_curve.append(current_equity)
            
            if current_equity <= 0 and not self.blown_up:
                self.blown_up = True
                self.blown_up_date = current_bar.name.strftime('%Y-%m-%d %H:%M')
                if open_trade:
                    open_trade.close(current_bar.name, current_bar['Close'])
                    self.cash += open_trade.pnl
                    self.trades.append(open_trade)
                    open_trade = None
                    current_position = 0

        # Close any open trade at the end of the data
        if open_trade:
            last_bar = self.data.iloc[-1]
            open_trade.close(last_bar.name, last_bar['Close'])
            self.cash += open_trade.pnl
            self.trades.append(open_trade)
            
        self.print_stats()
        return self.get_stats()

    def get_stats(self):
        total_pnl = sum([t.pnl for t in self.trades])
        win_rate = 0
        if len(self.trades) > 0:
            winning_trades = [t for t in self.trades if t.pnl > 0]
            win_rate = len(winning_trades) / len(self.trades) * 100
            
        max_drawdown = 0
        if self.equity_curve:
            equity_series = pd.Series(self.equity_curve)
            peak = equity_series.expanding(min_periods=1).max()
            drawdown = (equity_series - peak) / peak
            max_drawdown = drawdown.min() * 100
            
        return {
            'Initial Cash': self.initial_cash,
            'Final Cash': self.cash,
            'Total PnL': total_pnl,
            'Total Trades': len(self.trades),
            'Win Rate': win_rate,
            'Max Drawdown': max_drawdown,
            'Equity Curve': self.equity_curve,
            'Trades': self.trades,
            'Blown Up Date': getattr(self, 'blown_up_date', None)
        }

    def print_stats(self):
        print("\n======== BACKTEST RESULTS ========")
        print(f"Initial Cash: ${self.initial_cash:.2f}")
        total_pnl = sum([t.pnl for t in self.trades])
        print(f"Final Cash:   ${self.cash:.2f}")
        print(f"Total PnL:    ${total_pnl:.2f}")
        print(f"Total Trades: {len(self.trades)}")
        
        if len(self.trades) > 0:
            winning_trades = [t for t in self.trades if t.pnl > 0]
            win_rate = len(winning_trades) / len(self.trades) * 100
            print(f"Win Rate:     {win_rate:.2f}%")
            
        if self.equity_curve:
            equity_series = pd.Series(self.equity_curve)
            peak = equity_series.expanding(min_periods=1).max()
            drawdown = (equity_series - peak) / peak
            max_drawdown = drawdown.min() * 100
            print(f"Max Drawdown: {max_drawdown:.2f}%")
        print("==================================\n")
