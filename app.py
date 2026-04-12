import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

st.set_page_config(page_title="Top 20 Bullish Stocks", layout="wide")

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
            
            # Download data with 'auto_adjust' to ensure consistency
            df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
            
            # Safety check: ensure we have enough data
            if df is None or len(df) < 200:
                continue
            
            # Use pandas_ta to calculate indicators
            df['SMA50'] = ta.sma(df['Close'], length=50)
            df['SMA200'] = ta.sma(df['Close'], length=200)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            # Accessing the last row safely
            curr = df.iloc[-1]
            prev_3m = df.iloc[-63] if len(df) >= 63 else df.iloc[0]
            prev_day = df.iloc[-2]

            price = float(curr['Close'])
            sma50 = float(curr['SMA50'])
            sma200 = float(curr['SMA200'])
            rsi = float(curr['RSI'])
            three_month_ret = ((price - float(prev_3m['Close'])) / float(prev_3m['Close'])) * 100
            daily_change = ((price - float(prev_day['Close'])) / float(prev_day['Close'])) * 100

            # BULLISH LOGIC
            if price > sma50 > sma200 and three_month_ret > 0:
                results.append({
                    "Ticker": ticker,
                    "Price": round(price, 2),
                    "3M Return %": round(three_month_ret, 2),
                    "RSI": round(rsi, 2),
                    "Daily %": round(daily_change, 2)
                })
        except Exception as e:
            # This skips tickers that cause errors without crashing the whole app
            continue
        finally:
            progress_bar.progress((i + 1) / len(tickers))
    
    status_text.empty()
    progress_bar.empty()
    
    if not results:
        return pd.DataFrame()
        
    df_final = pd.DataFrame(results)
    return df_final.sort_values(by="3M Return %", ascending=False).head(20)

# --- UI ---
st.title("📈 Top 20 Bullish Stocks")
st.write("Criteria: Price > 50MA > 200MA with positive 3-month momentum.")

today_date = datetime.now().strftime('%Y-%m-%d')
data = get_daily_scan(today_date)

if not data.empty:
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.write("Scanning complete. No stocks met the criteria at this moment.")

if st.button('Force Re-scan'):
    st.cache_data.clear()
    st.rerun()