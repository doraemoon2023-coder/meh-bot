def make_card(buy_amount=0, buyer=""):
    mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 6.60

    img = Image.open(TEMPLATE_PATH).convert("RGB") if os.path.exists(TEMPLATE_PATH) else Image.new('RGB', (1024, 1536), 'black')
    W, H = img.size
    draw = ImageDraw.Draw(img)

    # BURA LAHAT NG LUMANG BOXES SA BABA - isang malaking black cover
    draw.rectangle([(0, 680), (W, 1220)], fill="black")
    # Grid lines balik
    for i in range(0, W, 120):
        draw.line([(i, 680), (i//2, 1220)], fill="#001a00", width=1)

    # TOP - 6.60x LIVE
    if buy_amount >= 0.1:
        draw.rectangle([(0, 0), (W, 200)], fill="#FFD700")
        draw.text((W//2, 20), f"🚀 NEW BUY ${buy_amount:.2f} 🚀", fill="black", font=get_font(55, True), anchor="mt")
        draw.text((W//2, 100), f"{buyer[:14]}... WELCOME!", fill="black", font=get_font(26, True), anchor="mt")
        # Still show gain below banner
        draw.rectangle([(0, 200), (W, 340)], fill="black")
        draw.text((W//2, 210), f"$MEH {gain:.2f}x", fill="#39FF14", font=get_font(90, True), anchor="mt")
        draw.text((W//2, 290), "BULLISH AF", fill="#FFEB00", font=get_font(60, True), anchor="mt")
    else:
        draw.rectangle([(0, 0), (W, 340)], fill="black")
        draw.text((W//2, 10), f"$MEH {gain:.2f}x", fill="#39FF14", font=get_font(95, True), anchor="mt")
        draw.text((W//2, 120), "BULLISH AF", fill="#FFEB00", font=get_font(65, True), anchor="mt")

    # MCap LIVE - isang box lang
    draw.rounded_rectangle([(60, 700), (490, 850)], radius=15, fill="#001100", outline="#00FF00", width=3)
    draw.rectangle([(180, 705), (370, 735)], fill="#39FF14")
    draw.text((275, 710), "MCap", fill="black", font=get_font(22, True), anchor="mt")
    draw.text((275, 760), f"${mcap:,.0f}", fill="white", font=get_font(50, True), anchor="mt")

    # Vol LIVE
    draw.rounded_rectangle([(530, 700), (960, 850)], radius=15, fill="#001100", outline="#00FF00", width=3)
    draw.rectangle([(650, 705), (840, 735)], fill="#39FF14")
    draw.text((745, 710), "Vol", fill="black", font=get_font(22, True), anchor="mt")
    draw.text((745, 760), f"${vol:,.0f}", fill="white", font=get_font(50, True), anchor="mt")

    # Liq LIVE
    draw.rounded_rectangle([(60, 870), (490, 1020)], radius=15, fill="#001100", outline="#00FF00", width=3)
    draw.rectangle([(180, 875), (370, 905)], fill="#39FF14")
    draw.text((275, 880), "Liq", fill="black", font=get_font(22, True), anchor="mt")
    draw.text((275, 930), f"${liq:,.0f}", fill="white", font=get_font(50, True), anchor="mt")

    # Price LIVE
    draw.rounded_rectangle([(530, 870), (960, 1020)], radius=15, fill="#001100", outline="#00FF00", width=3)
    draw.rectangle([(650, 875), (840, 905)], fill="#39FF14")
    draw.text((745, 880), "Price", fill="black", font=get_font(22, True), anchor="mt")
    draw.text((745, 935), f"${price:.10f}", fill="white", font=get_font(28, True), anchor="mt")

    # BURN - ISA LANG, may apoy na background na
    draw.rounded_rectangle([(15, 1040), (W-15, 1170)], radius=20, fill="#1A0000", outline="#FF4400", width=4)
    draw.text((W//2, 1050), "🔥 TOTAL BURNED 🔥", fill="#FF6600", font=get_font(30, True), anchor="mt")
    draw.text((W//2, 1090), f"{burned/1000000:.2f}M MEH {burn_pct:.2f}%", fill="#FFAA00", font=get_font(40, True), anchor="mt")

    # TO THE MOON footer
    draw.rectangle([(0, 1180), (W, H)], fill="black")
    draw.text((W//2, 1190), "TO THE MOON 🚀🚀🚀", fill="#FFFF00", font=get_font(45, True), anchor="mt")

    path = "/tmp/meh.png"
    img.save(path, quality=95)
    return path, gain, mcap, price, vol, burned, burn_pct
