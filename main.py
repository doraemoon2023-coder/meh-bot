# FIXED - lahat ng variable defined na!
def make_card(buy_amount=0, buyer=""):
    mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 6.60
    # ... rest of code same ...
    return path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr

async def mehcard(update, context):
    path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr = make_card()
    caption = f"🚀 $MEH {gain:.2f}x BULLISH AF! 🚀\nMCap ${mcap:,.0f} Vol ${vol:,.0f} Liq ${liq:,.0f}\nPrice ${price:.10f}\n🔥 {burned/1000000:.2f}M {burn_pct:.2f}%\n{CA}"
    await update.message.reply_photo(photo=open(path,'rb'), caption=caption)
