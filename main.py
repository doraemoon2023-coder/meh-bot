def make_card(buy_amount=0, buyer=""):
    mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 6.60
    try:
        if os.path.exists(TEMPLATE):
            img = Image.open(TEMPLATE).convert("RGB")
            W, H = img.size
        else:
            W, H = 1024, 1536
            img = Image.new('RGB', (W, H), 'black')
        draw = ImageDraw.Draw(img)

        # TOP - cover buo para walang doble
        if buy_amount >= 0.1:
            draw.rectangle([(0, 0), (W, int(H*0.15))], fill="#FFD700")
            draw.text((W//2, int(H*0.03)), f"NEW BUY ${buy_amount:.2f}!", fill="black", font=get_font(int(H*0.045)), anchor="mt")
        else:
            draw.rectangle([(0, 0), (W, int(H*0.16))], fill="black")
            draw.text((W//2, int(H*0.01)), f"$MEH {gain:.2f}x", fill="#39FF14", font=get_font(int(H*0.07)), anchor="mt")
            draw.text((W//2, int(H*0.085)), "BULLISH AF", fill="#FFEB00", font=get_font(int(H*0.05)), anchor="mt")

        # MCap - COVER BUONG LOOB NG BOX PARA WALANG DOBLE
        draw.rectangle([(int(W*0.05), int(H*0.54)), (int(W*0.49), int(H*0.695))], fill="#000000")
        draw.rounded_rectangle([(int(W*0.05), int(H*0.54)), (int(W*0.49), int(H*0.695))], radius=15, outline="#00FF00", width=3)
        draw.rectangle([(int(W*0.19), int(H*0.543)), (int(W*0.38), int(H*0.575))], fill="#39FF14")
        draw.text((int(W*0.285), int(H*0.558)), "MCap", fill="black", font=get_font(int(H*0.022)), anchor="mm")
        draw.text((int(W*0.27), int(H*0.635)), f"${mcap:,.0f}", fill="white", font=get_font(int(H*0.045)), anchor="mm")

        # Vol
        draw.rectangle([(int(W*0.51), int(H*0.54)), (int(W*0.95), int(H*0.695))], fill="#000000")
        draw.rounded_rectangle([(int(W*0.51), int(H*0.54)), (int(W*0.95), int(H*0.695))], radius=15, outline="#00FF00", width=3)
        draw.rectangle([(int(W*0.64), int(H*0.543)), (int(W*0.82), int(H*0.575))], fill="#39FF14")
        draw.text((int(W*0.73), int(H*0.558)), "Vol", fill="black", font=get_font(int(H*0.022)), anchor="mm")
        draw.text((int(W*0.73), int(H*0.635)), f"${vol:,.0f}", fill="white", font=get_font(int(H*0.045)), anchor="mm")

        # Liq
        draw.rectangle([(int(W*0.05), int(H*0.705)), (int(W*0.49), int(H*0.86))], fill="#000000")
        draw.rounded_rectangle([(int(W*0.05), int(H*0.705)), (int(W*0.49), int(H*0.86))], radius=15, outline="#00FF00", width=3)
        draw.rectangle([(int(W*0.19), int(H*0.708)), (int(W*0.38), int(H*0.74))], fill="#39FF14")
        draw.text((int(W*0.285), int(H*0.723)), "Liq", fill="black", font=get_font(int(H*0.022)), anchor="mm")
        draw.text((int(W*0.27), int(H*0.80)), f"${liq:,.0f}", fill="white", font=get_font(int(H*0.045)), anchor="mm")

        # Price
        draw.rectangle([(int(W*0.51), int(H*0.705)), (int(W*0.95), int(H*0.86))], fill="#000000")
        draw.rounded_rectangle([(int(W*0.51), int(H*0.705)), (int(W*0.95), int(H*0.86))], radius=15, outline="#00FF00", width=3)
        draw.rectangle([(int(W*0.64), int(H*0.708)), (int(W*0.82), int(H*0.74))], fill="#39FF14")
        draw.text((int(W*0.73), int(H*0.723)), "Price", fill="black", font=get_font(int(H*0.022)), anchor="mm")
        draw.text((int(W*0.73), int(H*0.80)), f"${price:.10f}", fill="white", font=get_font(int(H*0.023)), anchor="mm")

        # BURN - COVER BUONG BURN BOX PARA WALANG DOBLE NA 23.24M
        draw.rectangle([(0, int(H*0.875)), (W, int(H*0.96))], fill="black")
        draw.rounded_rectangle([(int(W*0.02), int(H*0.875)), (int(W*0.98), int(H*0.95))], radius=15, fill="#1A0000", outline="#FF4400", width=4)
        draw.text((W//2, int(H*0.895)), "🔥 TOTAL BURNED 🔥", fill="#FF6600", font=get_font(int(H*0.028)), anchor="mm")
        draw.text((W//2, int(H*0.925)), f"{burned/1000000:.2f}M MEH {burn_pct:.2f}%", fill="#FFAA00", font=get_font(int(H*0.035)), anchor="mm")
        draw.text((W//2, int(H*0.97)), "TO THE MOON 🚀🚀🚀", fill="#FFFF00", font=get_font(int(H*0.04)), anchor="mm")

        path = "/tmp/meh.png"
        img.save(path, quality=95)
        return path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr
    except Exception as e:
        print(f"make_card error: {e}")
        img = Image.new('RGB', (800, 600), 'black')
        d = ImageDraw.Draw(img)
        d.text((400, 300), f"$MEH {gain:.2f}x", fill="green", font=get_font(40), anchor="mm")
        path = "/tmp/meh.png"
        img.save(path)
        return path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr
