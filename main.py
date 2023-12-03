import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.markdown import hbold, hitalic
from db import Database
import random

# Bot token can be obtained via https://t.me/BotFather
TOKEN = ""

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

#Підключаємо і створюємо базу даних
database = Database("testbase.db")
database.create_table("Chats", statistic=False)
database.create_table("Statistic", statistic=True)

@dp.message(Command("answer"))
async def command_for_answer(message: types.Message):
    random_message = database.get_random_message("Chats", message.chat.id)
    if random_message:
        lower_text = random_message.lower()
        await message.answer(lower_text)


@dp.message(Command('stat'))
async def statistic(message: types.Message):
    get_statistic = database.get_statistic("Statistic", message.chat.id, message.from_user.id)
    await message.answer(f"🖐 Привіт, {hbold(message.from_user.full_name)} \n "
                         f"📩 Прийняв повідомлень: {hbold(get_statistic)} \n"
                         f"🔐 Чат: {hbold(message.chat.full_name)} \n"
                         f"🔰 {hitalic('Твоя статистика на цей чат')}")


@dp.message()
async def main_log(message: types.Message):
    chance_to_answer = random.randint(1, 100) #не обов'язкове
    #аби не було засора командами
    if message.text and message.text.startswith("/"):
        return
    # аби не було засора наліпками
    if message.sticker or message.video or message.caption:
        return
    #Підрахування шансів на відповідь, можна прибрати, це не обов'язкове
    if chance_to_answer > 60:
        random_message = database.get_random_message("Chats", message.chat.id)
        if random_message:
            #це для тексту з маленької букви, не обов'язкове
            lower_text = random_message.lower()
            await message.answer(lower_text)
    database.add_message("Chats", message.chat.id, message.text)
    database.add_count_messages("Statistic", message.chat.id, message.from_user.id)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
