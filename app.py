import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="4-Week Bullish Scanner", layout="wide")

# Helper for RSI (useful to see if a stock is 'overbought')
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=86400)
def get_daily_scan(date_string):
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "AVGO", "ADBE", "NFLX",
        "AMD", "COST", "CRM", "QCOM", "INTU", "AMAT", "MU", "TXN", "INTC", "AMGN",
        "HON", "LRCX", "VRTX", "SBUX", "MDLZ", "ISRG", "GILD", "REGN", "ADI", "BKNG",
        "PANW", "SNPS", "CDNS", "CSX", "PYPL", "ASML", "MELI", "MAR", "ORLY", "CTAS",
        "KLAC", "NXPI", "MNST", "ADSK", "KDP", "LULU", "PAYX", "ROST", "IDXX", "EXC",
        "LLY", "JPM", "V", "MA", "UNH", "HD", "PG", "JNJ", "XOM", "CVX", "WMT", "BAC",
        "ABBV", "KO", "PEP", "ORCL", "TMO", "DHR", "MCD", "ACN", "ABT",
        "DIS", "PFE", "VZ", "WFC", "SCHW", "CAT", "UPS", "NEE", "BMY", "RTX",
        "BA", "AXP", "LOW", "COP", "IBM", "DE", "GE", "GS", "PLTR", "UBER", "SQ", "SHOP",
        "DKNG", "COIN", "MSTR", "HOOD", "AI"
    ]
    
    results = []
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    for i, ticker in enumerate(tickers):
        try:
            status_text.text(f"Scanning {ticker}... ({i+1}/{len(tickers)})")
            
            # Fetch 6 months of data (enough for 50MA and RSI)
            df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
            
            if df is None or len(df) < 50:
                continue
            
            # 4-Week Logic Calculations
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['SMA50'] = df['Close'].rolling(window=50).mean()
            df['RSI'] = calculate_rsi(df['Close'])
            
            curr = df.iloc[-1]
            prev_4w = df.iloc[-20] # 20 trading days = approx 4 weeks
            
            price = float(curr['Close'])
            sma20 = float(curr['SMA20'])
            sma50 = float(curr['SMA50'])
            rsi = float(curr['RSI'])
            four_week_ret = ((price - float(prev_4w['Close'])) / float(prev_4w['Close'])) * 100

            # --- 4-WEEK BULLISH CRITERIA ---
            # 1. Price is above the 20-day SMA
            # 2. 20-day SMA is above the 50-day SMA (Upward Momentum)
            # 3. 4-week return is positive
            if price > sma20 > sma50 and four_week_ret > 0:
                results.append({
                    "Ticker": ticker,
                    "Price": round(price, 2),
                    "4W Return %": round(four_week_ret, 2),
                    "RSI": round(rsi, 2),
                    "SMA 20": round(sma20, 2)
                })
        except:
            continue
        finally:
            progress_bar.progress((i + 1) / len(tickers))
    
    status_text.empty()
    progress_bar.empty()
    
    if not results:
        return pd.DataFrame()
        
    df_final = pd.DataFrame(results)
    # Sort by the strongest 4-week performers
    return df_final.sort_values(by="4W Return %", ascending=False).head(20)

# --- UI ---
st.title("📈 Top 20 Bullish Stocks (4-Week Trend)")
st.write("Criteria: Price > 20MA > 50MA with positive gains over the last 20 trading days.")

today_date = datetime.now().strftime('%Y-%m-%d')
data = get_daily_scan(today_date)

if not data.empty:
    st.table(data)
    st.info("These stocks are showing strong short-to-medium term upward momentum.")
else:
    st.write("No stocks currently match the 4-week bullish criteria.")

if st.button('Re-scan Now'):
    st.cache_data.clear()
    st.rerun()