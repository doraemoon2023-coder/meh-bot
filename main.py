import os, asyncio, threading, requests, time
from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x39db5438317e583d46123f4b114fef376872e00d"
TOTAL_SUPPLY = 1000000000
CHANNEL_ID = os.environ.get("CHANNEL_ID")

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "MEH Bot LIVE - Clean Bullish No Cut!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

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
                        burn_pct = (burned / TOTAL_SUPPLY * 100)
                        break
        except:
            pass
        return mcap, price, vol, liq, burned, burn_pct, pair_addr
    except:
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
        img = Image.open("template.png").convert("RGB") if os.path.exists("template.png") else Image.new('RGB', (1024, 1300), 'black')
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        # TOP - $MEH LANG, WALANG BULLISH AF, MALIIT BLACK PARA HINDI PUTOL ULO!
        draw.rectangle([(0, 0), (W, int(H*0.07))], fill="black")
        draw.text((W//2, int(H*0.035)), f"$MEH {gain:.2f}x", fill="#39FF14", font=get_font(int(H*0.08)), anchor="mm")
        
        # 4 BOXES - MALINIS SA LOOB, WALANG DOBLE!
        draw.text((int(W*0.375), int(H*0.48)), f"${mcap:,.0f}", fill="white", font=get_font(int(H*0.06)), anchor="mm")
        draw.text((int(W*0.625), int(H*0.48)), f"${vol:,.0f}", fill="white", font=get_font(int(H*0.06)), anchor="mm")
        draw.text((int(W*0.375), int(H*0.625)), f"${liq:,.0f}", fill="white", font=get_font(int(H*0.06)), anchor="mm")
        draw.text((int(W*0.625), int(H*0.625)), f"${price:.10f}", fill="white", font=get_font(int(H*0.032)), anchor="mm")
        
        # Burn
        draw.text((W//2, int(H*0.81)), f"{burned/1000000:.2f}M MEH {burn_pct:.2f}%", fill="#FFAA00", font=get_font(int(H*0.05)), anchor="mm")

        if buy_amount >= 0.1:
            draw.rectangle([(0, 0), (W, int(H*0.07))], fill="#FFD700")
            draw.text((W//2, int(H*0.035)), f"NEW BUY ${buy_amount:.2f}!", fill="black", font=get_font(int(H*0.045)), anchor="mm")

        path = "/tmp/meh.png"
        img.save(path, quality=95)
        return path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr
    except Exception as e:
        print(f"Error: {e}")
        path = "/tmp/meh.png"
        Image.new('RGB', (800,600), 'black').save(path)
        return path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr

last_hash = ""
def monitor_buys(app):
    global last_hash
    while True:
        try:
            mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
            if not pair_addr:
                time.sleep(15)
                continue
            url = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={CA}&address={pair_addr}&page=1&offset=3&sort=desc"
            resp = requests.get(url, timeout=10).json()
            if resp.get('status') == '1' and resp.get('result'):
                for tx in resp['result'][:2]:
                    h = tx.get('hash','')
                    if h == last_hash:
                        break
                    if tx.get('from','').lower() == pair_addr.lower():
                        val = int(tx.get('value',0))
                        for dec in [9,18]:
                            tokens = val/(10**dec)
                            if 0 < tokens < TOTAL_SUPPLY:
                                usd = tokens*price
                                if usd >= 0.1:
                                    last_hash = h
                                    path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr = make_card(buy_amount=usd, buyer=tx.get('to',''))
                                    caption = f"NEW BUY ${usd:.2f}! $MEH {gain:.2f}x MCap ${mcap:,.0f}\n{CA}"
                                    if CHANNEL_ID:
                                        try:
                                            loop = asyncio.new_event_loop()
                                            asyncio.set_event_loop(loop)
                                            cid = int(CHANNEL_ID) if str(CHANNEL_ID).lstrip('-').isdigit() else CHANNEL_ID
                                            loop.run_until_complete(app.bot.send_photo(chat_id=cid, photo=open(path,'rb'), caption=caption))
                                        except:
                                            pass
                                    break
        except:
            pass
        time.sleep(15)

async def start(update, context):
    await update.message.reply_text("MEH Bot LIVE!\n/mehcard - Clean Bullish, No Cut Head, No BULLISH AF!")

async def mehcard(update, context):
    try:
        path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr = make_card()
        caption = f"$MEH {gain:.2f}x\nMCap ${mcap:,.0f} Vol ${vol:,.0f} Liq ${liq:,.0f}\nPrice ${price:.10f}\nBurned {burned/1000000:.2f}M {burn_pct:.2f}%\n{CA}"
        await update.message.reply_photo(photo=open(path,'rb'), caption=caption)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def run_bot():
    if not TOKEN:
        return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    threading.Thread(target=monitor_buys, args=(app,), daemon=True).start()
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
