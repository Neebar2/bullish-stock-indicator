import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="Stock Trend Dashboard", layout="wide")

@st.cache_data(ttl=86400)
def get_market_data(date_string):
    # List of 100 stocks
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
    
    bullish_results = []
    all_stocks_list = []
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    for i, ticker in enumerate(tickers):
        try:
            status_text.text(f"Analyzing {ticker}... ({i+1}/{len(tickers)})")
            
            # Rate limit protection: small sleep
            time.sleep(0.1) 
            
            df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
            
            if df is None or len(df) < 50:
                continue
            
            # Calculations
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['SMA50'] = df['Close'].rolling(window=50).mean()
            
            curr = df.iloc[-1]
            prev_2w = df.iloc[-10] if len(df) >= 10 else df.iloc[0]
            prev_4w = df.iloc[-20] if len(df) >= 20 else df.iloc[0]
            
            price = float(curr['Close'])
            sma20 = float(curr['SMA20'])
            sma50 = float(curr['SMA50'])
            
            two_week_ret = ((price - float(prev_2w['Close'])) / float(prev_2w['Close'])) * 100
            four_week_ret = ((price - float(prev_4w['Close'])) / float(prev_4w['Close'])) * 100

            # Add to full list
            all_stocks_list.append({
                "Ticker": ticker,
                "Price": round(price, 2),
                "2W Change %": round(two_week_ret, 2),
                "4W Change %": round(four_week_ret, 2)
            })

            # Check Bullish Criteria
            if price > sma20 > sma50 and four_week_ret > 0:
                bullish_results.append({
                    "Ticker": ticker,
                    "Price": round(price, 2),
                    "4W Return %": round(four_week_ret, 2),
                    "2W Return %": round(two_week_ret, 2)
                })
        except Exception:
            continue # Skip failed tickers
        finally:
            progress_bar.progress((i + 1) / len(tickers))
    
    status_text.empty()
    progress_bar.empty()
    
    # SAFETY CHECK: If no stocks found, create empty dataframes with columns
    if not bullish_results:
        df_bullish = pd.DataFrame(columns=["Ticker", "Price", "4W Return %", "2W Return %"])
    else:
        df_bullish = pd.DataFrame(bullish_results).sort_values(by="4W Return %", ascending=False).head(20)
        
    if not all_stocks_list:
        df_all = pd.DataFrame(columns=["Ticker", "Price", "2W Change %", "4W Change %"])
    else:
        df_all = pd.DataFrame(all_stocks_list).sort_values(by="Ticker")
    
    return df_bullish, df_all

# --- UI ---
st.title("📊 Market Trend Dashboard")
today_date = datetime.now().strftime('%Y-%m-%d')

bullish_df, all_df = get_market_data(today_date)

st.header("🔥 Top 20 Bullish Stocks (4-Week Trend)")
if not bullish_df.empty:
    st.table(bullish_df)
else:
    st.warning("No stocks currently meet the bullish criteria or data is temporarily unavailable due to rate limits.")

st.divider()

st.header("📋 Full Market Snapshot (100 Stocks)")
if not all_df.empty:
    st.dataframe(all_df, use_container_width=True, hide_index=True)
else:
    st.error("No market data available. Please wait 1 minute and click Refresh.")

if st.button('Refresh Data'):
    st.cache_data.clear()
    st.rerun()