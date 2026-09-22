import os
import asyncio
from aiohttp import web
from pyrogram import Client, filters

API_ID = 29608422
API_HASH = "3db2f8e109301f02f5d9c8f10dd79244"
BOT_TOKEN = "8227731967:AAEmgSiywxmGfe1GYhj9RSqaOtMvaAgS99k"
BIN_CHANNEL = -1004450462812
DOMAIN_URL = "https://sr-file-bot-1868.onrender.com"

# Memory Dictionary for File Mapping
file_db = {}

bot = Client(
    "video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

WATCH_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Watch Video</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #0f0f0f; color: #fff; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 90vh; }}
        .container {{ width: 100%; max-width: 800px; background: #1f1f1f; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); text-align: center; }}
        video {{ width: 100%; height: auto; border-radius: 8px; margin-top: 15px; outline: none; background: #000; }}
        .btn {{ display: inline-block; margin-top: 20px; padding: 12px 25px; background: #0088cc; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px; transition: 0.3s; }}
        .btn:hover {{ background: #006699; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🎬 অনলাইন প্লেয়ার</h2>
        <video controls autoplay name="media">
            <source src="{download_url}" type="video/mp4">
            আপনার ব্রাউজার ভিডিওটি সাপোর্ট করছে না।
        </video>
        <br>
        <a href="{download_url}" class="btn" download>📥 ডিরেক্ট ডাউনলোড করুন</a>
    </div>
</body>
</html>
"""

async def stream_handler(request):
    try:
        file_id_key = request.match_info['file_id_key']
        if file_id_key not in file_db:
            return web.Response(text="❌ ফাইলটি সার্ভারে খুঁজে পাওয়া যায়নি! নতুন করে বটে ফাইল পাঠান।", status=404)
        
        file_id = file_db[file_id_key]['file_id']
        mime_type = file_db[file_id_key].get('mime_type', 'video/mp4')
        file_name = file_db[file_id_key].get('file_name', 'video.mp4')
        
        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={
                'Content-Type': mime_type,
                'Content-Disposition': f'inline; filename="{file_name}"',
                'Accept-Ranges': 'bytes',
            }
        )
        await response.prepare(request)
        
        async for chunk in bot.stream_media(file_id):
            await response.write(chunk)
            
        return response
    except Exception as e:
        return web.Response(text=f"এরর: {str(e)}", status=500)

async def watch_handler(request):
    file_id_key = request.match_info['file_id_key']
    download_url = f"{DOMAIN_URL}/download/{file_id_key}"
    html_content = WATCH_HTML.format(download_url=download_url)
    return web.Response(text=html_content, content_type='text/html')

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text("👋 স্বাগতম! যেকোনো বড় ভিডিও ফাইল পাঠালে আমি প্লে এবং ডাউনলোড লিঙ্ক তৈরি করে দেব।")

@bot.on_message((filters.video | filters.document) & filters.private)
async def handle_media(client, message):
    status_msg = await message.reply_text("🔄 প্রসেসিং হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...", quote=True)
    try:
        # কপি করার চেষ্টা এবং File ID নেওয়া
        forwarded_msg = await message.copy(chat_id=BIN_CHANNEL)
        media = forwarded_msg.video or forwarded_msg.document
        
        file_key = str(forwarded_msg.id)
        file_db[file_key] = {
            'file_id': media.file_id,
            'mime_type': media.mime_type or 'video/mp4',
            'file_name': getattr(media, 'file_name', 'video.mp4')
        }
        
        watch_link = f"{DOMAIN_URL}/watch/{file_key}"
        download_link = f"{DOMAIN_URL}/download/{file_key}"
        
        reply_text = (
            "✅ **আপনার ফাইলের লিঙ্ক তৈরি হয়ে গেছে!**\n\n"
            f"🎬 **অনলাইন দেখার লিঙ্ক (Watch Online):**\n🔗 {watch_link}\n\n"
            f"📥 **ডাউনলোড লিঙ্ক (Direct Download):**\n🔗 {download_link}"
        )
        
        await status_msg.edit_text(reply_text, disable_web_page_preview=True)
    except Exception as e:
        await status_msg.edit_text(f"❌ এরর এসেছে:\n`{str(e)}`\n\n(বটটি চ্যানেলে Admin হিসেবে যুক্ত আছে কিনা নিশ্চিত করুন)")

async def main():
    port = int(os.environ.get("PORT", 5000))
    app = web.Application()
    
    app.router.add_get('/watch/{file_id_key}', watch_handler)
    app.router.add_get('/download/{file_id_key}', stream_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    await bot.start()
    print(">>> BOT AND WEB SERVER STARTED <<<")
    await asyncio.Event().wait()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
