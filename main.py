import os
import asyncio
from aiohttp import web
from pyrogram import Client, filters

API_ID = 29608422
API_HASH = "3db2f8e109301f02f5d9c8f10dd79244"
BOT_TOKEN = "8227731967:AAEmgSiywxmGfe1GYhj9RSqaOtMvaAgS99k"
BIN_CHANNEL = -1004450462812
DOMAIN_URL = "https://sr-file-bot-1868.onrender.com"

bot = Client(
    "video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

WATCH_HTML = """<!DOCTYPE html>
<html lang="en">
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
        <h2>Online Player</h2>
        <video controls autoplay name="media">
            <source src="{download_url}" type="video/mp4">
            Your browser does not support video playback.
        </video>
        <br>
        <a href="{download_url}" class="btn" download>Direct Download</a>
    </div>
</body>
</html>"""

async def download_handler(request):
    try:
        msg_id = int(request.match_info['msg_id'])
        msg = await bot.get_messages(BIN_CHANNEL, msg_id)
        if not msg or not (msg.video or msg.document):
            return web.Response(text="File not found in channel", status=404)

        media = msg.video or msg.document
        file_size = media.file_size
        file_name = getattr(media, 'file_name', 'video.mp4') or 'video.mp4'

        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={
                'Content-Type': media.mime_type or 'video/mp4',
                'Content-Length': str(file_size),
                'Content-Disposition': f'attachment; filename="{file_name}"',
                'Accept-Ranges': 'bytes',
            }
        )
        await response.prepare(request)

        async for chunk in bot.stream_media(msg, limit=0):
            await response.write(chunk)

        return response
    except Exception as e:
        return web.Response(text=f"Error: {str(e)}", status=500)

async def watch_handler(request):
    msg_id = request.match_info['msg_id']
    download_url = f"{DOMAIN_URL}/download/{msg_id}"
    html_content = WATCH_HTML.format(download_url=download_url)
    return web.Response(text=html_content, content_type='text/html')

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text("Welcome! Send any video file to get watch and download links.")

@bot.on_message((filters.video | filters.document) & filters.private)
async def handle_media(client, message):
    status_msg = await message.reply_text("Processing, please wait...", quote=True)
    try:
        forwarded_msg = await message.copy(chat_id=BIN_CHANNEL)
        msg_id = forwarded_msg.id

        watch_link = f"{DOMAIN_URL}/watch/{msg_id}"
        download_link = f"{DOMAIN_URL}/download/{msg_id}"

        reply_text = (
            "**Your File Links are Ready!**\n\n"
            f"**Watch Online:**\n{watch_link}\n\n"
            f"**Direct Download:**\n{download_link}"
        )

        await status_msg.edit_text(reply_text, disable_web_page_preview=True)
    except Exception as e:
        await status_msg.edit_text(f"Error:\n`{str(e)}`")

async def start_services():
    port = int(os.environ.get("PORT", 5000))
    app = web.Application()
    app.router.add_get('/watch/{msg_id}', watch_handler)
    app.router.add_get('/download/{msg_id}', download_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    await bot.start()
    print(">>> BOT AND SERVER STARTED <<<")
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(start_services())
