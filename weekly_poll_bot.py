import telebot
from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# ================= ТВОИ ДАННЫЕ =================
TOKEN = os.getenv('TOKEN')

# Группа 1: игра в четверг
CHAT_ID_1 = int(os.getenv('CHAT_ID_1', '-5163103543'))
# Группа 2: игра в субботу  
CHAT_ID_2 = int(os.getenv('CHAT_ID_2', '-5023630786'))
# ===============================================

# Русские названия месяцев
months_ru = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
    7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

bot = telebot.TeleBot(TOKEN)

# Словарь для хранения message_id закреплённых опросов
pinned_polls = {}

def send_weekly_poll(chat_id, poll_name):
    # Считаем дату ЗАВТРА по Москве
    now_msk = datetime.utcnow() + timedelta(hours=3)
    tomorrow = (now_msk + timedelta(days=1)).date()
    date_str = f"{tomorrow.day} {months_ru[tomorrow.month]} {tomorrow.year}"

    QUESTION = f"Считаемся на футбол на {date_str} ⚽?"
    OPTIONS = ["Буду", "Нас двое", "Под вопросом", "Не смогу"]

    try:
        msg = bot.send_poll(
            chat_id=chat_id,
            question=QUESTION,
            options=OPTIONS,
            is_anonymous=False,
            type="regular",
            allows_multiple_answers=False
        )
        print(f"✅ [{poll_name}] Опрос отправлен на {date_str}!")
        
        # Закрепляем опрос
        try:
            bot.pin_chat_message(chat_id, msg.message_id, disable_notification=True)
            pinned_polls[chat_id] = msg.message_id
            print(f"📌 [{poll_name}] Опрос закреплён!")
        except Exception as e:
            print(f"⚠️ [{poll_name}] Не удалось закрепить (нужны права админа): {e}")
            
    except Exception as e:
        print(f"❌ [{poll_name}] Ошибка: {e}")

def unpin_poll(chat_id, poll_name):
    try:
        if chat_id in pinned_polls:
            bot.unpin_chat_message(chat_id, pinned_polls[chat_id])
            del pinned_polls[chat_id]
            print(f"📍 [{poll_name}] Опрос откреплён!")
        else:
            bot.unpin_all_chat_messages(chat_id)
            print(f"📍 [{poll_name}] Все сообщения откреплены!")
    except Exception as e:
        print(f"⚠️ [{poll_name}] Не удалось открепить: {e}")

# Команда /poll для ручного запуска (тест)
@bot.message_handler(commands=['poll'])
def manual_poll(message):
    chat_id = message.chat.id
    print(f"📨 Команда /poll от {message.from_user.username} в группе {chat_id}")
    
    if chat_id == CHAT_ID_1:
        send_weekly_poll(CHAT_ID_1, "Группа 1 (чт)")
    elif chat_id == CHAT_ID_2:
        send_weekly_poll(CHAT_ID_2, "Группа 2 (сб)")
    else:
        send_weekly_poll(chat_id, "Неизвестная группа")

# Планировщик по Москве
scheduler = BackgroundScheduler(timezone="Europe/Moscow")

# Группа 1: опрос в среду 10:00, открепить в четверг 14:00
scheduler.add_job(
    lambda: send_weekly_poll(CHAT_ID_1, "Группа 1 (чт)"),
    trigger='cron',
    day_of_week='wed',
    hour=10,
    minute=0
)
scheduler.add_job(
    lambda: unpin_poll(CHAT_ID_1, "Группа 1 (чт)"),
    trigger='cron',
    day_of_week='thu',
    hour=14,
    minute=0
)

# Группа 2: опрос в пятницу 10:00, открепить в субботу 14:00
scheduler.add_job(
    lambda: send_weekly_poll(CHAT_ID_2, "Группа 2 (сб)"),
    trigger='cron',
    day_of_week='fri',
    hour=10,
    minute=0
)
scheduler.add_job(
    lambda: unpin_poll(CHAT_ID_2, "Группа 2 (сб)"),
    trigger='cron',
    day_of_week='sat',
    hour=14,
    minute=0
)

scheduler.start()

print("🤖 Бот запущен!")
print("📅 Группа 1: опрос в среду 10:00 → открепление в четверг 14:00")
print("📅 Группа 2: опрос в пятницу 10:00 → открепление в субботу 14:00")
print("💡 Для теста напиши /poll в группе")

# Держим бот онлайн + слушаем команды
try:
    bot.infinity_polling()
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
