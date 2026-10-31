
# BUPPY BUY BOT - FINAL CONFIGURED
# Contract: 0x21f85a2e7ee0f0b9ba10072c502324e8e23c22fb
# Auto posts to Telegram Chat ID: -1004313558031
# Generated: 2026

import requests
import time
import asyncio
from telegram import Bot

BUPPY_CONTRACT = "0x21f85a2e7ee0f0b9ba10072c502324e8e23c22fb"
BSCSCAN_API_KEY = "5PW3PRWESNAAYP2519RSSR524H4ESJUSU6"
TELEGRAM_BOT_TOKEN = "9184457080:AAGtHwVI16wo4g-nxT3GbQKzhphbv14PcxI"
TELEGRAM_CHAT_ID = "-1004313558031"

BSCSCAN_URL = "https://api.bscscan.com/api"
last_tx_hash = None

def get_txs():
    params = {
        "module": "account",
        "action": "tokentx",
        "contractaddress": BUPPY_CONTRACT,
        "page": 1,
        "offset": 10,
        "sort": "desc",
        "apikey": BSCSCAN_API_KEY
    }
    try:
        r = requests.get(BSCSCAN_URL, params=params, timeout=15).json()
        if r.get('status') == '1':
            return r.get('result', [])
        else:
            print(f"BSCScan: {r.get('message')} - {r.get('result')}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_bnb_price():
    try:
        return float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT", timeout=5).json()['price'])
    except:
        return 650.0

async def send_buy_alert(tx, bnb_price):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        value = int(tx['value']) / (10 ** int(tx['tokenDecimal']))
        buyer = tx['to']
        tx_hash = tx['hash']
        block_num = tx['blockNumber']
        
        buyer_short = f"{buyer[:6]}...{buyer[-4:]}"
        tx_short = f"{tx_hash[:6]}...{tx_hash[-4:]}"
        
        # Estimate USD - you can improve by fetching token price from DexScreener API
        # For now placeholder - fetch real price via DexScreener later
        usd_value = value * 0.0000001 * 1000  # replace with real price logic
        
        # Try get market cap from DexScreener
        try:
            ds = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{BUPPY_CONTRACT}", timeout=10).json()
            if ds.get('pairs'):
                pair = ds['pairs'][0]
                usd_value = float(pair.get('priceUsd', 0)) * value
                market_cap = pair.get('fdv', 'N/A')
                liquidity = pair.get('liquidity', {}).get('usd', 'N/A')
                price_change = pair.get('priceChange', {}).get('h24', '0')
            else:
                market_cap = "Calculating..."
                liquidity = "Calculating..."
                price_change = "+0%"
        except:
            market_cap = "$... "
            liquidity = "$... "
            price_change = "+0%"
        
        message = f"""⬆️ *BUPPY BOUGHT* ⬆️

📦 *Event:* BUY | Status: CONFIRMED ✅

💰 *Amount:* {value:,.2f} BUPPY (~${usd_value:.2f}) ⬆️ {price_change}% 24h
👤 *Buyer:* `{buyer_short}`
🪙 *Token:* BUPPY / BNB | PancakeSwap V2
🔗 *TX:* `{tx_short}`

💵 USD VALUE: ${usd_value:.2f}
📊 MARKET CAP: {market_cap}
💧 LIQUIDITY: {liquidity}

🔍 https://bscscan.com/tx/{tx_hash}
Just now • Block {block_num} • bscscan.com
"""
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        print(f"✅ Posted buy: {tx_hash} - {value} BUPPY")
    except Exception as e:
        print(f"Telegram error: {e}")

def main():
    global last_tx_hash
    print(f"🚀 BUPPY Buy Bot Started")
    print(f"Contract: {BUPPY_CONTRACT}")
    print(f"Chat ID: {TELEGRAM_CHAT_ID}")
    print("Monitoring every 15s...")
    
    # First fetch to set baseline
    txs = get_txs()
    if txs:
        last_tx_hash = txs[0]['hash']
        print(f"Baseline TX set: {last_tx_hash}")
    else:
        print("No transactions yet or check API key")
    
    bnb_price = get_bnb_price()
    
    while True:
        try:
            txs = get_txs()
            if not txs:
                time.sleep(15)
                continue
            
            # Check for new txs newer than last
            new_txs = []
            for tx in txs:
                if tx['hash'] == last_tx_hash:
                    break
                new_txs.append(tx)
            
            # Process newest first but send oldest new first
            for tx in reversed(new_txs):
                # Filter only buys (not zero address mint, and from != to avoid self)
                if tx['from'] == "0x0000000000000000000000000000000000000000":
                    continue
                # Consider all token transfers as buys for now - you can filter by pair later
                print(f"New tx detected: {tx['hash']}")
                asyncio.run(send_buy_alert(tx, bnb_price))
            
            if new_txs:
                last_tx_hash = txs[0]['hash']
                
        except Exception as e:
            print(f"Loop error: {e}")
        
        time.sleep(15)

if __name__ == "__main__":
    main()
