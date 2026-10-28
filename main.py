import os, asyncio, threading, requests, random, time
from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x39db5438317e583d46123f4b114fef376872e00d"
TOTAL_SUPPLY = 1000000000
# ILAGAY MO DITO YUNG CHANNEL ID MO BOSS - kunin mo sa @userinfobot
CHANNEL_ID = None  # Example: -1001234567890 o @yourchannel

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "MEH Bot LIVE - Auto Buy Alert $0.1!"

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
    W, H = 1024, 1150
    mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 6.60

    img = Image.new('RGB', (W, H), '#000000')
    draw = ImageDraw.Draw(img)
    for y in range(H):
        g = int(15 + (y/H)*10)
        draw.line([(0, y), (W, y)], fill=(0, g, 0))
    random.seed(123)
    for _ in range(100):
        x = random.randint(0, W)
        y = random.randint(0, 700)
        s = random.randint(2, 4)
        draw.ellipse([(x, y),(x+s, y+s)], fill=(0, 255, 100) if random.random()>0.5 else (255, 255, 255))
    for x in range(0, W, 80):
        draw.line([(x, 0),(x, H)], fill="#001a00", width=1)
    draw.rounded_rectangle([(0,0),(W-1,H-1)], radius=40, outline="#00FF00", width=6)

    # BUY ALERT BANNER IF BUY DETECTED
    if buy_amount >= 0.1:
        draw.rounded_rectangle([(20, 20),(W-20, 110)], radius=15, fill="#FFD700", outline="#FFA500", width=3)
        draw.text((W//2, 45), f"🚀 NEW BUY! ${buy_amount:.2f} 🚀", fill="black", font=get_font(35, True), anchor="mt")
        draw.text((W//2, 80), f"BUYER: {buyer[:15]}... • WELCOME!", fill="black", font=get_font(18, True), anchor="mt")
        title_y = 120
    else:
        title_y = 50

    draw.text((W//2, title_y), f"$MEH {gain:.2f}x", fill="#7FFF00", font=get_font(85, True), anchor="mt")
    draw.text((W//2, title_y+90), "BULLISH AF! 🚀🚀🚀", fill="#FFFF00", font=get_font(55, True), anchor="mt")

    logo_size = 300
    logo_x, logo_y = (W - logo_size)//2, title_y+130
    try:
        if os.path.exists("logo.png"):
            logo = Image.open("logo.png").convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
            glow = Image.new('RGBA', (logo_size+60, logo_size+60), (0,0,0,0))
            ImageDraw.Draw(glow).ellipse((0,0,logo_size+60, logo_size+60), fill=(0,255,0,40))
            img.paste(glow, (logo_x-30, logo_y-30), glow)
            mask = Image.new('L', (logo_size, logo_size), 0)
            ImageDraw.Draw(mask).ellipse((0,0,logo_size,logo_size), fill=255)
            img.paste(logo, (logo_x, logo_y), mask)
            draw.ellipse([(logo_x-5, logo_y-5),(logo_x+logo_size+5, logo_y+logo_size+5)], outline="#00FF00", width=4)
    except:
        pass

    rockets = [(logo_x-40, logo_y+50), (logo_x+logo_size+40, logo_y+50), (100, 300), (W-100, 300), (80, 500), (W-80, 500)]
    for rx, ry in rockets:
        draw.polygon([(rx, ry), (rx-10, ry+25), (rx+10, ry+25)], fill="white")
        draw.ellipse([(rx-6, ry+2),(rx+6, ry+10)], fill="#00FF00")
        draw.polygon([(rx-8, ry+25), (rx, ry+40), (rx-2, ry+25)], fill="#FF4500")

    box_w, box_h, gap, start_x, y_boxes = 220, 100, 20, 40, 680
    for i, (label, val) in enumerate([("MCap", f"${mcap:,.0f}"), ("Vol", f"${vol:,.0f}"), ("Liq", f"${liq:,.0f}"), ("Price", f"${price:.10f}")]):
        x = start_x + i*(box_w+gap)
        draw.rounded_rectangle([(x, y_boxes),(x+box_w, y_boxes+box_h)], radius=15, fill="#0A0A0A", outline="#00FF00", width=2)
        draw.text((x+box_w//2, y_boxes+12), label, fill="#00FF88", font=get_font(20, True), anchor="mt")
        draw.text((x+box_w//2, y_boxes+42), val, fill="white", font=get_font(24 if i<3 else 18, True), anchor="mt")

    y_burn = 810
    burn_h = 160
    for i in range(12, 0, -2):
        glow_c = (60 + i*8, 15 + i*2, 0)
        draw.rounded_rectangle([(40-i, y_burn-i),(W-40+i, y_burn+burn_h+i)], radius=22+i, fill=glow_c)
    draw.rounded_rectangle([(40, y_burn),(W-40, y_burn+burn_h)], radius=20, fill="#1A0000", outline="#FF2200", width=4)
    flame_y = y_burn + burn_h - 20
    for x in range(60, W-60, 25):
        random.seed(x)
        h1 = random.randint(15, 30)
        draw.polygon([(x, flame_y), (x+12, flame_y-h1), (x+24, flame_y)], fill="#FF4500")
    draw.text((W//2, y_burn+15), "🔥 TOTAL BURNED 23.24M 🔥", fill="#FF2200", font=get_font(24, True), anchor="mt")
    draw.text((W//2, y_burn+50), f"{burned/1000000:.2f}M MEH", fill="white", font=get_font(40, True), anchor="mt")
    draw.text((W//2, y_burn+100), f"{burn_pct:.2f}% BURNED • DEFLATIONARY", fill="#FFA500", font=get_font(18, True), anchor="mt")

    draw.rounded_rectangle([(40, 990),(W-40, 1040)], radius=15, fill="#001100", outline="#00FF00", width=2)
    draw.text((W//2, 1015), "🚀 TO THE MOON • AUTO BUY ALERT $0.1 🚀", fill="#00FF00", font=get_font(20, True), anchor="mm")

    path = "/tmp/meh.png"
    img.save(path, quality=95)
    return path, gain, mcap, price, vol, burned, burn_pct

# AUTO BUY MONITOR - BACKGROUND TASK
last_tx_hash = ""
def monitor_buys(app):
    global last_tx_hash
    print("AUTO BUY MONITOR STARTED - $0.1 MINIMUM")
    while True:
        try:
            mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
            if not pair_addr:
                time.sleep(10)
                continue
            
            # Get recent transactions from BscScan
            url = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={CA}&address={pair_addr}&page=1&offset=5&sort=desc"
            resp = requests.get(url, timeout=10).json()
            if resp.get('status') == '1' and resp.get('result'):
                txs = resp['result']
                for tx in txs[:3]:
                    tx_hash = tx.get('hash', '')
                    if tx_hash == last_tx_hash:
                        break
                    # Check if buy (from pair to user, not from user to pair)
                    # Buy = token goes from pair to buyer
                    from_addr = tx.get('from', '').lower()
                    to_addr = tx.get('to', '').lower()
                    if from_addr == pair_addr.lower():  # Buy
                        value = int(tx.get('value', 0))
                        for dec in [9, 18]:
                            amount_tokens = value / (10 ** dec)
                            if 0 < amount_tokens < TOTAL_SUPPLY:
                                usd_value = amount_tokens * price
                                if usd_value >= 0.1:  # $0.1 MINIMUM
                                    print(f"NEW BUY DETECTED: ${usd_value:.2f} - {tx_hash}")
                                    last_tx_hash = tx_hash
                                    # Make card with buy info
                                    path, gain, mcap, price, vol, burned, burn_pct = make_card(buy_amount=usd_value, buyer=to_addr)
                                    caption = f"🚀🚀🚀 NEW BUY ALERT! 🚀🚀🚀\n💰 ${usd_value:.2f} BUY!\n👤 Buyer: {to_addr[:10]}...{to_addr[-6:]}\n💎 $MEH {gain:.2f}x | MCap ${mcap:,.0f}\n🔥 Burned: {burned/1000000:.2f}M MEH\n\nTO THE MOON!\n\n{CA}"
                                    # Send to channel if set, else to logs
                                    try:
                                        import asyncio
                                        loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(loop)
                                        if CHANNEL_ID:
                                            loop.run_until_complete(app.bot.send_photo(chat_id=CHANNEL_ID, photo=open(path, 'rb'), caption=caption))
                                        else:
                                            print(f"Would send: {caption}")
                                    except Exception as e:
                                        print(f"Send error: {e}")
                                    break
        except Exception as e:
            print(f"Monitor error: {e}")
        time.sleep(15)  # Check every 15 seconds

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MEH Vip Bot LIVE with AUTO BUY ALERT!\n\nMin buy: $0.1\n/mehcard - Manual card")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path, gain, mcap, price, vol, burned, burn_pct = make_card()
    caption = f"🚀 $MEH {gain:.2f}x BULLISH AF! 🚀\n🔥 Burned: {burned/1000000:.2f}M MEH ({burn_pct:.2f}%) 🔥\n💰 MCap ${mcap:,.0f} | Vol ${vol:,.0f}\n\n{CA}"
    await update.message.reply_photo(photo=open(path, 'rb'), caption=caption)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    
    # Start auto buy monitor in background
    threading.Thread(target=monitor_buys, args=(app,), daemon=True).start()
    
    print("BOT LIVE - AUTO BUY $0.1 MONITOR")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
