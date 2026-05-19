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
from telegram import Update
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

# 🌐 FUNCTION: SOCKS5 proxies load karna
def load_socks5_pool():
    url = "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8')
            proxies = [line.strip() for line in html.splitlines() if line.strip()]
            if proxies:
                return proxies
    except Exception as e:
        logger.error(f"❌ Failed to fetch socks5.txt from GitHub: {e}")
    return []

# 🔥 PARALLEL ENGINE: Video details extract karna
def run_yt_dlp_parallel(url, proxy_url):
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'socket_timeout': 4, 
        'retries': 1,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'clients': ['tv', 'mweb', 'ios'],
                'skip': ['dash', 'hls']
            }
        }
    }
    if proxy_url:
        ydl_opts['proxy'] = proxy_url

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# 🔥 VOICE DOWNLOAD ENGINE: 🔥 NO-PROXY BYPASS (Timeout se bachne ke liye direct high-speed download)
def download_voice_locally(url, output_filename):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30, # High timeout backup
        'format': 'bestaudio/best',
        'outtmpl': output_filename,
        'nocheckcertificate': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
        }],
    }
    # No Proxy assigned here to get maximum GitHub Runner download speed (100MBps+)
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
    await update.message.reply_text(
        "Hey ! Your Welcome, Give me any youtube video link for Download I will give you the Download link of that video"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    check_runtime()
    url = update.message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        status = await update.message.reply_text("⏳ Connecting to SOCKS5 node parallelly...")
        
        loop = asyncio.get_running_loop()
        proxy_pool = await loop.run_in_executor(None, load_socks5_pool)
        
        if not proxy_pool:
            proxy_pool = [None]
        else:
            random.shuffle(proxy_pool)
            proxy_pool = proxy_pool[:10]

        info = None
        extracted_successfully = False
        selected_proxy = None

        for i, raw_proxy in enumerate(proxy_pool):
            proxy_url = f"socks5://{raw_proxy}" if raw_proxy else None
            
            try:
                if proxy_url:
                    await status.edit_text(f"⏳ Testing Node [{i+1}/{len(proxy_pool)}] parallelly...")
                
                info = await loop.run_in_executor(None, run_yt_dlp_parallel, url, proxy_url)
                if info:
                    extracted_successfully = True
                    selected_proxy = proxy_url
                    break 
            except Exception:
                continue 

        # RESPONSE BUILDER
        if extracted_successfully and info:
            try:
                video_title = info.get('title', 'Video File')
                thumbnail_url = info.get('thumbnail') 
                formats = info.get('formats', [])

                link_720p = None
                link_360p = None
                fallback_url = info.get('url')
                
                audio_url = None
                audio_size_bytes = 0

                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        raw_url = f.get('url')
                        if raw_url:
                            if f.get('height') == 360:
                                link_360p = raw_url
                            elif f.get('height') == 720:
                                link_720p = raw_url
                    
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                        audio_url = f.get('url')
                        audio_size_bytes = f.get('filesize') or f.get('filesize_approx') or 0

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

                # 🎛️ SMART AUDIO TO VOICE NOTE ROUTING
                audio_caption_part = ""
                send_voice_direct = False
                audio_size_mb = audio_size_bytes / (1024 * 1024) if audio_size_bytes else 0

                if audio_url:
                    if audio_size_mb > 50:
                        # 50MB se upar hone par clean direct text link dikhega
                        audio_caption_part = f"👇 <b>AUDIO DOWNLOAD LINK:</b>\n🔹 <a href='{audio_url}'>👉 CLICK HERE TO DOWNLOAD AUDIO (MP3/M4A) 👈</a>\n\n"
                    else:
                        send_voice_direct = True
                        # Clean execution: Ab caption mein koi faltu "Audio Status" text print nahi hoga!
                        audio_caption_part = ""
                
                # Cleaned Guide Layout without annoying logs
                guide_caption = (
                    f"🎯 <b>Video Title:</b> {video_title}\n\n"
                    f"👇 <b>VIDEO DOWNLOAD LINKS:</b>\n"
                    f"{links_text}"
                    f"{audio_caption_part}"
                    f"📖 <b>DOWNLOAD KAISE KAREIN? (EASY GUIDE):</b>\n"
                    f"1️⃣ Upar diye gaye blue color ke link text par click karein.\n"
                    f"2️⃣ Browser mein file open hote hi <b>Long Press</b> karein ya niche right side mein <b>3-dots (...)</b> par click karke <b>Download</b> daba dein! 🚀"
                )

                await status.delete()

                if thumbnail_url:
                    await update.message.reply_photo(photo=thumbnail_url, caption=guide_caption, parse_mode="HTML")
                else:
                    await update.message.reply_text(text=guide_caption, parse_mode="HTML", disable_web_page_preview=True)

                # 🔥 DIRECT VOICE NOTE UPLOAD ENGINE (If size <= 50MB)
                if send_voice_direct:
                    voice_status = await update.message.reply_text("📥 Processing Voice Note, sending directly to chat...")
                    
                    unique_id = random.randint(1000, 9999)
                    base_filename = f"voice_{unique_id}"
                    expected_file = f"{base_filename}.opus"
                    
                    try:
                        # 🚀 PIPELINE PATCH: Proxy hata di taaki GitHub network bypass speed se bina timeout download ho
                        await loop.run_in_executor(None, download_voice_locally, url, base_filename)
                        
                        if os.path.exists(expected_file) and os.path.getsize(expected_file) > 0:
                            with open(expected_file, 'rb') as voice_file:
                                await update.message.reply_voice(voice=voice_file)
                            await voice_status.delete()
                        else:
                            await voice_status.edit_text("⚠️ Voice note generation failed on runtime.")
                    except Exception as voice_err:
                        await voice_status.edit_text(f"⚠️ Voice conversion error: {voice_err}")
                    finally:
                        if os.path.exists(expected_file):
                            os.remove(expected_file)

            except Exception as send_error:
                await update.message.reply_text(f"❌ Sending Link Error: {send_error}")
        else:
            await status.edit_text("❌ Saari tested proxies blocked mili bhai. Dobara try karein!")
    else:
        await update.message.reply_text("Bhai, sahi YouTube video link bhejo!")

def main():
    app = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
    
    print("Bot is starting with Smart Voice Note Engine V31...")
    app.run_polling()

if __name__ == "__main__":
    main()
