import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import google.genai as genai

# ====================== ВПИШИ СВОИ ДАННЫЕ СЮДА ======================
TELEGRAM_TOKEN = 8771254894:AAEr1eRoMuL7Sz1IhH4--LQBPKnTcRJKVcU
GEMINI_API_KEY = AIzaSyAdu-sr4_Y3JkgBHNTQWKFXT958VALXH2g
CHAT_ID = 5305929867         # ←←← ТВОЙ TELEGRAM ID (число)

# ===================================================================

print("🚀 Запуск Тайлера...")

# Инициализация Gemini (новый пакет)
client = genai.Client(api_key=GEMINI_API_KEY)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Тайлер на связи.\nПиши что угодно, брат.")

@dp.message()
async def handle(message: types.Message):
    user_text = message.text.lower()
    
    try:
        # Если просит задание
        if any(word in user_text for word in ["задание", "task", "дай", "новое", "что сделать"]):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents="Придумай одно короткое и интересное задание. Максимум 2 предложения."
            )
            task = response.text[:800]
            await message.answer(f"📌 Новое задание:\n\n{task}")
        
        # Обычный ответ
        else:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Ты Тайлер — дерзкий коуч. Отвечай коротко и с характером. Клим написал: {message.text}"
            )
            await message.answer(response.text[:1600])
            
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("Понял тебя, Клим. Продолжай.")

# ====================== РАСПИСАНИЕ ======================
async def morning():
    await bot.send_message(CHAT_ID, "🌅 Доброе утро, Клим. Подъём, тигр.")

async def evening():
    await bot.send_message(CHAT_ID, "🕘 21:00. Задание сделал сегодня?")

async def main():
    scheduler.add_job(morning, 'cron', hour=7, minute=0)
    scheduler.add_job(evening, 'cron', hour=21, minute=0)
    scheduler.start()
    
    print("✅ Тайлер запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
