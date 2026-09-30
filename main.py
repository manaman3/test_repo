# ------------------------------------------------------------------
# Стандартная библиотека
# ------------------------------------------------------------------
import asyncio
import io
import json
import logging
import os
import random
from functools import lru_cache


# ------------------------------------------------------------------
# Сторонние библиотеки
# ------------------------------------------------------------------
import aiohttp
from faster_whisper import WhisperModel

from maxapi import Bot, Dispatcher, F
from maxapi.context import MemoryContext
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


class Voice():


    def __init__(self) -> None:
        self.users = list()

        self.users_sent = list()

        # Создаём пустой словарь
        self.words = dict()

 
    def check_user(self, id):
        if id in self.users:
            return True
        return False

    def add_user(self, id):
        if id not in self.users:
            self.users.append(id)

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

# model_path = "./whisper_model"
model = WhisperModel(
    "small.en",#"large-v3",           # или "turbo", "medium" — зависит от железа
    device="cpu",        # или "cpu"
    compute_type="int8" # или "int8" для CPU
#    download_root=model_path
)



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


@dp.bot_started()
async def bot_started(event: BotStarted):

    await bot.send_message(
        chat_id=event.chat_id,
        text="""
👋 Привет! Я помогу тебе учить английскую лексику.

Что я умею:
• 📖 Давать новые слова по темам
• 🔁 Проверять перевод слов — текстом или голосом
• ✍️ Проверять, правильно ли ты составил предложение

Команды:
/learn — учить новые слова
/practice — проверять перевод слов
/sentence — составлять предложения
/help — помощь
/start — начать сначала

Начни с /learn 👇
""")

@dp.message_created(Command("start"))
async def cmd_start(event: MessageCreated):
    """
    Обработчик команды /start
    """
    voice.remove_user(event.message.sender.user_id) # type: ignore
    voice.Sremove_user(event.message.sender.user_id) # type: ignore
    await event.message.answer("""
👋 Привет! Я помогу тебе учить английскую лексику.

Что я умею:
• 📖 Давать новые слова по темам
• 🔁 Проверять перевод слов — текстом или голосом
• ✍️ Проверять, правильно ли ты составил предложение

Команды:
/learn — учить новые слова
/practice — проверять перевод слов
/sentence — составлять предложения
/help — помощь
/start — начать сначала

Начни с /learn 👇""")


@dp.message_created(Command("help"))
async def cmd_help(event: MessageCreated):
    """
    Обработчик команды /help
    """
    voice.remove_user(event.message.sender.user_id) # type: ignore
    voice.Sremove_user(event.message.sender.user_id) # type: ignore
    await event.message.answer("""
📚 Помощь

Я помогу учить английский: слова, перевод, предложения.
Подскажу, что улучшить, и распознаю голосовые.

Можно писать текстом или отправлять голосовые.

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

🔁 Начинаем изучение: 

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
    voice.Sremove_user(event.message.sender.user_id) # type: ignore
    if voice.check_user(event.message.sender.user_id): # type: ignore
        await event.message.answer("Вы уже находитесь в режиме проверки слов")
        return
    voice.add_user(event.message.sender.user_id) # type: ignore
    await event.message.answer("""✅ Режим проверки слов включён.

Я буду присылать вам слова, а вы — отвечать переводом.
Можно писать текстом или отправлять голосовое.

🎤 Для лучшего распознавания говорите с небольшими паузами.
Распознавание занимает до 30 секунд.""")


    w = random_word()
    await event.message.answer(f"""

🔁 Начинаем проверку: 

🇷🇺 {w['translation']}""")
    print(f"{w['word']}")
    print(f"→ {w['translation']}")


    voice.words[event.message.sender.user_id] = w['word'] # type: ignore
        

@dp.message_created(Command("sentence"))
async def cmd_sentence(event: MessageCreated):
    voice.remove_user(event.message.sender.user_id) # type: ignore
    if voice.Scheck_user(event.message.sender.user_id): # type: ignore
        await event.message.answer("Вы уже находитесь в режиме составления предложения")
        return
    voice.Sadd_user(event.message.sender.user_id) # type: ignore
    await event.message.answer("""✅ Режим составления предложения включён.

Я буду присылать вам слово, а вы — придумывать с ним предложение.
Можно написать текстом или отправить голосовым.

🎤 Для лучшего распознавания говорите с небольшими паузами.
Распознавание занимает до 30 секунд.""")

    w = random_word()
    await event.message.answer(f"""
🔁 Составьте предложение с этим словом: 
🇷🇺 {w['word']}
            """)
    print(f"{w['word']}")
    print(f"→ {w['translation']}")
    voice.words[event.message.sender.user_id] = w['word'] # type: ignore

async def download_audio_to_memory(attachment: Audio) -> io.BytesIO:
    """Скачивает аудио по payload.url в BytesIO."""
    url = attachment.payload.url          # type: ignore
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp: # type: ignore
            resp.raise_for_status()
            data = await resp.read()
            return io.BytesIO(data)

@dp.message_created()
async def handle_voice(event: MessageCreated):
    """Лёгкий хендлер: сразу отвечает MAX'у 200, работа — в фоне."""
    asyncio.create_task(_process_voice(event))


async def _process_voice(event: MessageCreated):
    body = event.message.body
    if not voice.check_user(event.message.sender.user_id) and not voice.Scheck_user(event.message.sender.user_id): # type: ignore
        await event.message.answer("Вы уже не находитесь в режиме использующем голосовые сообщения и текстовые сообщения")
        return

    if not body or not body.attachments:
        if event.message.body and event.message.body.text: 
            text = event.message.body.text
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
                await event.message.answer(f"Обработка предложения")

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


        return  # не наше — молча выходим

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
        return


    # если вложение есть, но не Audio — можно тоже ответить
    await event.message.answer("Вложение не распознано как аудио или текст. Для помощи воспользуйтесь /help")


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

    await dp.handle_webhook(
        bot=bot,
        host='0.0.0.0',
        port=8080
    )

if __name__ == '__main__':
    print("подготовка к запуску")
    asyncio.run(main())
    print("запуск")