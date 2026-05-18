# ==================== CRITICAL TERMUX/VPS TIMEZONE FIX ====================
import pytz
import apscheduler.util
try:
    import apscheduler.triggers.base
except ImportError:
    pass

def fixed_astimezone(obj):
    if obj is None:
        return pytz.timezone('Asia/Kolkata')
    if isinstance(obj, str):
        return pytz.timezone(obj)
    return obj

apscheduler.util.astimezone = fixed_astimezone
# ======================================================================

import logging
import yt_dlp
import urllib.request
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔥 TOKEN JUGAD
TOKEN_PART1 = "8919342904:"
TOKEN_PART2 = "AAF5UdlNBRpW0gZloN2vDClCWBqdITn9afo"
BOT_TOKEN = TOKEN_PART1 + TOKEN_PART2

# 🌐 FUNCTION: Databay GitHub se direct fresh SOCKS5 proxies load karna
def load_socks5_pool():
    url = "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8')
            proxies = [line.strip() for line in html.splitlines() if line.strip()]
            if proxies:
                logger.info(f"✅ Successfully loaded {len(proxies)} fresh SOCKS5 proxies from Databay!")
                return proxies
    except Exception as e:
        logger.error(f"❌ Failed to fetch socks5.txt from GitHub: {e}")
    return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🚀 **Yt Downloader Engine V27 (Direct Link Mode) Active!**\n\n"
        "Link bhejo bhai. Ab bina buttons ke direct clickable download links caption mein milenge!"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        status = await update.message.reply_text("⏳ Databay GitHub pool se live SOCKS5 proxy connect kar raha hoon...")
        
        proxy_pool = load_socks5_pool()
        
        if not proxy_pool:
            await status.edit_text("⚠️ Proxy pool load nahi ho paya, direct line se try kar raha hoon...")
            proxy_pool = [None]
        else:
            random.shuffle(proxy_pool)
            proxy_pool = proxy_pool[:15]

        info = None
        extracted_successfully = False

        # SMART LOOP: Proxy check cycle
        for i, raw_proxy in enumerate(proxy_pool):
            proxy_url = f"socks5://{raw_proxy}" if raw_proxy else None
            
            try:
                if proxy_url:
                    await status.edit_text(f"⏳ Testing Proxy Node [{i+1}/{len(proxy_pool)}]: {raw_proxy}...")
                
                ydl_opts = {
                    'quiet': True, 
                    'no_warnings': True,
                    'socket_timeout': 4, 
                    'retries': 1,
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'nocheckcertificate': True,
                    'extractor_args': {
                        'youtube': {
                            'clients': ['tv', 'mweb', 'ios'],
                            'skip': ['dash', 'hls']
                        }
                    }
                }
                
                if proxy_url:
                    ydl_opts['proxy'] = proxy_url

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        extracted_successfully = True
                        break 
            except Exception:
                continue

        # 🔥 RESPONSE BUILDER (Direct Link in Caption)
        if extracted_successfully and info:
            try:
                video_title = info.get('title', 'Video File')
                thumbnail_url = info.get('thumbnail') 
                formats = info.get('formats', [])

                link_720p = None
                link_360p = None
                fallback_url = info.get('url')

                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        raw_url = f.get('url')
                        if raw_url:
                            if f.get('height') == 360:
                                link_360p = raw_url
                            elif f.get('height') == 720:
                                link_720p = raw_url

                if not link_720p and not link_360p:
                    link_720p = fallback_url

                # Direct HTML Hyperlinks build kar rahe hain text ke liye
                links_text = ""
                if link_720p:
                    links_text += f"🔹 <a href='{link_720p}'>👉 CLICK HERE TO DOWNLOAD (HD Quality) 👈</a>\n\n"
                if link_360p:
                    links_text += f"🔹 <a href='{link_360p}'>👉 CLICK HERE TO DOWNLOAD (360p SD) 👈</a>\n\n"
                
                if not links_text and fallback_url:
                    links_text += f"🔹 <a href='{fallback_url}'>👉 CLICK HERE TO DOWNLOAD (Best Quality) 👈</a>\n\n"

                # Ekdam easy and clear downloading guide instructions ke sath
                guide_caption = (
                    f"🎯 <b>Video Title:</b> {video_title}\n\n"
                    f"👇 <b>DOWNLOAD LINKS:</b>\n"
                    f"{links_text}"
                    f"📖 <b>DOWNLOAD KAISE KAREIN? (EASY GUIDE):</b>\n"
                    f"1️⃣ Upar diye gaye blue color ke <b>DOWNLOAD LINK</b> text par click karein.\n"
                    f"2️⃣ Aapke browser (Chrome) mein video play hona start ho jayegi.\n"
                    f"3️⃣ Video ke upar <b>Long Press (thodi der dabakar rakhein)</b> aur <b>'Download Video'</b> ka option aayega, uspar click karke save kar lein! 🚀\n\n"
                    f"<i>Tip: Agar long press nahi chal raha, toh video ke niche right side mein 3-dots (...) par click karke Download daba dein.</i>"
                )

                await status.delete()

                # Parse mode HTML use kiya hai taaki links sahi se hyperlink ban sakein
                if thumbnail_url:
                    await update.message.reply_photo(photo=thumbnail_url, caption=guide_caption, parse_mode="HTML")
                else:
                    await update.message.reply_text(text=guide_caption, parse_mode="HTML", disable_web_page_preview=True)
            except Exception as send_error:
                await update.message.reply_text(f"❌ Technical error while sending links: {send_error}")
        else:
            await status.edit_text("❌ Saari tested proxies blocked mili bhai. Naye pool ke liye ek baar fir se link bhej do!")
    else:
        await update.message.reply_text("Bhai, sahi YouTube video link bhejo!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
    
    print("Bot is starting with Direct Link Engine...")
    app.run_polling()

if __name__ == "__main__":
    main()
