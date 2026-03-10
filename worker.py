import os
import asyncio
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from scheduler import setup_scheduler

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

if not CHAT_ID:
    raise ValueError("CHAT_ID is not set")


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(),
    )

    setup_scheduler(bot, CHAT_ID)
    print("Scheduler worker started")

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
