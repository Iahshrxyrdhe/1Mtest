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
import random
import asyncio
import time
import sys
import os
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔥 TOKEN JUGAD
TOKEN_PART1 = "8919342904:"
TOKEN_PART2 = "AAF5UdlNBRpW0gZloN2vDClCWBqdITn9afo"
BOT_TOKEN = TOKEN_PART1 + TOKEN_PART2

# ⏱️ START TIME TRACKER
START_TIME = time.time()
MAX_RUN_TIME = 170 * 60  # 170 Minutes (2 Hours 50 Minutes)

# 🌐 List of Invidious Instances for ultra-fast fallback link extraction
INVIDIOUS_INSTANCES = [
    "https://invidious.nerdvpn.de",
    "https://yewtu.be",
    "https://invidious.flokinet.to",
    "https://inv.vern.cc",
    "https://invidious.privacydev.net",
    "https://iv.melmac.space"
]

# 🔥 EXTRACTION ENGINE: Multi-Client + Extractor Override
def run_yt_dlp_fast(url):
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'socket_timeout': 4.0, # Balanced timeout
        'retries': 1,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                # Force embedded and alternative player clients to bypass bot block
                'clients': ['web_embedded', 'android_embed', 'tvhtml5', 'ios'],
                'skip': ['dash', 'hls']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# 🛡️ AUTOMATIC AUTO-EXIT CHECKER
def check_runtime():
    elapsed_time = time.time() - START_TIME
    if elapsed_time >= MAX_RUN_TIME:
        logger.info("⏳ 170 minutes over! Safely exiting...")
        sys.exit(0)

# 🚀 WELCOME MESSAGE WITH PROFESSIONAL REPLY KEYBOARD
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    check_runtime()
    context.user_data['mode'] = None
    
    keyboard = [
        [KeyboardButton("📹 YT VIDEO DOWNLOADER"), KeyboardButton("🎵 AUDIO DOWNLOADER")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="Select Mode From Keyboard")
    
    await update.message.reply_text(
        "Hey ! Your Welcome, Give me any youtube video link for Download I will give you the Download link of that video",
        reply_markup=reply_markup
    )

# 📥 MAIN MESSAGE HANDLER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    check_runtime()
    text = update.message.text

    if text == "📹 YT VIDEO DOWNLOADER":
        context.user_data['mode'] = 'video'
        await update.message.reply_text("📥 **YT VIDEO DOWNLOADER MODE ACTIVE**\n\nNow send me any YouTube video link:")
        return
    elif text == "🎵 AUDIO DOWNLOADER":
        context.user_data['mode'] = 'audio'
        await update.message.reply_text("📥 **AUDIO DOWNLOADER MODE ACTIVE**\n\nNow send me any YouTube video link (Max 50MB):")
        return

    if "youtube.com" in text or "youtu.be" in text:
        current_mode = context.user_data.get('mode')
        if not current_mode:
            await update.message.reply_text("Bhai, pehle niche keyboard se ek mode select karo (Video ya Audio)!")
            return

        status = await update.message.reply_text("⚡ Processing link instantly via Bypass Pipeline...")
        loop = asyncio.get_running_loop()
        
        info = None
        extracted_successfully = False

        # 🚀 STEP 1: Direct Fetch with Spoofed Embedded Clients
        try:
            info = await loop.run_in_executor(None, run_yt_dlp_fast, text)
            if info:
                extracted_successfully = True
        except Exception as e:
            logger.info(f"Direct fetch restricted: {e}. Trying Invidious Bridge...")

        # 🛡️ STEP 2: Invidious Alternative Instance Router (If direct fails)
        if not extracted_successfully:
            await status.edit_text("⏳ Bypassing YouTube Restrictions... Please wait a moment.")
            
            # Extract video ID
            video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', text)
            if video_id_match:
                video_id = video_id_match.group(1)
                random.shuffle(INVIDIOUS_INSTANCES)
                
                # Try routing through mirror endpoints
                for instance in INVIDIOUS_INSTANCES[:3]:
                    try:
                        mirror_url = f"{instance}/watch?v={video_id}"
                        info = await loop.run_in_executor(None, run_yt_dlp_fast, mirror_url)
                        if info:
                            extracted_successfully = True
                            break
                    except Exception:
                        continue

        if not extracted_successfully or not info:
            await status.edit_text("❌ YouTube is heavily rate-limiting requests right now. Please try re-sending the link or try another video!")
            return

        # 📹 VIDEO MODE INTERACTION
        if current_mode == 'video':
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

                links_text = ""
                if link_720p:
                    links_text += f"🔹 <a href='{link_720p}'>👉 CLICK HERE TO DOWNLOAD (HD Quality) 👈</a>\n\n"
                if link_360p:
                    links_text += f"🔹 <a href='{link_360p}'>👉 CLICK HERE TO DOWNLOAD (360p SD) 👈</a>\n\n"
                
                if not link_720p and not link_360p:
                    best_stream = fallback_url
                    if not best_stream and formats:
                        for fmt in reversed(formats):
                            if fmt.get('url') and ('googlevideo.com' in fmt.get('url') or 'manifest' in fmt.get('url')):
                                best_stream = fmt.get('url')
                                break
                    if best_stream:
                        links_text += f"🔹 <a href='{best_stream}'>👉 CLICK HERE TO DOWNLOAD (Best Available Quality) 👈</a>\n\n"

                guide_caption = (
                    f"🎯 <b>Video Title:</b> {video_title}\n\n"
                    f"👇 <b>VIDEO DOWNLOAD LINKS:</b>\n"
                    f"{links_text}"
                    f"📖 <b>DOWNLOAD KAISE KAREIN? (EASY GUIDE):</b>\n"
                    f"1️⃣ Upar diye gaye blue color ke link text par click karein.\n"
                    f"2️⃣ Browser mein file open hote hi <b>Long Press</b> karein ya niche right side mein <b>3-dots (...)</b> par click karke <b>Download</b> daba dein! 🚀"
                )

                await status.delete()
                if thumbnail_url:
                    await update.message.reply_photo(photo=thumbnail_url, caption=guide_caption, parse_mode="HTML")
                else:
                    await update.message.reply_text(text=guide_caption, parse_mode="HTML", disable_web_page_preview=True)
            except Exception as e:
                await status.edit_text(f"❌ Video link builder error: {e}")

        # 🎵 AUDIO MODE INTERACTION
        elif current_mode == 'audio':
            try:
                video_title = info.get('title', 'Audio File')
                formats = info.get('formats', [])
                
                audio_size_bytes = 0
                for f in formats:
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                        audio_size_bytes = f.get('filesize') or f.get('filesize_approx') or 0

                audio_size_mb = audio_size_bytes / (1024 * 1024) if audio_size_bytes else 0

                if audio_size_mb > 50:
                    await status.edit_text("⚠️ **THIS AUDIO SIZE IS OUT OF LIMIT**")
                    return

                await status.edit_text("📥 Downloading audio track directly to Telegram...")
                
                unique_id = random.randint(1000, 9999)
                expected_file = f"audio_{unique_id}.m4a"

                # Direct high-speed worker download without broken proxies
                ydl_opts_dl = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'outtmpl': expected_file,
                    'nocheckcertificate': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts_dl) as ydl:
                    await loop.run_in_executor(None, ydl.download, [text])

                if os.path.exists(expected_file) and os.path.getsize(expected_file) > 0:
                    await status.edit_text("📤 Uploading audio player...")
                    with open(expected_file, 'rb') as audio_file:
                        await update.message.reply_audio(audio=audio_file, title=video_title, performer="Yt Downloader")
                    await status.delete()
                else:
                    await status.edit_text("⚠️ Download interrupted by network reset. Please try again.")
                
                if os.path.exists(expected_file):
                    os.remove(expected_file)

            except Exception as e:
                await status.edit_text(f"❌ Audio processing error: {e}")
    else:
        await update.message.reply_text("Bhai, sahi YouTube link bhejo ya keyboard se option select karo!")

def main():
    app = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is starting with Invidious Bypass Engine V36...")
    app.run_polling()

if __name__ == "__main__":
    main()
