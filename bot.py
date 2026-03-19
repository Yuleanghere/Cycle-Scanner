import requests
import time

# 1. Insert your Token and Chat ID here
TELEGRAM_BOT_TOKEN = "8678505929:AAHfWgTLfWjwNwGtNXafxtP1j7qV7rvbBp0"
TELEGRAM_CHAT_ID = "5549600755"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error Telegram: {e}")

def analyze_advanced_cycle(token_address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    try:
        response = requests.get(url).json()
        if not response.get('pairs'):
            return None

        pair = response['pairs'][0]
        symbol = pair.get('baseToken', {}).get('symbol', 'Unknown')
        price = float(pair.get('priceUsd', 0))
        liquidity = float(pair.get('liquidity', {}).get('usd', 0))
        
        # Fetch 1-hour (h1) data for faster signals
        vol_1h = float(pair.get('volume', {}).get('h1', 0))
        price_change_1h = float(pair.get('priceChange', {}).get('h1', 0))
        
        txns_1h = pair.get('txns', {}).get('h1', {})
        buys_1h = int(txns_1h.get('buys', 0))
        sells_1h = int(txns_1h.get('sells', 0))

        # Security 1: Liquidity must be over $50k to prevent scams
        if liquidity < 50000:
            return None

        # Calculate 1H Ratio: Check for unusual volume spikes
        vol_liq_ratio = (vol_1h / liquidity) * 100 if liquidity > 0 else 0
        
        signal = ""

        # Advanced BUY Signal: 
        # Price is stable (<= 5% change), huge volume spike (Ratio >= 5%), and Buys > Sells
        if price_change_1h <= 5 and vol_liq_ratio >= 5 and buys_1h > sells_1h:
            signal = (
                f"🟢 <b>BUY SIGNAL (1H ALERT): {symbol}</b>\n"
                f"Cycle: Accumulation Breakout (Smart Money Entering)\n"
                f"Price: ${price:.6f}\n"
                f"1H Volume: ${vol_1h:,.0f} (Volume Spike!)\n"
                f"Buys/Sells (1H): {buys_1h} / {sells_1h}"
            )

        # Advanced SELL Signal: 
        # Price pumps >= 15% in 1 hour OR heavy selling pressure (Sells > Buys + High Volume)
        elif price_change_1h >= 15 or (vol_liq_ratio >= 5 and sells_1h > buys_1h):
            signal = (
                f"🔴 <b>SELL SIGNAL (1H ALERT): {symbol}</b>\n"
                f"Cycle: Distribution (Prepare to dump)\n"
                f"Price: ${price:.6f}\n"
                f"1H Change: {price_change_1h}%\n"
                f"Buys/Sells (1H): {buys_1h} / {sells_1h}"
            )

        return signal

    except Exception as e:
        return None

# 2. List of token contracts to track
tokens_to_track = [
    "0x6982508145454Ce325dDbE47a25d4ec3d2311933", # PEPE
    "0x7d8146cf2166a041f72015e8df89b61bac2c2d49"  # Other token
]

print("🚀 Advanced 1H Tracker is now running...")
send_telegram_message("🤖 System Setup: Switched to 1H Timeframe for faster signals!")

# 3. System runs continuously
while True:
    for token in tokens_to_track:
        sig = analyze_advanced_cycle(token)
        if sig:
            print(f"✅ Found Signal for {token}! Sending to Telegram...")
            send_telegram_message(sig)
        time.sleep(2) # Sleep for 2 seconds to prevent API block
    
    print("Waiting 5 minutes before the next scan...")
    time.sleep(300) # Rescan every 5 minutes
