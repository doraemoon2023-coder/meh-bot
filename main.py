import os, asyncio, threading, requests, time
from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x39db5438317e583d46123f4b114fef376872e00d"
TOTAL_SUPPLY = 1000000000
CHANNEL_ID = None  # LAGAY MO CHANNEL ID DITO: -1001234567890

# YUNG IMAGE NA GUSTO MO - I-UPLOAD MO SA 【entity-GITHUB¦canonical_name=GitHub】 AS template.png
TEMPLATE_PATH = "template.png"  # yang image na may maraming rocket!

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "MEH Bot LIVE - Exact Design!"

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
        except:
            pass
        burn_pct = (burned / TOTAL_SUPPLY * 100) if TOTAL_SUPPLY > 0 else 2.32
        return mcap, price, vol, liq, burned, burn_pct, pair_addr
    except:
        return 66, 0.0000000694, 148, 34, 23240000, 2.32, ""

def get_font(size, bold=True):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def make_card(buy_amount=0, buyer=""):
    mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 6.60

    # LOAD EXACT TEMPLATE MO
    if os.path.exists(TEMPLATE_PATH):
        img = Image.open(TEMPLATE_PATH).convert("RGB")
        W, H = img.size
    else:
        # Fallback kung wala template - gumawa ng black
        W, H = 1024, 1300
        img = Image.new('RGB', (W, H), 'black')
    
    draw = ImageDraw.Draw(img)
    
    # Overlay with semi-transparent black boxes para mabura luma numbers
    # Tapos lagay bagong live numbers
    
    # TOP - $MEH 6.60x
    # Takpan luma
    draw.rectangle([(0, 0), (W, 220)], fill="black")
    # Bagong text - EXACT STYLE
    draw.text((W//2, 10), f"$MEH {gain:.2f}x", fill="#00FF00", font=get_font(85, True), anchor="mt", stroke_width=3, stroke_fill="black")
    draw.text((W//2, 110), "BULLISH AF", fill="#FFFF00", font=get_font(60, True), anchor="mt", stroke_width=3, stroke_fill="black")

    # BOXES - MCap, Vol, Liq, Price - takpan at palitan ng live data
    # MCap box
    draw.rounded_rectangle([(115, 740), (485, 880)], radius=15, fill="#001100", outline="#00FF00", width=3)
    draw.text((300, 750), "MCap", fill="#00FF00", font=get_font(22, True), anchor="mt")
    draw.text((300, 785), f"${mcap:,.0f}", fill="white", font=get_font(48, True), anchor="mt")
    
    # Vol box
    draw.rounded_rectangle([(540, 740), (910, 880)], radius=15, fill="#001100", outline="#00FF00", width=3)
    draw.text((725, 750), "Vol", fill="#00FF00", font=get_font(22, True), anchor="mt")
    draw.text((725, 785), f"${vol:,.0f}", fill="white", font=get_font(48, True), anchor="mt")
    
    # Liq box
    draw.rounded_rectangle([(115, 900), (485, 1040)], radius=15, fill="#001100", outline="#00FF00", width=3)
    draw.text((300, 910), "Liq", fill="#00FF00", font=get_font(22, True), anchor="mt")
    draw.text((300, 945), f"${liq:,.0f}", fill="white", font=get_font(48, True), anchor="mt")
    
    # Price box
    draw.rounded_rectangle([(540, 900), (910, 1040)], radius=15, fill="#001100", outline="#00FF00", width=3)
    draw.text((725, 910), "Price", fill="#00FF00", font=get_font(22, True), anchor="mt")
    draw.text((725, 955), f"${price:.10f}", fill="white", font=get_font(28, True), anchor="mt")

    # BURN BOX - EXACT NA MAY APOY
    draw.rounded_rectangle([(30, 1070), (W-30, 1200)], radius=20, fill="#1A0000", outline="#FF4400", width=4)
    draw.text((W//2, 1080), "🔥 TOTAL BURNED 🔥", fill="#FF6600", font=get_font(28, True), anchor="mt")
    draw.text((W//2, 1120), f"{burned/1000000:.2f}M MEH {burn_pct:.2f}%", fill="#FFAA00", font=get_font(36, True), anchor="mt")

    # BUY ALERT BANNER
    if buy_amount >= 0.1:
        draw.rounded_rectangle([(0, 0), (W, 140)], radius=0, fill="#FFD700")
        draw.text((W//2, 15), f"🚀 NEW BUY! ${buy_amount:.2f} 🚀", fill="black", font=get_font(40, True), anchor="mt")
        draw.text((W//2, 70), f"BUYER: {buyer[:12]}... WELCOME!", fill="black", font=get_font(20, True), anchor="mt")

    path = "/tmp/meh.png"
    img.save(path, quality=95)
    return path, gain, mcap, price, vol, burned, burn_pct

last_tx_hash = ""
def monitor_buys(app):
    global last_tx_hash
    print("AUTO BUY MONITOR STARTED $0.1")
    while True:
        try:
            mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
            if not pair_addr:
                time.sleep(10)
                continue
            url = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={CA}&address={pair_addr}&page=1&offset=5&sort=desc"
            resp = requests.get(url, timeout=10).json()
            if resp.get('status') == '1' and resp.get('result'):
                for tx in resp['result'][:3]:
                    tx_hash = tx.get('hash', '')
                    if tx_hash == last_tx_hash:
                        break
                    if tx.get('from', '').lower() == pair_addr.lower():
                        value = int(tx.get('value', 0))
                        for dec in [9, 18]:
                            amount_tokens = value / (10 ** dec)
                            if 0 < amount_tokens < TOTAL_SUPPLY:
                                usd_value = amount_tokens * price
                                if usd_value >= 0.1:
                                    print(f"BUY ${usd_value:.2f}")
                                    last_tx_hash = tx_hash
                                    path, gain, mcap, price, vol, burned, burn_pct = make_card(buy_amount=usd_value, buyer=tx.get('to',''))
                                    caption = f"🚀 NEW BUY ${usd_value:.2f}! 🚀\n$M EH {gain:.2f}x | MCap ${mcap:,.0f}\n🔥 Burned {burned/1000000:.2f}M\n{CA}"
                                    try:
                                        loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(loop)
                                        if CHANNEL_ID:
                                            loop.run_until_complete(app.bot.send_photo(chat_id=CHANNEL_ID, photo=open(path, 'rb'), caption=caption))
                                    except Exception as e:
                                        print(e)
                                    break
        except Exception as e:
            print(f"Monitor error: {e}")
        time.sleep(15)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MEH Bot LIVE - Exact Design!\n/mehcard")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path, gain, mcap, price, vol, burned, burn_pct = make_card()
    caption = f"🚀 $MEH {gain:.2f}x BULLISH AF! 🚀\n💰 MCap ${mcap:,.0f} Vol ${vol:,.0f}\n🔥 {burned/1000000:.2f}M Burned {burn_pct:.2f}%\n{CA}"
    await update.message.reply_photo(photo=open(path, 'rb'), caption=caption)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    threading.Thread(target=monitor_buys, args=(app,), daemon=True).start()
    print("BOT LIVE - EXACT DESIGN")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
