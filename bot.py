mport os
import time
import requests
import pandas as pd
import yfinance as yf

# Telegram Credentials
TELEGRAM_BOT_TOKEN = 7432874149
TELEGRAM_CHAT_ID = os.-5133609427

BRAND = "RAION SIGNALS"

# Aapke bataye huwe mukammal 12 currency pairs (Yahoo Finance Tickers)
PAIRS = {
    "EUR/JPY": "EURJPY=X",
    "EUR/USD": "EURUSD=X",
    "EUR/GBP": "EURGBP=X",
    "AUD/JPY": "AUDJPY=X",
    "CAD/JPY": "CADJPY=X",
    "AUD/USD": "AUDUSD=X",
    "GBP/JPY": "GBPJPY=X",
    "CHF/JPY": "CHFJPY=X",
    "GBP/USD": "GBPUSD=X",
    "AUD/CHF": "AUDCHF=X",
    "EUR/AUD": "EURAUD=X",
    "GBP/CAD": "GBPCAD=X"
}

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def calc_ind(df):
    # Technical Indicators calculation (EMA, RSI, Bollinger Bands)
    df['E20'] = df['Close'].ewm(span=20).mean()
    df['E50'] = df['Close'].ewm(span=50).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['BB_MID'] = df['Close'].rolling(window=20).mean()
    df['BB_STD'] = df['Close'].rolling(window=20).std()
    df['BB_UP'] = df['BB_MID'] + (2 * df['BB_STD'])
    df['BB_L'] = df['BB_MID'] - (2 * df['BB_STD'])
    return df

def get_fvg(df):
    # Simple FVG check logic
    if len(df) < 3:
        return None
    h1 = df['High'].iloc[-3]
    l1 = df['Low'].iloc[-1]
    if h1 < l1:
        return "BULL"
    l3 = df['Low'].iloc[-3]
    h3 = df['High'].iloc[-1]
    if l3 > h3:
        return "BEAR"
    return None

def run_bot():
    # Startup message taake Telegram par pata chal jaye engine run ho gaya hai
    print(f"\n=== {BRAND} Engine Running ===")
    send_telegram_message(f"🚀 *{BRAND} Live Engine Active!*\nAnalyzing real market data for FVG, Order Blocks, EMA, & RSI.")

    for pair, tkr in PAIRS.items():
        try:
            obj = yf.Ticker(tkr)
            df = obj.history(period="7d", interval="5m")
            if df is None or len(df) < 50:
                continue
            df = calc_ind(df)
            row = df.iloc[-1]
            close = row['Close']
            e20 = row['E20']
            e50 = row['E50']
            rsi = row['RSI']
            b_low = row['BB_L']
            b_up = row['BB_UP']
            fvg = get_fvg(df)

            action = None
            if e20 > e50 and close <= b_low and rsi < 40 and fvg == "BULL":
                action = "BUY"
            elif e20 < e50 and close >= b_up and rsi > 60 and fvg == "BEAR":
                action = "SELL"

            if action:
                msg = (
                    f"💎 *{BRAND} ULTRA VIP SIGNAL* 💎\n\n"
                    f"🌐 *Pair:* {pair}\n"
                    f"⚡ *Action:* {action} {'🟢' if action=='BUY' else '🔴'}\n"
                    f"⏱ *Timeframe:* 5m Closed Candle\n"
                    f"📈 *Indicators:* EMA + BB + RSI + FVG"
                )
                send_telegram_message(msg)
        except Exception as e:
            print(f"Error processing {pair}: {e}")

if __name__ == "__main__":
    
