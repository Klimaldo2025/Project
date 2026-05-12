import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")

print("🚀 Бот запускается...")
print(f"CHAT_ID загружен: {CHAT_ID}")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

@dp.message(Command("start"))
async def start(message: types.Message):
    print(f"✅ Получена команда /start от {message.from_user.id}")
    await message.answer("Тайлер на связи. Пиши что угодно.")

@dp.message()
async def handle(message: types.Message):
    print(f"📨 Получено сообщение от {message.from_user.id}: {message.text[:50]}...")
    
    try:
        if any(w in message.text.lower() for w in ["задание", "task", "дай", "новое"]):
            await message.answer("Генерирую задание...")
            resp = model.generate_content("Придумай короткое задание в 1-2 предложения.")
            await message.answer(resp.text[:700])
        else:
            await message.answer("Понял тебя, Клим. Говори дальше.")
        print("✅ Ответ отправлен успешно")
    except Exception as e:
        print(f"❌ Ошибка при ответе: {e}")
        await message.answer("Бот жив, но что-то пошло не так.")

async def main():
    print("⏳ Запускаю polling...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка polling: {e}")

if __name__ == "__main__":
    asyncio.run(main())
