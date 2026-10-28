import os, threading, requests
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x39db5438317e583d46123f4b114fef376872e00d"

# PARA HINDI MAG EXIT EARLY SA RENDER
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "MEH 12PM LIVE"
threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000))), daemon=True).start()

def get_data():
    return {'mcap':77,'vol':37,'liq':149,'price':0.000000081,'x':7.70}

def make_card():
    W,H = 1200, 700
    img = Image.new("RGB",(W,H),"black")
    d = ImageDraw.Draw(img)
    # grid
    for i in range(0,W,100):
        d.line([(i,0),(i-200,H)], fill="#0a3d0a", width=1)
    for i in range(0,H,100):
        d.line([(0,i),(W,i)], fill="#0a3d0a", width=1)
    # rockets - simple white
    try:
        f_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)
        f_med = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
        f_small = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
    except:
        f_big = f_med = f_small = ImageFont.load_default()

    # TITLE
    d.text((W//2, 30), "$MEH 7.70x", fill="white", font=f_big, anchor="mm", stroke_width=3, stroke_fill="black")
    # COIN - yellow circle
    d.ellipse([W//2-120, 80, W//2+120, 320], fill="#ffcc00", outline="black", width=4)
    d.text((W//2, 190), "MEH", fill="black", font=f_med, anchor="mm")
    d.text((W//2-30, 230), "☕", fill="black", font=f_med, anchor="mm")
    
    # 4 BOXES
    boxes = [("$ MCap","$77"), ("Vol","$37"), ("Liq","$149"), ("Price","$0.000000081")]
    bx_w, bx_h = 260, 120
    gap = 30
    start_x = (W - (4*bx_w+3*gap))//2
    y = 350
    for i,(label,val) in enumerate(boxes):
        x0 = start_x + i*(bx_w+gap)
        d.rounded_rectangle([x0,y,x0+bx_w,y+bx_h], radius=15, outline="#00ff88", width=3)
        d.text((x0+bx_w//2, y+30), label, fill="#00ff88", font=f_small, anchor="mm")
        d.text((x0+bx_w//2, y+80), val, fill="white", font=f_med, anchor="mm")

    # FIRE BOTTOM
    d.rectangle([0, 530, W, 600], fill="#220000")
    d.text((W//2, 565), "23.24M MEH 2.32%", fill="#ff6600", font=f_med, anchor="mm")

    path = "/tmp/meh.png"
    img.save(path)
    return path

async def mehcard(update: Update, context):
    p = make_card()
    caption = f"$MEH 7.70x | MCap $77 | Burned 23.24M (2.32%)\n{CA}"
    await update.message.reply_photo(photo=open(p,'rb'), caption=caption)

async def start(update: Update, context):
    await mehcard(update, context)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mehcard", mehcard))

print("MEH 12PM+ CODE LIVE")
app.run_polling()
