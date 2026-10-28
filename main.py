import os, threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# KEEP ALIVE PARA HINDI MAMATAY SA RENDER
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "MEH BOT LIVE"
threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000))), daemon=True).start()

async def start(update: Update, context):
    await update.message.reply_text("MEH BOT LIVE! Type /mehcard")

async def mehcard(update: Update, context):
    await update.message.reply_text("🚀 $MEH BSC! MCap $1.5M | Burn 2.32%")

# BUILD BOT
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mehcard", mehcard))

print("BOT STARTING - POLLING")
app.run_polling()
