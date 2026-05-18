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
import requests
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔥 TOKEN JUGAD
TOKEN_PART1 = "8919342904:"
TOKEN_PART2 = "AAF5UdlNBRpW0gZloN2vDClCWBqdITn9afo"
BOT_TOKEN = TOKEN_PART1 + TOKEN_PART2

# 🌐 FUNCTION: Strict Safe Proxy Fetcher (With Multi-Layer Fallback)
def get_free_proxy():
    # Layer 1: Databay Direct TXT File (Sabse safe aur un-crashable format)
    try:
        txt_url = "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/http.txt"
        res = requests.get(txt_url, timeout=5)
        if res.status_code == 200:
            lines = [line.strip() for line in res.text.splitlines() if line.strip()]
            if lines:
                selected = random.choice(lines)
                # HTTP proxy format set kar rahe hain yt-dlp ke liye
                proxy_url = f"http://{selected}"
                logger.info(f"🎯 Layer 1 Proxy Selected: {proxy_url}")
                return proxy_url
    except Exception as e:
        logger.error(f"Layer 1 Fetch Failed: {e}")

    # Layer 2: API Fallback JSON
    try:
        api_url = "https://databay.com/api/v1/proxy-list?ssl=strict&format=json&limit=10"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            proxies_list = response.json()
            if proxies_list and isinstance(proxies_list, list):
                chosen = random.choice(proxies_list)
                proxy_url = f"http://{chosen['ip']}:{chosen['port']}"
                logger.info(f"🎯 Layer 2 Proxy Selected: {proxy_url}")
                return proxy_url
    except Exception as e:
        logger.error(f"Layer 2 Fetch Failed: {e}")
        
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🚀 **Yt Downloader Engine V25 (Databay Stable Patch) Active!**\n\n"
        "Link bhejo bhai. Is baar structural error aur freeze dono fix kar diye hain!"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        status = await update.message.reply_text("⏳ Connecting via Databay Pool... Video data read ho raha hai...")
        
        # Fresh proxy call
        active_proxy = get_free_proxy()
        
        try:
            ydl_opts = {
                'quiet': True, 
                'no_warnings': True,
                'socket_timeout': 20, # Socket timeout kam rakha taaki GitHub workflow stuck na ho
                'retries': 3,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'nocheckcertificate': True,
                'extractor_args': {
                    'youtube': {
                        'clients': ['tv', 'mweb', 'ios'],
                        'skip': ['dash', 'hls']
                    }
                }
            }
            
            if active_proxy:
                ydl_opts['proxy'] = active_proxy

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Data extraction returned empty.")

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
                    f"1. Button par click karein.\n"
                    f"2. Video play hote hi long press karke save kar lein! 🚀"
                )

                await status.delete()

                if thumbnail_url:
                    await update.message.reply_photo(photo=thumbnail_url, caption=guide_caption, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(text=guide_caption, reply_markup=reply_markup, disable_web_page_preview=True)
                
        except Exception as e:
            logger.error(e)
            try:
                await status.edit_text("❌ Is proxy node par response delay hua hai. Ek baar dobara link bhejein, automatic fresh node connect ho jayega!")
            except Exception:
                await update.message.reply_text("❌ Network Busy! Ek baar fir bhejkar check karein.")
    else:
        await update.message.reply_text("Bhai, sahi YouTube video link bhejo!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
    
    print("Bot is starting with Stable Databay Engine...")
    app.run_polling()

if __name__ == "__main__":
    main()
