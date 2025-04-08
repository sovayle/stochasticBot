import requests
import os
from datetime import datetime

# CONFIGURATION
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")

SYMBOLS = ["EUR/JPY"]
TIMEFRAMES = {
    "5min": 30,
    "15min": 30,
    "4h": 30,
    "1day": 30
}

def fetch_data(symbol, interval):
    url = f"https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": 100,
        "apikey": TWELVE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "values" not in data:
        return []
    return data["values"]

def calculate_stochastic(values, k_period):
    closes = [float(c["close"]) for c in values]
    highs = [float(c["high"]) for c in values]
    lows = [float(c["low"]) for c in values]

    if len(closes) < k_period:
        return None

    recent_close = closes[0]
    low_n = min(lows[:k_period])
    high_n = max(highs[:k_period])

    if high_n - low_n == 0:
        return None

    k = ((recent_close - low_n) / (high_n - low_n)) * 100
    return round(k, 2)

def send_telegram_message(text, chat_ids):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for chat_id in chat_ids:
        payload = {"chat_id": chat_id, "text": text}
        requests.post(url, data=payload)

def main():
    chat_ids = [TELEGRAM_CHAT_ID]  # Add any additional chat IDs if necessary
    for tf, k_period in TIMEFRAMES.items():
        for symbol in SYMBOLS:
            values = fetch_data(symbol, tf)
            if not values:
                continue
            k = calculate_stochastic(values, k_period)

            # Check every 5 minutes for Stochastic 0 or 100
            if k == 0 or k == 100:
                send_telegram_message(f"📉 {symbol} ({tf}): Stochastic %K = {k}", chat_ids)

            # Check every 30th minute and send the Stochastic value regardless of 0 or 100
            current_time = datetime.now()
            if current_time.minute == 30:  # Check if it's the 30th minute
                send_telegram_message(f"📊 {symbol} ({tf}): Stochastic %K = {k}", chat_ids)

if __name__ == "__main__":
    main()
