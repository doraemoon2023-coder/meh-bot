import os, asyncio, threading, requests, time
from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x39db5438317e583d46123f4b114fef376872e00d"
TOTAL_SUPPLY = 1000000000
CHANNEL_ID = None  # LAGAY MO DITO: -1001234567890

TEMPLATE_PATH = "template.png"

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "MEH Bot LIVE - Exact Rocket Design!"

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
    except Exception as e:
        print(f"Data error: {e}")
        return 66, 0.0000000694, 148, 34, 23240000, 2.32, ""

def get_font(size, bold=True):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def make_card(buy_amount=0, buyer=""):
    mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 6.60

    # LOAD YOUR EXACT TEMPLATE
    if os.path.exists(TEMPLATE_PATH):
        img = Image.open(TEMPLATE_PATH).convert("RGB")
        W, H = img.size
    else:
        W, H = 1024, 1536
        img = Image.new('RGB', (W, H), '#000000')
    
    draw = ImageDraw.Draw(img)

    # BUY BANNER IF DETECTED
    if buy_amount >= 0.1:
        # Yellow banner sa taas
        draw.rectangle([(0, 0), (W, 180)], fill="#FFD700")
        draw.text((W//2, 20), f"🚀 NEW BUY! ${buy_amount:.2f} 🚀", fill="black", font=get_font(55, True), anchor="mt")
        draw.text((W//2, 95), f"{buyer[:18]}... WELCOME TO $MEH!", fill="black", font=get_font(28, True), anchor="mt")
    else:
        # Normal top - overwrite old 6.60x with live gain
        # Cover old text with black
        draw.rectangle([(0, 0), (W, 320)], fill="black")
        # Draw grid lines to match template
        for i in range(0, W, 100):
            draw.line([(i, 0), (i//2, 320)], fill="#003300", width=1)
        draw.text((W//2, 10), f"$MEH {gain:.2f}x", fill="#39FF14", font=get_font(110, True), anchor="mt", stroke_width=4, stroke_fill="black")
        draw.text((W//2, 145), "BULLISH AF", fill="#FFEB00", font=get_font(75, True), anchor="mt", stroke_width=4, stroke_fill="black")
        # Redraw some rockets sa taas para di mabura
        draw.text((W//2, 220), "🚀 🚀 🚀", fill="white", font=get_font(30), anchor="mt")

    # MCap LIVE
    draw.rectangle([(110, 740), (490, 885)], fill="#000A00")
    draw.rounded_rectangle([(110, 740), (490, 885)], radius=15, outline="#00FF00", width=3)
    draw.text((300, 755), "MCap", fill="black", font=get_font(24, True), anchor="mt")
    draw.rectangle([(210, 750), (390, 780)], fill="#39FF14")
    draw.text((300, 755), "MCap", fill="black", font=get_font(24, True), anchor="mt")
    draw.text((300, 795), f"${mcap:,.0f}", fill="white", font=get_font(52, True), anchor="mt", stroke_width=2, stroke_fill="black")

    # Vol LIVE
    draw.rectangle([(535, 740), (915, 885)], fill="#000A00")
    draw.rounded_rectangle([(535, 740), (915, 885)], radius=15, outline="#00FF00", width=3)
    draw.rectangle([(635, 750), (815, 780)], fill="#39FF14")
    draw.text((725, 755), "Vol", fill="black", font=get_font(24, True), anchor="mt")
    draw.text((725, 795), f"${vol:,.0f}", fill="white", font=get_font(52, True), anchor="mt", stroke_width=2, stroke_fill="black")

    # Liq LIVE
    draw.rectangle([(110, 905), (490, 1050)], fill="#000A00")
    draw.rounded_rectangle([(110, 905), (490, 1050)], radius=15, outline="#00FF00", width=3)
    draw.rectangle([(210, 910), (390, 940)], fill="#39FF14")
    draw.text((300, 915), "Liq", fill="black", font=get_font(24, True), anchor="mt")
    draw.text((300, 960), f"${liq:,.0f}", fill="white", font=get_font(52, True), anchor="mt", stroke_width=2, stroke_fill="black")

    # Price LIVE
    draw.rectangle([(535, 905), (915, 1050)], fill="#000A00")
    draw.rounded_rectangle([(535, 905), (915, 1050)], radius=15, outline="#00FF00", width=3)
    draw.rectangle([(635, 910), (815, 940)], fill="#39FF14")
    draw.text((725, 915), "Price", fill="black", font=get_font(24, True), anchor="mt")
    draw.text((725, 965), f"${price:.10f}", fill="white", font=get_font(30, True), anchor="mt", stroke_width=1, stroke_fill="black")

    # BURN BOX LIVE - with fire
    draw.rectangle([(20, 1075), (W-20, 1210)], fill="#1A0000")
    draw.rounded_rectangle([(20, 1075), (W-20, 1210)], radius=15, outline="#FF4400", width=4)
    draw.text((W//2, 1085), "🔥 TOTAL BURNED 🔥", fill="#FF6600", font=get_font(32, True), anchor="mt")
    draw.text((W//2, 1130), f"{burned/1000000:.2f}M MEH {burn_pct:.2f}%", fill="#FFAA00", font=get_font(42, True), anchor="mt", stroke_width=2, stroke_fill="black")

    path = "/tmp/meh.png"
    img.save(path, quality=95)
    return path, gain, mcap, price, vol, burned, burn_pct

last_tx_hash = ""
def monitor_buys(app):
    global last_tx_hash
    print("AUTO BUY MONITOR $0.1 STARTED")
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
                    if tx.get('from','').lower() == pair_addr.lower():
                        value = int(tx.get('value',0))
                        for dec in [9,18]:
                            tokens = value/(10**dec)
                            if 0 < tokens < TOTAL_SUPPLY:
                                usd = tokens*price
                                if usd >= 0.1:
                                    print(f"BUY DETECTED ${usd:.2f}")
                                    last_tx_hash = tx_hash
                                    path, gain, mcap, price, vol, burned, burn_pct = make_card(buy_amount=usd, buyer=tx.get('to',''))
                                    caption = f"🚀 NEW BUY! ${usd:.2f} 🚀\n$MEH {gain:.2f}x | MCap ${mcap:,.0f}\n🔥 {burned/1000000:.2f}M Burned\n{CA}"
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
    await update.message.reply_text("✅ MEH Bot LIVE - Exact Rocket Design!\n/mehcard")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path, gain, mcap, price, vol, burned, burn_pct = make_card()
    caption = f"🚀 $MEH {gain:.2f}x BULLISH AF! 🚀\n💰 MCap ${mcap:,.0f} Vol ${vol:,.0f}\n🔥 {burned/1000000:.2f}M Burned {burn_pct:.2f}%\n{CA}"
    await update.message.reply_photo(photo=open(path,'rb'), caption=caption)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    threading.Thread(target=monitor_buys, args=(app,), daemon=True).start()
    print("BOT LIVE - EXACT TEMPLATE")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
