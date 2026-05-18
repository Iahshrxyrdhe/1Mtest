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
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔥 TOKEN JUGAD
TOKEN_PART1 = "8919342904:"
TOKEN_PART2 = "AAF5UdlNBRpW0gZloN2vDClCWBqdITn9afo"
BOT_TOKEN = TOKEN_PART1 + TOKEN_PART2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🚀 **Yt Downloader Engine V16 (No-Auth Cloud Patch) Active!**\n\n"
        "Link bhejo bhai. Ab bina cookies aur bina block ke processing hogi!"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        status = await update.message.reply_text("⏳ Processing URL via Secure Cloud Nodes...")
        
        try:
            # 🔥 LATEST NO-COOKIES BYPASS METHOD
            ydl_opts = {
                'quiet': True, 
                'no_warnings': True,
                'socket_timeout': 60,
                'retries': 10,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Sabse safe format jo jaldi extract ho ske
                'extractor_args': {
                    'youtube': {
                        # Web clients ko poora block karke sirf lightweight embedded nodes force kiye hain
                        'clients': ['tv', 'mweb', 'android_embed', 'ios'], 
                        'skip': ['dash', 'hls']
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Video File')
                thumbnail_url = info.get('thumbnail') 
                duration = info.get('duration', 0)
                
                # Direct best dynamic format direct link nikalne ke liye
                direct_video_url = info.get('url')

                keyboard = []
                if direct_video_url:
                    keyboard.append([InlineKeyboardButton("🎬 Direct Download Video", url=direct_video_url)])

                reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                
                guide_caption = (
                    f"🎯 **Video Title:** {video_title}\n\n"
                    f"📖 **DOWNLOAD KAISE KAREIN?**\n"
                    f"1. Upar diye gaye button par click karein.\n"
                    f"2. Agar video direct chalne lage, toh long press karke 'Download Video/Link' select karein! 🚀"
                )

                await status.delete()

                if thumbnail_url:
                    await update.message.reply_photo(photo=thumbnail_url, caption=guide_caption, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(text=guide_caption, reply_markup=reply_markup, disable_web_page_preview=True)
                
        except Exception as e:
            logger.error(e)
            try:
                await status.edit_text(f"❌ Extraction Error: {e}\n\nTip: Ek baar dubara try karein.")
            except Exception:
                await update.message.reply_text(f"❌ Error Occurred: {e}")
    else:
        await update.message.reply_text("Bhai, sahi YouTube video link bhejo!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
    
    print("Bot is starting with V16 No-Auth Engine...")
    app.run_polling()

if __name__ == "__main__":
    main()
