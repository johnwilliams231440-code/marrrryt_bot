#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
import io
import threading
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image

# Force log output
sys.stdout.reconfigure(line_buffering=True)

print(f"[{datetime.now().isoformat()}] 📄 IMAGE TO PDF BOT STARTING...")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for health checks
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is running", 200

@flask_app.route('/health')
def health_check():
    return "OK", 200

# Get bot token
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ TELEGRAM_TOKEN not set!")
    sys.exit(1)

print(f"✅ Token found")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📄 *Image to PDF Bot*\n\nSend me an image and I'll convert it to PDF!",
        parse_mode="Markdown"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    
    try:
        await update.message.reply_text("🔄 Converting to PDF...")
        
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB
        if image.mode in ('RGBA', 'LA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        pdf_bytes = io.BytesIO()
        image.save(pdf_bytes, format='PDF')
        pdf_bytes.seek(0)
        
        await update.message.reply_document(
            document=pdf_bytes,
            filename=f"image_{user.id}.pdf",
            caption="✅ Converted to PDF!"
        )
        
        logger.info(f"PDF sent to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Failed to convert. Please try again.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

async def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_error_handler(error_handler)
    
    print("🤖 Bot is running!")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    def run_flask():
        port = int(os.environ.get("PORT", 5000))
        flask_app.run(host="0.0.0.0", port=port)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    asyncio.run(run_bot())
