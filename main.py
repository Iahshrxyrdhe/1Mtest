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

# 🧠 GLOBAL RAM CACHE FOR BOTH PROXY TYPES
GLOBAL_PROXY_POOL = []

def load_all_proxies_into_ram():
    global GLOBAL_PROXY_POOL
    socks5_url = "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt"
    socks4_url = "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks4.txt"
    
    temp_pool = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 🎯 SOCKS5 Load System
    try:
        req = urllib.request.Request(socks5_url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as response:
            lines = response.read().decode('utf-8').splitlines()
            for line in lines:
                if line.strip():
                    temp_pool.append(f"socks5://{line.strip()}")
        logger.info("✅ SOCKS5 Bank synced inside RAM.")
    except Exception as e:
        logger.error(f"❌ SOCKS5 download fail: {e}")

    # 🎯 SOCKS4 Load System
    try:
        req = urllib.request.Request(socks4_url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as response:
            lines = response.read().decode('utf-8').splitlines()
            for line in lines:
                if line.strip():
                    temp_pool.append(f"socks4://{line.strip()}")
        logger.info("✅ SOCKS4 Bank synced inside RAM.")
    except Exception as e:
        logger.error(f"❌ SOCKS4 download fail: {e}")

    if temp_pool:
        GLOBAL_PROXY_POOL = temp_pool
        logger.info(f"🔥 Total Dynamic Proxies Active in RAM: {len(GLOBAL_PROXY_POOL)}")

# 🔥 SINGLE PROXY METRIC WORKER
def extract_metric(url, proxy_url):
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'socket_timeout': 5.0, # 🛠️ FIX: Timeout 1.5s se badha kar 5.0s kiya taaki slow-but-working proxy skip na ho!
        'retries': 1,          # Allow 1 quick retry if handshake drops
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

# 🔥 CORE FILE DOWNLOAD PIPELINE via THE WINNING PROXY
def download_audio_pipeline(url, proxy_url, output_filename):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 20, # Extra breathing room for slow downloads
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': output_filename,
        'nocheckcertificate': True,
        'proxy': proxy_url
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# 🛡️ AUTOMATIC AUTO-EXIT CHECKER
def check_runtime():
    elapsed_time = time.time() - START_TIME
    if elapsed_time >= MAX_RUN_TIME:
        logger.info("⏳ 170 minutes over! Safely exiting...")
        sys.exit(0)

# 🚀 WELCOME MESSAGE
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
    global GLOBAL_PROXY_POOL
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

        status = await update.message.reply_text("⏳ Syncing SOCKS4/5 Dynamic Pools...")
        
        if not GLOBAL_PROXY_POOL:
            load_all_proxies_into_ram()
            
        if not GLOBAL_PROXY_POOL:
            await status.edit_text("❌ Data pools are currently un-reachable. Try again in 10 seconds.")
            return

        # Shuffle dynamic pool completely
        working_pool = list(GLOBAL_PROXY_POOL)
        random.shuffle(working_pool)

        info = None
        winning_proxy = None
        
        # ⚡ BATCH CONFIG: 5 proxies ek sath hit karengi but stable window ke sath
        batch_size = 5
        total_proxies_to_test = min(len(working_pool), 120) # Extends search grid up to 120 nodes
        
        await status.edit_text("🚀 Scanning multi-proxy channels with Smart-Wait Engine...")

        loop = asyncio.get_running_loop()
        
        for i in range(0, total_proxies_to_test, batch_size):
            current_batch = working_pool[i:i+batch_size]
            await status.edit_text(f"⚡ Stable Testing Cluster [{i+batch_size}/{total_proxies_to_test}]...")
            
            # Fire 5 workers simultaneously
            tasks = [loop.run_in_executor(None, extract_metric, text, proxy) for proxy in current_batch]
            
            try:
                # 🛠️ FIX: Timeout badha kar 5.5s kiya taaki active links successfully capture ho saken
                for completed_task in asyncio.as_completed(tasks, timeout=5.5):
                    try:
                        result = await completed_task
                        if result:
                            info = result
                            winning_proxy = current_batch[tasks.index(completed_task)]
                            break
                    except Exception:
                        continue
            except asyncio.TimeoutError:
                pass
            
            if info:
                break # Match found, breakout instantly!

        if not info:
            await status.edit_text("❌ Sabhi tested routes tight block par hain. Ek baar link dobara bhej kar dekhein!")
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

                await status.edit_text("📥 Extracting and streaming audio file via verified proxy...")
                
                unique_id = random.randint(1000, 9999)
                expected_file = f"audio_{unique_id}.m4a"

                # Direct download mapping with the identical proxy that cracked the extraction
                await loop.run_in_executor(None, download_audio_pipeline, text, winning_proxy, expected_file)

                if os.path.exists(expected_file) and os.path.getsize(expected_file) > 0:
                    await status.edit_text("📤 Uploading audio player to Telegram...")
                    with open(expected_file, 'rb') as audio_file:
                        await update.message.reply_audio(audio=audio_file, title=video_title, performer="Yt Downloader")
                    await status.delete()
                else:
                    await status.edit_text("⚠️ Connection dropped by proxy line during data pipe. Re-send link!")
                
                if os.path.exists(expected_file):
                    os.remove(expected_file)

            except Exception as e:
                await status.edit_text(f"❌ Audio processing error: {e}")
    else:
        await update.message.reply_text("Bhai, sahi YouTube link bhejo ya keyboard se option select karo!")

def main():
    print("Pre-loading combined SOCKS4 & SOCKS5 databanks into RAM memory...")
    load_all_proxies_into_ram()

    app = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is starting with Smart-Wait Cluster Engine V41...")
    app.run_polling()

if __name__ == "__main__":
    main()
