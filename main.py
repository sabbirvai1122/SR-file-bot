import os
import asyncio
from aiohttp import web
from pyrogram import Client, filters

# আপনার দেওয়া তথ্য ও নতুন ডোমেইন
API_ID = 29608422
API_HASH = "3db2f8e109301f02f5d9c8f10dd79244"
BOT_TOKEN = "8227731967:AAEmgSiywxmGfe1GYhj9RSqaOtMvaAgS99k"
BIN_CHANNEL = -1004450462812
DOMAIN_URL = "https://sr-file-bot-1868.onrender.com"

bot = Client(
    "video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
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
        .container { max-width: 700px; margin: auto; background: #1e1e1e; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .btn { display: inline-block; padding: 12px 24px; margin: 10px; color: white; background-color: #0088cc; text-decoration: none; border-radius: 6px; font-weight: bold; }
        .btn:hover { background-color: #006699; }
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
    await message.reply_text("👋 স্বাগতম! যেকোনো ২-৩ GB পর্যন্ত ভিডিও ফাইল পাঠালে আমি প্লে/ডাউনলোড লিঙ্ক তৈরি করে দেব।")

@bot.on_message((filters.video | filters.document) & filters.private)
async def handle_media(client, message):
    try:
        forwarded_msg = await message.copy(chat_id=BIN_CHANNEL)
        msg_id = forwarded_msg.id
        web_link = f"{DOMAIN_URL}/watch/{msg_id}"
        await message.reply_text(f"✅ **বড় ফাইলের লিঙ্ক তৈরি হয়েছে!**\n\n🔗 {web_link}", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ কোনো সমস্যা হয়েছে: {str(e)}")

async def main():
    app = web.Application()
    app.router.add_get('/watch/{msg_id}', watch_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()
    
    await bot.start()
    print("Bot Started!")
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
