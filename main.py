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

# 🌐 FUNCTION: Databay API se fresh Google-Compatible SOCKS5/HTTP Proxy nikalne ke liye
def get_free_proxy():
    try:
        # Hum unka unauthenticated API use kar rahe hain jo 100% free hai
        # Filter: google=true (YT bypass ke liye), ssl=strict (security ke liye)
        api_url = "https://databay.com/api/v1/proxy-list?ssl=strict&google=true&limit=20&format=json"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            proxies_list = response.json()
            if proxies_list and len(proxies_list) > 0:
                # Koi bhi ek random proxy utha lo list se rotation ke liye
                chosen = random.choice(proxies_list)
                proxy_url = f"{chosen['protocol']}://{chosen['ip']}:{chosen['port']}"
                logger.info(f"🔄 Selected Fresh Proxy: {proxy_url} ({chosen['country']})")
                return proxy_url
    except Exception as e:
        logger.error(f"Proxy API Fetch Error: {e}")
    
    # Fallback: Agar API down ho toh unki raw text file se direct utha lo
    try:
        txt_url = "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt"
        res = requests.get(txt_url, timeout=10)
        if res.status_code == 200:
            lines = res.text.splitlines()
            if lines:
                return f"socks5://{random.choice(lines)}"
    except Exception:
        pass
        
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🚀 **Yt Downloader Engine V24 (Databay Auto-Proxy Pool) Active!**\n\n"
        "Link bhejo bhai. Ab har request par automatic 5-minute fresh proxy rotate hogi!"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        status = await update.message.reply_text("⏳ Databay Pool se fresh proxy connect ho rahi hai...")
        
        # 🔥 Har bar naya proxy fetch hoga
        active_proxy = get_free_proxy()
        
        if active_proxy:
            await status.edit_text("⏳ Proxy connected! Ab video link bypass extraction chal rahi hai...")
        else:
            await status.edit_text("⏳ Proxy pool busy, direct secure line se fetch ho raha hai...")

        try:
            ydl_opts = {
                'quiet': True, 
                'no_warnings': True,
                'socket_timeout': 40,
                'retries': 5,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'nocheckcertificate': True,
                'extractor_args': {
                    'youtube': {
                        'clients': ['tv', 'mweb', 'ios', 'android'],
                        'skip': ['dash', 'hls']
                    }
                }
            }
            
            # Agar proxy mili toh options mein inject karo, varna direct bypass use karo
            if active_proxy:
                ydl_opts['proxy'] = active_proxy

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Video File')
                thumbnail_url = info.get('thumbnail') 
                duration = info.get('duration', 0)
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
                await status.edit_text(f"❌ Extraction Error bahi. Ek baar dubara link bhejo, proxy automatic rotate ho jayegi!")
            except Exception:
                await update.message.reply_text(f"❌ Connection Error: {e}")
    else:
        await update.message.reply_text("Bhai, sahi YouTube video link bhejo!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
    
    print("Bot is starting with Databay Rotating Proxy Pool Engine...")
    app.run_polling()

if __name__ == "__main__":
    main()
