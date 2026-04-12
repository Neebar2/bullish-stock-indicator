import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

st.set_page_config(page_title="Top 20 Bullish Stocks", layout="wide")

# This cache tells the app: "If you've already done this today, don't do it again."
@st.cache_data(ttl=86400)
def get_daily_scan(date_string):
    # 100 High-Volume NYSE & NASDAQ Stocks
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "AVGO", "ADBE", "NFLX",
        "AMD", "COST", "CRM", "QCOM", "INTU", "AMAT", "MU", "TXN", "INTC", "AMGN",
        "HON", "LRCX", "VRTX", "SBUX", "MDLZ", "ISRG", "GILD", "REGN", "ADI", "BKNG",
        "PANW", "SNPS", "CDNS", "CSX", "PYPL", "ASML", "MELI", "MAR", "ORLY", "CTAS",
        "KLAC", "NXPI", "MNST", "ADSK", "KDP", "LULU", "PAYX", "ROST", "IDXX", "EXC",
        "LLY", "JPM", "V", "MA", "UNH", "HD", "PG", "JNJ", "XOM", "CVX", "WMT", "BAC",
        "ABBV", "KO", "PEP", "COST", "ORCL", "TMO", "AVGO", "DHR", "MCD", "ACN", "ABT",
        "DIS", "PFE", "VZ", "WFC", "SCHW", "CAT", "UPS", "NEE", "BMY", "RTX", "AMAT",
        "BA", "AXP", "LOW", "COP", "IBM", "DE", "GE", "GS", "PLTR", "UBER", "SQ", "SHOP",
        "DKNG", "COIN", "MSTR", "HOOD", "AI"
    ]
    
    results = []
    
    # Progress indicator for the first run of the day
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    for i, ticker in enumerate(tickers):
        try:
            status_text.text(f"Scanning {ticker} ({i+1}/100)...")
            # Fetch data
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            
            if len(df) < 200: continue
            
            # Indicators
            df['SMA50'] = ta.sma(df['Close'], length=50)
            df['SMA200'] = ta.sma(df['Close'], length=200)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            curr = df.iloc[-1]
            prev_3m = df.iloc[-63] # ~3 months ago
            
            price = float(curr['Close'])
            sma50 = float(curr['SMA50'])
            sma200 = float(curr['SMA200'])
            rsi = float(curr['RSI'])
            three_month_ret = ((price - float(prev_3m['Close'])) / float(prev_3m['Close'])) * 100
            
            # --- BULLISH TREND LOGIC ---
            # 1. Price is above 50-day average
            # 2. 50-day average is above 200-day average (Structural Bull)
            # 3. Positive 3-month performance
            if price > sma50 > sma200 and three_month_ret > 0:
                results.append({
                    "Ticker": ticker,
                    "Price": round(price, 2),
                    "3M Return %": round(three_month_ret, 2),
                    "RSI (Momentum)": round(rsi, 2),
                    "Daily Change %": round(((price - float(df.iloc[-2]['Close'])) / float(df.iloc[-2]['Close'])) * 100, 2)
                })
        except:
            continue
        progress_bar.progress((i + 1) / len(tickers))
    
    status_text.empty()
    progress_bar.empty()
    
    df_final = pd.DataFrame(results)
    if not df_final.empty:
        # We take the top 20 based on 3-month strength
        return df_final.sort_values(by="3M Return %", ascending=False).head(20)
    else:
        return pd.DataFrame()

# --- INTERFACE ---
st.title("🚀 Top 20 Bullish Stocks (3-Month Trend)")
st.write("This scanner identifies stocks where the short-term trend is higher than the long-term trend, with strong 3-month momentum.")

today_date = datetime.now().strftime('%Y-%m-%d')
data = get_daily_scan(today_date)

if not data.empty:
    st.subheader(f"Top Performers as of {today_date}")
    st.dataframe(data, use_container_width=True, hide_index=True)
    st.info("Strategy: Buying stocks in a 'Golden Stack' (Price > 50MA > 200MA) that show consistent 3-month growth.")
else:
    st.warning("No stocks currently meet the strict bullish criteria. Check back after market close.")

st.caption("Data provided by Yahoo Finance. Updates once daily after market close.")