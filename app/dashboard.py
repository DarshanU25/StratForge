import os
from typing import Dict, Any
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Advanced Analytics", layout="wide", initial_sidebar_state="expanded")

# --- SUPABASE AUTHENTICATION SYSTEM ---
import os
from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(env_path)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except ImportError:
        st.error("Missing dependency! Please run: `pip install supabase python-dotenv`")
        st.stop()
else:
    st.warning("Missing Supabase credentials in backend `.env`. Bypassing Auth locally for development.")

if SUPABASE_URL and SUPABASE_KEY:
    if not st.session_state.get('authenticated', False):
        # Native premium CSS styling dynamically hooking the physical Streamlit login forms structurally
        st.markdown("""
        <style>
        @keyframes fadeUpLogin {
            0% { opacity: 0; transform: translateY(40px) scale(0.95); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }
        div.auth-container {
            animation: fadeUpLogin 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
            background: linear-gradient(145deg, rgba(20,20,20,0.9), rgba(15,15,15,0.7));
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.6), inset 0 0 20px rgba(0,255,136,0.05);
            max-width: 500px;
            margin: 40px auto;
            text-align: center;
        }
        .stTextInput>div>div>input { transition: 0.3s; border-radius: 8px !important; }
        .stTextInput>div>div>input:focus { border-color: #00ff88 !important; box-shadow: 0 0 10px rgba(0,255,136,0.3) !important; }
        @media (max-width: 768px) {
            div.auth-container { padding: 20px !important; margin: 20px auto !important; width: 95% !important; }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Deploy structural injection isolating form parameters natively over everything
        auth_ui = st.container()
        auth_ui.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        with auth_ui:
            st.markdown('<h1 style="text-align: center; font-size: 2.5rem; margin-bottom: 0;">🔐 StratForge</h1>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: #aaa; margin-bottom: 20px;">AI-Driven Quantitative Backtesting</p>', unsafe_allow_html=True)
            
            t_login, t_register = st.tabs(["Login", "Register"])
            
            import hashlib
            def get_hash(p): return hashlib.sha256(p.encode()).hexdigest()
            
            with t_login:
                email_l = st.text_input("Active Email", key="log_e")
                pass_l = st.text_input("Account Password", type="password", key="log_p")
                if st.button("Secure Login ➔", type="primary", use_container_width=True):
                    if email_l and pass_l:
                        try:
                            res = supabase.table('app_users').select('*').eq('email', email_l.lower()).eq('password_hash', get_hash(pass_l)).execute()
                            if len(res.data) > 0:
                                st.session_state.authenticated = True
                                st.session_state.user_email = res.data[0].get('email', email_l)
                                st.session_state.user_mobile = res.data[0].get('mobile', 'N/A')
                                st.rerun()
                            else:
                                st.error("Incorrect Email or Password.")
                        except Exception as e:
                            st.error(f"Database sync error: {e}")
                    else:
                        st.warning("Provide credentials.")
                        
            with t_register:
                email_r = st.text_input("Register New Email", key="reg_e")
                mobile_r = st.text_input("Mobile Number (incl. Country Code)", placeholder="+1 (999) 000-0000", key="reg_m")
                pass_r = st.text_input("Create Password", type="password", key="reg_p")
                if st.button("Register Account ➔", use_container_width=True):
                    if email_r and mobile_r and pass_r:
                        import re
                        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email_r):
                            st.error("Invalid Email Format.")
                        elif not re.match(r"^\+[1-9]\d{5,14}$", mobile_r.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")):
                            st.error("Invalid Mobile Format. E.164 required (+).")
                        else:
                            clean_mobile = "+" + "".join(filter(str.isdigit, mobile_r))
                            try:
                                res = supabase.table('app_users').insert({'email': email_r.lower(), 'mobile': clean_mobile, 'password_hash': get_hash(pass_r)}).execute()
                                # Auto-login immediately dynamically handling persistence organically
                                st.session_state.authenticated = True
                                st.session_state.user_email = email_r.lower()
                                st.session_state.user_mobile = clean_mobile
                                st.rerun()
                            except Exception as e:
                                if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                                    st.error("Email or Mobile is already registered! Please Login.")
                                else:
                                    st.error(f"Error: {e}")
                    else:
                        st.warning("Please provide all specific credentials natively.")
                        
        auth_ui.markdown('</div>', unsafe_allow_html=True)
        
        # Inject JavaScript dynamically assigning wrapper class explicitly since st.container natively ignores params
        import streamlit.components.v1 as components
        components.html("""<script>
            setTimeout(() => {
                const els = Array.from(window.parent.document.querySelectorAll('div[data-testid="stVerticalBlock"]'));
                for(let el of els) {
                    if(el.innerHTML.includes('StratForge')) {
                        el.classList.add('auth-container');
                        break;
                    }
                }
            }, 100);
        </script>""", height=0)
        
        st.stop()

# Build Header structurally natively splitting cleanly across 
c_header, c_profile = st.columns([5, 1])
with c_header:
    st.title("📈 Advanced Analytics Dashboard")
with c_profile:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(f"👤 {st.session_state.get('user_email', 'Guest')}"):
        st.markdown(f"**Mobile:** {st.session_state.get('user_mobile', 'N/A')}")
        st.markdown("**Status:** Verified")
        if st.button("Logout 🚪", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

# Global CSS for responsive scaling cleanly across ANY display
st.markdown("""
<style>
/* Universal Fluidity */
div.block-container { padding: 1rem 1rem !important; max-width: 1600px !important; width: 100% !important; }

/* Desktop / Ultrawide Monitors */
@media (min-width: 1440px) {
    div.block-container { max-width: 95% !important; padding: 2rem !important; }
    [data-testid="stMetricValue"] { font-size: 36px !important; }
}

/* Tablet / Notebook Optimizations */
@media (max-width: 1024px) {
    div.block-container { padding: 1.5rem !important; }
    h1 { font-size: 2.2rem !important; }
}

/* Deep Mobile Responsiveness (Phones) */
@media (max-width: 768px) {
    .stButton>button { padding: 14px !important; font-weight: bold; font-size: 16px !important; width: 100% !important; }
    [data-testid="stMetricValue"] { font-size: 24px !important; }
    [data-testid="stMetricDelta"] { font-size: 14px !important; }
    .stSelectbox>div>div>div { font-size: 16px !important; } /* Prevent iPhone auto-zoom */
    .stTextInput>div>div>input { font-size: 16px !important; } 
    .stTextArea>div>div>textarea { font-size: 16px !important; }
    div.row-widget.stRadio > div { flex-wrap: wrap !important; justify-content: center !important; }
    .tour-glow { padding: 1px !important; border-width: 2px !important; }
}
</style>
""", unsafe_allow_html=True)

# --- Tour State Machine ---
if 'has_visited' not in st.session_state:
    st.session_state.has_visited = True
    st.session_state.tour_active = True
    st.session_state.tour_step = 1

import json, base64

if "tour" in st.query_params and st.query_params["tour"] == "done":
    st.session_state.has_visited = True
    st.session_state.tour_active = False

# Native Zero-Database Cache Restorer: Parse URL explicitly reconstructing all past Widget params dynamically
if "app" in st.query_params and not st.session_state.get('app_loaded'):
    try:
        decoded = base64.urlsafe_b64decode(st.query_params["app"].encode()).decode()
        saved_state = json.loads(decoded)
        for k, v in saved_state.items():
            st.session_state[k] = v
    except Exception:
        pass
    st.session_state.app_loaded = True

if 'tour_active' not in st.session_state:
    st.session_state.tour_active = False

if st.session_state.get('just_finished_tour', False):
    st.session_state.just_finished_tour = False
    import streamlit.components.v1 as components
    components.html("""<script>
        setTimeout(() => {
            const openBtn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
            if (openBtn) openBtn.click();
            setTimeout(() => {
                const closeBtn = window.parent.document.querySelector('[data-testid="stSidebarCollapseButton"]');
                if (closeBtn) closeBtn.click();
            }, 1200); // Exposes sidebar briefly to structurally educate mobile users
        }, 500);
    </script>""", height=0)

disable_all = st.session_state.tour_active

if disable_all:
    step = st.session_state.tour_step
    import streamlit.components.v1 as components
    
    tour_ui = st.container()
    tour_ui.markdown('<span id="tour-hook"></span>', unsafe_allow_html=True)
    
    # Systematically yank the specific Python Container out of standard DOM and force it to float identically on Mobile and Desktop
    components.html("""<script>
        setTimeout(() => {
            const hook = window.parent.document.getElementById('tour-hook');
            if (hook) {
                let container = hook.closest('div[data-testid="stVerticalBlock"]');
                if (container) {
                    container.id = 'tour-hook-container';
                    container.style.position = 'fixed';
                    container.style.bottom = '20px';
                    container.style.left = '50%';
                    container.style.transform = 'translateX(-50%)';
                    container.style.width = '95%';
                    container.style.maxWidth = '600px';
                    container.style.backgroundColor = 'rgba(15, 15, 15, 0.95)';
                    container.style.backdropFilter = 'blur(10px)';
                    container.style.border = '2px solid #00ff88';
                    container.style.borderRadius = '15px';
                    container.style.padding = '15px';
                    container.style.zIndex = '9999999'; // Punch strictly over Mobile Sidebar Overlay constraints
                    container.style.boxShadow = '0 10px 40px rgba(0,0,0,0.9)';
                }
            }
        }, 100);
    </script>""", height=0)

    tour_ui.markdown("### 🧭 Interactive Tour")

    # Mobile-Exclusive Wizard Constraints natively suppressing the underlying heavy Streamlit execution view
    st.markdown("""
        <style>
        @media (max-width: 768px) {
            #tour-hook-container {
                position: fixed !important; top: 60px !important; left: 0 !important; right: 0 !important; bottom: 0 !important;
                width: 100vw !important; height: calc(100vh - 60px) !important; max-width: none !important; border-radius: 0 !important; border: none !important;
                background-color: #0e1117 !important; z-index: 99999999 !important; overflow-y: auto !important; padding: 30px 20px !important;
                transform: none !important; margin: 0 !important;
            }
            .mobile-mimic { display: block !important; }
            div[data-testid="stSidebar"] { display: none !important; }
        }
        @media (min-width: 769px) { .mobile-mimic { display: none !important; } }
        </style>
    """, unsafe_allow_html=True)

    # Manage Sidebar Visibility based on context (Desktop mainly, Mobile skips since it's completely overridden by the CSS above)
    if step == 1:
        components.html("""<script>
            setTimeout(()=> {
                const closeBtn = window.parent.document.querySelector('[data-testid="stSidebarCollapseButton"]');
                if (closeBtn) closeBtn.click();
            }, 300);
        </script>""", height=0)
    elif step >= 2 and step <= 6:
        components.html("""<script>
            setTimeout(()=> {
                const openBtn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
                if (openBtn) openBtn.click();
            }, 300);
        </script>""", height=0)
    else:
        components.html("""<script>
            setTimeout(()=> {
                const closeBtn = window.parent.document.querySelector('[data-testid="stSidebarCollapseButton"]');
                if (closeBtn) closeBtn.click();
            }, 300);
        </script>""", height=0)

    # Global CSS for the Pulse Highlight
    st.markdown("""
        <style>
        .tour-glow {
            box-shadow: 0 0 15px 5px #00ff88 !important;
            border: 2px solid #00ff88 !important;
            border-radius: 8px !important;
            padding: 2px !important;
            transition: all 0.3s ease-in-out;
        }
        </style>
    """, unsafe_allow_html=True)
    
    def inject_glow(target_text, wait_ms=1000):
        components.html(f"""<script>
            setTimeout(() => {{
                Array.from(window.parent.document.querySelectorAll('.tour-glow')).forEach(e => e.classList.remove('tour-glow'));
                const els = Array.from(window.parent.document.querySelectorAll('label, p, span, h2, h3'));
                const target = els.find(e => e.innerText && e.innerText.includes('{target_text}'));
                if (target) {{ 
                    target.scrollIntoView({{behavior: 'smooth', block: 'center'}}); 
                    let widget = target.closest('[data-testid="stSelectbox"], [data-testid="stNumberInput"], [data-testid="stCheckbox"], div[data-baseweb="textarea"]');
                    if(!widget) widget = target.parentElement;
                    if(widget) widget.classList.add('tour-glow');
                }}
            }}, {wait_ms});
        </script>""", height=0)

    if step == 1:
        tour_ui.info("👋 **Welcome to the Trading Dashboard!**\n\n**Step 1: The Sidebar Menu**\nThe control center of this application lives in the completely customizable Sidebar parameter panel.\n\n*💡 Example: Take a look at the very **top-left corner of your screen**. You'll see a small `>` arrow icon up there. That is exactly what you tap to open or close the dashboard config!*")
        components.html("""<script>
            setTimeout(() => {
                const btn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
                if (btn) { btn.classList.add('tour-glow'); }
            }, 1000);
        </script>""", height=0)

    elif step == 2:
        tour_ui.info("⚙️ **Step 2: Choose a Strategy.** We have 5 ready-to-use strategies that look for trades automatically.\n\n*💡 Example: Try picking 'MACD Momentum Trend' later to ride the wave of the market!* For now, we picked the **Opening Range Breakout (ORB)** strategy for you to look at.")
        st.session_state.strategy_mode_key = "Pre-built Strategies"
        st.session_state.strat_type_key = "Opening Range Breakout (ORB)"
        inject_glow("Active Strategy")
        
    elif step == 3:
        tour_ui.info("💰 **Step 3: Account Capital**\n\nHow much money are you starting with? The engine will simulate your profits based on this exact amount.\n\n*💡 Example: If you type $1,000,000, your trade sizes will be much bigger than if you test with just $1,000.* We left it at $10,000 for you.")
        st.session_state.account_capital_key = 10000.0
        inject_glow("Initial Capital ($)")
        
    elif step == 4:
        tour_ui.info("📈 **Step 4: Dynamic Growth Compounding**\n\nInstead of risking the exact same amount perfectly flat every day, this allows your trade size to organically increase as your account makes money!\n\n*💡 Example: If your account grows from $10,000 to $12,000, the system mathematically buys slightly more on the next trade to snowball your profits!*")
        st.session_state.compound_growth_key = True
        inject_glow("Compound Growth")
        
    elif step == 5:
        tour_ui.info("⏰ **Step 5: Trading Hours**\n\nYou can tell the bot to completely ignore chaotic times of the day (like late night chops).\n\n*💡 Example: Try setting the Start Hour to '14' (2:00 PM) and End Hour to '18' (6:00 PM) to strictly trade only during the volatile London/US Session hours!*")
        st.session_state.session_start_key = 9
        st.session_state.session_end_key = 23
        inject_glow("Start Hour")
        
    elif step == 6:
        tour_ui.info("🛡️ **Step 6: Protecting Your Money**\n\nWe just turned on the Trailing Stop Loss! It safely locks in your profits so winning trades never turn into losing ones.\n\n*💡 Example: We set the 'Trigger' to $15 and 'Lock' to $5. If your active trade hits $15 in profit, your Stop Loss mathematically shifts up to guarantee you walk away with at least $5 no matter what happens!*")
        st.session_state.use_be_key = True
        st.session_state.be_trigger_key = 15.0
        st.session_state.be_lock_key = 5.0
        inject_glow("Enable Trailing SL Lock")
        
    elif step == 7:
        tour_ui.info("⌨️ **Step 7: Build Your Own Strategy**\n\nWe flipped to the Custom Builder tab! You can build anything using easy English without being a programmer! The system creates real code based on your typing.\n\n*💡 Example: Try typing exactly this: `buy when price crosses above ema 20` and the engine evaluates it!*")
        st.session_state.strategy_mode_key = "Custom Strategy Builder"
        inject_glow("Script (DSL)")
        
    elif step == 8:
        tour_ui.info("🚀 **Step 8: AI Results & Charts**\n\nThe system evaluated thousands of candles mathematically! Scroll down to see the **Equity Curve** chart.\n\n*💡 Example: Look for the 'AI Strategy Optimization' text! It automatically tells you EXACTLY what 2-hour window is statistically making the most money based on your data!*")
        st.session_state.strategy_mode_key = "Pre-built Strategies"
        st.session_state.strat_type_key = "Dynamic SMA Crossover"
        inject_glow("Visual Trade", wait_ms=3000)
        
    def get_mimic_html(s):
        h, c = "", ""
        if s == 1: 
            h = "🧭 Navigation Control"
            c = "↖️ <b>Look at the Top-Left Corner!</b><br>Tapping the <code>></code> arrow button opens the full configurations."
        elif s == 2: 
            h = "🔧 Strategy Parameters"
            c = "Active Strategy:<br><b>Opening Range Breakout (ORB) ▼</b>"
        elif s == 3: 
            h = "💼 Account & Risk Settings"
            c = "Initial Capital ($):<br><b>$10,000.0</b>"
        elif s == 4: 
            h = "⚖️ Execution Parameters"
            c = "☑️ <b>Compound Growth (Dynamic Lot Sizing)</b>"
        elif s == 5: 
            h = "⚖️ Execution Parameters"
            c = "Trading Session (IST)<br>Start Hour: <b>9</b><br>End Hour: <b>23</b>"
        elif s == 6: 
            h = "⚖️ Execution Parameters"
            c = "☑️ <b>Enable Trailing SL Lock</b><br>Trigger: <b>$15.0</b> | Lock: <b>$5.0</b>"
        elif s == 7: 
            h = "📝 Custom Strategy Environment"
            c = "Script (DSL) Builder:<br><code>buy when price crosses above ema...</code>"
        elif s == 8: 
            h = "🔎 Visual Trade Inspector"
            c = "📊 <b>Equity Curves & Optimal AI Trades</b>"
            
        return f'''<div class="mobile-mimic" style="background:#1e1e1e; padding:15px; border-radius:10px; margin: 20px 0;">
            <div style="color:#aaa; font-size:12px; margin-bottom:5px; text-transform:uppercase; font-weight:bold;">{h}</div>
            <div style="border:2px solid #00ff88; padding:10px; border-radius:8px; background:#2d2d2d; color:#fff; font-size:16px; box-shadow: 0 0 15px rgba(0,255,136,0.5);">
                {c}
            </div>
        </div>'''
        
    tour_ui.markdown(get_mimic_html(step), unsafe_allow_html=True)
        
    b1, b2 = tour_ui.columns(2)
    if b1.button("Next Step ⏭️" if step < 8 else "Finish Tour 🔓", use_container_width=True, type="primary"):
        if step < 8:
            st.session_state.tour_step += 1
            st.rerun()
        else:
            st.session_state.tour_active = False
            st.session_state.just_finished_tour = True
            st.query_params["tour"] = "done"
            st.rerun()
    if step < 8 and b2.button("Skip Tour ❌", use_container_width=True):
        st.session_state.tour_active = False
        st.session_state.has_visited = True  # Ensure they aren't forced into tour again on reload
        st.session_state.just_finished_tour = True
        st.query_params["tour"] = "done"
        st.rerun()
    st.divider()
    
# --- Header Menu (Nav Bar) ---
if "strategy_mode_key" not in st.session_state:
    st.session_state.strategy_mode_key = "Pre-built Strategies"

try:
    strategy_mode = st.segmented_control(
        "Navigation",
        ["Pre-built Strategies", "Custom Strategy Builder"],
        label_visibility="collapsed",
        key="strategy_mode_key",
        disabled=disable_all
    )
    if not strategy_mode: # Handle deselection
        st.session_state.strategy_mode_key = "Pre-built Strategies"
        strategy_mode = "Pre-built Strategies"
except AttributeError:
    try:
        strategy_mode = st.pills("Navigation", ["Pre-built Strategies", "Custom Strategy Builder"], label_visibility="collapsed", key="strategy_mode_key", disabled=disable_all)
        if not strategy_mode:
            st.session_state.strategy_mode_key = "Pre-built Strategies"
            strategy_mode = "Pre-built Strategies"
    except AttributeError:
        # Fallback to horizontal radio
        st.markdown("<style>div.row-widget.stRadio > div{flex-direction:row;justify-content:center;background:#f0f2f6;padding:10px;border-radius:10px;}</style>", unsafe_allow_html=True)
        strategy_mode = st.radio("Navigation", ["Pre-built Strategies", "Custom Strategy Builder"], horizontal=True, label_visibility="collapsed", key="strategy_mode_key", disabled=disable_all)
st.divider()

# --- Session State Config ---
default_code = "ema1 = ema 5 of 5m\nema2 = ema 30 of 5m\ncross_up = crossing above ema1 ema2\nbuy when cross_up"
if 'custom_code' not in st.session_state:
    st.session_state.custom_code = default_code

# --- Sidebar Content ---
st.sidebar.header("🔧 Strategy Parameters")

strat_type = "Dynamic SMA Crossover"
strat_params = {}

if strategy_mode == "Pre-built Strategies":
    strat_type = st.sidebar.selectbox("Active Strategy", [
        "Dynamic SMA Crossover",
        "Opening Range Breakout (ORB)",
        "RSI Mean Reversion",
        "MACD Momentum Trend",
        "Bollinger Band Breakout"
    ], key="strat_type_key", disabled=disable_all)
    st.sidebar.divider()
    
    if strat_type == "Dynamic SMA Crossover":
        c_s1, c_s2 = st.sidebar.columns(2)
        strat_params['sma_fast_len'] = c_s1.number_input("SMA Fast", min_value=2, max_value=200, value=5, disabled=disable_all, key="sma_fast_key")
        strat_params['sma_slow_len'] = c_s2.number_input("SMA Slow", min_value=5, max_value=500, value=30, disabled=disable_all, key="sma_slow_key")
    elif strat_type == "Opening Range Breakout (ORB)":
        st.sidebar.info("Fixed Action: Physical Break of 14:00 MT5 (17:30 IST) Ranges inherently bound.")
    elif strat_type == "RSI Mean Reversion":
        strat_params['rsi_period'] = st.sidebar.number_input("RSI Period", min_value=2, max_value=100, value=14, disabled=disable_all, key="rsi_period_key")
        c_r1, c_r2 = st.sidebar.columns(2)
        strat_params['rsi_upper'] = c_r1.number_input("Overbought", min_value=10, max_value=100, value=70, disabled=disable_all, key="rsi_upper_key")
        strat_params['rsi_lower'] = c_r2.number_input("Oversold", min_value=10, max_value=100, value=30, disabled=disable_all, key="rsi_lower_key")
    elif strat_type == "MACD Momentum Trend":
        c_m1, c_m2, c_m3 = st.sidebar.columns(3)
        strat_params['macd_fast'] = c_m1.number_input("Fast", min_value=2, max_value=50, value=12, disabled=disable_all, key="macd_fast_key")
        strat_params['macd_slow'] = c_m2.number_input("Slow", min_value=5, max_value=100, value=26, disabled=disable_all, key="macd_slow_key")
        strat_params['macd_sig'] = c_m3.number_input("Signal", min_value=2, max_value=50, value=9, disabled=disable_all, key="macd_sig_key")
    elif strat_type == "Bollinger Band Breakout":
        c_b1, c_b2 = st.sidebar.columns(2)
        strat_params['bb_length'] = c_b1.number_input("BB Length", min_value=5, max_value=200, value=20, disabled=disable_all, key="bb_len_key")
        strat_params['bb_std'] = c_b2.number_input("BB Std Dev", min_value=0.5, max_value=5.0, value=2.0, disabled=disable_all, key="bb_std_key")
else:
    st.sidebar.success("Custom Strategy Builder Enabled")

custom_code = st.session_state.custom_code

with st.sidebar.expander("💼 Account & Risk Settings", expanded=disable_all):
    account_capital = st.number_input("Initial Capital ($)", min_value=10.0, max_value=1000000.0, value=1000.0, key="account_capital_key", disabled=disable_all)
    leverage = st.selectbox("Leverage (1:X)", options=[1, 10, 50, 100, 200, 500], index=3, disabled=disable_all, key="leverage_key")
    lot_size = st.number_input("Lot Size (1.0 = Standard)", min_value=0.01, max_value=100.0, value=0.10, step=0.01, disabled=disable_all, key="lot_size_key")
    st.divider()
    sl_usd = st.number_input("Stop Loss Amount ($)", min_value=1, max_value=5000, value=10, disabled=disable_all, key="sl_usd_key")
    tp_usd = st.number_input("Take Profit Amount ($)", min_value=1, max_value=10000, value=20, disabled=disable_all, key="tp_usd_key")
    spread_pips = st.number_input("Spread Penalty (Pips)", min_value=0.0, max_value=20.0, value=1.0, step=0.1, disabled=disable_all, key="spread_pips_key")

with st.sidebar.expander("⚖️ Execution Parameters", expanded=disable_all):
    use_be = st.checkbox("Enable Trailing SL Lock", value=True, key="use_be_key", disabled=disable_all)
    c_t1, c_t2 = st.columns([1, 1])
    be_trigger_usd = c_t1.number_input("Trigger at Profit ($)", min_value=1.0, max_value=5000.0, value=15.0, key="be_trigger_key", disabled=not use_be or disable_all)
    be_lock_usd = c_t2.number_input("Lock SL at Profit ($)", min_value=-5000.0, max_value=5000.0, value=5.0, key="be_lock_key", disabled=not use_be or disable_all)
    active_be_trigger = be_trigger_usd if use_be else 0.0
    active_be_lock = be_lock_usd if use_be else 0.0
    st.divider()
    analysis_days = st.number_input("Analysis Duration (Days)", min_value=1, max_value=400, value=30, disabled=disable_all, key="analysis_days_key")
    compound_growth = st.checkbox("Compound Growth (Dynamic Lot Sizing)", value=False, key="compound_growth_key", disabled=disable_all)
    st.divider()
    st.write("Trading Session (IST)")
    session_start = st.number_input("Start Hour", min_value=0, max_value=23, value=9, key="session_start_key", disabled=disable_all)
    session_end = st.number_input("End Hour", min_value=0, max_value=23, value=23, key="session_end_key", disabled=disable_all)

st.sidebar.divider()
run_btn_1 = st.sidebar.button("🚀 Apply Parameters & Run", use_container_width=True, type="primary", disabled=disable_all)

run_btn_2 = False

ema_config_gui: Dict[str, Dict[str, Any]] = {}

# Dead Multi-Timeframe path builder mapping arrays removed since Backend processes CSV scopes correctly autonomously.

# --- Inline Strategy Editor ---
if strategy_mode == "Custom Strategy Builder":
    st.subheader("📝 Custom Strategy Environment")
    
    col_ed, col_doc = st.columns([6, 4])
    
    with col_ed:
        st.session_state.custom_code = st.text_area(
            "Script (DSL) - Type your rules below:", 
            value=st.session_state.custom_code, 
            height=370,
            disabled=disable_all
        )
        run_btn_2 = st.button("🚀 Compile & Run Script", use_container_width=True, type="primary", disabled=disable_all)
                
    with col_doc:
        st.markdown("**📖 Syntax & Examples Reference**")
        with st.container(height=400):
            try:
                import os
                syntax_path = os.path.join(os.path.dirname(__file__), "strategy_syntax.md")
                with open(syntax_path, "r", encoding="utf-8") as f:
                    st.markdown(f.read())
            except Exception:
                st.warning("`strategy_syntax.md` reference not found.")
                
    st.divider()

    # --- Code Analysis Engine ---
    from engine.strategy_parser import parse_and_analyze_strategy
    parsed_cfg, syntax_errors = parse_and_analyze_strategy(st.session_state.custom_code)
    
    if syntax_errors:
        st.error(f"🚨 **Code Analysis Engine: {len(syntax_errors)} Syntax Error(s) Detected**")
        for err in syntax_errors:
            if str(err['line']) == '0' or str(err['line']) == 'EOF':
                st.warning(f"**Structural Error**: {err['error']}")
            else:
                st.warning(f"**Line {err['line']}**: {err['error']}")
            st.info(f"💡 **Suggested Fix**: {err['suggestion']}")
        
        st.stop() # Halt execution safely after full UI is rendered
    else:
        st.success("✅ Code Analysis Engine: Syntax Passed!")

class APITrade:
    def __init__(self, data):
        self.entry_time = pd.to_datetime(data["entry_time"]) if data["entry_time"] else None
        self.exit_time = pd.to_datetime(data["exit_time"]) if data["exit_time"] else None
        self.direction = data["direction"]
        self.size = data["size"]
        self.entry_price = data["entry_price"]
        self.exit_price = data["exit_price"]
        self.pnl = data["pnl"]

@st.cache_data(show_spinner=False)
def run_simulation(sl, tp, cap, lev, lot, days, compound, s_start, s_end, spread, ema_cfg, strict_paths, be_trigger, be_lock, strat_mode, custom_str, st_type, st_params):
    from datetime import datetime, timedelta
    start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    psize = lot * 100000 
    
    # HTTP payload mapper explicitly wrapping isolated sidebars cleanly into strict API formatting
    payload = {
        "strat_mode": strat_mode,
        "st_type": st_type,
        "custom_str": custom_str,
        "st_params": st_params,
        "sl_usd": sl,
        "tp_usd": tp,
        "account_capital": cap,
        "leverage": lev,
        "lot_size": lot,
        "analysis_days": days,
        "compound_growth": compound,
        "session_start": s_start,
        "session_end": s_end,
        "spread_pips": spread,
        "ema_config_gui": ema_cfg,
        "active_be_trigger": be_trigger,
        "active_be_lock": be_lock
    }
    
    # Target backend service uniformly mapping execution endpoints 
    import os
    base_url = os.environ.get("BACKEND_API_URL", "http://127.0.0.1:8000")
    API_URL = base_url if "/api/v1/simulate" in base_url else f"{base_url.rstrip('/')}/api/v1/simulate"
    
    import json
    import hashlib
    payload_str = json.dumps(payload, sort_keys=True)
    config_hash = hashlib.sha256(payload_str.encode()).hexdigest()
    
    results = None
    cache_hit = False
    
    # Step 1: Global Cache Probe natively across ALL users
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            cache_res = supabase.table('backtest_cache').select('results_json').eq('config_hash', config_hash).execute()
            if len(cache_res.data) > 0:
                results = cache_res.data[0]['results_json']
                cache_hit = True
        except Exception:
            pass # Failsafe against absolute database downtime
            
    # Step 2: High-Performance Internal Engine Execution (Cache Miss / First User) natively serverless
    if not cache_hit:
        try:
            from engine.strategy import DynamicSMAStrategy, ORBStrategy, RSIReversalStrategy, MACDTrendStrategy, BollingerBreakoutStrategy
            from engine.strategy_parser import parse_strategy_text
            from engine.strategy import BuilderStrategy
            from engine.backtester import Backtester
            
            data_paths = {'5m': os.path.join(os.path.dirname(__file__), "data", "EURUSD_5m.csv")}
            for tf in ['15m', '30m', '1h', '1d']:
                tf_path = os.path.join(os.path.dirname(__file__), "data", f"EURUSD_{tf}.csv")
                if os.path.exists(tf_path):
                    data_paths[tf] = tf_path
                    
            if strat_mode == "Pre-built Strategies":
                S_CLASS = DynamicSMAStrategy
                if st_type == "Opening Range Breakout (ORB)": S_CLASS = ORBStrategy
                elif st_type == "RSI Mean Reversion": S_CLASS = RSIReversalStrategy
                elif st_type == "MACD Momentum Trend": S_CLASS = MACDTrendStrategy
                elif st_type == "Bollinger Band Breakout": S_CLASS = BollingerBreakoutStrategy
                
                class BoundStrategy(S_CLASS):
                    def __init__(self, data):
                        super().__init__(data, sl_usd=sl, tp_usd=tp, position_size=psize, ema_config=ema_cfg, **st_params)
            else:
                parsed_config = parse_strategy_text(custom_str)
                class BoundStrategy(BuilderStrategy):
                    def __init__(self, data):
                        super().__init__(data, config=parsed_config, sl_usd=sl, tp_usd=tp, position_size=psize, ema_config=ema_cfg)
                        
            tester = Backtester(
                data_paths=data_paths, 
                strategy_class=BoundStrategy, 
                ema_config=ema_cfg,
                primary_tf='5m',
                start_date=start,
                cash=cap,
                leverage=lev,
                position_size=psize,
                compound=compound,
                session_start=s_start,
                session_end=s_end,
                spread_pips=spread,
                break_even_trigger=be_trigger,
                break_even_lock=be_lock
            )
            
            results = tester.run()
            
            import math
            def _clean_float(val):
                if pd.isna(val) or math.isnan(val) or math.isinf(val): return None
                return float(val)
            
            serialized_trades = []
            for t in results['Trades']:
                try:
                    serialized_trades.append({
                        "entry_time": str(t.entry_time) if pd.notna(t.entry_time) else None,
                        "exit_time": str(t.exit_time) if pd.notna(t.exit_time) else None,
                        "direction": int(t.direction),
                        "size": float(t.size),
                        "entry_price": float(t.entry_price),
                        "exit_price": float(t.exit_price) if t.exit_price else None,
                        "pnl": _clean_float(t.pnl)
                    })
                except Exception: pass
                    
            results['Trades'] = serialized_trades
            results['Equity Curve'] = [_clean_float(x) for x in results.get('Equity Curve', [])]
            results['Blown Up Date'] = str(results.get('Blown Up Date')) if results.get('Blown Up Date') else None
            
            # Step 3: Global Cache Push sequentially distributing processing load natively
            if SUPABASE_URL and SUPABASE_KEY:
                try:
                    supabase.table('backtest_cache').insert({'config_hash': config_hash, 'results_json': results}).execute()
                except Exception:
                    pass
        except Exception as e:
            raise Exception(f"Internal Engine Execution Failed! Ensure data is mounted securely.\nError: {str(e)}")
            
    # Resolve Payload Types implicitly overriding raw execution strings cleanly
    if 'Trades' in results:
        results['Trades'] = [APITrade(t) for t in results['Trades']]
        
    current_dir = os.path.dirname(__file__)
    data_path = os.path.join(current_dir, "data", "EURUSD_5m.csv")
    df_raw = pd.read_csv(data_path, encoding='utf-16le', names=['DateTime', 'Open', 'High', 'Low', 'Close', 'TickVol', 'Spread'], on_bad_lines='skip')
    df_raw['DateTime'] = pd.to_datetime(df_raw['DateTime'], errors='coerce')
    df_raw.set_index('DateTime', inplace=True)
    for col in ['Open', 'High', 'Low', 'Close']: df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')

    return results, df_raw

with st.spinner("🚀 Running Engine Simulation & Validating Dependencies..."):
    try:
        force_tour = (disable_all and step == 8)
        if run_btn_1 or run_btn_2 or 'backend_results' not in st.session_state or force_tour:
            
            # Formally Execute Margin Validation Pre-Check
            approx_price = 1.10 # Base heuristic for EURUSD pairing algorithms natively
            contract_size = 100000 # Standard lot scaling
            required_margin = (lot_size * contract_size * approx_price) / leverage
            
            if required_margin > account_capital:
                st.error(f"### 🛑 Insufficient Capital For Execution!\n\nYou do not have sufficient capital to execute this order.\n\nYour trade size mandates a holding margin constraint of **${required_margin:,.2f}** (Trading {lot_size} lots at 1:{leverage} leverage), but your Account Capital is only **${account_capital:,.2f}**.\n\nThe exchange has rejected your parameters.\n\n**Action Required to proceed:**\n1. Increase your Initial Capital.\n2. Apply higher Leverage (e.g., 1:100 or 1:500).\n3. Decrease your Lot Size structurally.", icon="🚨")
                st.stop()

            # Formally Serialize User Activity state into Sharable Config Cache seamlessly on trigger execution
            state_to_save = {k: v for k, v in st.session_state.items() if k.endswith('_key') or k == 'custom_code'}
            st.query_params["app"] = base64.urlsafe_b64encode(json.dumps(state_to_save).encode()).decode()

            results, df_raw = run_simulation(sl_usd, tp_usd, account_capital, leverage, lot_size, analysis_days, compound_growth, session_start, session_end, spread_pips, ema_config_gui, None, active_be_trigger, active_be_lock, strategy_mode, custom_code, strat_type, strat_params)
            
            # Formally synchronize explicit backtest evaluations permanently across passive page reruns
            st.session_state.backend_results = results
            st.session_state.backend_df = df_raw
        else:
            # Sync to perfectly matched old evaluations if User interacts exclusively with Sidebar parameters without actively compiling
            results = st.session_state.backend_results
            df_raw = st.session_state.backend_df

    except Exception as e:
        st.error(f"Error executing backtester: {e}")
        st.stop()

# Calculate Streaks
max_win_streak = 0
max_loss_streak = 0
current_win_streak = 0
current_loss_streak = 0

for t in results['Trades']:
    if t.pnl is not None:
        if t.pnl > 0:
            current_win_streak += 1
            current_loss_streak = 0
            if current_win_streak > max_win_streak:
                max_win_streak = current_win_streak
        elif t.pnl <= 0:
            current_loss_streak += 1
            current_win_streak = 0
            if current_loss_streak > max_loss_streak:
                max_loss_streak = current_loss_streak

# Calculate Optimal Trading Window
best_time_str = "N/A"
best_window_pnl = 0
best_win_cnt = 0
best_loss_cnt = 0

if len(results['Trades']) > 0:
    hourly_pnl = {h: 0.0 for h in range(24)}
    hourly_wins = {h: 0 for h in range(24)}
    hourly_losses = {h: 0 for h in range(24)}
    
    for t in results['Trades']:
        try:
            trade_ist = pd.to_datetime(t.entry_time) + pd.Timedelta(hours=3, minutes=30)
            h = trade_ist.hour
            if t.pnl is not None:
                hourly_pnl[h] += t.pnl
                if t.pnl > 0: hourly_wins[h] += 1
                elif t.pnl <= 0: hourly_losses[h] += 1
        except Exception:
            pass
            
    pnl_array = [hourly_pnl.get(h, 0) for h in range(24)]
    
    best_window_pnl = -float('inf')
    best_start = 0
    best_length = 1
    
    for length in range(1, 15):
        for start_h in range(24):
            w_pnl = sum(pnl_array[(start_h + j) % 24] for j in range(length))
            w_wins = sum(hourly_wins.get((start_h + j) % 24, 0) for j in range(length))
            w_loss = sum(hourly_losses.get((start_h + j) % 24, 0) for j in range(length))
                
            if w_pnl > best_window_pnl and (w_wins + w_loss) > 0:
                best_window_pnl = w_pnl
                best_start = start_h
                best_length = length
                best_win_cnt = w_wins
                best_loss_cnt = w_loss
                
    if best_window_pnl > 0:
        end_h = (best_start + best_length - 1) % 24
        best_time_str = f"{best_start:02d}:00 to {end_h:02d}:59"

# --- Top Level Metrics ---
# Responsive 3x2 Grid perfectly tailored for Tablets and Mobiles to prevent horizontal scaling crunches
c1, c2, c3 = st.columns(3)
c1.metric("Total PnL", f"${results['Total PnL']:,.2f}", f"Bal: ${results['Final Cash']:.2f}")
c2.metric("Total Trades Exe.", f"{results['Total Trades']}")
c3.metric("Win Rate", f"{results['Win Rate']:.2f}%")

st.markdown("<br>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)
c4.metric("Max Drawdown", f"{results['Max Drawdown']:.2f}%")
c5.metric("Max Win Streak", f"{max_win_streak} 🔥")
c6.metric("Max Loss Streak", f"{max_loss_streak} 🧊")

st.markdown("---")

# Health check logic
if results.get('Blown Up Date'):
    st.error(f"🚨 **MARGIN CALL!** Your account capital (`${account_capital:,.2f}`) mathematically exhausted to exactly zero and blew up on **{results['Blown Up Date']}**. Trading logic was permanently halted exactly on that day.")
elif float(results['Final Cash']) <= 0:
    st.error("🚨 **MARGIN CALL!** Your account capital blew up completely (-100% loss). Your Risk or Lot Size was too high.")
elif float(results['Max Drawdown']) < -50.0:
    st.warning("⚠️ **DANGER!** Your account suffered massive drawdowns exceeding -50%. The strategy survived, but risk is extremely high.")
else:
    st.success("✅ **ACCOUNT HEALTHY.** Survival secured across test period with manageable drawdown.")

if best_window_pnl > 0:
    total_window_trades = best_win_cnt + best_loss_cnt
    window_wr = (best_win_cnt / total_window_trades * 100) if total_window_trades > 0 else 0
    st.info(f"💡 **AI Strategy Optimization:** The mathematically optimal trading window generated from this dataset is **{best_time_str} IST**. Filtering exactly to this block captures **+${best_window_pnl:,.2f}** with a highly isolated win concentration ({window_wr:.1f}% Win Rate, {best_loss_cnt} total losses).")

# --- Interactive Charts ---
col_L, col_R = st.columns([2, 1])

with col_L:
    st.subheader("📊 Capital Equity Curve")
    if len(results['Equity Curve']) > 0:
        df_eq = pd.DataFrame(results['Equity Curve'], columns=['Capital'])
        fig_eq = px.line(df_eq, y='Capital', 
                         title='Cumulative Portfolio Value', 
                         template='plotly_dark')
        # Fill visually below line
        fig_eq.update_traces(fill='tozeroy', line_color='#00ff88')
        st.plotly_chart(fig_eq, use_container_width=True)
    else:
        st.info("⚠️ Not enough data points to plot the equity curve.")

with col_R:
    st.subheader("💰 Individual Trade Results")
    trades = results['Trades']
    if len(trades) > 0:
        pnls = [t.pnl for t in trades]
        df_trades = pd.DataFrame({'Trade ID': range(1, len(pnls)+1), 'Profit': pnls})
        df_trades['Result Category'] = ['Win' if x > 0 else 'Loss' for x in df_trades['Profit']]
        
        fig_bar = px.bar(df_trades, x='Trade ID', y='Profit', color='Result Category', 
                         color_discrete_map={'Win': '#00ff88', 'Loss': '#ff4444'},
                         template='plotly_dark')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("⚠️ Zero trades executed under current parameters.")

st.divider()
st.subheader("📜 Detailed Trade Log (IST Timezone)")

if len(results['Trades']) > 0:
    trade_list = []
    for t in results['Trades']:
        try:
            entry_ist = (pd.to_datetime(t.entry_time) + pd.Timedelta(hours=3, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
            exit_ist = (pd.to_datetime(t.exit_time) + pd.Timedelta(hours=3, minutes=30)).strftime('%Y-%m-%d %H:%M:%S') if t.exit_time else "Open"
        except Exception:
            entry_ist = str(t.entry_time)
            exit_ist = str(t.exit_time)
            
        trade_list.append({
            "Entry Time (IST)": entry_ist,
            "Exit Time (IST)": exit_ist,
            "Direction": "Long" if t.direction == 1 else "Short",
            "Size": round(t.size, 2),
            "Entry Price": round(t.entry_price, 5),
            "Exit Price": round(t.exit_price, 5) if t.exit_price else None,
            "PnL ($)": round(t.pnl, 2) if t.pnl else 0.0
        })
    df_log = pd.DataFrame(trade_list)
    st.dataframe(df_log, use_container_width=True)
else:
    st.info("No trades to display.")

# --- Visual Trade Inspector ---
st.divider()
st.subheader("🔎 Visual Trade Inspector")
if len(results['Trades']) > 0:
    st.markdown("Select a specific trade by its **Trade Number** from the Detailed Log above to automatically visualize the execution logic exactly as it happened on the timeframe.")
    
    trade_idx = st.number_input("Select Trade Execution Number:", min_value=1, max_value=len(results['Trades']), value=1)
    selected_trade = results['Trades'][trade_idx - 1]
    
    e_time = selected_trade.entry_time
    x_time = selected_trade.exit_time
    
    if x_time:
        # Guarantee the plot formally starts before the exact 14:00 MT5 (17:30 IST) ORB formation window natively
        # so the user can accurately see the physical range creation every single time, even if execution delayed extensively.
        orb_origin_mt5 = e_time.replace(hour=13, minute=45, second=0, microsecond=0)
        
        # Pull chart background strictly 15 mins before ORB creation, OR 25 mins before entry, whichever mathematically occurred EARLIER.
        start_plot = min(e_time - pd.Timedelta(minutes=25), orb_origin_mt5)
        
        # Buffer exactly 5 candles after exit for structured execution context
        end_plot = x_time + pd.Timedelta(minutes=25)
        
        mask = (df_raw.index >= start_plot) & (df_raw.index <= end_plot)
        df_plot = df_raw.loc[mask]
        
        if not df_plot.empty:
            import plotly.graph_objects as go
            
            # Convert timezone and extract string literals so Plotly renders Categorical Ticks natively (no hour rounding)
            ist_index = df_plot.index + pd.Timedelta(hours=3, minutes=30)
            e_time_ist = e_time + pd.Timedelta(hours=3, minutes=30)
            x_time_ist = x_time + pd.Timedelta(hours=3, minutes=30)
            
            x_labels = ist_index.strftime('%Y-%m-%d %H:%M')
            e_label = e_time_ist.strftime('%Y-%m-%d %H:%M')
            x_label = x_time_ist.strftime('%Y-%m-%d %H:%M')
            
            fig = go.Figure(data=[go.Candlestick(x=x_labels,
                            open=df_plot['Open'], high=df_plot['High'],
                            low=df_plot['Low'], close=df_plot['Close'],
                            increasing_line_color='#00ff88', decreasing_line_color='#ff4444',
                            name="Price Action")])
                            
            # ORB physical levels dynamically removed from Visual Trade Inspector per request.

                            
            # Add active Entry Marker cleanly over boundaries
            fig.add_trace(go.Scatter(x=[e_label], y=[selected_trade.entry_price], 
                                     mode='markers', marker=dict(size=18, color='cyan', symbol='triangle-right', line=dict(width=2, color='white')),
                                     name=f'Entry ({"Long" if selected_trade.direction == 1 else "Short"})'))
                                     
            # Add valid Exit Marker matching directional PnL parameters
            exit_color = '#00ff88' if selected_trade.pnl > 0 else '#ff4444'
            fig.add_trace(go.Scatter(x=[x_label], y=[selected_trade.exit_price], 
                                     mode='markers', marker=dict(size=18, color=exit_color, symbol='triangle-left', line=dict(width=2, color='white')),
                                     name=f'Exit ({round(selected_trade.pnl, 2)}$)'))
                                     
            fig.update_layout(title=f"Execution Candlestick Plot for Trade #{trade_idx}",
                              xaxis_title="Time (IST Zone)",
                              yaxis_title="Asset Price",
                              template='plotly_dark',
                              xaxis_rangeslider_visible=False,
                              xaxis_type='category',
                              height=600)
                              
            st.plotly_chart(fig, use_container_width=True)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Selected Direction", 'Long 🔼' if selected_trade.direction == 1 else 'Short 🔽')
            c2.metric("Executed Entry Price", f"{selected_trade.entry_price:.5f}")
            c3.metric("Resolved Exit Price", f"{selected_trade.exit_price:.5f}")
            c4.metric("Extracted Net Profit", f"${selected_trade.pnl:.2f}")
        else:
            st.warning("Could not extract chart background dataset structure. Array mapping might be out of temporal bounds.")
    else:
        st.info("This recorded trade is actively Open. Technical chart rendering logic is engineered exclusively for closed histories.")
