import os, asyncio, threading, requests, time
from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x39db5438317e583d46123f4b114fef376872e00d"
TOTAL_SUPPLY = 1000000000
TEMPLATE = "template.png"
CHANNEL_ID = os.environ.get("CHANNEL_ID")

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "MEH Bot LIVE - Final No Error!"

def run_flask():
    try:
        port = int(os.environ.get("PORT", 10000))
        flask_app.run(host="0.0.0.0", port=port)
    except Exception as e:
        print(e)

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
        if os.path.exists(TEMPLATE):
            img = Image.open(TEMPLATE).convert("RGB")
            W, H = img.size
        else:
            W, H = 1024, 1536
            img = Image.new('RGB', (W, H), 'black')
        draw = ImageDraw.Draw(img)
        if buy_amount >= 0.1:
            draw.rectangle([(0, 0), (W, int(H*0.12))], fill="#FFD700")
            draw.text((W//2, int(H*0.02)), f"NEW BUY ${buy_amount:.2f}!", fill="black", font=get_font(int(H*0.04)), anchor="mt")
        else:
            draw.rectangle([(0, 0), (W, int(H*0.14))], fill="black")
            draw.text((W//2, int(H*0.01)), f"$MEH {gain:.2f}x", fill="#39FF14", font=get_font(int(H*0.07)), anchor="mt")
            draw.text((W//2, int(H*0.08)), "BULLISH AF", fill="#FFEB00", font=get_font(int(H*0.05)), anchor="mt")
        draw.rectangle([(int(W*0.18), int(H*0.59)), (int(W*0.45), int(H*0.665))], fill="#020D02")
        draw.text((int(W*0.32), int(H*0.633)), f"${mcap:,.0f}", fill="white", font=get_font(int(H*0.04)), anchor="mm")
        draw.rectangle([(int(W*0.58), int(H*0.59)), (int(W*0.88), int(H*0.665))], fill="#020D02")
        draw.text((int(W*0.73), int(H*0.633)), f"${vol:,.0f}", fill="white", font=get_font(int(H*0.04)), anchor="mm")
        draw.rectangle([(int(W*0.18), int(H*0.705)), (int(W*0.45), int(H*0.785))], fill="#020D02")
        draw.text((int(W*0.32), int(H*0.752)), f"${liq:,.0f}", fill="white", font=get_font(int(H*0.04)), anchor="mm")
        draw.rectangle([(int(W*0.58), int(H*0.705)), (int(W*0.88), int(H*0.785))], fill="#020D02")
        draw.text((int(W*0.73), int(H*0.752)), f"${price:.10f}", fill="white", font=get_font(int(H*0.022)), anchor="mm")
        draw.rectangle([(int(W*0.12), int(H*0.87)), (int(W*0.88), int(H*0.92))], fill="#1A0202")
        draw.text((W//2, int(H*0.895)), f"{burned/1000000:.2f}M MEH {burn_pct:.2f}%", fill="#FFAA00", font=get_font(int(H*0.03)), anchor="mm")
        path = "/tmp/meh.png"
        img.save(path, quality=95)
        return path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr
    except Exception as e:
        print(f"make_card error: {e}")
        img = Image.new('RGB', (800, 600), 'black')
        d = ImageDraw.Draw(img)
        d.text((400, 300), f"$MEH {gain:.2f}x", fill="green", font=get_font(40), anchor="mm")
        path = "/tmp/meh.png"
        img.save(path)
        return path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr

last_hash = ""
def monitor_buys(app):
    global last_hash
    print("AUTO BUY MONITOR $0.1 STARTED")
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
                                    print(f"BUY ${usd:.2f}")
                                    last_hash = h
                                    path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr = make_card(buy_amount=usd, buyer=tx.get('to',''))
                                    caption = f"🚀 NEW BUY! ${usd:.2f} 🚀\n$MEH {gain:.2f}x MCap ${mcap:,.0f}\n{CA}"
                                    if CHANNEL_ID:
                                        try:
                                            loop = asyncio.new_event_loop()
                                            asyncio.set_event_loop(loop)
                                            cid = int(CHANNEL_ID) if str(CHANNEL_ID).lstrip('-').isdigit() else CHANNEL_ID
                                            loop.run_until_complete(app.bot.send_photo(chat_id=cid, photo=open(path,'rb'), caption=caption))
                                        except Exception as e:
                                            print(e)
                                    break
        except Exception as e:
            print(f"Monitor error: {e}")
        time.sleep(15)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MEH Bot LIVE - Exact Design No Error!\n/mehcard")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr = make_card()
        caption = f"🚀 $MEH {gain:.2f}x BULLISH AF! 🚀\n💰 MCap ${mcap:,.0f} | Vol ${vol:,.0f} | Liq ${liq:,.0f}\n💵 Price ${price:.10f}\n🔥 {burned/1000000:.2f}M {burn_pct:.2f}%\n{CA}"
        await update.message.reply_photo(photo=open(path,'rb'), caption=caption)
    except Exception as e:
        print(f"mehcard error: {e}")
        await update.message.reply_text(f"Error: {e}")

def run_bot():
    if not TOKEN:
        print("TOKEN missing!")
        return
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("mehcard", mehcard))
        threading.Thread(target=monitor_buys, args=(app,), daemon=True).start()
        print("BOT LIVE FINAL")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
