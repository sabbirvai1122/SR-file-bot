import os
from flask import Flask, render_template_string
import telebot

# আপনার টেলিগ্রাম বট টোকেন
BOT_TOKEN = "8227731967:AAEmgSiywxmGfe1GYhj9RSqaOtMvaAgS99k"

# Render থেকে লিঙ্ক পাওয়ার পর নিচের ডোমেইনটি পরিবর্তন করে দেবেন
DOMAIN_URL = "https://your-app-name.onrender.com" 

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

video_db = {}

@bot.message_handler(content_types=['video'])
def handle_video(message):
    file_id = message.video.file_id
    file_size = message.video.file_size
    video_key = message.video.file_unique_id
    
    video_db[video_key] = {
        'file_id': file_id,
        'size': file_size
    }
    
    web_link = f"{DOMAIN_URL}/watch/{video_key}"
    bot.reply_to(message, f"✅ আপনার ভিডিও লিঙ্ক তৈরি হয়েছে:\n\n🔗 {web_link}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Player</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: white; text-align: center; padding: 20px; }
        .container { max-width: 700px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; }
        .btn { display: inline-block; padding: 10px 20px; margin: 10px; color: white; background-color: #0088cc; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎥 আপনার ভিডিও প্রস্তুত</h2>
        <p>নিচের বোতামে ক্লিক করে ভিডিওটি ডাউনলোড বা দেখতে পারেন:</p>
        <a href="#" class="btn">HD Quality (Original)</a>
        <a href="#" class="btn">SD Quality (360p)</a>
    </div>
</body>
</html>
"""

@app.route('/watch/<video_key>')
def watch_video(video_key):
    if video_key in video_db:
        return render_template_string(HTML_TEMPLATE)
    return "ভিডিও পাওয়া যায়নি!", 404

if __name__ == '__main__':
    import threading
    threading.Thread(target=lambda: bot.infinity_polling(skip_pending=True)).start()
    app.run(host='0.0.0.0', port=5000)
