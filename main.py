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

GLOBAL_PROXY_POOL = []

def load_all_proxies_into_ram():
    global GLOBAL_PROXY_POOL
    socks5_url = "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt"
    socks4_url = "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks4.txt"
    
    temp_pool = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        req = urllib.request.Request(socks5_url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as response:
            for line in response.read().decode('utf-8').splitlines():
                if line.strip(): temp_pool.append(f"socks5://{line.strip()}")
    except Exception: pass

    try:
        req = urllib.request.Request(socks4_url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as response:
            for line in response.read().decode('utf-8').splitlines():
                if line.strip(): temp_pool.append(f"socks4://{line.strip()}")
    except Exception: pass

    if temp_pool:
        GLOBAL_PROXY_POOL = temp_pool
        logger.info(f"🔥 Pool Synced inside RAM: {len(GLOBAL_PROXY_POOL)} nodes ready.")

# ⚡ STEP 1: Fast Core Extractor (Sirf connection test karega bina heavy formats load kiye)
def extract_fast_core(url, proxy_url):
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'socket_timeout': 7.0,     # Balanced optimal timeout for free nodes
        'retries': 1,
        'extract_flat': True,      # 🔥 CRITICAL FIX: Heavy parsing disabled (No formats/subtitles download overhead)
        'skip_download': True,
        'nocheckcertificate': True,
        'proxy': proxy_url,
        'extractor_args': {
            'youtube': {
                'clients': ['tvhtml5', 'web_embedded', 'android', 'ios'],
                'skip': ['dash', 'hls']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# ⚡ STEP 2: Lazy Format Extractor (Jab proxy confirm ho jaye, tab formats nikalne ke liye)
def extract_full_formats(url, proxy_url):
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'socket_timeout': 15.0, 
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'nocheckcertificate': True,
        'proxy': proxy_url
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def download_audio_pipeline(url, proxy_url, output_filename):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 25,
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': output_filename,
        'nocheckcertificate': True,
        'proxy': proxy_url
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def check_runtime():
    if (time.time() - START_TIME) >= MAX_RUN_TIME:
        sys.exit(0)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    check_runtime()
    context.user_data['mode'] = None
    keyboard = [[KeyboardButton("📹 YT VIDEO DOWNLOADER"), KeyboardButton("🎵 AUDIO DOWNLOADER")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Hey ! Your Welcome, Give me any youtube video link...", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global GLOBAL_PROXY_POOL
    check_runtime()
    text = update.message.text

    if text == "📹 YT VIDEO DOWNLOADER":
        context.user_data['mode'] = 'video'
        await update.message.reply_text("📥 **YT VIDEO DOWNLOADER MODE ACTIVE**\n\nSend link:")
        return
    elif text == "🎵 AUDIO DOWNLOADER":
        context.user_data['mode'] = 'audio'
        await update.message.reply_text("📥 **AUDIO DOWNLOADER MODE ACTIVE**\n\nSend link:")
        return

    if "youtube.com" in text or "youtu.be" in text:
        current_mode = context.user_data.get('mode')
        if not current_mode:
            await update.message.reply_text("Bhai, pehle niche keyboard se ek mode select karo!")
            return

        status = await update.message.reply_text("⏳ Analyzing SOCKS Clusters in RAM...")
        
        if not GLOBAL_PROXY_POOL:
            load_all_proxies_into_ram()

        working_pool = list(GLOBAL_PROXY_POOL)
        random.shuffle(working_pool)

        # Build search matrix
        batch_size = 4  # Smaller intense concurrent batch to avoid local network chocking
        total_proxies_to_test = min(len(working_pool), 100)
        
        await status.edit_text("🚀 Scanning paths with Ultra-Light Connection Engine...")
        loop = asyncio.get_running_loop()
        
        winning_proxy = None
        basic_info = None

        for i in range(0, total_proxies_to_test, batch_size):
            current_batch = working_pool[i:i+batch_size]
            await status.edit_text(f"⚡ Testing Router Cluster [{i+batch_size}/{total_proxies_to_test}] (Smart-Hold)...")
            
            # Fire flat/light workers
            tasks = [loop.run_in_executor(None, extract_fast_core, text, proxy) for proxy in current_batch]
            
            try:
                # Increased timeout to 8.5 seconds to perfectly preserve working slow proxies
                for completed_task in asyncio.as_completed(tasks, timeout=8.5):
                    try:
                        result = await completed_task
                        if result and (result.get('title') or result.get('id')):
                            basic_info = result
                            winning_proxy = current_batch[tasks.index(completed_task)]
                            break
                    except Exception:
                        continue
            except asyncio.TimeoutError:
                pass
            
            if basic_info:
                break

        if not basic_info or not winning_proxy:
            await status.edit_text("❌ All paths currently choked. Please hit send again to shuffle a fresh batch!")
            return

        # 🎯 STEP 3: Proxy verified! Now lazily load complete download maps using the working proxy
        await status.edit_text("🎯 Path Verified! Building high-speed download streams...")
        
        try:
            info = await loop.run_in_executor(None, extract_full_formats, text, winning_proxy)
        except Exception:
            info = basic_info # Fallback to basic if heavy parsing breaks

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
                if link_720p: links_text += f"🔹 <a href='{link_720p}'>👉 CLICK HERE TO DOWNLOAD (HD 720p) 👈</a>\n\n"
                if link_360p: links_text += f"🔹 <a href='{link_360p}'>👉 CLICK HERE TO DOWNLOAD (SD 360p) 👈</a>\n\n"
                
                if not link_720p and not link_360p:
                    best_stream = fallback_url
                    if not best_stream and formats:
                        for fmt in reversed(formats):
                            if fmt.get('url') and ('googlevideo.com' in fmt.get('url') or 'manifest' in fmt.get('url')):
                                best_stream = fmt.get('url')
                                break
                    if best_stream: links_text += f"🔹 <a href='{best_stream}'>👉 CLICK HERE TO DOWNLOAD (Best Available) 👈</a>\n\n"

                guide_caption = (
                    f"🎯 <b>Video Title:</b> {video_title}\n\n"
                    f"👇 <b>VIDEO DOWNLOAD LINKS:</b>\n{links_text}"
                    f"📖 <b>GUIDE:</b> Long press blue link and select download!"
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
                await status.edit_text("📥 Extracting and streaming audio file via verified proxy...")
                
                unique_id = random.randint(1000, 9999)
                expected_file = f"audio_{unique_id}.m4a"

                await loop.run_in_executor(None, download_audio_pipeline, text, winning_proxy, expected_file)

                if os.path.exists(expected_file) and os.path.getsize(expected_file) > 0:
                    await status.edit_text("📤 Uploading audio player to Telegram...")
                    with open(expected_file, 'rb') as audio_file:
                        await update.message.reply_audio(audio=audio_file, title=video_title, performer="Yt Downloader")
                    await status.delete()
                else:
                    await status.edit_text("⚠️ Connection dropped during download stream. Try sending link again!")
                
                if os.path.exists(expected_file): os.remove(expected_file)
            except Exception as e:
                await status.edit_text(f"❌ Audio processing error: {e}")
    else:
        await update.message.reply_text("Bhai, sahi YouTube link bhejo!")

def main():
    load_all_proxies_into_ram()
    app = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is starting with Light-Weight Split Architecture V42...")
    app.run_polling()

if __name__ == "__main__":
    main()
