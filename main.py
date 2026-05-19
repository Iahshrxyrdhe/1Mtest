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
import asyncio
import time
import sys
import os
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

def fetch_socks5_only():
    url = "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    proxies = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as response:
            for line in response.read().decode('utf-8').splitlines():
                if line.strip():
                    proxies.append(f"socks5://{line.strip()}")
        return proxies
    except Exception as e:
        logger.error(f"❌ Failed to fetch SOCKS5 repository: {e}")
        return []

def test_single_proxy(url, proxy_url):
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'socket_timeout': 4.0,
        'retries': 0,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'nocheckcertificate': True,
        'proxy': proxy_url,
        'extractor_args': {
            'youtube': {
                'clients': ['android', 'web_embedded', 'tvhtml5', 'ios'],
                'skip': ['dash', 'hls']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# 🔥 CORE FILE DOWNLOAD PIPELINE WITH AUTO-DIRECT FALLBACK
def download_audio_pipeline(url, proxy_url, output_filename):
    # 🎯 Attempt 1: Proxy ke sath try karo
    ydl_opts_proxy = {
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 15,
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': output_filename,
        'nocheckcertificate': True,
        'proxy': proxy_url
    }
    try:
        logger.info(f"🔄 Trying audio download via proxy: {proxy_url}")
        with yt_dlp.YoutubeDL(ydl_opts_proxy) as ydl:
            ydl.download([url])
            return True
    except Exception as e:
        logger.warning(f"⚠️ Proxy reset connection: {e}. Switching to Direct Cloud Pipeline instantly!")
        
        # 🎯 Attempt 2: Bypassing proxy and downloading directly via server network if proxy resets
        ydl_opts_direct = {
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 25,
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': output_filename,
            'nocheckcertificate': True,
            'extractor_args': {
                'youtube': {
                    'clients': ['tvhtml5', 'android_embed'],
                    'skip': ['dash', 'hls']
                }
            }
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts_direct) as ydl:
                ydl.download([url])
                return True
        except Exception as direct_err:
            logger.error(f"❌ Direct fallback also failed: {direct_err}")
            return False

def check_runtime():
    elapsed_time = time.time() - START_TIME
    if elapsed_time >= MAX_RUN_TIME:
        sys.exit(0)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    check_runtime()
    context.user_data['mode'] = None
    keyboard = [[KeyboardButton("📹 YT VIDEO DOWNLOADER"), KeyboardButton("🎵 AUDIO DOWNLOADER")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="Select Mode From Keyboard")
    await update.message.reply_text("Hey ! Your Welcome, Give me any youtube video link...", reply_markup=reply_markup)

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

        status = await update.message.reply_text("⏳ Fetching fresh SOCKS5 proxy bank...")
        loop = asyncio.get_running_loop()
        socks5_pool = await loop.run_in_executor(None, fetch_socks5_only)
        
        if not socks5_pool:
            await status.edit_text("❌ Unable to load SOCKS5 repository. Try again!")
            return

        random.shuffle(socks5_pool)
        total_to_check = min(len(socks5_pool), 80) 
        
        info = None
        winning_proxy = None

        for index, proxy in enumerate(socks5_pool[:total_to_check], start=1):
            await status.edit_text(f"⚡ Testing SOCKS5 Route: [{index}/{total_to_check}]...")
            try:
                result = await loop.run_in_executor(None, test_single_proxy, text, proxy)
                if result and (result.get('title') or result.get('formats')):
                    info = result
                    winning_proxy = proxy
                    break
            except Exception:
                continue

        if not info or not winning_proxy:
            await status.edit_text("❌ Is batch ki saari SOCKS5 proxies busy mili. Dobara link bhejein!")
            return

        # 📹 VIDEO MODE
        if current_mode == 'video':
            try:
                video_title = info.get('title', 'Video File')
                thumbnail_url = info.get('thumbnail') 
                formats = info.get('formats', [])

                link_720p, link_360p, fallback_url = None, None, info.get('url')

                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        raw_url = f.get('url')
                        if raw_url:
                            if f.get('height') == 360: link_360p = raw_url
                            elif f.get('height') == 720: link_720p = raw_url

                links_text = ""
                if link_720p: links_text += f"🔹 <a href='{link_720p}'>👉 CLICK HERE TO DOWNLOAD (HD Quality) 👈</a>\n\n"
                if link_360p: links_text += f"🔹 <a href='{link_360p}'>👉 CLICK HERE TO DOWNLOAD (360p SD) 👈</a>\n\n"
                
                if not link_720p and not link_360p:
                    best_stream = fallback_url
                    if not best_stream and formats:
                        for fmt in reversed(formats):
                            if fmt.get('url') and ('googlevideo.com' in fmt.get('url') or 'manifest' in fmt.get('url')):
                                best_stream = fmt.get('url')
                                break
                    if best_stream: links_text += f"🔹 <a href='{best_stream}'>👉 CLICK HERE TO DOWNLOAD (Best Available Quality) 👈</a>\n\n"

                guide_caption = (
                    f"🎯 <b>Video Title:</b> {video_title}\n\n"
                    f"👇 <b>VIDEO DOWNLOAD LINKS:</b>\n{links_text}"
                    f"📖 <b>DOWNLOAD KAISE KAREIN?:</b>\n1️⃣ Upar diye gaye link par click karein.\n2️⃣ Browser mein file open hote hi long press karke download karein! 🚀"
                )

                await status.delete()
                if thumbnail_url:
                    await update.message.reply_photo(photo=thumbnail_url, caption=guide_caption, parse_mode="HTML")
                else:
                    await update.message.reply_text(text=guide_caption, parse_mode="HTML", disable_web_page_preview=True)
            except Exception as e:
                await status.edit_text(f"❌ Video link builder error: {e}")

        # 🎵 AUDIO MODE
        elif current_mode == 'audio':
            try:
                video_title = info.get('title', 'Audio File')
                await status.edit_text("📥 Extracting and streaming audio file safely...")
                
                unique_id = random.randint(1000, 9999)
                expected_file = f"audio_{unique_id}.m4a"

                # 🛠️ FIX: Runs the smart-pipeline that automatically drops proxies if Errno 104 occurs
                success = await loop.run_in_executor(None, download_audio_pipeline, text, winning_proxy, expected_file)

                if success and os.path.exists(expected_file) and os.path.getsize(expected_file) > 0:
                    await status.edit_text("📤 Uploading audio to chat...")
                    with open(expected_file, 'rb') as audio_file:
                        await update.message.reply_audio(audio=audio_file, title=video_title, performer="Yt Downloader")
                    await status.delete()
                else:
                    await status.edit_text("❌ Audio stream timed out on both proxy and fallback networks. Re-send link!")
                
                if os.path.exists(expected_file): os.remove(expected_file)
            except Exception as e:
                await status.edit_text(f"❌ Audio processing error: {e}")
    else:
        await update.message.reply_text("Bhai, sahi YouTube link bhejo!")

def main():
    app = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is starting with Bulletproof Audio Fallback Engine V45...")
    app.run_polling()

if __name__ == "__main__":
    main()
