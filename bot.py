import time
import urllib.request
import json
import ssl
import requests
import yfinance as yf
import pandas as pd
import numpy as np

TOKEN = "9144870164:AAE4RSQvSvS_GibuOViRDHFYH04k2Fptor"
MY_CHAT_ID = "7432874149"
GROUP_CHAT_ID = "-5133609427"

BRAND = "RAION SIGNALS"
CHATS = [MY_CHAT_ID, GROUP_CHAT_ID]

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "EUR/JPY": "EURJPY=X",
    "AUD/CAD": "AUDCAD=X",
    "CAD/JPY": "CADJPY=X",
    "CAD/CHF": "CADCHF=X",
    "CHF/JPY": "CHFJPY=X",
    "GBP/JPY": "GBPJPY=X",
    "EUR/GBP": "EURGBP=X",
    "AUD/USD": "AUDUSD=X",
    "NZD/USD": "NZDUSD=X"
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

sess = requests.Session()
sess.headers['User-Agent'] = 'Mozilla/5.0'

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for cid in CHATS:
        payload = {"chat_id": cid, "text": text, "parse_mode": "Markdown"}
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, context=ctx) as res:
                pass
        except Exception as e:
            print(f"TG Error: {e}")

def calc_ind(df):
    df['E20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['E50'] = df['Close'].ewm(span=50, adjust=False).mean()
    mid = df['Close'].rolling(20).mean()
    std = df['Close'].rolling(20).std()
    df['BB_U'] = mid + (std * 2)
    df['BB_L'] = mid - (std * 2)
    delta = df['Close'].diff()
    g = delta.where(delta > 0, 0).rolling(14).mean()
    l = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = g / l
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def get_fvg(df):
    if len(df) < 3:
        return None
    h1 = df['High'].iloc[-3]
    l1 = df['Low'].iloc[-3]
    h3 = df['High'].iloc[-1]
    l3 = df['Low'].iloc[-1]
    if h1 < l3:
        return "BULL"
    if l1 > h3:
        return "BEAR"
    return None

def run_bot():
    print(f"\n=== {BRAND} Engine Running ===")
    for pair, tkr in PAIRS.items():
        try:
            obj = yf.Ticker(tkr, session=sess)
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
            b_up = row['BB_U']
            fvg = get_fvg(df)
            
            action = None
            if e20 > e50 and close <= b_low and rsi < 40 and fvg == "BULL":
                action = "BUY"
            elif e20 < e50 and close >= b_up and rsi > 60 and fvg == "BEAR":
                action = "SELL"
                
            if action:
                msg = (
                    f"💎 *{BRAND} ULTRA VIP SIGNAL* 💎\n\n"
                    f"🌍 *Pair:* {pair}\n"
                    f"⚡ *Action:* {action} {'🟢' if action=='BUY' else '🔴'}\n"
                    f"⏰ *Timeframe:* 5m Closed Candle\n"
                    f"📈 *Indicators:* EMA + BB + RSI + FVG\n"
                    f"🎯 *Target:* Direct Win"
                )
                send_msg(msg)
                time.sleep(2)
        except Exception as e:
            print(f"Err {pair}: {e}")

if __name__ == "__main__":
    run_bot()
          
