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
CHAT_ID = 5305929867

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Память
user_data = {"mood": "", "last_task": "", "done": 0, "total": 0, "fail": 0}

try:
    with open("user_data.json", "r", encoding="utf-8") as f:
        user_data = json.load(f)
except:
    pass

def save_data():
    with open("user_data.json", "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

# ====================== БЕЗОПАСНАЯ ОТПРАВКА ======================
async def safe_reply(message: types.Message, text: str):
    if len(text) > 1800:
        text = text[:1800] + "\n\n..."
    try:
        await message.answer(text)
    except:
        await message.answer("Понял тебя.")

# ====================== РАСПИСАНИЕ ======================
async def morning():
    await bot.send_message(chat_id=os.getenv("CHAT_ID"), text="🌅 Доброе утро, Клим. Готов работать или опять спать?")

async def evening():
    await bot.send_message(chat_id=os.getenv("CHAT_ID"), text="21:00. Задание сделал сегодня?")

# ====================== ОСНОВНОЙ ХЕНДЛЕР ======================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Тайлер на связи. Пиши.")

@dp.message()
async def handle(message: types.Message):
    global user_data
    text = message.text.lower()

    # Если просит задание
    if any(w in text for w in ["задание", "task", "дай", "новое", "что делать"]):
        try:
            resp = model.generate_content("Придумай короткое задание (макс 2 предложения).")
            task = resp.text[:600]
            user_data["last_task"] = task
            user_data["total"] += 1
            save_data()
            await safe_reply(message, f"Задание:\n\n{task}")
        except:
            await safe_reply(message, "Сделай сегодня 30-минутную прогулку + холодный душ.")
        return

    # Обычный ответ
    try:
        prompt = f"Ты Тайлер — дерзкий коуч. Отвечай коротко (макс 3-4 предложения). Подкалывай иногда. Клим написал: {message.text}"
        resp = model.generate_content(prompt)
        await safe_reply(message, resp.text)
    except:
        await safe_reply(message, "Понял. Что дальше?")

# ====================== ЗАПУСК ======================
async def main():
    # Используем переменную окружения вместо hardcoded ID
    scheduler.add_job(morning, 'cron', hour=7, minute=0)
    scheduler.add_job(evening, 'cron', hour=21, minute=0)
    scheduler.start()

    print("✅ Тайлер запущен на Railway")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
