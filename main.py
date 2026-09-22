import os
import asyncio
from aiohttp import web
from pyrogram import Client, filters

API_ID = 29608422
API_HASH = "3db2f8e109301f02f5d9c8f10dd79244"
BOT_TOKEN = "8227731967:AAEmgSiywxmGfe1GYhj9RSqaOtMvaAgS99k"
BIN_CHANNEL = -1004450462812
DOMAIN_URL = "https://sr-file-bot-1868.onrender.com"

# in_memory=True যুক্ত করা হয়েছে যেন সেশন ফাইল নিয়ে Render-এ ঝামেলা না হয়
bot = Client(
    "video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Streamer</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: white; text-align: center; padding: 20px; }
        .container { max-width: 700px; margin: auto; background: #1e1e1e; padding: 25px; border-radius: 12px; }
        .btn { display: inline-block; padding: 12px 24px; margin: 10px; color: white; background-color: #0088cc; text-decoration: none; border-radius: 6px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎥 আপনার ভিডিও প্রস্তুত</h2>
        <p>ভিডিওটি স্ট্রিম বা ডাউনলোড করুন:</p>
        <a href="#" class="btn">▶ High Speed Stream / Download</a>
    </div>
</body>
</html>
"""

async def watch_handler(request):
    return web.Response(text=HTML_TEMPLATE, content_type='text/html')

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text("👋 স্বাগতম! যেকোনো বড় ভিডিও ফাইল পাঠালে আমি লিঙ্ক তৈরি করে দেব।")

@bot.on_message((filters.video | filters.document) & filters.private)
async def handle_media(client, message):
    status_msg = await message.reply_text("🔄 প্রসেসিং হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...", quote=True)
    try:
        forwarded_msg = await message.copy(chat_id=BIN_CHANNEL)
        msg_id = forwarded_msg.id
        web_link = f"{DOMAIN_URL}/watch/{msg_id}"
        await status_msg.edit_text(f"✅ **বড় ফাইলের লিঙ্ক তৈরি হয়েছে!**\n\n🔗 {web_link}")
    except Exception as e:
        await status_msg.edit_text(f"❌ এরর এসেছে:\n`{str(e)}`")

async def main():
    # Render-এর দেয়া ডাইনামিক PORT ব্যবহার করা হয়েছে
    port = int(os.environ.get("PORT", 5000))
    app = web.Application()
    app.router.add_get('/watch/{msg_id}', watch_handler)
    
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
