import os
import time
import asyncio
import threading
import requests
from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

CA = "0x39db5438317e583d46123f4b114fef376872e00d"
TOTAL_SUPPLY = 1_000_000_000
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")
API_KEY = os.environ.get("BSCSCAN_API_KEY", "") or os.environ.get("ETHERSCAN_API_KEY", "")

last_hash = ""

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "MEH Bot is running!"

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
            if API_KEY:
                bsc_url = f"https://api.etherscan.io/v2/api?chainid=56&module=account&action=tokenbalance&contractaddress={CA}&address={dead}&tag=latest&apikey={API_KEY}"
                resp = requests.get(bsc_url, timeout=10).json()
                print(f"Burn check: {resp}")
                if resp.get('status') == '1' and resp.get('result'):
                    raw = int(resp['result'])
                    for dec in [9, 18]:
                        test = raw / (10 ** dec)
                        if 1000000 < test < TOTAL_SUPPLY:
                            burned = test
                            burn_pct = (burned / TOTAL_SUPPLY * 100)
                            break
        except Exception as e:
            print(f"Burn error: {e}")
        return mcap, price, vol, liq, burned, burn_pct, pair_addr
    except Exception as e:
        print(f"Live data error: {e}")
        return 66, 0.0000000694, 148, 34, 23240000, 2.32, ""

def make_card(buy_amount=None, buyer=None):
    mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
    gain = mcap / 10.0 if mcap else 6.6

    if os.path.exists("template.png"):
        img = Image.open("template.png").convert("RGBA")
        W, H = img.size
    else:
        W, H = 1000, 1150
        img = Image.new("RGBA", (W, H), (0,0,0,255))
    
    W, H = img.size
    draw = ImageDraw.Draw(img, "RGBA")

    def get_font(size, bold=False):
        try:
            for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
                if os.path.exists(p):
                    return ImageFont.truetype(p, size)
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()

    # Top small bar - $MEH Xx
    top_h = int(H * 0.07)
    draw.rectangle([(0,0),(W, top_h)], fill=(0,0,0,255))
    txt_top = f"$MEH {gain:.2f}x"
    f_top = get_font(int(W*0.06), bold=True)
    bbox = draw.textbbox((0,0), txt_top, font=f_top)
    tw = bbox[2]-bbox[0]
    th = bbox[3]-bbox[1]
    draw.text(((W-tw)//2, (top_h-th)//2), txt_top, font=f_top, fill=(255,255,255,255))

    # Buy banner
    offset = top_h
    if buy_amount:
        banner_h = int(H * 0.06)
        draw.rectangle([(0, offset),(W, offset+banner_h)], fill=(255,215,0,255))
        buyer_short = (buyer[:6]+"..."+buyer[-4:]) if buyer and len(buyer)>10 else (buyer or "")
        txt_buy = f"NEW BUY ${buy_amount:.2f} {buyer_short}"
        f_buy = get_font(int(W*0.038), bold=True)
        bbox = draw.textbbox((0,0), txt_buy, font=f_buy)
        tw = bbox[2]-bbox[0]
        th = bbox[3]-bbox[1]
        draw.text(((W-tw)//2, offset+(banner_h-th)//2), txt_buy, font=f_buy, fill=(0,0,0,255))
        offset += banner_h

    # Boxes
    box_area_top = int(H*0.58)
    boxes = [
        f"${mcap:,.0f}",
        f"${vol:,.0f}",
        f"${liq:,.0f}",
        f"${price:.10f}"[:12],
    ]
    box_w = int(W*0.44)
    box_h = int(H*0.095)
    gap_x = int(W*0.04)
    gap_y = int(H*0.015)
    start_x = (W - (box_w*2 + gap_x))//2
    start_y = box_area_top
    f_value = get_font(int(W*0.038), bold=True)

    for i, val in enumerate(boxes):
        col = i % 2
        row = i // 2
        x = start_x + col*(box_w+gap_x)
        y = start_y + row*(box_h+gap_y)
        draw.rectangle([(x+2, y+int(box_h*0.35)), (x+box_w-2, y+box_h-2)], fill=(0,0,0,255))
        fv = get_font(int(W*0.032), bold=True) if i==3 else f_value
        bbox = draw.textbbox((0,0), val, font=fv)
        tw = bbox[2]-bbox[0]
        draw.text((x + (box_w-tw)//2, y + int(box_h*0.45)), val, font=fv, fill=(255,255,255,255))

    # Burn box
    burn_y = start_y + 2*(box_h+gap_y) + int(H*0.02)
    burn_h = int(H*0.13)
    burn_w = int(W*0.92)
    bx = (W-burn_w)//2
    draw.rectangle([(bx+2, burn_y+int(burn_h*0.35)), (bx+burn_w-2, burn_y+burn_h-2)], fill=(20,0,0,255))
    burn_text = f"{burned/1_000_000:.2f}M MEH {burn_pct:.2f}%"
    f_burn = get_font(int(W*0.05), bold=True)
    bbox = draw.textbbox((0,0), burn_text, font=f_burn)
    tw = bbox[2]-bbox[0]
    draw.text(((W-tw)//2, burn_y+int(burn_h*0.5)), burn_text, font=f_burn, fill=(255,80,0,255))

    out_path = "/tmp/meh_card.png"
    img.convert("RGB").save(out_path, "PNG")
    return out_path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Generating MEH card...")
        path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr = make_card()
        caption = f"$MEH {gain:.2f}x | MCap ${mcap:,.0f} | Burned {burned/1_000_000:.2f}M ({burn_pct:.2f}%)\n{CA}"
        await update.message.reply_photo(photo=open(path,'rb'), caption=caption)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        print(f"mehcard error: {e}")

def monitor_buys(app):
    global last_hash
    print("Monitor buys started V2")
    while True:
        try:
            mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
            if not pair_addr:
                time.sleep(15)
                continue
            if not API_KEY:
                print("No API_KEY set")
                time.sleep(30)
                continue
            url = f"https://api.etherscan.io/v2/api?chainid=56&module=account&action=tokentx&contractaddress={CA}&address={pair_addr}&page=1&offset=5&sort=desc&apikey={API_KEY}"
            resp = requests.get(url, timeout=15).json()
            print(f"Checking buys V2: {resp.get('status')} {resp.get('message')}")
            if resp.get('status') == '1' and resp.get('result'):
                for tx in resp['result'][:3]:
                    h = tx.get('hash','')
                    if h == last_hash:
                        break
                    if tx.get('from','').lower() == pair_addr.lower():
                        val = int(tx.get('value',0))
                        for dec in [9,18]:
                            tokens = val/(10**dec)
                            if 0 < tokens < TOTAL_SUPPLY:
                                usd = tokens*price
                                print(f"BUY ${usd:.2f}")
                                if usd >= 0.1:
                                    last_hash = h
                                    path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr2 = make_card(buy_amount=usd, buyer=tx.get('to',''))
                                    caption = f"NEW BUY ${usd:.2f}! $MEH {gain:.2f}x MCap ${mcap:,.0f}\n{CA}"
                                    if CHANNEL_ID:
                                        try:
                                            loop = asyncio.new_event_loop()
                                            asyncio.set_event_loop(loop)
                                            cid = int(CHANNEL_ID) if str(CHANNEL_ID).lstrip('-').isdigit() else CHANNEL_ID
                                            loop.run_until_complete(app.bot.send_photo(chat_id=cid, photo=open(path,'rb'), caption=caption))
                                        except Exception as e:
                                            print(f"Send error: {e}")
                                    break
        except Exception as e:
            print(f"Monitor error: {e}")
        time.sleep(15)

def main():
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not set!")
        return
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("mehcard", mehcard))
    application.add_handler(CommandHandler("start", mehcard))
    threading.Thread(target=lambda: app_flask.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000))), daemon=True).start()
    threading.Thread(target=monitor_buys, args=(application,), daemon=True).start()
    print("Bot polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
