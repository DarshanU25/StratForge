# StratForge 📈

StratForge is an advanced, AI-driven quantitative backtesting and trading dashboard. Built with Streamlit and powered by a robust Python backend, it allows traders to seamlessly test pre-built strategies, construct custom logic using a Domain-Specific Language (DSL), and analyze equity curves on built-in market data.

## Features

- **Pre-built Strategies**: Out-of-the-box support for Dynamic SMA Crossover, Opening Range Breakout (ORB), RSI Mean Reversion, MACD Momentum Trend, and Bollinger Band Breakout.
- **Custom Strategy Builder (DSL)**: Write your own trading rules in plain English. The built-in parser converts your logic into executable code (e.g., `buy when price crosses above ema 20`).
- **Interactive Tour**: An intuitive onboarding wizard for new users to explore the dashboard.
- **Risk Management settings**: Fine-tune Initial Capital, Leverage, Lot Size, Stop Loss, Take Profit, and Spread Penalty.
- **Advanced Execution Parameters**: Includes Compound Growth (dynamic lot sizing), Trailing Stop Loss Lock, and Session Time filters (e.g., London/US hours).
- **Backend Analytics Engine**: High-performance backtester with global cache capabilities to optimize recurrent evaluations.
- **Secure Authentication**: Integrated user registration and login powered by Supabase.

## Prerequisites

- **Python 3.8+**
- **Supabase Account** (for authentication schema)

## Setup & Configuration

1. **Install Dependencies**:
   ```bash
   pip install -r app/requirements.txt
   pip install supabase python-dotenv
   ```
   *(Note: The main required packages include `streamlit`, `pandas`, `plotly`, `requests`, `supabase`, and `python-dotenv`.)*

2. **Environment Variables**:
   In the `app/` directory, update or create a `.env` file containing your Supabase credentials:
   ```env
   SUPABASE_URL="your-supabase-url"
   SUPABASE_ANON_KEY="your-supabase-anon-key"
   ```
   *Note: If no Supabase credentials are provided, the system will bypass authentication locally for development purposes.*

3. **Data**:
   The engine relies on CSV files located in `app/data/` (e.g., `EURUSD_5m.csv`). Ensure your data directory is populated.

## How to Run

Navigate to the project root and start the Streamlit application:

```bash
cd app
streamlit run dashboard.py
```
This will open the application in your default web browser (usually at `http://localhost:8501`).

## How to Register & Sign In

The App includes a secure, animated authentication modal built natively into Streamlit.

**To Register:**
1. Open the app in your browser.
2. In the floating authentication modal, click on the **"Register"** tab.
3. Enter your active Email address.
4. Enter your Mobile Number (including the country code, e.g., `+1 999 000-0000`).
5. Create a secure password.
6. Click **"Register Account"**. You will be auto-logged in upon successful registration.

**To Sign In:**
1. Open the app and navigate to the **"Login"** tab on the authentication modal.
2. Enter your registered Email address.
3. Enter your Password.
4. Click **"Secure Login"**. If successful, you'll be granted access to the main dashboard.

## Project Structure

- `app/dashboard.py` - The main Streamlit entry point containing the UI, authentication wrapper, and the API payload generator.
- `app/engine/` - Contains the robust backtesting logic, strategy classes (`strategy.py`), DSL parser (`strategy_parser.py`), and the core `backtester.py`.
- `app/data/` - Holds historical tick and timeframe data for simulation (e.g., `EURUSD_5m.csv`).
- `app/strategy_syntax.md` - Reference documentation for the Custom Strategy DSL.
