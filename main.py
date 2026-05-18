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
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔥 TOKEN JUGAD
TOKEN_PART1 = "8919342904:"
TOKEN_PART2 = "AAF5UdlNBRpW0gZloN2vDClCWBqdITn9afo"
BOT_TOKEN = TOKEN_PART1 + TOKEN_PART2

# 🔑 SCRAPERAPI KEY: Apni API Key yahan quotes ke andar zaroor check kar lena bhai!
SCRAPER_API_KEY = "85d4df19802f4fb311ddd179e352cc2f"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🚀 **Yt Downloader Engine V20 (Speed & Freeze Patch) Active!**\n\n"
        "Link bhejo bhai. Ab bina freeze hue fast extraction hogi!"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        status = await update.message.reply_text("⏳ Secure tunnel active... Fast link extraction chal rahi hai...")
        
        # 🔥 PROXY STRING
        proxy_string = f"http://scraperapi:{SCRAPER_API_KEY}@proxy-server.scraperapi.com:8001"

        try:
            ydl_opts = {
                'quiet': True, 
                'no_warnings': True,
                'socket_timeout': 30, # 👈 Timeout kam kiya taaki bot atke nahi, jaldi response kare
                'retries': 5,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # 👈 Safe & Light format force kiya hai fast loading ke liye
                'proxy': proxy_string,
                'nocheckcertificate': True,
                'extractor_args': {
                    'youtube': {
                        'clients': ['tv', 'mweb', 'android'], # 👈 Multi-client backup lagaya hai
                        'skip': ['dash', 'hls']
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Video File')
                thumbnail_url = info.get('thumbnail') 
                duration = info.get('duration', 0)
                formats = info.get('formats', [])

                link_720p = None
                link_360p = None
                direct_audio_url = None

                # Direct URL fallback agar niche formats load hone mein deri ho
                fallback_url = info.get('url')

                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        raw_url = f.get('url')
                        if raw_url:
                            if f.get('height') == 360:
                                link_360p = raw_url
                            elif f.get('height') == 720:
                                link_720p = raw_url
                    
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                        if f.get('ext') == 'm4a' or f.get('format_note') == 'low':
                            raw_url = f.get('url')
                            if raw_url:
                                direct_audio_url = raw_url

                # Agar specific formats na milein toh main single link use karega
                if not link_720p and not link_360p:
                    link_720p = fallback_url

                keyboard = []
                if link_720p:
                    keyboard.append([InlineKeyboardButton("🎬 Download Video (HD/Best)", url=link_720p)])
                if link_360p:
                    keyboard.append([InlineKeyboardButton("🎥 Download Video (360p SD)", url=link_360p)])

                send_audio_as_file = True
                if direct_audio_url:
                    if duration > 10800:
                        keyboard.append([InlineKeyboardButton("🎵 Download Audio/MP3", url=direct_audio_url)])
                        send_audio_as_file = False

                reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                
                guide_caption = (
                    f"🎯 **Video Title:** {video_title}\n\n"
                    f"📖 **DOWNLOAD KAISE KAREIN?**\n"
                    f"1. Upar diye gaye button par click karein.\n"
                    f"2. Video chalne par long press karke save kar lein! 🚀"
                )

                await status.delete()

                if thumbnail_url:
                    await update.message.reply_photo(photo=thumbnail_url, caption=guide_caption, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(text=guide_caption, reply_markup=reply_markup, disable_web_page_preview=True)
                
        except Exception as e:
            logger.error(e)
            try:
                await status.edit_text(f"❌ Server side delay hua hai bahi. Ek baar dubara link bhejein, IP badal kar fast connect ho jayega!")
            except Exception:
                await update.message.reply_text(f"❌ Connection Timeout! Please try again.")
    else:
        await update.message.reply_text("Bhai, sahi YouTube video link bhejo!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
    
    print("Bot is starting with V20 Speed Optimized Engine...")
    app.run_polling()

if __name__ == "__main__":
    main()
