import os, requests
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x5c59232e53c47a812c80e5d99ccf924cee875070"
CALLED = 30060
CHATS = set()

def get_real():
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{CA}"
        r = requests.get(url, timeout=15).json()
        pairs = [p for p in r.get('pairs',[]) if p.get('chainId')=='bsc']
        if not pairs: pairs = r.get('pairs',[])
        if not pairs: return None
        pair = max(pairs, key=lambda x: float(x.get('liquidity',{}).get('usd',0) or 0))
        price = float(pair.get('priceUsd') or 0)
        mcap = float(pair.get('marketCap') or pair.get('fdv') or 0)
        if mcap==0 and price>0: mcap = price * 1000000000
        return {'price':price,'mcap':mcap,'liq':float(pair.get('liquidity',{}).get('usd',0) or 0),'vol':float(pair.get('volume',{}).get('h24',0) or 0),'change':float(pair.get('priceChange',{}).get('h24',0) or 0)}
    except: return None

def make_card(data):
    W,H=1200,700
    img=Image.new('RGB',(W,H),(10,15,10))
    draw=ImageDraw.Draw(img)
    draw.rounded_rectangle([(5,5),(W-5,H-5)], radius=30, outline=(50,255,100), width=3)
    try:
        font_big=ImageFont.truetype("DejaVuSans-Bold.ttf",70)
        font_med=ImageFont.truetype("DejaVuSans-Bold.ttf",38)
        font_small=ImageFont.truetype("DejaVuSans.ttf",28)
    except:
        font_big=font_med=font_small=ImageFont.load_default()
    x_mult=data['mcap']/CALLED
    draw.text((40,30), f"$MEH {x_mult:.2f}x", fill=(80,255,120), font=font_big)
    draw.text((40,115), "MEH / WBNB • BSC", fill=(180,180,180), font=font_med)
    draw.text((40,170), "AUTO EVERY 3 MIN", fill=(80,255,120), font=font_med)
    draw.text((40,260), "MCap", fill=(150,180,150), font=font_small)
    draw.text((40,295), f"${data['mcap']:,.0f}", fill=(80,255,120), font=font_med)
    draw.text((40,380), "Price", fill=(150,180,150), font=font_small)
    draw.text((40,415), f"${data['price']:.10f}", fill=(200,255,200), font=font_med)
    draw.text((650,260), "Vol 24h", fill=(150,180,150), font=font_small)
    draw.text((650,295), f"${data['vol']:,.0f}", fill=(255,255,255), font=font_med)
    draw.text((650,360), "Liq", fill=(150,180,150), font=font_small)
    draw.text((650,395), f"${data['liq']:,.0f}", fill=(255,255,255), font=font_med)
    path="/tmp/meh.png"
    img.save(path)
    return path

async def send_card(bot, chat_id):
    d=get_real()
    if not d: return
    p=make_card(d)
    x=d['mcap']/CALLED
    cap=f"🚀 $MEH {x:.2f}x BSC! AUTO 3MIN\n💰 ${d['mcap']:,.0f} | 💵 ${d['price']}\n📊 dexscreener.com/bsc/{CA}"
    try: await bot.send_photo(chat_id=chat_id, photo=open(p,'rb'), caption=cap)
    except: pass

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHATS.add(update.effective_chat.id)
    await send_card(context.bot, update.effective_chat.id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHATS.add(update.effective_chat.id)
    await send_card(context.bot, update.effective_chat.id)

async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    for cid in list(CHATS):
        try: await send_card(context.bot, cid)
        except: pass

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mehcard", mehcard))
app.add_handler(CommandHandler("burn", mehcard))
app.add_handler(CommandHandler("chart", mehcard))
app
