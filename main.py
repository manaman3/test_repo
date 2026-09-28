import asyncio
import logging
from maxapi import Bot, Dispatcher, F
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types import MessageCreated, Command, BotStarted


from maxapi import Bot, Dispatcher, F
from maxapi.filters.callback_payload import CallbackPayload
from maxapi.filters.command import CommandStart
from maxapi.types import (
    CallbackButton,
    MessageCreated,
    MessageCallback,
)
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder





import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from maxapi import Bot, Dispatcher, F
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types import (
    MessageCreated,
    MessageCallback,
    CallbackButton,
    Command,
)
from maxapi.types.command import BotCommand
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.methods.set_commands import SetCommands
from sm_2 import Scheduler, Card






class Voice():


    def __init__(self) -> None:
        self.users = list()




        
    def check_user(self, id):
        if id in self.users:
            return True
        return False

    def add_user(self, id):
        if id not in self.users:
            self.users.append(id)
        


    def remove_user(self, id):
        pass

voice = Voice()

import json
import random
from functools import lru_cache








import asyncio
import io
import aiohttp
from maxapi import Bot, Dispatcher, F
from maxapi.types import MessageCreated
from maxapi.types.attachments.audio import Audio
from faster_whisper import WhisperModel



import os

TOKEN = os.getenv("MAX_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("MAX_BOT_TOKEN не задан")




# model_path = "./whisper_model"
# Загружаем модель один раз при старте (можно вынести в отдельный поток)
model = WhisperModel(
    "medium",#"large-v3",           # или "turbo", "medium" — зависит от железа
    device="cpu",        # или "cpu"
    compute_type="int8", # или "int8" для CPU
#    download_root=model_path
)


async def download_voice_to_memory(attachment: Audio) -> io.BytesIO:
    """Скачивает голосовое сообщение в BytesIO без сохранения на диск."""
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.download_url) as resp:
            resp.raise_for_status()
            data = await resp.read()
            return io.BytesIO(data)



















@lru_cache(maxsize=1)
def _load_words(path: str = "words.json") -> tuple[dict, ...]:
    """Кэширует словарь — файл читается один раз за всё время работы."""
    with open(path, "r", encoding="utf-8") as f:
        return tuple(json.load(f))


def random_word(path: str = "words.json") -> dict:
    return random.choice(_load_words(path))


def random_words(n: int = 5, path: str = "words.json") -> list[dict]:
    return random.sample(_load_words(path), min(n, len(_load_words(path))))



w = random_word()


logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()


class SchoolPayload(CallbackPayload, prefix="schoolpayload"):
    foo: str
    action: str




class StudentPayload(CallbackPayload, prefix="studentpayload"):
    bar: str
    value: int



# ──────────────────────────────────────────────
# Ветки состояний
# ──────────────────────────────────────────────
class TextDialog(StatesGroup):
    waiting_text = State()
    confirming   = State()

class VoiceDialog(StatesGroup):
    waiting_voice = State()
    confirming    = State()

# ──────────────────────────────────────────────
# Хелпер: пользователь уже в какой-то ветке?
# ──────────────────────────────────────────────
async def is_in_dialog(context: MemoryContext) -> bool:
    """True, если пользователь уже находится внутри любой ветки."""
    current = await context.get_state()
    return current is not None

# # ──────────────────────────────────────────────
# # /start — точка входа
# # ──────────────────────────────────────────────
# @dp.message_created(Command('start'))
# async def start(event: MessageCreated, context: MemoryContext):
#     # Если пользователь уже в диалоге — не сбрасываем его молча
#     if await is_in_dialog(context):
#         await event.message.answer(
#             "⚠️ Вы уже находитесь в активном диалоге.\n"
#             "Завершите его или отправьте /cancel, чтобы начать заново."
#         )
#         return

#     await event.message.answer(
#         "Выберите режим работы:\n"
#         "1️⃣ — Текстовый диалог\n"
#         "2️⃣ — Голосовой диалог\n\n"
#         "Отправьте «1» или «2»."
#     )





##################################





@dp.bot_started()
async def bot_started(event: BotStarted):


    kb = InlineKeyboardBuilder()
    kb.row(
        CallbackButton(
            text="Школьник",
            payload=SchoolPayload(foo="123", action="edit").pack(),
        ),
        CallbackButton(
            text="Студент",
            payload=StudentPayload(bar="abc", value=42).pack(),
        ),
    )
    # await event.message.answer("Нажми кнопку!", attachments=[kb.as_markup()])




    await bot.send_message(
        chat_id=event.chat_id,
        text="""
Привет! 👋
Я бот для изучения английского языка. Все режимы бесплатны.

Давай настроим обучение под тебя.
Выбери свой уровень английского:



Нажми на кнопку ниже 👇

""", attachments=[kb.as_markup()])



@dp.message_callback(SchoolPayload.filter())
async def on_first_callback(event: MessageCallback, payload: SchoolPayload):
    await event.answer(
        new_text=f"Вы выбрали уровень школьника"
    )


    #### логика сохранения уровня в бд (redis)



@dp.message_callback(StudentPayload.filter())
async def on_second_callback(event: MessageCallback, payload: StudentPayload):
    await event.answer(
        new_text=f"Вы выбрали уровень студента"
    )


    #### логика сохранения уровня в бд (redis)





@dp.message_created(Command("start"))
async def cmd_start(event: MessageCreated):
    """
    Обработчик команды /start
    commands_info: 🚀 Запустить бота и пройти онбординг
    """
    await event.message.answer(
        "👋 Привет! Я — тренажёр лексики изучения английского.\n\n"
        "Что я умею:\n"
        "• 📖 Подбирать слова по экзаменационным темам\n"
        "• 🔁 Повторять их по системе интервального повторения\n"
        "• 📊 Показывать твой прогресс\n\n"
        "Начни с /topics, чтобы выбрать тему, или /review, чтобы повторить слова."
    )







@dp.message_created(Command("learn"))
async def cmd_learn(event: MessageCreated):
    """

    """
    await event.message.answer("Вы выбрали режим изучения слов")


    kb = InlineKeyboardBuilder()
    kb.row(
        CallbackButton(
            text="Следующее слово",
            payload="next_lesson_word",
        )
    )


    w = random_word()
    await event.message.answer(f"""

🔁 Начинаем повторение: 

📖 {w['word']}
🔊 {w['transcription']}

🇷🇺 {w['translation']}

💬 {w['sentence']}

    """, attachments=[kb.as_markup()])
    print(f"{w['word']}  {w['transcription']}")
    print(f"→ {w['translation']}")
    print(f"Пример: {w['sentence']}")

        

    # import json
    # import random

    # with open("words.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)

    # words = data["words"]
    # print(random.choice(words))








@dp.message_callback(F.callback.payload.startswith("next_lesson_word"))
async def learn_callback_word(event: MessageCallback, context: MemoryContext) -> None:
    print("fewgerger")
    kb = InlineKeyboardBuilder()
    kb.row(
        CallbackButton(
            text="Следующее слово",
            payload="next_lesson_word",
        )
    )


    w = random_word()
    await event.edit(f"""

🔁 Начинаем повторение: 

📖 {w['word']}
🔊 {w['transcription']}

🇷🇺 {w['translation']}

💬 {w['sentence']}

    """, attachments=[kb.as_markup()])
    print(f"{w['word']}  {w['transcription']}")
    print(f"→ {w['translation']}")
    print(f"Пример: {w['sentence']}")







### practice







@dp.message_created(Command("practice"))
async def cmd_practice(event: MessageCreated):
    """

    """
    
    if voice.check_user(event.message.sender.user_id): # ignore
        await event.message.answer("Вы уже находитесь в режиме проверки слов")
        return
        

    voice.add_user(event.message.sender.user_id) # ignore

    await event.message.answer("Вы выбрали режим проверки слов")


    kb = InlineKeyboardBuilder()
    kb.row(
        CallbackButton(
            text="Следующее слово",
            payload="next_lesson_word",
        )
    )


    w = random_word()
    await event.message.answer(f"""

🔁 Начинаем повторение: 

📖 {w['word']}
🔊 {w['transcription']}

🇷🇺 {w['translation']}

💬 {w['sentence']}

    """, attachments=[kb.as_markup()])
    print(f"{w['word']}  {w['transcription']}")
    print(f"→ {w['translation']}")
    print(f"Пример: {w['sentence']}")

        

    # import json
    # import random

    # with open("words.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)

    # words = data["words"]
    # print(random.choice(words))








@dp.message_callback(F.callback.payload.startswith("next_practice_word"))
async def practice_callback_word(event: MessageCallback, context: MemoryContext) -> None:
    print("fewgerger")
    kb = InlineKeyboardBuilder()
    kb.row(
        CallbackButton(
            text="Следующее слово",
            payload="next_lesson_word",
        )
    )


    w = random_word()
    await event.edit(f"""

🔁 Начинаем повторение: 

📖 {w['word']}
🔊 {w['transcription']}

🇷🇺 {w['translation']}

💬 {w['sentence']}

    """, attachments=[kb.as_markup()])
    print(f"{w['word']}  {w['transcription']}")
    print(f"→ {w['translation']}")
    print(f"Пример: {w['sentence']}")












# @dp.message_created(F.message.attachments)
# async def handle_voice(event: MessageCreated):

#     print("qqqqqqqqqq")
#     for attachment in event.message.attachments:
#         if not isinstance(attachment, Audio):
#             continue

#         # 1. Скачиваем в память
#         audio_buffer = await download_voice_to_memory(attachment)

#         # 2. Транскрибируем напрямую из BytesIO
#         # faster-whisper умеет работать с file-like объектами
#         segments, info = model.transcribe(
#             audio_buffer,
#             language="ru",          # можно не указывать — авто-детект
#             beam_size=5,
#             vad_filter=True,        # отсекает тишину
#             vad_parameters=dict(min_silence_duration_ms=500)
#         )

#         text = "".join(segment.text for segment in segments).strip()

#         await event.message.answer(f"📝 Распознанный текст:\n\n{text}")
#         return

#     await event.message.answer("Пожалуйста, отправьте голосовое сообщение.")



















































# ──────────────────────────────────────────────
# Запуск
# ──────────────────────────────────────────────
async def main():

    commands_to_set = [
        BotCommand(name="start",      description="🚀 Запустить бота и пройти онбординг"),
        BotCommand(name="learn",     description="📖 Выбрать тему для изучения"),
        BotCommand(name="practice",     description="🔁 Начать сессию повторения слов"),
        BotCommand(name="dictionary", description="📚 Мой личный словарь"),
        BotCommand(name="progress",   description="📊 Мой прогресс"),
        BotCommand(name="remind",     description="⏰ Настроить напоминания"),
        BotCommand(name="help",       description="❓ Помощь и список команд"),
    ]


    setter = SetCommands(bot, commands=commands_to_set)
    result = await setter.fetch()




    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())