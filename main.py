import asyncio
from aiohttp import web
from pyrogram import Client, filters

API_ID = 29608422
API_HASH = "3db2f8e109301f02f5d9c8f10dd79244"
BOT_TOKEN = "8227731967:AAEmgSiywxmGfe1GYhj9RSqaOtMvaAgS99k"

bot = Client("simple_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.all)
async def echo_all(client, message):
    await message.reply_text("✅ বট এখন লাইভ আছে এবং মেসেজ পাচ্ছে!")

async def handle_web(request):
    return web.Response(text="Server Running")

async def main():
    app = web.Application()
    app.router.add_get('/', handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()
    
    await bot.start()
    print(">>> BOT STARTED SUCCESSFULLY <<<")
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
