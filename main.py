import os
from aiohttp import web
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Update, Message, BotCommand
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

from scheduler import get_weekly_focus_message, get_daily_result_message

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
PORT = int(os.getenv("PORT", "8080"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

if not WEBHOOK_HOST:
    raise ValueError("WEBHOOK_HOST is not set")

WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(),
)

dp = Dispatcher()
router = Router()

HELLO_TEXT = (
    "👋 Привіт, колеги!\n\n"
    "Я бот-нагадувач цієї групи.\n"
    "Моя задача — допомагати з регулярними апдейтами:\n\n"
    "📌 Щопонеділка о 09:00 нагадую скинути фокус на тиждень.\n"
    "📊 Щодня з понеділка по п’ятницю о 16:55 нагадую скинути результат за день.\n\n"
    "Доступні команди:\n"
    "/hello — коротко про мене\n"
    "/weekly — показати нагадування про фокус на тиждень\n"
    "/day — показати нагадування про результат за день\n\n"
    "Працюю тихо, стабільно і без зайвого шуму 🙂"
)


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(HELLO_TEXT)


@router.message(Command("hello"))
async def hello_handler(message: Message):
    await message.answer(HELLO_TEXT)


@router.message(Command("weekly"))
async def weekly_handler(message: Message):
    await message.answer(get_weekly_focus_message())


@router.message(Command("day"))
async def day_handler(message: Message):
    await message.answer(get_daily_result_message())


dp.include_router(router)


async def healthcheck(request):
    return web.Response(text="OK")


async def telegram_webhook(request):
    try:
        data = await request.json()
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
        return web.Response(text="ok")
    except Exception as e:
        print(f"Webhook error: {e}")
        return web.Response(status=500, text="error")


async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

    await bot.set_my_commands([
        BotCommand(command="hello", description="Про бота"),
        BotCommand(command="weekly", description="Нагадування про фокус на тиждень"),
        BotCommand(command="day", description="Нагадування про результат за день"),
    ])

    print(f"Webhook set to: {WEBHOOK_URL}")


async def on_shutdown(app):
    await bot.delete_webhook(drop_pending_updates=False)
    await bot.session.close()
    print("Bot shutdown complete")


def create_app():
    app = web.Application()
    app.router.add_get("/", healthcheck)
    app.router.add_post(WEBHOOK_PATH, telegram_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=PORT)
