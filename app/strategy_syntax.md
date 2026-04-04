# Custom Strategy Builder Syntax

The Custom Strategy Builder uses a simple Domain-Specific Language (DSL) to allow rapid creation and testing of trading strategies without writing any Python code.

## 1. Defining Indicators

You MUST assign an indicator to a variable name before using it. We support standard moving averages along with advanced oscillators and volatility bands.

**Basic Syntax:**
```text
<variable_name> = <indicator_type> <params...> [of <timeframe>]
```

- `<variable_name>`: Any name containing letters/numbers/underscores (e.g., `fast_ema`, `my_rsi`).
- `<timeframe>` (Optional): `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`. Defaults to `5m`.

### Supported Indicators

**1. Moving Averages (`ema`, `sma`) and RSI/ATR**
`Format: <type> <period> of <tf>`
`Boolean Format: <type>_bool <period> of <tf>`
```text
ema1 = ema 5 of 5m
rsi_val = rsi 14
rsi_state = rsi_bool 14  # True if RSI > 50
ema_state = ema_bool 20  # True if Price > EMA 20
```

**2. MACD**
`Format: macd_line <fast> <slow> <signal> of <tf>`
`Boolean Format: macd_line_bool <fast> <slow> <signal> of <tf>`
```text
m_line = macd_line 12 26 9
m_bullish = macd_line_bool 12 26 9  # True if MACD > Signal
m_sig = macd_signal 12 26 9
```

**3. Bollinger Bands (`bb_upper`, `bb_lower`)**
`Format: <type> <period> <std_dev> of <tf>`
`Boolean Format: <type>_bool <period> <std_dev> of <tf>`
```text
bb_up = bb_upper 20 2
is_out_top = bb_upper_bool 20 2  # True if Price > Upper Band
is_out_bot = bb_lower_bool 20 2  # True if Price < Lower Band
```

## 2. Defining Cross Conditions (Entry Triggers)

Cross conditions detect when exactly one indicator crosses another.

**Syntax:**
```text
<variable_name> = crossing above <indicator_1> <indicator_2>
<variable_name> = crossing below <indicator_1> <indicator_2>
```

**Examples:**
```text
cross_up = crossing above ema1 ema2
cross_down = crossing below ema1 ema2
```

## 3. Defining Trend Filters
Trend filters check if the price action is bullish or bearish on specific timeframes. A bullish trend means the exact Close of that timeframe is greater than its Open.

**Syntax:**
```text
<variable_name> = trend bullish <timeframe>
<variable_name> = trend bearish <timeframe>
```

**Examples:**
```text
trend_1h = trend bullish 1h
trend_1d = trend bearish 1d
```

## 4. Boolean Comparisons (State Filters)

You can now create boolean variables by comparing an indicator to a number or another indicator. This is useful for checking if an indicator is in a specific state (e.g., Overbought).

**Syntax:**
```text
<variable_name> = <source_var> <operator> <value_or_var>
```

- `<operator>`: `>`, `<`, `>=`, `<=`, `==`.

**Examples:**
```text
# Compare to a number
rsi1 = rsi 14
is_overbought = rsi1 > 70
is_oversold = rsi1 < 30

# Compare two indicators (Trend State)
ema_fast = ema 5
ema_slow = ema 20
is_bullish_state = ema_fast > ema_slow
```

## 5. Execution Rules (Buy/Sell)

These are the final rules that tell the engine when to execute a trade. You can combine multiple boolean conditions using `and`. If you write multiple `buy when` rules, the engine will execute if *any* of them are true (OR logic). 

**Syntax:**
```text
buy when <condition_1> and <condition_2> ...
sell when <condition_1> and <condition_2> ...
```

**Examples:**
```text
buy when cross_up and is_bullish_state and is_oversold
sell when cross_down and is_overbought
```

---

## Full Strategy Example

```text
# Master Strategy Example (Using ALL Indicators)

```text
# --- SECTION 1: INDICATOR DEFINITIONS (Values) ---
ema_fast = ema 9 of 5m
ema_slow = ema 21 of 5m
sma_long = sma 200 of 5m
rsi_val = rsi 14 of 5m
atr_vol = atr 14 of 5m
mac_line = macd_line 12 26 9 of 5m
mac_sig = macd_signal 12 26 9 of 5m
bb_up = bb_upper 20 2 of 5m
bb_low = bb_lower 20 2 of 5m

# --- SECTION 2: BOOLEAN STATES (Logic) ---
# Check if price is above moving averages
is_ema_bullish = ema_bool 21
is_sma_bullish = sma_bool 200

# Check oscillators for overbought/oversold
is_overbought = rsi_val > 70
is_oversold = rsi_val < 30

# Check MACD and BB states
is_macd_bullish = macd_line_bool 12 26 9
is_price_above_bb = bb_upper_bool 20 2
is_price_below_bb = bb_lower_bool 20 2

# Check multi-timeframe trend
is_trend_bullish = trend bullish 1h

# --- SECTION 3: ENTRY TRIGGERS (Events) ---
cross_up = crossing above ema_fast ema_slow
cross_down = crossing below ema_fast ema_slow

# --- SECTION 4: EXECUTION RULES ---
# Buy when moving average crosses up, while trend is bullish and RSI is not overbought
buy when cross_up and is_trend_bullish and is_macd_bullish

# Sell when moving average crosses down OR Price hits the Upper Bollinger Band
sell when cross_down or is_price_above_bb or is_overbought
```

