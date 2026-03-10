import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from scheduler import setup_scheduler

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super-secret-path")
PORT = int(os.getenv("PORT", "8080"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

if not CHAT_ID:
    raise ValueError("CHAT_ID is not set")

if not WEBHOOK_HOST:
    raise ValueError("WEBHOOK_HOST is not set")

WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


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
    setup_scheduler(bot, CHAT_ID)
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
