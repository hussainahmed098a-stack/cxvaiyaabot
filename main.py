import os
import threading
from flask import Flask
from openai import OpenAI
import telebot

# =========================
# Environment Variables
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not found")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable not found")

# =========================
# Telegram Bot
# =========================
bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# Hugging Face OpenAI Client
# =========================
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# =========================
# Flask App (Render)
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram AI Bot Running!"

# =========================
# Commands
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 Hello!\n\nSend me any message and I will reply using DeepSeek AI."
    )

# =========================
# Chat Handler
# =========================
@bot.message_handler(func=lambda m: True)
def chat(message):
    try:
        thinking = bot.reply_to(message, "🤖 Thinking...")

        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1:fastest",
            messages=[
                {
                    "role": "user",
                    "content": message.text
                }
            ],
            max_tokens=1024
        )

        reply = response.choices[0].message.content

        if not reply:
            reply = "No response generated."

        bot.edit_message_text(
            chat_id=thinking.chat.id,
            message_id=thinking.message_id,
            text=reply[:4096]
        )

    except Exception as e:
        bot.reply_to(message, f"Error:\n{str(e)}")

# =========================
# Run Bot
# =========================
def run_bot():
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
