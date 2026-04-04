import re
from typing import Tuple, List, Dict

class ParseError(Exception):
    pass

class ParsedStrategyConfig:
    def __init__(self):
        self.indicators = {}  # {name: {'type': 'ema'|'sma'|'rsi'|'atr'|'macd_line'|'macd_signal'|'bb_upper'|'bb_lower', 'period': int, 'tf': str, ...}}
        self.comparisons = {} # {name: {'left': str, 'op': str, 'right': str|float}}
        self.conditions = {}  # {name: {'type': 'cross_up'|'cross_down', 'args': [ind1, ind2]} or {'type': 'trend_up'|'trend_down', 'tf': str}}
        self.buy_rules = []   # list of lists (OR of ANDs), e.g., [['cross_up', 'trend_1h']]
        self.sell_rules = []  # list of lists (OR of ANDs)

def parse_and_analyze_strategy(text: str) -> Tuple[ParsedStrategyConfig, List[Dict]]:
    config = ParsedStrategyConfig()
    errors = []
    
    if not text or not text.strip():
        return config, [{"line": 0, "error": "Strategy script is empty.", "suggestion": "Write your strategy code, for example: `ema1 = ema 5 of 5m\nbuy when cross_up`"}]
        
    lines = text.split('\n')
    defined_vars = set()
    
    for i, original_line in enumerate(lines):
        line_num = i + 1
        line = original_line.split('#')[0].strip()
        if not line or line.startswith('```'):
            continue
            
        try:
            # Execution rules
            if line.startswith('buy when '):
                rules_str = line[len('buy when '):].strip()
                # Split by ' or ' to treat them as separate rule sets
                or_rule_strs = [r.strip() for r in rules_str.split(' or ')]
                for r_str in or_rule_strs:
                    and_rules = [r.strip() for r in r_str.split(' and ')]
                    for r in and_rules:
                        if r not in defined_vars:
                            errors.append({"line": line_num, "error": f"Wrong variable selection: Undefined '{r}'.", "suggestion": f"Define '{r}' above before using it."})
                    config.buy_rules.append(and_rules)
                continue
                
            if line.startswith('sell when '):
                rules_str = line[len('sell when '):].strip()
                or_rule_strs = [r.strip() for r in rules_str.split(' or ')]
                for r_str in or_rule_strs:
                    and_rules = [r.strip() for r in r_str.split(' and ')]
                    for r in and_rules:
                        if r not in defined_vars:
                            errors.append({"line": line_num, "error": f"Wrong variable selection: Undefined '{r}'.", "suggestion": f"Define '{r}' above before using it."})
                    config.sell_rules.append(and_rules)
                continue
                
            # Variables
            if '=' not in line:
                if 'ema' in line or 'crossing' in line:
                    errors.append({"line": line_num, "error": "Missing space or variable assignment.", "suggestion": f"Assign the result to a variable, e.g., `my_var = {line}`"})
                else:
                    errors.append({"line": line_num, "error": "Invalid syntax. Expected an assignment '=' or a 'buy/sell when' rule.", "suggestion": "Use format `variable = expression` or `buy when condition`."})
                continue
                
            parts = line.split('=', 1)
            var_name = parts[0].strip()
            expr = parts[1].strip()
            
            if not re.match(r'^[a-zA-Z0-9_]+$', var_name):
                errors.append({"line": line_num, "error": f"Invalid variable name '{var_name}'.", "suggestion": "Variable names must not contain spaces or special characters. Use `my_var_1` instead."})
            
            defined_vars.add(var_name)
            
            # Indicator parsing
            # Single Parameter Indicators: ema, sma, rsi, atr (with optional _bool)
            if re.match(r'^(ema|sma|rsi|atr)(?:_bool)?\s*\d+', expr):
                m = re.match(r'^(ema|sma|rsi|atr)(_bool)?\s+(\d+)(?:\s+of\s+([0-9a-zA-Z]+))?$', expr)
                if not m:
                    errors.append({"line": line_num, "error": f"Malformed indicator syntax '{expr}'. Missing space error.", "suggestion": "Format must strictly have spaces: `<type> <number> of <timeframe>`, e.g., `rsi 14 of 5m` or `rsi_bool 14`."})
                    continue
                ind_type = m.group(1)
                is_bool = bool(m.group(2))
                period = int(m.group(3))
                tf = m.group(4) if m.group(4) else '5m'
                
                if tf not in ['1m', '5m', '15m', '30m', '1h', '4h', '1d']:
                    errors.append({"line": line_num, "error": f"Unsupported timeframe '{tf}'.", "suggestion": "Use standard timeframes like `5m`, `15m`, `1h`, `1d`."})
                
                config.indicators[var_name] = {'type': ind_type, 'period': period, 'tf': tf, 'is_bool': is_bool}
                continue
                
            # Dual Parameter Indicators: bb_upper, bb_lower (with optional _bool)
            if re.match(r'^(bb_upper|bb_lower)(?:_bool)?\s*\d+', expr):
                m = re.match(r'^(bb_upper|bb_lower)(_bool)?\s+(\d+)\s+(\d+(?:\.\d+)?)(?:\s+of\s+([0-9a-zA-Z]+))?$', expr)
                if not m:
                    errors.append({"line": line_num, "error": f"Malformed dual-parameter indicator syntax '{expr}'.", "suggestion": "Format must be `<type> <period> <std_dev> of <tf>`, e.g., `bb_upper 20 2 of 5m`."})
                    continue
                ind_type = m.group(1)
                is_bool = bool(m.group(2))
                p1 = int(m.group(3))
                p2 = float(m.group(4)) if '.' in m.group(4) else int(m.group(4))
                tf = m.group(5) if m.group(5) else '5m'
                
                if tf not in ['1m', '5m', '15m', '30m', '1h', '4h', '1d']:
                    errors.append({"line": line_num, "error": f"Unsupported timeframe '{tf}'.", "suggestion": "Use standard timeframes like `5m`, `15m`, `1h`, `1d`."})
                
                config.indicators[var_name] = {'type': ind_type, 'p1': p1, 'p2': p2, 'tf': tf, 'period': p1, 'is_bool': is_bool}
                continue
                
            # Triple Parameter Indicators: macd_line, macd_signal (with optional _bool)
            if re.match(r'^(macd_line|macd_signal)(?:_bool)?\s*\d+', expr):
                m = re.match(r'^(macd_line|macd_signal)(_bool)?\s+(\d+)\s+(\d+)\s+(\d+)(?:\s+of\s+([0-9a-zA-Z]+))?$', expr)
                if not m:
                    errors.append({"line": line_num, "error": f"Malformed MACD syntax '{expr}'.", "suggestion": "Format must be `<macd_type> <fast> <slow> <signal> of <tf>`, e.g., `macd_line 12 26 9 of 5m`."})
                    continue
                ind_type = m.group(1)
                is_bool = bool(m.group(2))
                fast = int(m.group(3))
                slow = int(m.group(4))
                sig = int(m.group(5))
                tf = m.group(6) if m.group(6) else '5m'
                
                if tf not in ['1m', '5m', '15m', '30m', '1h', '4h', '1d']:
                    errors.append({"line": line_num, "error": f"Unsupported timeframe '{tf}'.", "suggestion": "Use standard timeframes like `5m`, `15m`, `1h`, `1d`."})
                
                config.indicators[var_name] = {'type': ind_type, 'fast': fast, 'slow': slow, 'sig': sig, 'tf': tf, 'period': slow, 'is_bool': is_bool}
                continue
                
            # Crossing parsing
            if expr.startswith('cross'):
                m = re.match(r'^crossing\s+(above|below)\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)$', expr)
                if not m:
                    errors.append({"line": line_num, "error": f"Malformed crossing syntax '{expr}'.", "suggestion": "Format must be exactly `crossing above <ind1> <ind2>` or `crossing below <ind1> <ind2>`."})
                    continue
                direction = 'cross_up' if m.group(1) == 'above' else 'cross_down'
                arg1 = m.group(2)
                arg2 = m.group(3)
                
                missing = [a for a in [arg1, arg2] if a not in defined_vars]
                if missing:
                    errors.append({"line": line_num, "error": f"Wrong variable selection. Indicators {missing} are not defined.", "suggestion": f"You must define {missing} as an indicator FIRST before using them in a crossing condition."})
                
                config.conditions[var_name] = {'type': direction, 'args': [arg1, arg2]}
                continue
                
            # Trend Check parsing
            if expr.startswith('trend'):
                m = re.match(r'^trend\s+(bullish|bearish)\s+([0-9a-zA-Z]+)$', expr)
                if not m:
                    errors.append({"line": line_num, "error": f"Malformed trend syntax '{expr}'.", "suggestion": "Format must be exactly `trend bullish <timeframe>` or `trend bearish <timeframe>`, e.g., `trend bullish 1h`."})
                    continue
                direction = 'trend_up' if m.group(1) == 'bullish' else 'trend_down'
                tf = m.group(2)
                config.conditions[var_name] = {'type': direction, 'tf': tf}
                continue

            # Comparison parsing: var = ref op value/ref
            m = re.match(r'^([a-zA-Z0-9_]+)\s*(>|<|>=|<=|==)\s*([a-zA-Z0-9_.]+)$', expr)
            if m:
                left = m.group(1)
                op = m.group(2)
                right_raw = m.group(3)
                
                if left not in defined_vars:
                    errors.append({"line": line_num, "error": f"Wrong variable selection: '{left}' is not defined.", "suggestion": f"Define '{left}' as an indicator or value before using it in a comparison."})
                
                # Check if right side is a number or a variable
                try:
                    right = float(right_raw)
                except ValueError:
                    right = right_raw
                    if right not in defined_vars:
                        errors.append({"line": line_num, "error": f"Wrong variable selection: '{right}' is not defined.", "suggestion": f"Define '{right}' before using it in a comparison."})
                
                config.comparisons[var_name] = {'left': left, 'op': op, 'right': right}
                continue
                
            errors.append({"line": line_num, "error": f"Unrecognized expression '{expr}'", "suggestion": "Check the Syntax Reference. Valid expressions start with `ema`, `sma`, `crossing`, `trend`, or use comparison operators like `>`."})
            
        except Exception as e:
            errors.append({"line": line_num, "error": f"Parser crash: {str(e)}", "suggestion": "Unexpected systemic error while evaluating this line."})
            
    if not config.buy_rules and not config.sell_rules:
        errors.append({"line": "EOF", "error": "Strategy has no execution rules!", "suggestion": "You must add at least one execution rule like `buy when <condition>` or `sell when <condition>` to complete the strategy."})
        
    return config, errors

def parse_strategy_text(text: str) -> ParsedStrategyConfig:
    config, errors = parse_and_analyze_strategy(text)
    if errors:
        raise ParseError(f"Line {errors[0]['line']}: {errors[0]['error']}")
    return config
