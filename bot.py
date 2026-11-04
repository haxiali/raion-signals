import os
import time
import requests
import pandas as pd
import yfinance as yf

# === CREDENTIALS (Hardcoded) ===
TELEGRAM_BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "-5133609427"
ADMIN_ID = "7432874149"  # Aapki di gayi ID

BRAND = "RAION SIGNALS"

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

def send_telegram_message(message, chat_id=TELEGRAM_CHAT_ID):
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        print("Error: Telegram Bot Token missing!")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Telegram Response Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def calc_ind(df):
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
    print(f"\n=== {BRAND} Engine Running ===")
    
    # Startup message group aur admin dono par bhejne ke liye
    startup_msg = f"🚀 *{BRAND} Live Engine Active!*\nScanning 12 currency pairs with optimized logic."
    send_telegram_message(startup_msg, TELEGRAM_CHAT_ID)
    send_telegram_message(startup_msg, ADMIN_ID)

    for pair, tkr in PAIRS.items():
        try:
            print(f"Analyzing {pair} ({tkr})...")
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
            fvg = get_fvg(df)

            action = None
            if e20 > e50 and rsi < 45 and (fvg == "BULL" or close <= row['BB_L']):
                action = "BUY"
            elif e20 < e50 and rsi > 55 and (fvg == "BEAR" or close >= row['BB_UP']):
                action = "SELL"

            if action:
                msg = (
                    f"💎 *{BRAND} ULTRA VIP SIGNAL* 💎\n\n"
                    f"🌐 *Pair:* {pair}\n"
                    f"⚡ *Action:* {action} {'🟢' if action=='BUY' else '🔴'}\n"
                    f"⏱ *Timeframe:* 5m Closed Candle\n"
                    f"📈 *Indicators:* EMA + RSI + FVG / BB"
                )
                # Signals group aur admin dono ko bhejne ke liye
                send_telegram_message(msg, TELEGRAM_CHAT_ID)
                send_telegram_message(msg, ADMIN_ID)
                print(f"Signal sent for {pair}: {action}")
        except Exception as e:
            print(f"Error processing {pair}: {e}")

if __name__ == "__main__":
    run_bot()
    
