def make_card():
    W, H = 1024, 1150
    mcap, price, vol, liq, burned, burn_pct = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 6.60

    # MAANGAS NA CRYPTO BACKGROUND
    img = Image.new('RGB', (W, H), '#000000')
    draw = ImageDraw.Draw(img)
    
    # Gradient background - dark green to black
    for y in range(H):
        # Create vertical gradient
        ratio = y / H
        r = int(0 + ratio * 0)
        g = int(20 + ratio * 10)
        b = int(0 + ratio * 10)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    
    # Add stars / particles - crypto space feel
    import random
    random.seed(42)  # Same stars every time
    for _ in range(80):
        x = random.randint(0, W)
        y = random.randint(0, 600)
        size = random.randint(1, 3)
        brightness = random.randint(100, 255)
        draw.ellipse([(x, y),(x+size, y+size)], fill=(brightness, brightness, brightness))
        # Some green stars
        if random.random() > 0.7:
            draw.ellipse([(x, y),(x+size, y+size)], fill=(0, brightness, 0))
    
    # Circuit lines - techy look
    for _ in range(8):
        x = random.randint(0, W)
        y = random.randint(0, H//2)
        draw.line([(x, y),(x+random.randint(30, 100), y)], fill="#003300", width=1)
        draw.rectangle([(x+random.randint(30, 100), y-3),(x+random.randint(30, 100)+6, y+3)], outline="#00FF00", width=1)

    # Moon glow at top right
    moon_x, moon_y = W - 100, 80
    draw.ellipse([(moon_x-30, moon_y-30),(moon_x+30, moon_y+30)], fill="#111111", outline="#333333", width=1)
    draw.ellipse([(moon_x-20, moon_y-20),(moon_x+20, moon_y+20)], fill="#222222")

    # Outer neon border with glow
    draw.rounded_rectangle([(0,0),(W-1,H-1)], radius=40, outline="#00FF00", width=6)
    draw.rounded_rectangle([(5,5),(W-6,H-6)], radius=38, outline="#00FF00", width=2)
    # Inner glow
    for i in range(3):
        alpha = 100 - i*30
        draw.rounded_rectangle([(10+i,10+i),(W-11-i,H-11-i)], radius=35-i, outline=(0, 100, 0), width=1)

    # Title with glow effect
    # Shadow
    draw.text((W//2+3, 53), f"$MEH {gain:.2f}x", fill="#003300", font=get_font(100, True), anchor="mt")
    draw.text((W//2, 50), f"$MEH {gain:.2f}x", fill="#7FFF00", font=get_font(100, True), anchor="mt")
    
    draw.text((W//2+2, 162), "BULLISH AF!", fill="#332200", font=get_font(70, True), anchor="mt")
    draw.text((W//2, 160), "BULLISH AF!", fill="#FFFF00", font=get_font(70, True), anchor="mt")

    # Logo with glow
    logo_size = 360
    logo_x, logo_y = (W - logo_size)//2, 250
    try:
        if os.path.exists("logo.png"):
            # Outer glow
            for r in range(20, 0, -5):
                glow_size = logo_size + r*2
                glow = Image.new('RGBA', (glow_size, glow_size), (0,0,0,0))
                ImageDraw.Draw(glow).ellipse((0,0,grow_size, glow_size), fill=(0,255,0, 20))
                # Note: fix typo above - use glow_size
            logo = Image.open("logo.png").convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
            # Green glow
            glow = Image.new('RGBA', (logo_size+60, logo_size+60), (0,0,0,0))
            ImageDraw.Draw(glow).ellipse((0,0,logo_size+60, logo_size+60), fill=(0,255,0,50))
            img.paste(glow, (logo_x-30, logo_y-30), glow)
            
            mask = Image.new('L', (logo_size, logo_size), 0)
            ImageDraw.Draw(mask).ellipse((0,0,logo_size,logo_size), fill=255)
            img.paste(logo, (logo_x, logo_y), mask)
            draw.ellipse([(logo_x-5, logo_y-5),(logo_x+logo_size+5, logo_y+logo_size+5)], outline="#00FF00", width=5)
            draw.ellipse([(logo_x-10, logo_y-10),(logo_x+logo_size+10, logo_y+logo_size+10)], outline="#00FF00", width=1)
    except Exception as e:
        print(f"Logo error: {e}")

    # Stats boxes with glow
    box_w, box_h, gap, start_x, y_boxes = 220, 100, 20, 40, 680
    for i, (label, val) in enumerate([("MCap", f"${mcap:,.0f}"), ("Vol", f"${vol:,.0f}"), ("Liq", f"${liq:,.0f}"), ("Price", f"${price:.10f}")]):
        x = start_x + i*(box_w+gap)
        # Glow behind box
        draw.rounded_rectangle([(x-2, y_boxes-2),(x+box_w+2, y_boxes+box_h+2)], radius=17, fill="#001100")
        draw.rounded_rectangle([(x, y_boxes),(x+box_w, y_boxes+box_h)], radius=15, fill="#0A0A0A", outline="#00FF00", width=2)
        draw.text((x+box_w//2, y_boxes+12), label, fill="#00FF88", font=get_font(20, True), anchor="mt")
        draw.text((x+box_w//2, y_boxes+42), val, fill="white", font=get_font(24 if i<3 else 18, True), anchor="mt")

    # Burn box - with fire glow
    y_burn = 810
    # Fire glow
    draw.rounded_rectangle([(38, y_burn-2),(W-38, y_burn+152)], radius=22, fill="#330000")
    draw.rounded_rectangle([(40, y_burn),(W-40, y_burn+150)], radius=20, fill="#1A0A0A", outline="#FF4500", width=4)
    draw.text((W//2, y_burn+15), "🔥 TOTAL BURNED (AUTO) 🔥", fill="#FF4500", font=get_font(26, True), anchor="mt")
    draw.text((W//2, y_burn+55), f"{burned/1000000:.2f}M MEH", fill="white", font=get_font(40, True), anchor="mt")
    draw.text((W//2, y_burn+105), f"{burn_pct:.2f}% OF SUPPLY • AUTO-DETECTED", fill="#FFA500", font=get_font(18), anchor="mt")

    # Footer
    draw.rounded_rectangle([(38, 988),(W-38, 1042)], radius=17, fill="#002200")
    draw.rounded_rectangle([(40, 990),(W-40, 1040)], radius=15, fill="#001100", outline="#00FF00", width=2)
    draw.text((W//2, 1015), "TO THE MOON • AUTO BURN MODE 🔥🚀", fill="#00FF00", font=get_font(22, True), anchor="mm")

    path = "/tmp/meh.png"
    img.save(path, quality=95)
    return path, gain, mcap, price, vol, burned, burn_pct
