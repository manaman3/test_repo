FROM python:3.11-slim

WORKDIR /app

# Сначала зависимости — для кэширования слоёв
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем код
COPY . .

# Если бот работает через long polling, EXPOSE не нужен.
# Если через webhook — раскомментируйте и укажите порт.
 EXPOSE 8080

CMD ["python", "main.py"]