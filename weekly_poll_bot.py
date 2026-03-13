import telebot
from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# ================= ТВОИ ДАННЫЕ =================
TOKEN = os.getenv('TOKEN')
CHAT_ID = int(os.getenv('CHAT_ID'))
# ===============================================

# Русские названия месяцев
months_ru = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
    7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

bot = telebot.TeleBot(TOKEN)

def send_weekly_poll():
    # Считаем дату ЗАВТРА по Москве
    now_msk = datetime.utcnow() + timedelta(hours=3)
    tomorrow = (now_msk + timedelta(days=1)).date()
    date_str = f"{tomorrow.day} {months_ru[tomorrow.month]} {tomorrow.year}"

    QUESTION = f"Считаемся на футбол на {date_str} ⚽?"
    OPTIONS = ["Буду", "Нас двое", "Под вопросом", "Не смогу"]

    try:
        msg = bot.send_poll(
            chat_id=CHAT_ID,
            question=QUESTION,
            options=OPTIONS,
            is_anonymous=False,
            type="regular",
            allows_multiple_answers=False
        )
        print(f"✅ Опрос отправлен на {date_str}!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# Команда /poll для ручного запуска (тест)
@bot.message_handler(commands=['poll'])
def manual_poll(message):
    print(f"📨 Команда /poll от {message.from_user.username}")
    send_weekly_poll()

# Планировщик: КАЖДУЮ ПЯТНИЦУ в 10:00 по Москве
scheduler = BackgroundScheduler(timezone="Europe/Moscow")
scheduler.add_job(
    send_weekly_poll,
    trigger='cron',
    day_of_week='fri',
    hour=10,
    minute=0
)
scheduler.start()

print("🤖 Бот запущен! Следующий опрос — в эту пятницу в 10:00 по Москве")
print("💡 Для теста напиши /poll в группе")

# Держим бот онлайн + слушаем команды
try:
    bot.infinity_polling()
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
