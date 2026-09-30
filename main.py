# ------------------------------------------------------------------
# Стандартная библиотека
# ------------------------------------------------------------------
import asyncio
import io
import json
import logging
import os
import random
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional

# ------------------------------------------------------------------
# Сторонние библиотеки
# ------------------------------------------------------------------
import aiohttp
from aiohttp import web
from faster_whisper import WhisperModel

from maxapi import Bot, Dispatcher, F
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.filters.callback_payload import CallbackPayload
from maxapi.filters.command import CommandStart
from maxapi.methods.set_commands import SetCommands
from maxapi.types import (
    BotCommand,
    BotStarted,
    CallbackButton,
    Command,
    MessageCallback,
    MessageCreated,
)
from maxapi.types.attachments.audio import Audio
from maxapi.types.command import BotCommand
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

# ------------------------------------------------------------------
# Локальные модули
# ------------------------------------------------------------------
import ai_check







print("123")



class Voice():


    def __init__(self) -> None:
        self.users = list()

        self.users_sent = list()

        # Создаём пустой словарь
        self.words = dict()

        # # Добавление: ключ = id, значение = слово
        # words[1] = "привет"
        # words[2] = "мир"
        # words[3] = "питон"




        
    def check_user(self, id):
        if id in self.users:
            return True
        return False

    def add_user(self, id):
        if id not in self.users:
            self.users.append(id)

    
        


    # def remove_user(self, id):
    #     pass


    def remove_user(self, id) -> None:
        """Удаляет пользователя из списков users и users_sent, если он там есть."""
        if id in self.users:
            self.users.remove(id)



    def Sremove_user(self, id) -> None:
        """Удаляет пользователя из списков users и users_sent, если он там есть."""

        if id in self.users_sent:
            self.users_sent.remove(id)


    def Scheck_user(self, id):
        if id in self.users_sent:
            return True
        return False

    def Sadd_user(self, id):
        if id not in self.users_sent:
            self.users_sent.append(id)

    
        


    def remove_word(self, word_id) -> None:
        """Удаляет слово из словаря по его id."""
        if word_id in self.words:
            del self.words[word_id]






voice = Voice()


TOKEN = os.getenv("MAX_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("MAX_BOT_TOKEN не задан")




# ──────────────────────────────────────────────
# Настройки Webhook
# ──────────────────────────────────────────────
# URL, по которому MAX будет стучаться (должен быть доступен из интернета)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://ваш-домен.com/webhook")
# Локальный адрес и порт, который слушает сервер
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
# Секретный токен (опционально, если MAX его поддерживает — защитит от левых запросов)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")




# цау цау

# model_path = "./whisper_model"
# Загружаем модель один раз при старте (можно вынести в отдельный поток)
model = WhisperModel(
    "small.en",#"large-v3",           # или "turbo", "medium" — зависит от железа
    device="cpu",        # или "cpu"
    compute_type="int8" # или "int8" для CPU
#    download_root=model_path
)


# async def download_voice_to_memory(attachment: Audio) -> io.BytesIO:
#     """Скачивает голосовое сообщение в BytesIO без сохранения на диск."""
#     async with aiohttp.ClientSession() as session:
#         async with session.get(attachment.download_url) as resp:
#             resp.raise_for_status()
#             data = await resp.read()
#             return io.BytesIO(data)



















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

print("ttt")
logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()
print("sss")

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





##################################





@dp.bot_started()
async def bot_started(event: BotStarted):

    await bot.send_message(
        chat_id=event.chat_id,
        text="""
👋 Привет! Я — тренажёр лексики изучения английского.

Что я умею:
• 📖 Давать слова для изучения
• 🔁 Проверять их с помощью голосовых сообщений
• 📊 Проверять правильность составления предложения

Начни с /learn, чтобы начать изучение, или /practice, чтобы перейти к проверке 
Для предложений используйте /sentence 
Если что-то непонятно к вашему распоряжению /help
""")



@dp.message_created(Command("start"))
async def cmd_start(event: MessageCreated):
    """
    Обработчик команды /start
    """
    voice.remove_user(event.message.sender.user_id) # type: ignore
    voice.Sremove_user(event.message.sender.user_id) # type: ignore
    await event.message.answer(
        "👋 Привет! Я — тренажёр лексики изучения английского.\n\n"
        "Что я умею:\n"
        "• 📖 Давать слова для изучения\n"
        "• 🔁 Проверять их с помощью голосовых сообщений\n"
        "• 📊 Проверять правильность составления предложения\n\n"
        "Начни с /learn, чтобы начать изучение, или /practice, чтобы перейти к проверке " \
        "Для предложений используйте /sentence "
        "Если что-то непонятно к вашему распоряжению /help"
    )




@dp.message_created(Command("help"))
async def cmd_help(event: MessageCreated):
    """
    Обработчик команды /start
    """
    voice.remove_user(event.message.sender.user_id) # type: ignore
    voice.Sremove_user(event.message.sender.user_id) # type: ignore
    await event.message.answer("""
📚 Помощь

Я помогу учить английский: слова, перевод, предложения.
А также дам AI рекомендации и распознаю ваши голосовые.

Режимы:
📖 Учить слова
🔤 Проверка слов
✍️ Составить предложение



Команды:
/start — начать сначала
/learn — учить слова
/practice — проверить слова
/sentence — составить и проверить предложение
/help — помощь

Всё бесплатно.""")






@dp.message_created(Command("learn"))
async def cmd_learn(event: MessageCreated):
    """

    """
    voice.remove_user(event.message.sender.user_id) # type: ignore
    voice.Sremove_user(event.message.sender.user_id) # type: ignore
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
    voice.Sremove_user(event.message.sender.user_id) # type: ignore
    if voice.check_user(event.message.sender.user_id): # type: ignore
        await event.message.answer("Вы уже находитесь в режиме проверки слов")
        return
        

    voice.add_user(event.message.sender.user_id) # type: ignore

    await event.message.answer("Вы выбрали режим проверки слов. Бот будет отправлять вам слова, а вы должны в голосовом сообщении сказать перевод."
    "(для наилучшего качества распознавания делайте паузы во время записи соообщения)")




    w = random_word()
    await event.message.answer(f"""

🔁 Начинаем проверку: 

🇷🇺 {w['translation']}



    """)
    print(f"{w['word']}")
    print(f"→ {w['translation']}")


    voice.words[event.message.sender.user_id] = w['word'] # type: ignore
        








@dp.message_created(Command("sentence"))
async def cmd_sentence(event: MessageCreated):
    """

    """
    voice.remove_user(event.message.sender.user_id) # type: ignore
    
    if voice.Scheck_user(event.message.sender.user_id): # type: ignore
        await event.message.answer("Вы уже находитесь в режиме составления предложения")
        return
        

    voice.Sadd_user(event.message.sender.user_id) # type: ignore

    await event.message.answer("Вы выбрали режим составления предложения. Бот будет отправлять вам слова, а вы должны придумать предложение и отправить его голосовым сообщением."
    "(для наилучшего качества распознавания делайте паузы во время записи соообщения)")




    w = random_word()
    await event.message.answer(f"""
🔁 Составьте предложение с этим словом: 
🇷🇺 {w['translation']}
            """)
    print(f"{w['word']}")
    print(f"→ {w['translation']}")


    voice.words[event.message.sender.user_id] = w['word'] # type: ignore
        



        
















async def download_audio_to_memory(attachment: Audio) -> io.BytesIO:
    """Скачивает аудио по payload.url в BytesIO."""
    url = attachment.payload.url          # ← вот здесь, а не download_url # type: ignore
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp: # type: ignore
            resp.raise_for_status()
            data = await resp.read()
            return io.BytesIO(data)

@dp.message_created()
async def handle_voice(event: MessageCreated):
    """Лёгкий хендлер: сразу отвечает MAX'у 200, работа — в фоне."""
    body = event.message.body
    if not body or not body.attachments:
        return
    asyncio.create_task(_process_voice(event))


async def _process_voice(event: MessageCreated):
    body = event.message.body
    if not body or not body.attachments:
        return                                 # не наше — молча выходим


    if not voice.check_user(event.message.sender.user_id) and not voice.Scheck_user(event.message.sender.user_id): # type: ignore
        await event.message.answer("Вы уже не находитесь в режиме использующем голосовые сообщения")
        return
        

    for att in body.attachments:
        if not isinstance(att, Audio):
            continue

        try:
            buffer = await download_audio_to_memory(att)


        except Exception as e:
            logging.exception("Не удалось скачать аудио")
            await event.message.answer(f"❌ Ошибка скачивания: {e}")
            return

        size = len(buffer.getvalue())
        # await event.message.answer(f"🎤 Аудио получено: {size} байт")
        # здесь можно отдать buffer в Whisper:
        # segments, info = model.transcribe(buffer, ...)

        # faster-whisper умеет работать с file-like объектами
        await event.message.answer(f"Начало распознавания голосового сообщения")
        segments, info = model.transcribe(
            buffer,
            language="en",          # можно не указывать — авто-детект
            beam_size=5,
            vad_filter=True,        # отсекает тишину
            vad_parameters=dict(min_silence_duration_ms=500),
            initial_prompt=voice.words[event.message.sender.user_id] # type: ignore
        )

        text = "".join(segment.text for segment in segments).strip()


        if voice.check_user(event.message.sender.user_id): # type: ignore
            if voice.words[event.message.sender.user_id] in text.lower(): # type: ignore
                await event.message.answer(f'Правильно! ✅ \nЭто слово "{voice.words[event.message.sender.user_id]}"') # type: ignore
            else:
                await event.message.answer(f'Неправильно! ❌ \nЭто слово "{voice.words[event.message.sender.user_id]}" \nТвой ответ: {text}') # type: ignore


            w = random_word()
            await event.message.answer(f"""
🔁 Следующее слово: 
🇷🇺 {w['translation']}
            """)
            print(f"{w['word']}")
            print(f"→ {w['translation']}")


            voice.words[event.message.sender.user_id] = w['word'] # type: ignore

        else:
            ## AI


            result = ai_check.check_sentence(sentence=text, word=voice.words[event.message.sender.user_id]) # type: ignore


            result = ai_check.format_result(result, text)


            await event.message.answer(str(result))

            w = random_word()
            await event.message.answer(f"""
🔁 Составьте предложение с этим словом: 
🇷🇺 {w['word']}
            """)
            print(f"{w['word']}")
            print(f"→ {w['translation']}")


            voice.words[event.message.sender.user_id] = w['word'] # type: ignore









        # await event.message.answer(f"📝 Распознанный текст:\n\n{text}")
        return


    # если вложение есть, но не Audio — можно тоже ответить
    await event.message.answer("Вложение не распознано как аудио.")




















# import logging

# @dp.message_created()
# async def debug_any(event: MessageCreated):
#     logging.info("=== DEBUG message_created ===")
#     logging.info("body: %s", event.message.body)
#     if event.message.body:
#         logging.info("text: %r", getattr(event.message.body, "text", None))
#         logging.info("attachments: %r", getattr(event.message.body, "attachments", None))
#         atts = getattr(event.message.body, "attachments", None) or []
#         for i, att in enumerate(atts):
#             logging.info("att[%d] type=%s dict=%s", i, type(att).__name__, att.__dict__)
#     logging.info("=== /DEBUG ===")
















# @dp.message_created(F.message.attachments)
# async def handle_voice(event: MessageCreated):
#     """Обработчик голосовых и аудио-сообщений."""
#     attachments = event.message.body.attachments
#     if not attachments:
#         return

#     for attachment in attachments:
#         if not isinstance(attachment, Audio):
#             continue

#         # 1. Скачиваем аудио в память (без сохранения на диск)
#         try:
#             audio_buffer = await download_voice_to_memory(attachment)
#         except Exception as e:
#             logging.error(f"Не удалось скачать аудио: {e}")
#             await event.message.answer("❌ Не удалось скачать голосовое сообщение.")
#             return

#         # 2. Здесь можно делать что угодно с аудио:
#         #    - отправить в Whisper для транскрипции
#         #    - сохранить в файл
#         #    - отправить обратно пользователю
#         # Для примера просто сообщим, что файл получен:
#         await event.message.answer(
#             f"🎤 Получено аудио: {attachment.duration} сек. "
#             f"({len(audio_buffer.getvalue())} байт)"
#         )
#         return

#     await event.message.answer("Пожалуйста, отправьте голосовое сообщение.")












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
#             language="eu",          # можно не указывать — авто-детект
#             beam_size=5,
#             vad_filter=True,        # отсекает тишину
#             vad_parameters=dict(min_silence_duration_ms=500)
#         )

#         text = "".join(segment.text for segment in segments).strip()

#         await event.message.answer(f"📝 Распознанный текст:\n\n{text}")
#         return

#     await event.message.answer("Пожалуйста, отправьте голосовое сообщение.")



















































# # ──────────────────────────────────────────────
# # Запуск
# # ──────────────────────────────────────────────
# async def main():

#     commands_to_set = [
#         BotCommand(name="start",      description="🚀 Запустить бота и пройти онбординг"),
#         BotCommand(name="learn",     description="📖 Выбрать тему для изучения"),
#         BotCommand(name="practice",     description="🔁 Начать сессию повторения слов"),
#         BotCommand(name="dictionary", description="📚 Мой личный словарь"),
#         BotCommand(name="progress",   description="📊 Мой прогресс"),
#         BotCommand(name="remind",     description="⏰ Настроить напоминания"),
#         BotCommand(name="help",       description="❓ Помощь и список команд"),
#     ]


#     setter = SetCommands(bot, commands=commands_to_set)
#     result = await setter.fetch()




#     # await dp.start_polling(bot) # polling вместо вебхуков





# # ──────────────────────────────────────────────
# # HTTP-обработчик входящих обновлений от MAX
# # ──────────────────────────────────────────────
# async def handle_webhook(request: web.Request) -> web.Response:
#     # Проверка секрета (если задан)
#     if WEBHOOK_SECRET:
#         if request.headers.get("X-Max-Secret") != WEBHOOK_SECRET:
#             return web.Response(status=403)

#     try:
#         event_json = await request.json()
#     except Exception:
#         return web.Response(status=400)

#     # Передаём событие в диспетчер — он вызовет нужный хендлер
#     await dp.process_update_webhook(event_json, bot)
#     return web.Response(status=200)


# async def healthcheck(_: web.Request) -> web.Response:
#     return web.Response(text="ok")




async def main() -> None:
    # 1. Регистрируем команды
    commands_to_set = [
        BotCommand(name="start",      description="🚀 Запустить бота"),
        BotCommand(name="learn",      description="📖 Начать изучение слов"),
        BotCommand(name="practice",   description="🔁 Начать сессию проверки слов"),
        BotCommand(name="sentence", description="📚 Проверка предложений"),
        BotCommand(name="help",       description="❓ Помощь и список команд"),
    ]
    setter = SetCommands(bot, commands=commands_to_set)
    await setter.fetch()

    # # 2. Поднимаем aiohttp-сервер
    # app = web.Application()
    # app.router.add_post("/webhook", handle_webhook)
    # app.router.add_get("/health", healthcheck)

    # runner = web.AppRunner(app)
    # await runner.setup()
    # site = web.TCPSite(runner, HOST, PORT)
    # await site.start()

    # print(f"🌐 Webhook-сервер запущен на http://{HOST}:{PORT}/webhook")

    # # 3. Сообщаем MAX, куда слать обновления
    # #    (в некоторых версиях maxapi метод может называться set_webhook / subscribe_webhook)
    # try:
    #     await bot.set_webhook(url=WEBHOOK_URL)
    #     print(f"✅ Webhook зарегистрирован: {WEBHOOK_URL}")
    # except AttributeError:
    #     print("⚠️ Метод set_webhook не найден — зарегистрируйте URL через API MAX вручную.")
    # except Exception as e:
    #     print(f"⚠️ Не удалось установить webhook: {e}")

    # # 4. Держим процесс живым
    # try:
    #     await asyncio.Event().wait()
    # finally:
    #     await runner.cleanup()




# async def main():
    # Запускает FastAPI-сервер на 0.0.0.0:8080
    await dp.handle_webhook(
        bot=bot,
        host='0.0.0.0',
        port=8080,
        # ssl_certfile="/certs/fullchain.pem",   # путь внутри контейнера
        # ssl_keyfile="/certs/privkey.pem",       # путь внутри контейнера
    )




if __name__ == '__main__':
    print("подготовка к запуску")
    asyncio.run(main())
    print("запуск")