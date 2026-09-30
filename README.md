# test_repo

```markdown
# 🎓 English Vocabulary Trainer Bot for MAX

Телеграм-подобный бот в мессенджере **MAX** для изучения английской лексики.
Помогает учить слова, проверять перевод (текстом и голосом) и проверять
правильность составления предложений через LLM.

---

## 📋 Содержание

- [Возможности](#возможности)
- [Команды бота](#команды-бота)
- [Как выглядит бот в чате](#как-выглядит-бот-в-чате)
- [Стек](#стек)
- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Установка Docker](#установка-docker)
- [Настройка Swap](#настройка-swap)
- [HTTPS через Certbot](#https-через-certbot)
- [Сертификаты Минцифры](#сертификаты-минцифры)
- [Установка проекта](#установка-проекта)
- [Регистрация вебхука](#регистрация-вебхука)
- [Управление](#управление)
- [Обновление](#обновление)
- [Пересборка](#пересборка)
- [Тестовый стенд](#тестовый-стенд)
- [Решение проблем](#решение-проблем)
- [Переменные окружения](#переменные-окружения)

---

## ✨ Возможности

- 📖 **Учить слова** — карточки по темам с переводом и примерами
- 🔁 **Проверка слов** — перевод слова текстом или голосом
- ✍️ **Составить предложение** — проверка грамматики через LLM
- 🎤 **Распознавание речи** — STT для голосовых сообщений
- 🧠 **AI-рекомендации** — подсказки, что улучшить
- 💬 **Текстовый и голосовой ввод** — на выбор ученика

---

## 🎮 Команды бота

| Команда | Описание |
|---|---|
| `/start` | Начать сначала |
| `/learn` | Учить новые слова по темам |
| `/practice` | Проверка перевода слов — текстом или голосом |
| `/sentence` | Составить и проверить предложение |
| `/menu` | Главное меню |
| `/help` | Помощь |

---

## 💬 Как выглядит бот в чате

### `/start`

```
👋 Привет! Я помогу тебе учить английскую лексику.

Что я умею:
• 📖 Давать новые слова по темам
• 🔁 Проверять перевод слов — текстом или голосом
• ✍️ Проверять, правильно ли ты составил предложение

Команды:
/learn — учить новые слова
/practice — проверять перевод слов
/sentence — составлять предложения
/menu — главное меню
/help — помощь
/start — начать сначала

Начни с /learn 👇
```

### `/help`

```
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

Всё бесплатно.
```

### `/practice`

```
✅ Режим проверки слов включён.

Я буду присылать тебе слова, а ты — отвечать переводом.
Можно писать текстом или отправлять голосовое.

🎤 Для лучшего распознавания говори с небольшими паузами.
Распознавание занимает до 30 секунд.
```

### `/sentence`

```
✅ Режим составления предложения включён.

Я буду присылать тебе слово, а ты — придумывать с ним предложение.
Можно написать текстом или отправить голосовым.

🎤 Для лучшего распознавания говори с небольшими паузами.
Распознавание занимает до 30 секунд.
```

### Проверка предложения

```
🔁 Составь предложение с этим словом:
🇷🇺 <перевод слова>
🇬🇧 <слово>

Пример: <пример употребления>
```

После ответа ученика бот возвращает:

```
🟡 Почти получилось

Твоё предложение: I want achieve good results
Исправлено: I want to achieve good results

Ошибки:
• «want achieve» → «want to achieve»
  После глагола 'want' используется инфинитив с частицей 'to'.

Оценка: 7/10

Ещё можно сказать:
• I want to get good results.
• I aim to achieve good results.

💡 Повтори использование инфинитива с частицей 'to'.
```

---

## 🛠 Стек

- **Python 3.11**
- **MAX Bot API** (`maxapi`)
- **OpenAI SDK** → GenAPI (OpenAI-совместимый прокси)
- **Pydantic**, **python-dotenv**
- **Docker**, **Docker Compose**
- **Nginx** + **Let's Encrypt** (Certbot)
- **Сертификаты Минцифры** — для российских API

---

## 📦 Требования

- VPS с Ubuntu 22.04+ (тестировалось на 24.04.2 LTS)
- Домен, указывающий на VPS
- Токен бота MAX
- Ключ GenAPI (или другого OpenAI-совместимого провайдера)

---

## 🚀 Быстрый старт

```bash
git clone https://github.com/<USERNAME>/<REPO>.git
cd <REPO>
cp .env.example .env
nano .env
docker compose up -d --build
```

---

## 🐳 Установка Docker

```bash
sudo apt update
sudo apt install -y docker.io git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker
```

Установка Docker Compose как CLI-плагина:

```bash
sudo mkdir -p /usr/local/lib/docker/cli-plugins

sudo curl -SL \
  https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose

sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

docker compose version
```

---

## 💾 Настройка Swap

Нужен для работы LLM/STT и Docker на слабых VPS.

```bash
# 1. Создание swap-файла на 2 ГБ
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile

# 2. Форматирование и активация
sudo mkswap /swapfile
sudo swapon /swapfile

# 3. Автозапуск при перезагрузке
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 4. Оптимизация под Docker
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# 5. Проверка
free -h
```

---

## 🔒 HTTPS через Certbot

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

sudo certbot --nginx \
  -d <ВАШ_ДОМЕН> \
  --register-unsafely-without-email \
  --agree-tos \
  --non-interactive
```

> Для продакшена укажите `--email your@mail.ru` вместо
> `--register-unsafely-without-email`.

---

## 🇷🇺 Сертификаты Минцифры

Нужны для корректной работы с российскими API (GenAPI, GigaChat, Yandex).

```bash
# 1. Перейти в директорию CA-сертификатов
cd /usr/local/share/ca-certificates

# 2. Скачать корневой и промежуточный сертификаты
curl -O https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt
curl -O https://gu-st.ru/content/lending/russian_trusted_sub_ca_pem.crt

# 3. Обновить хранилище доверенных сертификатов
update-ca-certificates
```

> Ссылки периодически обновляются. Актуальные — на сайте Минцифры.

---

## 📂 Установка проекта

```bash
git clone https://github.com/<USERNAME>/<REPO>.git
cd <REPO>

cp .env.example .env
nano .env

docker compose up -d --build
```

---

## 🔗 Регистрация вебхука

После запуска бота зарегистрируйте вебхук в MAX:

```bash
curl -X POST "https://platform-api2.max.ru/subscriptions" \
  -H "Authorization: <ВАШ_ТОКЕН>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://<ВАШ_ДОМЕН>/webhook",
    "update_types": ["message_created", "message_callback", "bot_started"]
  }' -k
```

> Флаг `-k` нужен, если используете самоподписанные или российские CA.

---

## 🎛 Управление

### Логи

```bash
docker compose logs            # вывести логи и выйти
docker compose logs --tail 50  # последние 50 строк
docker compose logs -f         # следить (Ctrl+C — выйти из слежения)
```

> `Ctrl+C` останавливает **только просмотр логов**, контейнер продолжает
> работать.

### Статус

```bash
docker compose ps
```

### Остановка

```bash
docker compose down    # остановить и удалить контейнеры
docker compose stop    # только остановить
```

---

## 🔄 Обновление

```bash
cd ~/<REPO>
git pull
docker compose up -d --build
docker compose logs -f
```

---

## 🧱 Пересборка

Полная пересборка без кэша:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 🖥 Тестовый стенд

Бот разрабатывался и тестировался на VPS со следующими характеристиками:

| Параметр | Значение |
|---|---|
| **ОС** | Ubuntu 24.04.2 LTS (Noble Numbat) |
| **Ядро** | 6.8.0-142-generic |
| **Архитектура** | x86_64 |
| **CPU** | 1 vCPU — Intel(R) Xeon(R) CPU E5-2620 0 @ 2.00GHz |
| **RAM** | 709 MiB |
| **Swap** | 2.4 GiB (из них 2 GiB — swap-файл) |
| **Диск** | 5.8 GiB (root) |
| **Docker** | docker.io + плагин docker compose |
| **Nginx** | reverse proxy + Certbot |
| **Домен** | hopto.org (No-IP) |

> Стенд минимальный — важно следить за свободным местом и swap.
> Подробнее см. раздел [Решение проблем](#решение-проблем).

---

## 🩺 Решение проблем

### Не хватает места на диске

```bash
docker system df
docker system prune -a
docker builder prune -a

# Если используется containerd
sudo systemctl stop docker docker.socket containerd
sudo rm -rf /var/lib/containerd/io.containerd.content.v1.content/*
sudo rm -rf /var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/*
sudo rm -rf /var/lib/docker/*
sudo systemctl start containerd docker
```

### Ошибка 502 Bad Gateway в nginx

Nginx не может достучаться до бота. Проверьте:

```bash
docker compose ps
docker compose logs bot --tail 100
docker compose exec nginx wget -qO- http://bot:8080/ || echo fail
```

В `nginx.conf` upstream должен ссылаться на **имя сервиса**:

```nginx
location /webhook {
    proxy_pass http://bot:8080/webhook;
}
```

А не на статический IP — он меняется после пересборки.

### Ошибка SSL при запросе к российскому API

Убедитесь, что установлены сертификаты Минцифры и контейнер их видит.
При необходимости — пересоберите образ.

### `json_schema` не поддерживается

Если LLM возвращает поля с другими именами (`grade` вместо `score`),
используется нормализация ответа — см. `bot/llm.py`.

### `curl` к API MAX не проходит

Проверьте, что используется `-k` (если CA не доверенный) и что в
`Authorization` нет лишних пробелов.

---

## 🔑 Переменные окружения

| Переменная | Обязательна | Описание |
|---|---|---|
| `MAX_BOT_TOKEN` | да | Токен бота MAX |
| `GENAPI_API_KEY` | да | Ключ GenAPI |
| `GENAPI_BASE_URL` | нет | По умолчанию `https://proxy.gen-api.ru/v1` |
| `GENAPI_MODEL` | нет | По умолчанию `gemini-2.5-flash-preview-04-17` |
| `WEBHOOK_URL` | да | Публичный URL вебхука |
| `WEBHOOK_PORT` | нет | По умолчанию `8080` |

---

## 📄 Лицензия

Учебный проект. Используйте свободно.
```

---

## Что заменено на транслит / плейсхолдеры

| Было | Стало |
|---|---|
| `hackatonmax2026.hopto.org` | `<ВАШ_ДОМЕН>` |
| `github.com/manaman3/test_repo` | `github.com/<USERNAME>/<REPO>` |
| `Authorization:токен` | `Authorization: <ВАШ_ТОКЕН>` |
| IP-адреса в логах | не упоминаются |
| `platform-api2.max.ru` | оставлен — это публичный эндпоинт MAX |

Если хочешь, могу отдельно вынести конфиг nginx и `.env.example` в README как отдельные файлы.