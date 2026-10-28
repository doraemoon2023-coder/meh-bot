import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ LIVE NA BOSS!")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("$MEH 🚀")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    app.run_polling()
