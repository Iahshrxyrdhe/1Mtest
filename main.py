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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔥 TOKEN JUGAD
TOKEN_PART1 = "8919342904:"
TOKEN_PART2 = "AAF5UdlNBRpW0gZloN2vDClCWBqdITn9afo"
BOT_TOKEN = TOKEN_PART1 + TOKEN_PART2

# 🌐 FUNCTION: Databay GitHub se direct fresh SOCKS5 proxies load karna (No-Crash Engine)
def load_socks5_pool():
    url = "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt"
    try:
        # Browser ki tarah acting karne ke liye headers (Anti-Block)
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8')
            # Lines ko split karke khali spaces saaf karna
            proxies = [line.strip() for line in html.splitlines() if line.strip()]
            if proxies:
                logger.info(f"✅ Successfully loaded {len(proxies)} fresh SOCKS5 proxies from Databay!")
                return proxies
    except Exception as e:
        logger.error(f"❌ Failed to fetch socks5.txt from GitHub: {e}")
    return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🚀 **Yt Downloader Engine V26 (Smart SOCKS5 Pool) Active!**\n\n"
        "Link bhejo bhai. Ab dead proxies automatic skip hongi aur live proxy par fast download hoga!"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        status = await update.message.reply_text("⏳ Databay GitHub pool se live SOCKS5 proxy connect kar raha hoon...")
        
        # Fresh pool fetch karo
        proxy_pool = load_socks5_pool()
        
        if not proxy_pool:
            # Fallback agar pool fetch na ho paye kisi vajah se
            await status.edit_text("⚠️ Proxy pool load nahi ho paya, direct line se try kar raha hoon...")
            # 10 random fresh elements list fail hone par shuffle try ke liye
            proxy_pool = [None]
        else:
            # Pool ko random shuffle kar do taaki har user ko alag proxy mile
            random.shuffle(proxy_pool)
            # Sirf top 15 proxies test karenge fast processing ke liye
            proxy_pool = proxy_pool[:15]

        info = None
        extracted_successfully = False

        # 🔥 SMART LOOP: Ek ek karke proxy check karega, jo fast chalegi usse link nikalega
        for i, raw_proxy in enumerate(proxy_pool):
            proxy_url = f"socks5://{raw_proxy}" if raw_proxy else None
            
            try:
                if proxy_url:
                    await status.edit_text(f"⏳ Testing Proxy Node [{i+1}/{len(proxy_pool)}]: {raw_proxy}...")
                
                ydl_opts = {
                    'quiet': True, 
                    'no_warnings': True,
                    'socket_timeout': 4, # 👈 Sabse zaroori: Sirf 4 second wait karega, slow proxy ko turant chhod dega!
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
                        break # 🔥 Link mil gaya! Loop se baahar nikal jao
            except Exception as proxy_error:
                logger.warning(f"Node {raw_proxy} failed or timed out. Trying next...")
                continue # Agar ye proxy fail hui ya slow hui, toh bina ruke agli par jao

        # 🔥 RESPONSE BUILDER
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

                keyboard = []
                if link_720p:
                    keyboard.append([InlineKeyboardButton("🎬 Download Best Video (HD)", url=link_720p)])
                if link_360p:
                    keyboard.append([InlineKeyboardButton("🎥 Download 360p SD", url=link_360p)])

                reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                
                guide_caption = (
                    f"🎯 **Video Title:** {video_title}\n\n"
                    f"📖 **DOWNLOAD KAISE KAREIN?**\n"
                    f"1. Neeche diye button par click karein.\n"
                    f"2. Play hote hi long press karke save kar lein! 🚀"
                )

                await status.delete()

                if thumbnail_url:
                    await update.message.reply_photo(photo=thumbnail_url, caption=guide_caption, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(text=guide_caption, reply_markup=reply_markup, disable_web_page_preview=True)
            except Exception as send_error:
                await update.message.reply_text(f"❌ Technical error while sending buttons: {send_error}")
        else:
            await status.edit_text("❌ Saari tested proxies blocked ya slow milin bahi. Ek baar fir se link send karo naye pool ke liye!")
    else:
        await update.message.reply_text("Bhai, sahi YouTube video link bhejo!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
    
    print("Bot is starting with Smart SOCKS5 Swapper Engine...")
    app.run_polling()

if __name__ == "__main__":
    main()
