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

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# ====================== ПАМЯТЬ ======================
user_data = {
    "name": "Клим",
    "mood_history": [],
    "last_task": "",
    "done_tasks": 0,
    "total_tasks": 0,
    "fail_streak": 0,
    "total_messages": 0
}

try:
    with open("user_data.json", "r", encoding="utf-8") as f:
        user_data.update(json.load(f))
except:
    pass

def save_data():
    with open("user_data.json", "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

# ====================== БЕЗОПАСНЫЙ ОТПРАВЩИК ======================
async def safe_send(message: types.Message, text: str):
    """Разбивает длинное сообщение и отправляет частями"""
    if not text:
        return
    MAX_LEN = 3900
    for i in range(0, len(text), MAX_LEN):
        part = text[i:i+MAX_LEN]
        try:
            await message.answer(part)
        except:
            await message.answer("Сообщение слишком длинное, но я тебя понял.")

# ====================== РАСПИСАНИЕ ======================
async def morning_message():
    await bot.send_message(
        chat_id=ВАШ_ID, 
        text="🌅 Доброе утро, Клим. Подъём, тигр. Сегодня будем работать или в тюфяки записываемся?"
    )

async def evening_check():
    text = "🕘 21:00. Ну что, чемпион... Задание сделал или опять пропустил?"
    await bot.send_message(chat_id=ВАШ_ID, text=text)

# ====================== ГЕНЕРАЦИЯ ЗАДАНИЯ ======================
async def generate_task():
    prompt = """
    Придумай одно конкретное, интересное и разнообразное задание.
    Чередуй типы: физуха, продуктивность, саморазвитие, дисциплина.
    Задание должно быть реалистичным. Не используй отжимания чаще 1 раза в 4 дня.
    Ответ должен быть не длиннее 600 символов.
    """
    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0.8})
        return response.text.strip()
    except:
        return "Прогуляйся 40 минут быстрым шагом + прочитай 15 страниц книги."

# ====================== ОСНОВНОЙ ХЕНДЛЕР ======================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Тайлер на связи. Теперь буду следить за тобой жёстче.")

@dp.message()
async def handle(message: types.Message):
    global user_data
    user_text = message.text
    lower = user_text.lower()

    user_data["total_messages"] += 1

    # Обновляем настроение
    if any(w in lower for w in ["настроение", "чувствую", "херово", "норм", "отлично", "заебался"]):
        user_data["mood_history"].append(user_text[:120])
        if len(user_data["mood_history"]) > 7:
            user_data["mood_history"].pop(0)

    # Генерация задания
    if any(word in lower for word in ["задание", "task", "дай", "новое", "придумай", "что делать"]):
        task = await generate_task()
        user_data["last_task"] = task[:500]
        user_data["total_tasks"] += 1
        save_data()
        
        await safe_send(message, f"Новое задание специально для тебя:\n\n{task}")
        return

    # Основной ответ от Тайлера
    prompt = f"""
Ты — Тайлер, дерзкий коуч и брат.
Отвечай естественно, с характером, подкалывай если нужно, но не переходи в токсик.
Не используй слова: пидорас, гей, и подобную токсичную лексику.

Инфо о Климе:
- Настроение: {user_data['mood_history'][-1] if user_data['mood_history'] else 'неизвестно'}
- Последнее задание: {user_data.get('last_task', 'нет')}
- Выполнено: {user_data['done_tasks']} из {user_data['total_tasks']}
- Пропуски подряд: {user_data['fail_streak']}

Клим написал: {user_text}
Отвечай живо и задавай вопросы.
"""

    try:
        response = model.generate_content(prompt)
        reply = response.text
        await safe_send(message, reply)
    except Exception as e:
        await message.answer("Понял тебя. Говори дальше.")

# ====================== ЗАПУСК ======================
async def main():
    scheduler.add_job(morning_message, 'cron', hour=7, minute=0)
    scheduler.add_job(evening_check, 'cron', hour=21, minute=0)
    scheduler.start()

    print("✅ Тайлер запущен (исправленная версия)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())