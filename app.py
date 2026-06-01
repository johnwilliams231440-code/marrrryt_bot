#!/usr/bin/env python3
"""
IMAGE TO PDF TELEGRAM BOT
Converts images to PDF files
"""

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

# Setup logging
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

print(f"✅ Token found: {TOKEN[:5]}...")

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📄 *Image to PDF Bot*\n\n"
        "Send me an image and I'll convert it to PDF!\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show help\n\n"
        "*How to use:*\n"
        "Just send any image (JPG, PNG, WEBP)\n"
        "I'll send you back a PDF file\n\n"
        "✅ Supports multiple images at once!",
        parse_mode="Markdown"
    )

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *How to use:*\n\n"
        "1️⃣ Send one or more images\n"
        "2️⃣ Bot converts them to PDF\n"
        "3️⃣ Receive PDF file\n\n"
        "*Supported formats:*\n"
        "• JPG / JPEG\n"
        "• PNG\n"
        "• WEBP\n\n"
        "You can send multiple images in one message!",
        parse_mode="Markdown"
    )

# Handle photos
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Get the photo (Telegram sends different sizes, get the largest)
    photo = update.message.photo[-1]
    file = await photo.get_file()
    
    # Download image
    image_bytes = await file.download_as_bytearray()
    
    try:
        # Send processing message
        status_msg = await update.message.reply_text("🔄 Converting image to PDF...")
        
        # Open image with PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert RGB if needed (for PNG with transparency)
        if image.mode in ('RGBA', 'LA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save as PDF
        pdf_bytes = io.BytesIO()
        image.save(pdf_bytes, format='PDF')
        pdf_bytes.seek(0)
        
        # Send PDF
        await update.message.reply_document(
            document=pdf_bytes,
            filename=f"image_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            caption="✅ Converted to PDF!"
        )
        
        # Delete status message
        await status_msg.delete()
        logger.info(f"✅ PDF sent to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Failed to convert image. Please try again.")

# Handle document images (when user sends as file)
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    
    # Check if it's an image
    if document.mime_type not in ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']:
        await update.message.reply_text("⚠️ Please send an image file (JPG, PNG, or WEBP)")
        return
    
    user = update.effective_user
    file = await document.get_file()
    
    # Download image
    image_bytes = await file.download_as_bytearray()
    
    try:
        status_msg = await update.message.reply_text("🔄 Converting to PDF...")
        
        # Open image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB
        if image.mode in ('RGBA', 'LA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save as PDF
        pdf_bytes = io.BytesIO()
        image.save(pdf_bytes, format='PDF')
        pdf_bytes.seek(0)
        
        # Send PDF
        await update.message.reply_document(
            document=pdf_bytes,
            filename=f"image_{user.id}.pdf",
            caption="✅ Converted to PDF!"
        )
        
        await status_msg.delete()
        logger.info(f"✅ PDF sent to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Failed to convert. Please try again.")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# Run the bot
async def run_bot():
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    app.add_error_handler(error_handler)
    
    print("🤖 Bot is running!")
    print("💡 Send /start on Telegram")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    await asyncio.Event().wait()

# Main entry point
if __name__ == "__main__":
    def run_flask():
        port = int(os.environ.get("PORT", 5000))
        flask_app.run(host="0.0.0.0", port=port)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    asyncio.run(run_bot())#!/usr/bin/env python3
"""
IMAGE TO PDF TELEGRAM BOT
Converts images to PDF files
"""

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

# Setup logging
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

print(f"✅ Token found: {TOKEN[:5]}...")

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📄 *Image to PDF Bot*\n\n"
        "Send me an image and I'll convert it to PDF!\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show help\n\n"
        "*How to use:*\n"
        "Just send any image (JPG, PNG, WEBP)\n"
        "I'll send you back a PDF file\n\n"
        "✅ Supports multiple images at once!",
        parse_mode="Markdown"
    )

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *How to use:*\n\n"
        "1️⃣ Send one or more images\n"
        "2️⃣ Bot converts them to PDF\n"
        "3️⃣ Receive PDF file\n\n"
        "*Supported formats:*\n"
        "• JPG / JPEG\n"
        "• PNG\n"
        "• WEBP\n\n"
        "You can send multiple images in one message!",
        parse_mode="Markdown"
    )

# Handle photos
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Get the photo (Telegram sends different sizes, get the largest)
    photo = update.message.photo[-1]
    file = await photo.get_file()
    
    # Download image
    image_bytes = await file.download_as_bytearray()
    
    try:
        # Send processing message
        status_msg = await update.message.reply_text("🔄 Converting image to PDF...")
        
        # Open image with PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert RGB if needed (for PNG with transparency)
        if image.mode in ('RGBA', 'LA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save as PDF
        pdf_bytes = io.BytesIO()
        image.save(pdf_bytes, format='PDF')
        pdf_bytes.seek(0)
        
        # Send PDF
        await update.message.reply_document(
            document=pdf_bytes,
            filename=f"image_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            caption="✅ Converted to PDF!"
        )
        
        # Delete status message
        await status_msg.delete()
        logger.info(f"✅ PDF sent to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Failed to convert image. Please try again.")

# Handle document images (when user sends as file)
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    
    # Check if it's an image
    if document.mime_type not in ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']:
        await update.message.reply_text("⚠️ Please send an image file (JPG, PNG, or WEBP)")
        return
    
    user = update.effective_user
    file = await document.get_file()
    
    # Download image
    image_bytes = await file.download_as_bytearray()
    
    try:
        status_msg = await update.message.reply_text("🔄 Converting to PDF...")
        
        # Open image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB
        if image.mode in ('RGBA', 'LA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save as PDF
        pdf_bytes = io.BytesIO()
        image.save(pdf_bytes, format='PDF')
        pdf_bytes.seek(0)
        
        # Send PDF
        await update.message.reply_document(
            document=pdf_bytes,
            filename=f"image_{user.id}.pdf",
            caption="✅ Converted to PDF!"
        )
        
        await status_msg.delete()
        logger.info(f"✅ PDF sent to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Failed to convert. Please try again.")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# Run the bot
async def run_bot():
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    app.add_error_handler(error_handler)
    
    print("🤖 Bot is running!")
    print("💡 Send /start on Telegram")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    await asyncio.Event().wait()

# Main entry point
if __name__ == "__main__":
    def run_flask():
        port = int(os.environ.get("PORT", 5000))
        flask_app.run(host="0.0.0.0", port=port)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    asyncio.run(run_bot())
