from aiogram.types import Message

from db.User import User
from loguru import logger
from translations.get_phrase import get_phrase, DEFAULT_LANGUAGE


def only_registered(func, phrase_tag="user_not_registered"):
    async def wrapper(message: Message):
        user = await User.aio_get_or_none(
            telegram_user_id=message.from_user.id,
            telegram_chat_id=message.chat.id,
        )
        if not user:
            logger.info(f"User {message.from_user.id} not registered")
            await message.reply(get_phrase(phrase_tag, DEFAULT_LANGUAGE))
            return
        return await func(message, user)

    return wrapper
