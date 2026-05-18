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
        "🚀 **Yt Downloader Engine V15 (API Cloud Proxy Node) Active!**\n\n"
        "Link bhejo bhai. Ab bina cookies ke bypass tunnel se extraction hogi!"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        status = await update.message.reply_text("⏳ API Proxy tunnel se secure data fetch ho raha hai...")
        
        # 🔗 INVIDIOUS INSTANCE BYPASS: Direct YT block todne ke liye proxy instance par routing
        # Agar direct nahi chalta, toh hum link ko ek aise proxy domain par convert kar dete hain jise YT block nahi karta
        video_id_match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11})", url)
        if video_id_match:
            video_id = video_id_match.group(1)
            # Yahan hum reliable invidious node use kar rahe hain jo yt-dlp ko direct support karta hai
            target_url = f"https://invidious.nerdvpn.de/watch?v={video_id}"
        else:
            target_url = url

        try:
            ydl_opts = {
                'quiet': True, 
                'no_warnings': True,
                'socket_timeout': 60,
                'retries': 10,
                'format': 'best',
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'hls']
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=False)
                video_title = info.get('title', 'Video File')
                thumbnail_url = info.get('thumbnail') 
                duration = info.get('duration', 0)
                formats = info.get('formats', [])

                link_720p = None
                link_360p = None
                direct_audio_url = None

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

                if not link_720p and not link_360p:
                    for f in reversed(formats):
                        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                            raw_url = f.get('url')
                            if raw_url:
                                link_720p = raw_url
                            break

                keyboard = []
                if link_720p:
                    keyboard.append([InlineKeyboardButton("🎬 Download 720p HD", url=link_720p)])
                if link_360p:
                    keyboard.append([InlineKeyboardButton("🎥 Download 360p SD", url=link_360p)])

                send_audio_as_file = True
                if direct_audio_url:
                    if duration > 10800:
                        keyboard.append([InlineKeyboardButton("🎵 Download Audio/MP3", url=direct_audio_url)])
                        send_audio_as_file = False

                reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                
                guide_caption = (
                    f"🎯 **Video Title:** {video_title}\n\n"
                    f"📖 **DOWNLOAD KAISE KAREIN?**\n"
                    f"1. Upar diye gaye quality button par click karein.\n"
                    f"2. Agar video browser mein direct play hone lage, toh us button par **Long Press** aur **'Download Link'** select karein. Background mein turant download shuru ho jayegi! 🚀"
                )

                await status.delete()

                if thumbnail_url:
                    await update.message.reply_photo(photo=thumbnail_url, caption=guide_caption, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(text=guide_caption, reply_markup=reply_markup, disable_web_page_preview=True)

                if direct_audio_url and send_audio_as_file:
                    try:
                        await update.message.reply_chat_action(action="upload_voice")
                        await update.message.reply_audio(
                            audio=direct_audio_url,
                            title=f"{video_title}",
                            performer="YtDownloader",
                            caption="🎵 **Direct Video Audio File**",
                            read_timeout=60,
                            write_timeout=60
                        )
                    except Exception as audio_err:
                        logger.error(f"Audio connection error fallback: {audio_err}")
                        await update.message.reply_text(f"🎵 **Audio Link:**\n[Click here]({direct_audio_url})", parse_mode="Markdown")
                
        except Exception as e:
            logger.error(e)
            try:
                await status.edit_text(f"❌ Extraction Error: Node busy. Ek baar dubara link bhejein.")
            except Exception:
                await update.message.reply_text(f"❌ Error Occurred: {e}")
    else:
        await update.message.reply_text("Bhai, sahi YouTube video link bhejo!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
    
    print("Bot is starting with Cloud Node Engine...")
    app.run_polling()

if __name__ == "__main__":
    main()
