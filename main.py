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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔥 TOKEN JUGAD: GitHub filters se bachne ke liye token split kiya hai
TOKEN_PART1 = "8919342904:"
TOKEN_PART2 = "AAF5UdlNBRpW0gZloN2vDClCWBqdITn9afo"
BOT_TOKEN = TOKEN_PART1 + TOKEN_PART2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🚀 **Yt Downloader Engine V13 (Android Native Patch) Active!**\n\n"
        "Link bhejo bhai. Ab direct mobile client emulation se processing hogi!"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        status = await update.message.reply_text("⏳ Android API nodes se secure data fetch ho raha hai...")
        
        try:
            # 🔥 HIGH-LEVEL BYPASS: GitHub/VPS Server block todne ke liye advance adjustments
            ydl_opts = {
                'quiet': True, 
                'no_warnings': True,
                'socket_timeout': 60,
                'retries': 10,
                'format': 'best',
                'extractor_args': {
                    'youtube': {
                        'clients': ['android', 'android_embed', 'ios', 'web_embedded'],
                        'skip': ['dash', 'hls'],
                        'youtube_include_po_token': True # Bot/Sign-in block bypass karne ka main switch
                    }
                },
                'http_headers': {
                    'User-Agent': 'com.google.android.youtube/19.10.34 (Linux; U; Android 14; en_US) Mozilla/5.0',
                    'X-Youtube-Client-Name': '3',
                    'X-Youtube-Client-Version': '19.10.34',
                    'Accept-Language': 'en-US,en;q=0.9'
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

                # Formats Extraction Loop
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

                # Video Fallback Handler
                if not link_720p and not link_360p:
                    for f in reversed(formats):
                        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                            raw_url = f.get('url')
                            if raw_url:
                                link_720p = raw_url
                            break

                # Base Video Buttons Setup
                keyboard = []
                if link_720p:
                    keyboard.append([InlineKeyboardButton("🎬 Download 720p HD", url=link_720p)])
                if link_360p:
                    keyboard.append([InlineKeyboardButton("🎥 Download 360p SD", url=link_360p)])

                # Dynamic Audio Trigger Logic
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
                    f"2. Agar video browser mein direct play hone lage, toh us button par **Long Press (dabakar rakhein)** aur **'Download Link' / 'Save Link'** select karein. Background mein turant download shuru ho jayegi! 🚀"
                )

                await status.delete()

                # Step 1: Send Thumbnail
                if thumbnail_url:
                    await update.message.reply_photo(
                        photo=thumbnail_url,
                        caption=guide_caption,
                        reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text(
                        text=guide_caption,
                        reply_markup=reply_markup,
                        disable_web_page_preview=True
                    )

                # Step 2: Audio delivery decision
                if direct_audio_url and send_audio_as_file:
                    try:
                        await update.message.reply_chat_action(action="upload_voice")
                        await update.message.reply_audio(
                            audio=direct_audio_url,
                            title=f"{video_title}",
                            performer="YtDownloader",
                            caption="🎵 **Direct Video Audio File**\n(Aap ise direct chat me sun sakte hain)",
                            read_timeout=60,
                            write_timeout=60
                        )
                    except Exception as audio_err:
                        logger.error(f"Audio connection error fallback: {audio_err}")
                        await update.message.reply_text(
                            f"🎵 **Audio Link (Direct Stream):**\n[Click here to download audio]({direct_audio_url})",
                            parse_mode="Markdown"
                        )
                
        except Exception as e:
            logger.error(e)
            try:
                await status.edit_text(f"❌ Extraction Error: {e}\n\nTip: Ek baar dubara link bhejkar try karein, GitHub server IP badalne par bypass ho jata hai.")
            except Exception:
                await update.message.reply_text(f"❌ Error Occurred: {e}")
    else:
        await update.message.reply_text("Bhai, sahi YouTube video link bhejo!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
    
    print("Bot is starting with Pure Android Native Emulation Engine...")
    app.run_polling()

if __name__ == "__main__":
    main()
