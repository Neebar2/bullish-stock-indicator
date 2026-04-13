import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Stock Trend Dashboard", layout="wide")

# Helper for RSI
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=86400)
def get_market_data(date_string):
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
            df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
            
            if df is None or len(df) < 50:
                continue
            
            # Calculations
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['SMA50'] = df['Close'].rolling(window=50).mean()
            
            curr = df.iloc[-1]
            prev_2w = df.iloc[-10] # 10 trading days = 2 weeks
            prev_4w = df.iloc[-20] # 20 trading days = 4 weeks
            
            price = float(curr['Close'])
            sma20 = float(curr['SMA20'])
            sma50 = float(curr['SMA50'])
            
            two_week_ret = ((price - float(prev_2w['Close'])) / float(prev_2w['Close'])) * 100
            four_week_ret = ((price - float(prev_4w['Close'])) / float(prev_4w['Close'])) * 100

            # Data for the "All Stocks" table
            stock_data = {
                "Ticker": ticker,
                "Price": round(price, 2),
                "2W Change %": round(two_week_ret, 2),
                "4W Change %": round(four_week_ret, 2)
            }
            all_stocks_list.append(stock_data)

            # BULLISH CRITERIA (Table 1)
            if price > sma20 > sma50 and four_week_ret > 0:
                bullish_results.append({
                    "Ticker": ticker,
                    "Price": round(price, 2),
                    "4W Return %": round(four_week_ret, 2),
                    "2W Return %": round(two_week_ret, 2),
                    "Trend": "Strong Bullish"
                })
        except:
            continue
        finally:
            progress_bar.progress((i + 1) / len(tickers))
    
    status_text.empty()
    progress_bar.empty()
    
    df_bullish = pd.DataFrame(bullish_results).sort_values(by="4W Return %", ascending=False).head(20)
    df_all = pd.DataFrame(all_stocks_list).sort_values(by="Ticker")
    
    return df_bullish, df_all

# --- UI LAYOUT ---
st.title("📊 Market Trend Dashboard")
today_date = datetime.now().strftime('%Y-%m-%d')

# Run Scan
bullish_df, all_df = get_market_data(today_date)

# 1. TOP 20 BULLISH TABLE
st.header("🔥 Top 20 Bullish Stocks (4-Week Trend)")
st.write("Criteria: Price > 20MA > 50MA and positive 4-week performance.")
if not bullish_df.empty:
    st.table(bullish_df)
else:
    st.info("No stocks currently meet the specific bullish criteria.")

st.divider()

# 2. ALL STOCKS ANALYZED TABLE
st.header("📋 Full Market Snapshot (100 Stocks)")
st.write("Current prices and 2-week performance for all tracked tickers.")
if not all_df.empty:
    # We use st.dataframe here because it is searchable and scrollable
    st.dataframe(all_df, use_container_width=True, hide_index=True)
else:
    st.error("Error loading market data.")

# Controls
if st.button('Force Re-scan Now'):
    st.cache_data.clear()
    st.rerun()

st.caption(f"Last updated: {today_date}. Note: Price changes based on previous close.")
