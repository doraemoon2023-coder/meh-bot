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
            api_key = os.environ.get("BSCSCAN_API_KEY", "") or os.environ.get("ETHERSCAN_API_KEY", "")
            # V2 API - chainid 56 = BSC
            bsc_url = f"https://api.etherscan.io/v2/api?chainid=56&module=account&action=tokenbalance&contractaddress={CA}&address={dead}&tag=latest&apikey={api_key}"
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

def monitor_buys(app):
    global last_hash
    while True:
        try:
            mcap, price, vol, liq, burned, burn_pct, pair_addr = get_live_data()
            if not pair_addr:
                print("No pair_addr yet")
                time.sleep(15)
                continue
            api_key = os.environ.get("BSCSCAN_API_KEY", "") or os.environ.get("ETHERSCAN_API_KEY", "")
            url = f"https://api.etherscan.io/v2/api?chainid=56&module=account&action=tokentx&contractaddress={CA}&address={pair_addr}&page=1&offset=5&sort=desc&apikey={api_key}"
            resp = requests.get(url, timeout=15).json()
            print(f"Checking buys V2: status={resp.get('status')} msg={resp.get('message')}")
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
                                print(f"Detected BUY ${usd:.2f} hash {h[:10]}")
                                if usd >= 0.1:
                                    last_hash = h
                                    path, gain, mcap, price, vol, liq, burned, burn_pct, pair_addr = make_card(buy_amount=usd, buyer=tx.get('to',''))
                                    caption = f"NEW BUY ${usd:.2f}! $MEH {gain:.2f}x MCap ${mcap:,.0f}\n{CA}"
                                    if CHANNEL_ID:
                                        try:
                                            loop = asyncio.new_event_loop()
                                            asyncio.set_event_loop(loop)
                                            cid = int(CHANNEL_ID) if str(CHANNEL_ID).lstrip('-').isdigit() else CHANNEL_ID
                                            print(f"Sending bullish card to {cid}")
                                            loop.run_until_complete(app.bot.send_photo(chat_id=cid, photo=open(path,'rb'), caption=caption))
                                            print("Sent bullish card!")
                                        except Exception as e:
                                            print(f"Send error: {e}")
                                    break
        except Exception as e:
            print(f"Monitor error: {e}")
        time.sleep(15)
