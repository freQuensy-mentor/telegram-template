import asyncio
import uuid
from math import lgamma

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from mixpanel import Mixpanel

import config
from loguru import logger
from db.User import User
from translations.get_phrase import get_phrase
from utils.login_requied import only_registered

bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher()

if config.MIXPANEL_TOKEN:
    mixpanel = Mixpanel(config.MIXPANEL_TOKEN)
else:
    mixpanel = None
    logger.warning("MIXPANEL_TOKEN is not set")


@dp.message(Command("start"))
async def start_handler(message: Message):
    assert message.from_user
    user, created = await User.aio_get_or_create(
        telegram_user_id=message.from_user.id, telegram_chat_id=message.chat.id
    )
    if created:
        if mixpanel:
            mixpanel.track(
                distinct_id=uuid.uuid4().hex,
                event_name="start",
                properties={
                    "telegram_chat_id": message.chat.id,
                    "telegram_user_id": message.from_user.id,
                    "user_id": user.user_id,
                },
            )
        await message.reply(get_phrase("welcome"))
        logger.info(f"User created: {user.user_id}")
    else:
        await message.reply(get_phrase("welcome_back"))


@dp.message(Command("do_something"))
@only_registered
async def help_handler(message: Message, db_user: User):
    assert message.from_user
    if mixpanel:
        mixpanel.track(
            distinct_id=uuid.uuid4().hex,
            event_name="do_something",
            properties={
                "telegram_chat_id": message.chat.id,
                "telegram_user_id": message.from_user.id,
                "user_id": db_user.user_id,
            },
        )
    logger.info(f"do_something for user {db_user.user_id}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
