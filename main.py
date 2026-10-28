import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context):
    await update.message.reply_text("✅ MEH Bot LIVE with new card design!\nUse /mehcard")

async def mehcard(update: Update, context):
    await update.message.reply_text("Generating new MEH card...")
    try:
        # Open template
        base = Image.open("meh_template.png").convert("RGBA")
        draw = ImageDraw.Draw(base)
        
        # Dito mo papalitan yung numbers galing sa contract
        # Halimbawa lang to boss
        # draw.text((x, y), "NEW VALUE", fill="white", font=font)

        base.save("new_card.png")
        await update.message.reply_photo(photo=open("new_card.png", "rb"),
            caption="🔥 BUY $MEH\n23.24M MEH 2.32% Burned\n\n0x39db5438317e583d46123f4b114fef376872e00d")
    except Exception as e:
        print(e)
        await update.message.reply_text(f"Error: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mehcard", mehcard))
print("MEH BOT LIVE - New Design")
app.run_polling()
