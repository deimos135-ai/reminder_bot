from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo
from datetime import datetime

kyiv_tz = ZoneInfo("Europe/Kyiv")

weekly_focus_messages = [
    "📌 Доброго ранку, колеги! Будь ласка, скиньте свій фокус на тиждень.\n\n1. Головні задачі\n2. Пріоритети\n3. Можливі блокери",
    "🗓 Понеділок — час визначити фокус на тиждень. Напишіть, будь ласка, коротко ваші основні пріоритети.",
    "🚀 Колеги, стартуємо тиждень. Скиньте свій фокус: що головне, що в пріоритеті, де можуть бути ризики.",
    "📍 Нагадування: поділіться, будь ласка, своїм фокусом на цей тиждень.",
    "📝 Прошу скинути фокус на тиждень: ключові задачі, пріоритети, важливі цілі."
]

daily_result_messages = [
    "📊 Колеги, час підбити підсумок дня. Скиньте, будь ласка, свій результат за сьогодні.\n\n- Що зроблено\n- Що лишилось в роботі\n- Чи є блокери",
    "📝 Нагадування: поділіться коротко результатом за день.\n\n- Що зроблено\n- Що в роботі\n- Чи є труднощі",
    "✅ Будь ласка, скиньте ваш підсумок за день.\n\n- Виконано\n- У процесі\n- Блокери",
    "📌 Прошу написати результат за день: що вдалося зробити, що завершено, що лишилось у роботі.",
    "📣 Колеги, скиньте, будь ласка, короткий звіт за день."
]


def get_rotating_message(messages, start_date=None):
    if start_date is None:
        start_date = datetime(2025, 1, 1, tzinfo=kyiv_tz).date()
    today = datetime.now(kyiv_tz).date()
    index = (today - start_date).days % len(messages)
    return messages[index]


def get_weekly_focus_message():
    return get_rotating_message(weekly_focus_messages)


def get_daily_result_message():
    return get_rotating_message(daily_result_messages)


async def send_weekly_focus(bot, chat_id: int):
    now_kyiv = datetime.now(kyiv_tz).strftime("%Y-%m-%d %H:%M:%S")
    text = get_weekly_focus_message()
    try:
        print(f"[{now_kyiv}] Sending weekly focus reminder to chat {chat_id}")
        await bot.send_message(chat_id=chat_id, text=text)
        print(f"[{now_kyiv}] Weekly focus reminder sent")
    except Exception as e:
        print(f"[{now_kyiv}] Error sending weekly focus reminder: {e}")


async def send_daily_result(bot, chat_id: int):
    now_kyiv = datetime.now(kyiv_tz).strftime("%Y-%m-%d %H:%M:%S")
    text = get_daily_result_message()
    try:
        print(f"[{now_kyiv}] Sending daily result reminder to chat {chat_id}")
        await bot.send_message(chat_id=chat_id, text=text)
        print(f"[{now_kyiv}] Daily result reminder sent")
    except Exception as e:
        print(f"[{now_kyiv}] Error sending daily result reminder: {e}")


def setup_scheduler(bot, chat_id: int):
    scheduler = AsyncIOScheduler(timezone=kyiv_tz)

    scheduler.add_job(
        send_weekly_focus,
        trigger=CronTrigger(day_of_week="mon", hour=9, minute=0, timezone=kyiv_tz),
        args=[bot, chat_id],
        id="weekly_focus_reminder",
        replace_existing=True,
    )

    scheduler.add_job(
        send_daily_result,
        trigger=CronTrigger(day_of_week="mon-fri", hour=16, minute=55, timezone=kyiv_tz),
        args=[bot, chat_id],
        id="daily_result_reminder",
        replace_existing=True,
    )

    scheduler.start()
    print("Scheduler started")
    return scheduler
