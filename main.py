import os, asyncio, threading, requests, time
from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x39db5438317e583d46123f4b114fef376872e00d"
TOTAL_SUPPLY = 1000000000
CHANNEL_ID = None
TEMPLATE_PATH = "template.png"

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "MEH Bot LIVE!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

def get_live_data():
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{CA}"
        r = requests.get(url, timeout=10).json()
        pair = r['pairs'][0] if r.get('pairs') else {}
        mcap = float(pair.get('fdv', 0) or pair.get('marketCap', 0) or 66)
        price = float(pair.get('priceUsd', 0) or 0.0000000694)
        vol = float(pair.get('volume', {}).get('h24', 0) or 148)
        liq = float(pair.get('liquidity', {}).get('usd', 0) or 34)
        pair_addr = pair.get('pairAddress', '')
        burned = 23240000
        burn_pct = 2.32
        try:
            dead = "0x000000000000000000000000000000000000dEaD"
            bsc_url = f"https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress={CA}&address={dead}&tag=latest"
            resp = requests.get(bsc_url, timeout=8).json()
            if resp.get('status') == '1' and resp.get('result'):
                raw = int(resp['result'])
                for dec in [9, 18]:
                    test = raw / (10 ** dec)
                    if 1000000 < test < TOTAL_SUPPLY:
                        burned = test
                        break
                burn_pct = (burned / TOTAL_SUPPLY * 100)
        except:
            pass
        return mcap, price, vol, liq, burned, burn_pct, pair_addr
    except Exception as e:
        print(f"Data error: {e}")
        return 66, 0.0000000694, 148, 34, 23240000, 2.32, ""

def get_font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

def make_card(buy_amount=0, buyer=""):
    mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 6.60
    try:
        if os.path.exists(TEMPLATE_PATH):
            img = Image.open(TEMPLATE_PATH).convert("RGB")
            W, H = img.size
        else:
            W, H = 1024, 1536
            img = Image.new('RGB', (W, H), 'black')
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 680), (W, 1220)], fill="black")
        if buy_amount >= 0.1:
            draw.rectangle([(0, 0), (W, 200)], fill="#FFD700")
            draw.text((W//2, 20), f"NEW BUY ${buy_amount:.2f}", fill="black", font=get_font(50), anchor="mt")
            draw.rectangle([(0, 200), (W, 340)], fill="black")
            draw.text((W//2, 210), f"$MEH {gain:.2f}x", fill="#39FF14", font=get_font(80), anchor="mt")
            draw.text((W//2, 290), "BULLISH AF", fill="#FFEB00", font=get_font(50), anchor="mt")
        else:
            draw.rectangle([(0, 0), (W, 340)], fill="black")
            draw.text((W//2, 10), f"$MEH {gain:.2f}x", fill="#39FF14", font=get_font(90), anchor="mt")
            draw.text((W//2, 120), "BULLISH AF", fill="#FFEB00", font=get_font(60), anchor="mt")
        draw.rounded_rectangle([(60, 700), (490, 850)], radius=15, fill="#001100", outline="#00FF00", width=3)
        draw.text((275, 760), f"${mcap:,.0f}", fill="white", font=get_font(45), anchor="mt")
        draw.rounded_rectangle([(530, 700), (960, 850)], radius=15, fill="#001100", outline="#00FF00", width=3)
        draw.text((745, 760), f"${vol:,.0f}", fill="white", font=get_font(45), anchor="mt")
        draw.rounded_rectangle([(60, 870), (490, 1020)], radius=15, fill="#001100", outline="#00FF00", width=3)
        draw.text((275, 930), f"${liq:,.0f}", fill="white", font=get_font(45), anchor="mt")
        draw.rounded_rectangle([(530, 870), (960, 1020)], radius=15, fill="#001100", outline="#00FF00", width=3)
        draw.text((745, 935), f"${price:.10f}", fill="white", font=get_font(26), anchor="mt")
        draw.rounded_rectangle([(15, 1040), (W-15, 1170)], radius=20, fill="#1A0000", outline="#FF4400", width=4)
        draw.text((W//2, 1090), f"{burned/1000000:.2f}M MEH {burn_pct:.2f}%", fill="#FFAA00", font=get_font(38), anchor="mt")
        draw.rectangle([(0, 1180), (W, H)], fill="black")
        draw.text((W//2, 1190), "TO THE MOON", fill="#FFFF00", font=get_font(40), anchor="mt")
        path = "/tmp/meh.png"
        img.save(path, quality=95)
        return path, gain, mcap, price, vol, burned, burn_pct
    except Exception as e:
        print(f"Card error: {e}")
        # Fallback simple card
        img = Image.new('RGB', (600, 400), 'black')
        ImageDraw.Draw(img).text((300, 200), f"$MEH {gain:.2f}x", fill="green", font=get_font(40), anchor="mm")
        path = "/tmp/meh.png"
        img.save(path)
        return path, gain, mcap, price, vol, burned, burn_pct

last_tx_hash = ""
def monitor_buys(app):
    global last_tx_hash
    print("AUTO BUY MONITOR STARTED")
    while True:
        try:
            mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
            if not pair_addr:
                time.sleep(10)
                continue
            url = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={CA}&address={pair_addr}&page=1&offset=3&sort=desc"
            resp = requests.get(url, timeout=10).json()
            if resp.get('status') == '1' and resp.get('result'):
                for tx in resp['result'][:2]:
                    tx_hash = tx.get('hash', '')
                    if tx_hash == last_tx_hash:
                        break
                    if tx.get('from','').lower() == pair_addr.lower():
                        value = int(tx.get('value',0))
                        for dec in [9,18]:
                            tokens = value/(10**dec)
                            if 0 < tokens < TOTAL_SUPPLY:
                                usd = tokens*price
                                if usd >= 0.1:
                                    print(f"BUY ${usd:.2f}")
                                    last_tx_hash = tx_hash
                                    path, gain, mcap, price, vol, burned, burn_pct = make_card(buy_amount=usd, buyer=tx.get('to',''))
                                    caption = f"NEW BUY ${usd:.2f}! $MEH {gain:.2f}x MCap ${mcap:,.0f} {CA}"
                                    try:
                                        loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(loop)
                                        if CHANNEL_ID:
                                            loop.run_until_complete(app.bot.send_photo(chat_id=CHANNEL_ID, photo=open(path,'rb'), caption=caption))
                                    except Exception as e:
                                        print(e)
                                    break
        except Exception as e:
            print(f"Monitor error {e}")
        time.sleep(15)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("MEH Bot LIVE! /mehcard")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path, gain, mcap, price, vol, burned, burn_pct = make_card()
    caption = f"$MEH {gain:.2f}x BULLISH! MCap ${mcap:,.0f} Vol ${vol:,.0f} Burned {burned/1000000:.2f}M {CA}"
    await update.message.reply_photo(photo=open(path,'rb'), caption=caption)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    threading.Thread(target=monitor_buys, args=(app,), daemon=True).start()
    print("BOT LIVE")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
